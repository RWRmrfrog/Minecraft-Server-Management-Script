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

    # Extract the zip file
    extract_path = latest_backup_path.stem

    with ZipFile(latest_backup_path, "r") as zf:
        zf.extractall(extract_path)

    print("Extracted latest backup...")

    # Copy resource & behavior packs
    resource_packs = Path(extract_path) / "resource_packs"
    shutil.copytree(server_utils.dev_resource, resource_packs)

    behavior_packs = Path(extract_path) / "behavior_packs"
    shutil.copytree(server_utils.dev_behavior, behavior_packs)

    print("Copied packs...")

    # Generate a new name for the zip file
    new_name = latest_backup_time.strftime("BE_%m-%d-%y")

    # Zip up the file once again
    shutil.make_archive(new_name, "zip", extract_path)

    # Delete the extracted folder
    shutil.rmtree(extract_path)

    # Rename the zip file to .mcworld
    mcworld = Path(new_name + ".zip")
    mcworld = mcworld.rename(mcworld.with_suffix(".mcworld"))

    print(f"New .mcworld file created: {mcworld}")

    destination = server_utils.web_world_path + str(mcworld)
    shutil.move(mcworld, destination)


#unmined-cli web render --world="%APPDATA%\.minecraft\saves\New World" --output="%USERPROFILE%\Desktop\MyMap"