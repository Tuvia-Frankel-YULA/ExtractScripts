import os
import sys
import tkinter
from tkinter import filedialog
from collections.abc import Callable
from typing import Any, Tuple
import tkinter.messagebox

import student_names
import updates

scripts: list[Tuple[str, Callable[[str, str], Any]]] = [
    ("Student names", student_names.run_tasks)
]

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
in_default_folder = os.path.join(script_directory, 'in')
out_default_folder = os.path.join(script_directory, 'out')

global file_in_text
global folder_out_text


def show_gui():
    os.makedirs(in_default_folder, exist_ok=True)
    os.makedirs(out_default_folder, exist_ok=True)

    window = tkinter.Tk()
    window.title('Yula Scripts')
    window.geometry('900x500')

    global file_in_text
    file_in_text = tkinter.StringVar()
    file_in_text.set(os.path.join(in_default_folder, 'names.csv'))
    file_entry('Input Filename: ', window, file_in_text, file_in_open_file_dialog)

    global folder_out_text
    folder_out_text = tkinter.StringVar()
    folder_out_text.set(out_default_folder)
    file_entry('Output folder: ', window, folder_out_text, folder_out_open_file_dialog)

    lb_label = tkinter.Label(window, text='Select script to run:')
    lb_label.grid()

    lb = tkinter.Listbox(window, selectmode=tkinter.SINGLE)

    i = 0
    for script in scripts:
        lb.insert(i, script[0])
        i += 1

    lb.grid(sticky='NSWE')

    def do_action():
        try:
            for selection in lb.curselection():
                func: Callable[[str, str], Any] = scripts[selection][1]
                func(file_in_text.get(), folder_out_text.get())
            tkinter.messagebox.showinfo('Success', 'All tasks completed successfully! Check output folder.')
        except BaseException as e:
            tkinter.messagebox.showerror('Error!', str(e))
            raise e

    btn = tkinter.Button(window, text="Do action", command=do_action)
    btn.grid(sticky='WE')

    window.columnconfigure('all', weight=1)
    window.rowconfigure(3, weight=1)
    window.mainloop()


def file_entry(label: str, window, file_text, open_dialog_func):
    file_frame = tkinter.Frame(window)
    file_frame.grid(sticky='WE')

    file_label = tkinter.Label(file_frame, text=label)
    file_label.grid(row=0, column=0)

    file_in_entry: tkinter.Entry = tkinter.Entry(file_frame, textvariable=file_text)
    file_in_entry.grid(row=0, column=1, sticky='WE')

    file_in_file_chooser_btn = tkinter.Button(file_frame, text="...", command=open_dialog_func)
    file_in_file_chooser_btn.grid(row=0, column=2)

    file_frame.columnconfigure(1, weight=1)


def file_in_open_file_dialog():
    file_name = filedialog.askopenfilename(
        title='Open csv file',
        filetypes=[('CSV file (*.csv)', '*.csv')],
        initialdir=in_default_folder)
    file_in_text.set(file_name)


def folder_out_open_file_dialog():
    folder_name = filedialog.askdirectory(
        title='Output csv folder',
        initialdir=in_default_folder)
    folder_out_text.set(folder_name)
