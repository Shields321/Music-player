#maybe for this file allow users to download the requirements into a folder of their choosing
import os
import platform
import subprocess
import requests
import zipfile
import tarfile
import shutil
import sys

def check_ffmpeg_installed():
    """ Check if FFmpeg is already installed and accessible. """
    try:
        # Check if ffmpeg command is available
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0  # Return True if FFmpeg is found
    except FileNotFoundError:
        return False  # FFmpeg is not installed

def download_ffmpeg():
    if check_ffmpeg_installed():
        print("FFmpeg is already installed.")
        return  # Exit the function if FFmpeg is already installed

    os_type = platform.system()
    ffmpeg_url = ""
    
    if os_type == 'Windows':
        ffmpeg_url = "https://github.com/GyanD/codexffmpeg/releases/download/2024-10-31-git-87068b9600/ffmpeg-2024-10-31-git-87068b9600-full_build.zip"
        download_path = "ffmpeg-release-full.zip"
        extract_path = "ffmpeg"
    elif os_type == 'Darwin':  # macOS
        ffmpeg_url = "https://evermeet.bash.io/ffmpeg"
        download_path = "ffmpeg"
        extract_path = ""
    elif os_type == 'Linux':
        ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        download_path = "ffmpeg-release-amd64-static.tar.xz"
        extract_path = "ffmpeg"

    # Download the FFmpeg binary
    print(f"Downloading FFmpeg from {ffmpeg_url}...")
    response = requests.get(ffmpeg_url)

    # Check if the download was successful
    if response.status_code != 200:
        print(f"Failed to download FFmpeg. Status code: {response.status_code}")
        sys.exit(1)

    with open(download_path, 'wb') as f:
        f.write(response.content)

    # Validate the ZIP file (for Windows)
    if os_type == 'Windows':
        try:
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            print(f"Extracted FFmpeg to {extract_path}.")
        except zipfile.BadZipFile:
            print("Downloaded file is not a valid ZIP file.")
            sys.exit(1)
        
        # Look for ffmpeg.exe in the extracted files
        ffmpeg_executable = ""
        for root, dirs, files in os.walk(extract_path):
            if 'ffmpeg.exe' in files:
                ffmpeg_executable = os.path.join(root, 'ffmpeg.exe')
                break
        
        if not ffmpeg_executable:
            print("FFmpeg executable not found in the extracted files.")
            sys.exit(1)

    elif os_type == 'Darwin':
        ffmpeg_executable = download_path
    elif os_type == 'Linux':
        with tarfile.open(download_path, 'r:xz') as tar_ref:
            tar_ref.extractall(extract_path)
        ffmpeg_executable = os.path.join(extract_path, "ffmpeg")

    # Move FFmpeg binary to a standard location
    target_path = "/usr/local/bin/ffmpeg" if os_type != 'Windows' else os.path.join(os.environ["USERPROFILE"], "ffmpeg.exe")

    print(f"Moving FFmpeg to {target_path}...")
    shutil.move(ffmpeg_executable, target_path)

    # Add to system PATH
    update_system_path(target_path, os_type)

    # Cleanup: Delete the downloaded file
    cleanup_files(download_path, extract_path)

def cleanup_files(download_path, extract_path):
    """ Delete downloaded and extracted files. """
    try:
        if os.path.exists(download_path):
            os.remove(download_path)
            print(f"Deleted downloaded file: {download_path}")
        if os.path.isdir(extract_path):
            shutil.rmtree(extract_path)
            print(f"Deleted extracted directory: {extract_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def update_system_path(ffmpeg_path, os_type):
    if os_type == 'Windows':
        # Get current PATH
        current_path = os.environ["PATH"]
        # Check if FFmpeg is already in PATH
        if ffmpeg_path not in current_path:
            # Add FFmpeg to PATH
            new_path = current_path + ";" + os.path.dirname(ffmpeg_path)
            os.system(f'setx PATH "{new_path}"')
            print("FFmpeg added to PATH.")
        else:
            print("FFmpeg is already in PATH.")
    else:
        # Unix-like systems (Linux/macOS)
        shell_config_file = os.path.expanduser("~/.bashrc" if os.path.exists(os.path.expanduser("~/.bashrc")) else "~/.zshrc")
        with open(shell_config_file, 'a') as f:
            f.write(f'\nexport PATH="$PATH:{os.path.dirname(ffmpeg_path)}"\n')
        print("FFmpeg added to PATH. Please restart your terminal.")

if __name__ == "__main__":
    download_ffmpeg()
