import importlib

import deps
import gui
import updates

if __name__ == '__main__':
    deps.check_deps()
    if updates.check_update():
        updates.download_update()
        importlib.reload(gui)

gui.show_gui()

