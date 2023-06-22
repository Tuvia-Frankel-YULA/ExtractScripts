import importlib

import gui
import updates

if __name__ == '__main__':
    if updates.check_update():
        updates.download_update()
        importlib.reload(gui)

    gui.show_gui()

