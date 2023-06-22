import gui
import updates

if __name__ == '__main__':
    if updates.check_update():
        updates.download_update()

    gui.show_gui()

