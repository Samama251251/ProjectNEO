import os
import sys
import platform
import ctypes
import json

#* cleans and parses the response to json
def clean_content(response):
    content = response.strip('```').replace('json', '')
    clean_content = content.replace('`','')
    return json.loads(clean_content)


#* Give admin access to the assistant
def admin_access():
    if platform.system() == "Windows":
        # Windows: Check for admin rights
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
        if not is_admin:
            # Relaunch the script with admin rights
            print("\033[1;33mRequesting admin access...\033[1;0m")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            print("\033[1;32mAdmin Acess Granted...\033[1;0m")
    else:
        # Unix-based: Check for root access
        if os.geteuid() != 0:
            print("Requesting root access...")
            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
            print("\033[32;0mAdmin Acess Granted...\033[1;0m")