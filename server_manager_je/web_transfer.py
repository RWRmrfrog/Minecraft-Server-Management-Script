import os
import datetime
from pathlib import Path
from zipfile import ZipFile
import shutil
import server_utils

def copy_world_to_web():
    # Dictionary to store backup files and their creation times
    backups = {}

    # Get all .zip files in the backups directory
    pathlist = Path(server_utils.backups_path).glob('*.zip')

    for path in pathlist:
        # Get creation time
        ti_c = os.path.getctime(path)
        # Convert the time into datetime
        c_ti = datetime.datetime.fromtimestamp(ti_c)

        backups[c_ti] = path

    # Sort the backups by creation time, newest first
    sorted_backups = {key: val for key, val in sorted(backups.items(), key=lambda ele: ele[0], reverse=True)}

    # Get the latest backup
    latest_backup_path = sorted_backups[next(iter(sorted_backups))]
    latest_backup_time = next(iter(sorted_backups))

    new_name = latest_backup_time.strftime("JE_%m-%d-%y")
    new_name = Path(new_name + ".zip")

    destination = server_utils.web_world_path + str(new_name)
    shutil.move(latest_backup_path, destination)