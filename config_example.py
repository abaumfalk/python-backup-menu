from backup_menu.main import mount_manager, backup_borg

title = [
    "******************",
    "* BACKUP-STARTER *",
    "******************",
]

actions = {
    'mount local': lambda: mount_manager(['UUID=c71806bf-2bd1-443e-9f43-3bb610297b8a'], sudo=True),
    'borg backup': lambda repo_folder: backup_borg(
        'Silentmaxx-borg',
        [
            "/media/baumfalk/Daten/",
            "/home/baumfalk"],
        repo_folder,
        exclude_from='/home/baumfalk/backup/excludelist-borg',
    ),
}

options = {
    'borg backup to local disk': [
        'mount local',
        'borg backup',
    ]
}
