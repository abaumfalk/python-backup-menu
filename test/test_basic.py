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
