from backup_menu.main import mount_manager, backup_borg, mount_borg

title = [
    "******************",
    "* BACKUP-STARTER *",
    "******************",
]


actions = {
    'mount local': lambda: mount_manager(target='/media/baumfalk/Sicherung'),
    'borg backup': lambda repo_folder: backup_borg(
        'Silentmaxx-borg',
        [
            "/media/baumfalk/Daten/",
            "/home/baumfalk"],
        repo_folder,
        exclude_from='/home/baumfalk/backup/excludelist-borg',
    ),
    'mount Silentmaxx-borg': lambda repo_folder: mount_borg(
        repo_folder,
        'Silentmaxx-borg',
    ),
    'mount USB disk': lambda: mount_manager(target='/media/baumfalk/TOSHIBA_EXT4'),
}

options = {
    'borg backup to local disk': [
        'mount local',
        'borg backup',
    ],
    'borg backup to USB disk': [
        'mount USB disk',
        'borg backup',
    ],
    'mount local borg backup': [
        'mount local',
        'mount Silentmaxx-borg',
        'show mountpoint',
    ],
    'mount borg backup from USB disk': [
        'mount USB disk',
        'mount Silentmaxx-borg',
        'show mountpoint',
    ],
}
