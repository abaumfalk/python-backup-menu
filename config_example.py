from backup_menu.main import mount_manager, Borg

title = [
    "******************",
    "* BACKUP-STARTER *",
    "******************",
]


actions = {
    'mount local': lambda: mount_manager(target='/media/baumfalk/Sicherung'),
    'borg backup': lambda repo_folder: Borg.backup_borg(
        'Silentmaxx-borg',
        [
            "/media/baumfalk/Daten/",
            "/home/baumfalk"],
        repo_folder,
        exclude_from='/home/baumfalk/backup/excludelist-borg',
    ),
    'mount Silentmaxx-borg': lambda repo_folder: Borg.mount_borg(
        repo_folder,
        'Silentmaxx-borg',
    ),
    'mount USB disk': lambda: mount_manager(target='/media/baumfalk/TOSHIBA_EXT4'),
    'mount NAS': lambda: mount_manager(target='/media/baumfalk/nas/Arno'),
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
    'borg backup to NAS': [
        'mount NAS',
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
    'mount borg backup from NAS': [
        'mount NAS',
        'mount Silentmaxx-borg',
        'show mountpoint',
    ],
}
