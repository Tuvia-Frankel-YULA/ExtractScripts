import os
import shutil
import sys
import time
import tkinter
import urllib.request

import dload

version_file_url = 'https://raw.githubusercontent.com/Tuvia-Frankel-YULA/ExtractScripts/main/version.txt'
update_zip_url = 'https://github.com/Tuvia-Frankel-YULA/ExtractScripts/archive/refs/heads/main.zip'


def check_update() -> bool:
    window = tkinter.Tk()

    label = tkinter.Label(window, text="Checking for updates...")
    label.pack()

    window.update()

    script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    version_file = os.path.join(script_directory, 'version.txt')
    with open(version_file) as version_file:
        version_str = version_file.read()
        version = int(version_str)

        with urllib.request.urlopen(version_file_url) as request:
            remote_version_str = request.read()
            remote_version = int(remote_version_str)

            time.sleep(1)

            window.update()
            window.quit()
            window.destroy()
            time.sleep(1)

            return remote_version > version


def download_update():
    window = tkinter.Tk()

    label = tkinter.Label(window, text="Downloading update:")
    label.pack()

    window.update()
    time.sleep(1)

    script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

    dload.save_unzip(update_zip_url, script_directory)

    os.remove(os.path.join(script_directory, 'main.zip'))

    shutil.copytree(os.path.join(script_directory, 'ExtractScripts-main'), script_directory, dirs_exist_ok=True)
    os.removedirs(os.path.join(script_directory, 'ExtractScripts-main'))

    window.update()
    window.quit()
    window.destroy()
    time.sleep(1)
