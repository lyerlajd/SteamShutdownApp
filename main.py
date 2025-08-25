import logging
from monitor import monitor_steam
from utils import is_admin

# --- Logging setup ---
logging.basicConfig(
    filename="steam_download_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Admin check ---
if not is_admin():
    print("Script must be run as administrator. Exiting.")
    logging.error("Script not run as administrator.")
    exit(1)

# --- Start monitoring ---
if __name__ == "__main__":
    monitor_steam()
