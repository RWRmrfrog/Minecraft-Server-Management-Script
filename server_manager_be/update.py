import requests
import re
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Function to get the latest Minecraft Bedrock Dedicated Server download link for Windows
def get_latest_minecraft_bds_zip():
    url = "https://www.minecraft.net/en-us/download/server/bedrock"

    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("The request timed out.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        return None
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    match = re.search(r'href="(.*?bin-win.*?\.zip)"', response.text)
    
    if not match:
        raise Exception("Failed to find the Windows server ZIP download link.")
    
    download_link = match.group(1)
    
    if not download_link.startswith('http'):
        download_link = 'https://www.minecraft.net' + download_link

    print(f"Latest Download URL: {download_link}")
    
    return download_link

# Function to extract version number from file name
def extract_version_from_filename(filename):
    version_match = re.search(r'bedrock-server-(\d+\.\d+\.\d+\.\d+)\.zip', filename)
    if version_match:
        return version_match.group(1)
    return None

# Function to compare version numbers
def is_newer_version(local_version, remote_version):
    local_parts = list(map(int, local_version.split('.')))
    remote_parts = list(map(int, remote_version.split('.')))
    return remote_parts > local_parts

# Function to find the latest version in the 'downloads' folder
def get_latest_local_version(downloads_folder):
    latest_local_version = None
    latest_local_file = None

    for file_name in os.listdir(downloads_folder):
        if file_name.endswith('.zip'):
            version = extract_version_from_filename(file_name)
            if version:
                if not latest_local_version or is_newer_version(latest_local_version, version):
                    latest_local_version = version
                    latest_local_file = file_name

    return latest_local_version, latest_local_file

# Function to check if update is needed by comparing file names
def check_for_update(downloads_folder, download_url):
    # Extract the remote file name from the download URL
    remote_file_name = download_url.split('/')[-1]
    remote_version = extract_version_from_filename(remote_file_name)
    if not remote_version:
        raise Exception("Could not extract version from remote file name.")
    
    print(f"Remote version: {remote_version}")

    # Get the latest local version from the downloads folder
    latest_local_version, latest_local_file = get_latest_local_version(downloads_folder)
    
    if not latest_local_file:
        print("No local files found. Downloading the latest version.")
        return True

    print(f"Latest local version: {latest_local_version}")

    # Compare versions and determine if an update is needed
    if is_newer_version(latest_local_version, remote_version):
        print(f"Update needed: Newer version available. Remote: {remote_version}, Local: {latest_local_version}")
        return True
    else:
        print(f"No update needed. Local version ({latest_local_version}) is up to date.")
        return False

# Function to download the ZIP file into the 'downloads' folder
def download_zip(download_url, downloads_folder, session, headers):
    filename = os.path.join(downloads_folder, download_url.split('/')[-1])

    try:
        response = session.get(download_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        print(f"Downloaded: {filename}")

    except requests.exceptions.Timeout:
        print("The download timed out.")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error occurred during download: {e}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred during download: {err}")
    except Exception as e:
        print(f"An error occurred during download: {e}")
