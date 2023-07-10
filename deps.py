import os
import subprocess
import sys
import tkinter


def check_deps():
    window = tkinter.Tk()
    label = tkinter.Label(window, text="Checking dependencies...")
    label.pack()
    window.update()

    script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

    installed_file = os.path.join(script_directory, '.installed')

    if not os.path.exists(installed_file):
        subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            os.path.join(script_directory, 'requirements.txt')])

        with open(installed_file, 'w') as file:
            file.write('Installed!')

    window.update()
    window.quit()
    window.destroy()