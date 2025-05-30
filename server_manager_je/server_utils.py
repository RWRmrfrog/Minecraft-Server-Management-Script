from pathlib import Path

world_path = f'../world'
backup_time = '04:00'

web_world_path = 'C:/Path/to/website/world_backups/'
backups_path = '../backups'
jar_name = 'server.jar'

server = None
isRunning = True

def mkdir(dirNames):
    for folder in dirNames:
        path = Path(f'../{folder}')
        path.mkdir(parents=True, exist_ok=True)