import os
import time
import psutil
import shutil
import logging
from utils import limited_os_walk, get_all_drives, get_network_usage, get_disk_usage, inform
import requests

CHECK_INTERVAL = 30   # seconds
THRESHOLD = 102400      # 1 MB/s

# --- Clean folder utility ---
# def clean_folder(folder):
#     try:
#         for item in os.listdir(folder):
#             item_path = os.path.join(folder, item)
#             if os.path.isdir(item_path):
#                 shutil.rmtree(item_path)
#             else:
#                 os.remove(item_path)
#         logging.info(f"Cleaned folder: {folder}")
#     except Exception as e:
#         logging.error(f"Failed to clean folder {folder}: {e}")

# find steam directories
def find_steam_dirs(max_depth=3):
    matches = []
    drives = get_all_drives()
    for drive in drives:
        for root, dirs, files in limited_os_walk(drive, max_depth=max_depth):
            if "steam.exe" in (f.lower() for f in files):
                matches.append(root)
    return matches

# find downloading directories   
def find_downloading_dirs(steam_dirs, max_depth=3):
    matches = []
    for steam_dir in steam_dirs:
        for root, dirs, files in limited_os_walk(steam_dir, max_depth=max_depth):
            if root.lower().endswith("downloading"):
                matches.append(root)
    return matches

# find steam process
def find_steam_process():
    for process in psutil.process_iter(['pid', 'name']):
        if "steam.exe" in process.info['name'].lower():
            steam_process = process
            break
    if steam_process:
        return steam_process
    else:
        return None
    
# --- Main monitoring loop ---
def monitor_steam():
    inform("Starting Steam download monitor...")

    # Get steam directories
    steam_dirs = find_steam_dirs()
    for dir in steam_dirs:
        inform(f"\tFound Steam directory: {dir}")

    # Get downloading directories
    downloading_dirs = find_downloading_dirs(steam_dirs)
    for dir in downloading_dirs:
        inform(f"\tFound downloading directory: {dir}")

    # Exit if there is no downloading directory
    if not downloading_dirs:
        inform("No downloading directory found. Exiting", "warning")
        exit(1)
    
    # Get Steam process
    steam_process = find_steam_process()
    if not steam_process:
            inform("Steam is not running. Exiting.", "warning")
            exit(1)
    else:
        inform(f"Steam process found: {steam_process.name} PID: {steam_process.pid}")

    inform("Monitoring Steam downloads...")

    # Confirmed steam is on and that downloading folder exists
    # If both are below certain thresholds, start shutdown.

    # TODO finish getting looping through for any games downloading
    def get_steam_game(downloading_dir):
        steam_url = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
        steam_games = requests.get(steam_url)['applist']['apps']
        folders = os.listdir(downloading_dir)

    # TODO finish what to do if there are things downloading
    def monitor_download(threshold_net=1000000, threshold_disk=1000000, check_interval=30, steam_process=None):
        downloading=True
        
        while downloading:
            # Check network usage
            network_usage = get_network_usage()
            inform(f"Network usage: {network_usage} bytes in the last second.")

            # Check disk usage for steam_process
            disk_usage = get_disk_usage(steam_process.pid)
            inform(f"Disk usage for Steam process: {disk_usage}")

            

            if network_usage > threshold_net or disk_usage > threshold_disk:
                # inform which game is downloading
                for downloading_dir in downloading_dirs:
                    if (folder.isdigit() for folder in os.listdir(downloading_dir)):
                        # check if folder in steam games list
                        get_steam_game(downloading_dir)

                        
                # inform()
                time.sleep(check_interval)
                continue
            else:
                soft_shutdown(threshold_net, threshold_disk, check_interval=5, steam_process=None)


    def soft_shutdown(threshold_net=1000000, threshold_disk=1000000, check_interval=5, steam_process=None):
        shutdown = True

        while shutdown:
            time.sleep(5)

            # Check network usage
            network_usage = get_network_usage()
            inform(f"Network usage: {network_usage} bytes in the last second.")
            
            # Check disk usage for steam_process
            disk_usage = get_disk_usage(steam_process.pid)
            inform(f"Disk usage for Steam process: {disk_usage}")

            if network_usage > threshold_net or disk_usage > threshold_disk:
                os.system("shutdown /a")
                
                inform("A download was discovered during the soft shutdown. Stopping shutdown.")
                shutdown = False
                monitor_download()
            else:
                continue
