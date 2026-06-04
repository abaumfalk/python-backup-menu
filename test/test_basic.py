from pathlib import Path

from backup_menu.main import load_config


def test_load_config():
    config = load_config(Path('./config_example.py'))
    assert isinstance(config, tuple)
    assert len(config) == 3
    assert isinstance(config[0], list)
    assert isinstance(config[1], dict)
    assert isinstance(config[2], dict)
