import gui
import updates

if __name__ == '__main__':
    if updates.check_update():
        updates.download_update()
    else:
        gui.show_gui()

