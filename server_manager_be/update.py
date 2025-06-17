import requests
import re
import os

# Function to get the latest Minecraft Bedrock Dedicated Server download link for Windows
def get_latest_minecraft_bds_zip():
    API_URL = "https://net-secondary.web.minecraft-services.net/api/v1.0/download/links"
    DOWNLOAD_TYPE = "serverBedrockWindows"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching download URL: {e}")
        return None

    links = data.get("result", {}).get("links", [])
    for link in links:
        if link.get("downloadType") == DOWNLOAD_TYPE:
            download_url = link.get("downloadUrl")
            print(f"Successfully found download URL: {download_url}")
            return download_url

    print(f"No download link found for '{DOWNLOAD_TYPE}'. Available types: {[l.get('downloadType') for l in links]}")

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