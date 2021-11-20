import argparse
import importlib.util
import subprocess
import sys
from contextlib import contextmanager, ExitStack
from datetime import datetime
from inspect import signature
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ContextManager


@contextmanager
def mount_manager(mount_options, sudo=False):
    def prepend_sudo(c):
        return ['sudo'] + c

    with TemporaryDirectory() as target:
        cmd = ['mount', *mount_options, target]
        if sudo:
            cmd = prepend_sudo(cmd)
        subprocess.run(cmd, check=True)
        try:
            yield Path(target)
        finally:
            cmd = ['sudo', '-S', 'umount', target]
            if sudo:
                cmd = prepend_sudo(cmd)
            subprocess.run(cmd, check=True)


def backup_borg(repo_name, source, repo_folder, exclude_from=None):
    now = datetime.now()
    name = now.strftime("%Y%m%d-%H%M%S")

    if not isinstance(source, list):
        source = [source]

    cmd = [
        "/usr/bin/borg",
        "create",
        "--list",
        "--filter=AME",
        f"{repo_folder / repo_name}::{name}",
        *source,
    ]
    if exclude_from is not None:
        cmd.append(f"--exclude-from={exclude_from}")
    env = {
        'BORG_RELOCATED_REPO_ACCESS_IS_OK': 'yes',
    }
    fp = subprocess.run(cmd, check=False)

    # check return code (0:ok, 1:warning)
    if fp.returncode not in [0, 1]:
        raise Exception(f"Command returned error-code {fp.returncode}")

    return name


@contextmanager
def mount_borg(repo_folder, repo_name):
    with TemporaryDirectory() as target:
        cmd = [
            "/usr/bin/borg",
            "mount",
            f"{repo_folder / repo_name}",
            target
        ]
        subprocess.run(cmd, check=True)

        yield target

        cmd = [
            "/usr/bin/borg",
            "umount",
            target
        ]
        while True:
            fp = subprocess.run(cmd, check=False, capture_output=True)
            if fp.returncode == 0:
                break
            input(f"Error {fp.stderr}, RETURN to retry")


def show_mount_point(mount_point):
    cmd = ['xdg-open', mount_point]
    subprocess.run(cmd, check=True)
    input(f"backup is mounted at {mount_point} - press ENTER to unmount")


class Runner:
    def __init__(self, title, actions, options):
        self.title = title

        self.actions = {
            'show mountpoint': show_mount_point
        }
        self.actions.update(actions)

        self.options = options

    def start(self):
        self._show_title()
        option = self._get_option()

        ret = None
        with ExitStack() as stack:
            for action_name in option:
                print(f"executing '{action_name}'")
                action = self.actions[action_name]
                sig = signature(action)
                if sig.parameters:
                    ret = action(ret)
                else:
                    ret = action()
                if isinstance(ret, ContextManager):
                    ret = stack.enter_context(ret)

        input("Ready - press ENTER to finish.")

    def _show_title(self):
        for t in self.title:
            print(t)

    def _get_option(self):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='config', type=Path, help="path to a configuration file", required=True)

    args = parser.parse_args()
    config_file = args.config
    if not config_file.is_file():
        print(f"could not find config file '{config_file}'")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location('config', config_file)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    title = getattr(config, 'title', [])
    actions = config.actions
    options = config.options

    r = Runner(title, actions, options)
    r.start()
