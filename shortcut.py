import os
import pythoncom
from win32com import shell # type: ignore

SHORTCUT_NAME = "Steam Monitor.lnk"

# --- Create a desktop shortcut for the exe ---
def create_shortcut(exe_path):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, SHORTCUT_NAME)

    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    shell_link.SetPath(exe_path)
    shell_link.SetWorkingDirectory(os.path.dirname(exe_path))
    shell_link.SetDescription("Steam Download Monitor")

    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)

    print(f"✅ Shortcut created on desktop: {shortcut_path}")
