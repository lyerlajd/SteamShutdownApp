import os
import psutil
import ctypes
import logging

# --- Admin check ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# --- Limited-depth os.walk ---
def limited_os_walk(start_path, max_depth=3):
    start_path = os.path.abspath(start_path)
    num_sep = start_path.count(os.sep)
    for root, dirs, files in os.walk(start_path):
        yield root, dirs, files
        if root.count(os.sep) - num_sep >= max_depth - 1:
            dirs[:] = []

# --- Get all drives ---
def get_all_drives():
    drives = []
    for partition in psutil.disk_partitions(all=False):
        if os.name == "nt":
            if "cdrom" in partition.opts or not os.path.exists(partition.device):
                continue
        drives.append(partition.device)
    return drives

# --- Network usage in 1-second window ---
def get_network_usage():
    net1 = psutil.net_io_counters()
    psutil.time.sleep(1)
    net2 = psutil.net_io_counters()
    return (net2.bytes_sent - net1.bytes_sent) + (net2.bytes_recv - net1.bytes_recv)

# --- Disk usage for a process ---
def get_disk_usage(pid):
    try:
        proc = psutil.Process(pid)
        io1 = proc.io_counters()
        psutil.time.sleep(1)
        io2 = proc.io_counters()
        return (io2.read_bytes - io1.read_bytes) + (io2.write_bytes - io1.write_bytes)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0
    
# --- Send messages to console and log file ---
def inform(message, logType="info"):
    # print message to console
    print(message)

    # add message to log file
    match logType:
        case "info":
            logging.info(message)
        case "warning":
            logging.warning(message)
        case _:
            logging.info(message)
            