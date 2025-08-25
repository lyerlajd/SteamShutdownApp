import os
import time
import psutil
import shutil
import logging
from utils import limited_os_walk, get_all_drives, get_network_usage, get_disk_usage

CHECK_INTERVAL = 30   # seconds
THRESHOLD = 1024      # 1 KB/s

# --- Clean folder utility ---
def clean_folder(folder):
    try:
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        logging.info(f"Cleaned folder: {folder}")
    except Exception as e:
        logging.error(f"Failed to clean folder {folder}: {e}")

# TODO replace function with one from test.py --- Find all steamapps/downloading folders ---
def find_downloading_dirs(max_depth=3):
    matches = []
    drives = get_all_drives()
    for drive in drives:
        for root, dirs, files in limited_os_walk(drive, max_depth=max_depth):
            if root.lower().endswith("steamapps\\downloading"):
                matches.append(root)
    return matches

# --- Main monitoring loop ---
def monitor_steam():
    logging.info("Starting Steam download monitor...")
    downloading_dirs = find_downloading_dirs()
    print("Found downloading directories:")
    for d in downloading_dirs:
        print(f" - {d}")
        logging.info(f"Found downloading directory: {d}")

    if not downloading_dirs:
        print("No steamapps/downloading folders found.")
        logging.warning("No steamapps/downloading folders found.")
        return

    # Locate Steam process
    steam_pid = None
    for proc in psutil.process_iter(['pid', 'name']):
        if "steam.exe" in proc.info['name'].lower():
            steam_pid = proc.info['pid']
            break

    if not steam_pid:
        print("Steam process not found.")
        logging.error("Steam process not found.")
        return

    print("Monitoring Steam downloads...")
    logging.info("Monitoring Steam downloads...")

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
