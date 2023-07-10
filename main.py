#!/bin/python3

import importlib

import deps

if __name__ == '__main__':
    deps.check_deps()
    deps = importlib.reload(deps)

import gui
import updates

if __name__ == '__main__':
    if updates.check_update():
        updates.download_update()
        gui = importlib.reload(gui)

gui.show_gui()

