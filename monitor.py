import os
import time
import psutil
import shutil
import logging
from utils import limited_os_walk, get_all_drives, get_network_usage, get_disk_usage, inform

CHECK_INTERVAL = 30   # seconds
THRESHOLD = 1024      # 1 KB/s

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

    if not downloading_dirs:
        inform("No steamapps/downloading folders found.", "warning")
        return
    
    # Get Steam process
    steam_process = find_steam_process()
    if not steam_process:
            inform("Steam is not running. Exiting.")
            exit(1)
    else:
        inform(f"Steam process found: {steam_process.name} PID: {steam_process.pid}")

    inform("Monitoring Steam downloads...")

    # ! this is where I made it before needing to stop so I can sleep

    while True:
        any_active = False
        for d in downloading_dirs:
            if os.path.exists(d) and os.listdir(d):
                net_usage = get_network_usage()
                disk_usage = get_disk_usage(steam_pid)
                if net_usage > THRESHOLD or disk_usage > THRESHOLD:
                    any_active = True
                    logging.info(f"Activity detected in {d} (Net: {net_usage} B/s, Disk: {disk_usage} B/s)")
                    break

        if not any_active:
            time.sleep(CHECK_INTERVAL)
            still_active = False
            for d in downloading_dirs:
                if os.path.exists(d) and os.listdir(d):
                    still_active = True
                    break

            if not still_active:
                print("All downloads completed. Cleaning up downloading folders...")
                logging.info("All downloads completed. Cleaning up downloading folders...")
                for d in downloading_dirs:
                    if os.path.exists(d) and os.listdir(d):
                        clean_folder(d)
                print("✅ Finished cleanup. You can now shut down safely.")
                logging.info("Finished cleanup.")
                break

        time.sleep(CHECK_INTERVAL)
