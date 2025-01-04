import subprocess
import time
from threading import Thread
import shutil
import schedule
import logging
from datetime import datetime
from pathlib import Path
from configparser import ConfigParser
import MCBE_wd_manager

# Load configuration from file
config = ConfigParser()
config.read('config.ini')

# Configuration
server_path = config.get('settings', 'server_path')
world_path = config.get('settings', 'world_path')
backup_time = config.get('settings', 'backup_time')

commandline_options = ["powershell.exe", '-ExecutionPolicy', 'Unrestricted', server_path + '/Update.ps1']
server = None
isRunning = True
input_thread = None
log_thread = None

# Setup logging
log_path = Path(server_path) / 'logs'
log_path.mkdir(parents=True, exist_ok=True)

def setup_logging():
    """ Setup logging with a new file """
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    log_filename = log_path / f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"Logging started in new file: {log_filename}")

def mkdir():
    for folder in ['logs', 'backups', 'downloads']:
        path = Path(server_path) / folder
        path.mkdir(parents=True, exist_ok=True)

def user_input():
    global isRunning
    while isRunning:
        command = input()
        if command.strip().lower() == 'stop':
            stop()
        elif command.strip().lower() == 'restart':
            restart_server()
        else:
            server.stdin.write(command.encode() + b'\n')
            server.stdin.flush()

def stop():
    global isRunning
    if server and server.poll() is None:  # Check if the server process is still running
        logging.info("Shutting down server...")
        try:
            server.stdin.write(b'stop\n')
            server.stdin.flush()
            time.sleep(5)
        except OSError as e:
            logging.error(f"Error while stopping server: {e}")
        finally:
            isRunning = False
            logging.info("Server Shutdown Successfully!")
            server.wait()  # Wait for server process to terminate completely
    else:
        logging.warning("Server is not running or already stopped.")

def restart_server():
    global server
    stop()
    setup_logging()  # Reset logging to a new file on restart
    backup()

def start():
    global server
    global isRunning
    isRunning = True
    setup_logging()  # Set up logging initially when the server starts
    try:
        server = subprocess.Popen([server_path + 'bedrock_server'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        logging.error("Server executable not found.")
        return
    mkdir()
    logging.info(f"Next Backup is at {backup_time}")
    start_input_thread()
    start_log_reading_thread()

def start_input_thread():
    global input_thread
    input_thread = Thread(target=user_input)
    input_thread.start()

def start_log_reading_thread():
    global log_thread
    log_thread = Thread(target=read_logs)
    log_thread.start()

def read_logs():
    while isRunning:
        line = server.stdout.readline()
        if not line:
            break
        txt = line.decode('utf-8').strip()
        print(txt)
        logging.info(txt)

def backup():
    global server
    logging.info("Stopping the server for backup...")
    stop()
    logging.info("Backing up...")
    backup_name = time.strftime("%m-%d-%y-%I%M")
    backup_path = Path(server_path) / 'backups' / backup_name
    shutil.make_archive(backup_path, 'zip', world_path)
    logging.info("Finished backup!")
    logging.info("Running Update Script...")
    process = subprocess.Popen(commandline_options, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    logging.info("Server Updated Successfully!")
    if (datetime.today() == datetime.today().replace(day=1)):
        MCBE_wd_manager.main()

    # Restart server after backup and update
    start()

# Initial startup
start()

# Schedule daily backups
schedule.every().day.at(backup_time).do(backup)
logging.info(f"Jobs: {len(schedule.get_jobs())}")

while True:
    schedule.run_pending()
    time.sleep(1)