"""
Module providing a general backup menu.
"""
import argparse
import importlib.util
import os
import subprocess
import sys
from contextlib import contextmanager, ExitStack
from datetime import datetime
from inspect import signature
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ContextManager, Callable


@contextmanager
def mount_manager(mount_args=None, target=None, sudo=False):
    """A context manager for filesystem mounts.

    :param mount_args: arguments for the mount command
    :param target: if not none, target will be appended to the mount command and thus used as mount point
    :param sudo: boolean indicating if root rights are required to execute the mount
    :return: yields the mount point
    """
    command = ['mount']
    if mount_args is not None:
        command += mount_args

    if target is not None:
        target = Path(target)
        if not target.is_dir():
            raise Exception(f"target mount point '{target}' does not exist")
        command.append(str(target))

    def prepend_sudo(cmd):
        return ['sudo'] + cmd

    def do_mount(cmd):
        if sudo:
            cmd = prepend_sudo(cmd)
        subprocess.run(cmd, check=True)

    def do_umount():
        cmd = ['umount', target]
        if sudo:
            cmd = prepend_sudo(cmd)

        while True:
            finished_process = subprocess.run(cmd, capture_output=True, check=False)
            if finished_process.returncode == 0:
                break
            input(f"Error {finished_process.stderr}, RETURN to retry")

    def try_yield(mount_point):
        try:
            yield Path(mount_point)
        finally:
            do_umount()

    if target is None:
        with TemporaryDirectory() as temp_dir:
            command.append(temp_dir)
            do_mount(command)
            yield from try_yield(Path(temp_dir))
    else:
        if not target.is_mount():
            do_mount(command)
        else:
            print(f"omitting mount - {target} is already a mountpoint")
        yield from try_yield(target)


class Borg:
    env = {'BORG_RELOCATED_REPO_ACCESS_IS_OK': 'yes'}
    borg = "/usr/bin/borg"

    @classmethod
    def backup_borg(cls, repo_name, source, repo_folder: Path, options=None):
        """Execute a borg backup.

        :param repo_name: name of the borg repo
        :param source: sources to be backed up
        :param repo_folder: path to the borg repo
        :param options: borg options, passed to the borg command as --option=value
        :return: name of the borg archive that was added to the repo
        """
        now = datetime.now()
        name = now.strftime("%Y%m%d-%H%M%S")

        if not isinstance(source, list):
            source = [source]
        options = options or {}

        cmd = [
            cls.borg,
            "create",
            "--stats",
            "--progress",
            f"{repo_folder / repo_name}::{name}",
            *source,
        ]
        for option, value in options.items():
            cmd.append(f"--{option}={value}")
        finished_process = subprocess.run(cmd, check=False, env=os.environ.update(cls.env))

        # check return code (0:ok, 1:warning)
        if finished_process.returncode not in [0, 1]:
            raise Exception(f"Command returned error-code {finished_process.returncode}")

        return name

    @classmethod
    @contextmanager
    def mount_borg(cls, repo_folder: Path, repo_name):
        """Context manager mounting a borg repo.

        :param repo_folder: folder containing the borg repo
        :param repo_name: name of the borg repo
        :return: yields the mount point where the repo was mounted
        """
        with TemporaryDirectory() as target:
            cmd = [
                cls.borg,
                "mount",
                f"{repo_folder / repo_name}",
                target
            ]
            subprocess.run(cmd, check=True, env=os.environ.update(cls.env))

            yield target

            cmd = [
                cls.borg,
                "umount",
                target
            ]
            while True:
                finished_process = subprocess.run(cmd, check=False, capture_output=True, env=os.environ.update(cls.env))
                if finished_process.returncode == 0:
                    break
                input(f"Error {finished_process.stderr}, RETURN to retry")


def show_mount_point(mount_point):
    """Show the content of a mount point and prompt for confirmation when finished.

    :param mount_point: path to the mount point
    """
    cmd = ['xdg-open', mount_point]
    subprocess.run(cmd, check=True)
    input(f"backup is mounted at {mount_point} - press ENTER to unmount")


class Runner:
    def __init__(self, actions):
        self.actions: dict[str, Callable] = {
            'show mountpoint': show_mount_point
        }
        self.actions.update(actions)

    def execute(self, action_names: list):
        ret = None
        with ExitStack() as stack:
            for action_name in action_names:
                print(f"executing '{action_name}'")
                action = self.actions[action_name]
                if isinstance(action, dict):
                    env = action.get('env', {})
                    for key, value in env.items():
                        os.environ[key] = value
                    action = action['action']
                sig = signature(action)
                if sig.parameters:
                    ret = action(ret)
                else:
                    ret = action()
                if isinstance(ret, ContextManager):
                    ret = stack.enter_context(ret)


class Menu:  # pylint: disable=too-few-public-methods
    """Class representing the menu-controlled application.
    """
    def __init__(self, title, options: dict[str, list]):
        self.title = title
        self.options = options

    def get_option(self) -> list:
        """Starts the menu app.
        """
        self._show_title()
        return self._get_option()

    def _show_title(self):
        for line in self.title:
            print(line)

    def _get_option(self) -> list:
        keys = list(self.options.keys())

        while True:
            print("Menu:")
            for idx, key in enumerate(keys):
                print(f"{idx+1}: {key}")

            line = input('\nChoice: ')
            try:
                if not line.isdigit():
                    raise IndexError

                idx = int(line) - 1
                if idx < 0:
                    raise IndexError

                return self.options[keys[idx]]
            except IndexError:
                print('Invalid choice!')
                print()
                continue

        return []  # should never be reached


def parse_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='config', type=Path, help="path to a configuration file", required=True)
    parser.add_argument('-o', dest='option', help="option to be executed (omits the menu)")

    return vars(parser.parse_args())


def load_config(config_file: Path):
    if not config_file.is_file():
        raise RuntimeError(f"could not find config file '{config_file}'")

    spec = importlib.util.spec_from_file_location('config', config_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load config file '{config_file}'")

    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    for item in ['title', 'actions', 'options']:
        if not hasattr(config, item):
            raise RuntimeError(f"could not find '{item}' in config file '{config_file}'")

    return config.title, config.actions, config.options


def main():
    """Entry point for the menu application.
    """
    args = parse_args()

    try:
        title, actions, options = load_config(args['config'])
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    try:
        run(args, title, actions, options)
    except RuntimeError as e:
        print(e)
        sys.exit(1)


def run(args: dict, title: list, actions: dict, options: dict):
    if args['option'] is None:
        menu = Menu(title, options)
        action_names = menu.get_option()
    else:
        name = args['option']
        if name not in options:
            raise RuntimeError(f"Invalid option '{name}'")
        action_names = options[name]

    runner = Runner(actions)
    runner.execute(action_names)

    print("Finished.")


if __name__ == "__main__":
    main()
