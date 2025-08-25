# SteamShutdownApp

## Steam Shutdown File Tree
steam_monitor/  
├── main.py        # entry point: runs monitoring  
├── monitor.py     # Steam monitoring functions  
├── shortcut.py    # create desktop shortcuts  
└── utils.py       # helper functions: OS walk, network/disk usage, admin check  

Give user option to enter their steam directory (type, drag and drop, or browse), or search for it with Python


# main.py
`main.py` is the entry point for Steam Shutdown. It sets up the basic logging, checks if the app is running as admin, and then starts the download monitoring process.

## Logging
Steam Shutdown uses [Python's built in library for event logging](https://docs.python.org/3/library/logging.html).
By default, the logging file is `steam_download_monitor.log`. But you can change this to a filename and location of your choice.

## Running as Admin

- successfully finds if user is running script as admin or not

## Monitoring
The last thing that main.py does, is run the `monitor_steam()` function, the main loop of `monitor.py`.

# monitor.py


# shortcut.py

# utils.py


## OS Walking
1. Find all drives.
    - get_all_drives() from utils.py
    - successfully finds any drives on the PC
2. Find Steam directories within drives.
    - 
    - successfully finds Steam directories within a specified depth, default 3
3. Find Downloading directories within steam directories.
4. 