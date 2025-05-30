from subprocess import Popen, PIPE
import time
from threading import Thread
import shutil
import schedule
import logging as log
from datetime import datetime
from pathlib import Path
import web_transfer
import server_utils

def start_server():
    setup_logging()  # Set up logging initially when the server starts
    
    try:
        server_utils.server = Popen(['java', '-Xmx2G', '-Xms1G', '-jar', server_utils.jar_name, 'nogui'], cwd='../', stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True, bufsize=1)
    except FileNotFoundError:
        log.error('Java server jar not found or Java not installed.')
        return
    
    log.info(f'Next Backup is at {server_utils.backup_time}')

    server_utils.isRunning = True
    
    Thread(target=user_input).start()
    Thread(target=read_logs).start()

def stop_server():
    if server_utils.server and server_utils.server.poll() is None:  # Check if the server process is still running
        log.info('Shutting down server...')

        try:
            server_utils.server.stdin.write('stop\n')
            server_utils.server.stdin.flush()
            server_utils.server.wait()
        except OSError as err:
            log.error(f'Error while stopping server: {err}')
        finally:
            server_utils.isRunning = False
            log.info('Shutdown server successfully!')
    else:
        log.warning('Server is not running or already stopped.')

def setup_logging():
    for handler in log.root.handlers[:]:
        log.root.removeHandler(handler)
    
    log_filename = f"../logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    
    log.basicConfig(filename=log_filename, level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    log.info(f'Logging started in new file: {log_filename}')

def user_input():
    while server_utils.isRunning:
        command = input()
        if command.strip().lower() == 'stop':
            stop_server()
        elif command.strip().lower() == 'restart':
            restart_server()
        else:
            server_utils.server.stdin.write(command + '\n')
            server_utils.server.stdin.flush()

def read_logs():
    while server_utils.isRunning:
        line = server_utils.server.stdout.readline()
        if not line: break  # Exit loop if no more output

        txt = line.strip()

        print(txt, flush=True)  # ✅ Forces real-time output
        log.info(txt)  # ✅ Log to file and console

def backup():
    log.info('Backing up...')
    backup_name = time.strftime('%m-%d-%y-%I%M')
    backup_path = Path(server_utils.backups_path) / backup_name
    shutil.make_archive(backup_path, 'zip', server_utils.world_path)
    log.info('Finished backup!')
    if datetime.now().day == 1 and datetime.now().hour == 4:
        web_transfer.copy_world_to_web()

def restart_server():
    stop_server()
    setup_logging()
    backup()
    start_server()
        
def main():
    # Initial startup
    server_utils.mkdir(['logs', 'backups'])
    start_server()

    # Schedule daily backups
    schedule.every().day.at(server_utils.backup_time).do(restart_server)
    log.info(f'Jobs: {len(schedule.get_jobs())}')

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()