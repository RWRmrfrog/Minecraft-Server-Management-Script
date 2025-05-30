from pathlib import Path

world_path = f'../worlds/world'
backup_time = '04:00'

web_world_path = 'C:/Path/to/website/world_backups/'
dev_resource = '../development_resource_packs'
dev_behavior = '../development_behavior_packs'
backups_path = '../backups'
downloads_path = '../downloads'

server = None
isRunning = True

def mkdir(dirNames):
    for folder in dirNames:
        path = Path(f'../{folder}')
        path.mkdir(parents=True, exist_ok=True)