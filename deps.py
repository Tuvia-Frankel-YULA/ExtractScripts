import os
import subprocess
import sys


def check_deps():
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
