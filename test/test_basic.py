import re
from pathlib import Path

import pytest

from backup_menu.main import load_config, run


def test_load_config():
    config = load_config(Path('./config_example.py'))
    assert isinstance(config, tuple)
    assert len(config) == 3
    assert isinstance(config[0], list)
    assert isinstance(config[1], dict)
    assert isinstance(config[2], dict)


def test_invalid_option():
    title, actions, options = load_config(Path('./config_example.py'))
    with pytest.raises(RuntimeError):
        run({'option': 'invalid'}, title, actions, options)


def test_dry_run(capfd):
    title, actions, options = load_config(Path('./config_example.py'))
    run({'option': 'borg backup to local disk', 'dry_run': True}, title, actions, options)
    out, err = capfd.readouterr()
    assert err == ''

    expected = [
        "executing 'mount local'",
        "dry-run: ['mount', '/media/baumfalk/Sicherung']",
        "executing 'borg backup'",
        re.compile("dry-run: \['/usr/bin/borg', 'create', '--stats', '--progress', "
            "'/media/baumfalk/Sicherung/Silentmaxx-borg::.*', "
            "'/media/baumfalk/Daten/', '/home/baumfalk', "
            "'--exclude-from=/home/baumfalk/backup/excludelist-borg'\], return .*"),
        "dry-run: ['umount', PosixPath('/media/baumfalk/Sicherung')]",
        "Finished.",
    ]

    for idx, line in enumerate(out.splitlines()):
        exp = expected[idx]
        if isinstance(exp, str):
            assert exp == line
        else:
            assert exp.match(line)
