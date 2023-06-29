import os
import sys
import tkinter
from tkinter import filedialog
from collections.abc import Callable
from typing import Any, Tuple
import tkinter.messagebox

import configdata
import platform
import senior_sys
import student_names

show_grade_select = False

scripts: list[Tuple[str, Callable[[str, str], Any], str]] = [
    ('Senior Systems - Student Roster', senior_sys.run_student_membership_extract, 'student_membership_extract'),
    ('Senior Systems - Teacher Roster', senior_sys.run_teacher_membership_extract, 'teacher_membership_extract'),
    ('Senior Systems - Teacher Info', senior_sys.run_teacher_extract, 'teacher_extract'),
    ('Senior Systems - Student Info', senior_sys.run_student_extract, 'student_extract'),
    ('Senior Systems - Course Info', senior_sys.run_course_extract, 'course_extract'),
    # ('Student accounts from student list.', student_names.run_tasks, 'student_names')
]

csv_filetypes = [('CSV file (*.csv)', '*.csv')]

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
in_default_folder = os.path.join(script_directory, 'in')
out_default_folder = os.path.join(script_directory, 'out')

global is_boys_school
global is_girls_school
global semester_str
global freshman_year
global allow_nine
global allow_ten
global allow_eleven
global allow_twelve

global file_in_text

global config_data
config_data: configdata.Config


def show_gui():
    os.makedirs(in_default_folder, exist_ok=True)
    os.makedirs(out_default_folder, exist_ok=True)

    global config_data
    config_data = configdata.Config()

    window = tkinter.Tk()
    window.title('Yula Scripts')
    window.geometry('900x900')

    tkinter.Label(window, text="Config: ").grid(sticky='WE')

    school_layout = tkinter.Frame(window)
    school_layout.grid(sticky='WE')

    school_label = tkinter.Label(school_layout, text="Which school?: ")
    school_label.grid(row=0, column=0)

    global is_boys_school
    is_boys_school = tkinter.IntVar()
    is_boys_school.set(0 if config_data.is_girls else 1)

    is_boys_check = tkinter.Checkbutton(school_layout, text="Boys", variable=is_boys_school, command=set_is_boys)
    is_boys_check.grid(row=0, column=1)

    global is_girls_school
    is_girls_school = tkinter.IntVar()
    is_girls_school.set(1 if config_data.is_girls else 0)

    is_girls_check = tkinter.Checkbutton(school_layout, text="Girls", variable=is_girls_school, command=set_is_girls)
    is_girls_check.grid(row=0, column=2)

    semester_layout = tkinter.Frame(window)
    semester_layout.grid(sticky='WE')

    global semester_str
    semester_str = tkinter.StringVar()
    semester_str.set(str(config_data.semester))
    tkinter.Label(semester_layout, text='Current Semester: ').grid(row=0, column=0)
    tkinter.Spinbox(semester_layout, from_=1, to=2, increment=1, textvariable=semester_str, command=set_semester).grid(
        row=0, column=1, sticky='WE')

    semester_layout.columnconfigure(1, weight=1)

    if show_grade_select:
        year_layout = tkinter.Frame(window)
        year_layout.grid(sticky='WE')

        year_label = tkinter.Label(year_layout, text="Year freshmen graduate: ")
        year_label.grid(row=0, column=0)

        global freshman_year
        freshman_year = tkinter.StringVar()
        freshman_year.set(str(config_data.year))
        year_field = tkinter.Spinbox(year_layout, from_=0, to=10000, increment=1, textvariable=freshman_year,
                                     command=set_freshman_year)
        year_field.grid(row=0, column=1, sticky='WE')

        year_layout.columnconfigure(1, weight=1)

        grades_layout = tkinter.Frame(window)
        grades_layout.grid(sticky="WE")

        grades_label = tkinter.Label(grades_layout, text='Process students in grade: ')
        grades_label.grid(row=0, column=0)

        global allow_nine
        allow_nine = tkinter.IntVar()
        allow_nine.set(9 in config_data.grades)
        nineth_checkbox = tkinter.Checkbutton(grades_layout, text="9th", variable=allow_nine, command=set_allow_nine)
        nineth_checkbox.grid(row=0, column=1)

        global allow_ten
        allow_ten = tkinter.IntVar()
        allow_ten.set(10 in config_data.grades)
        tenth_checkbox = tkinter.Checkbutton(grades_layout, text="10th", variable=allow_ten, command=set_allow_ten)
        tenth_checkbox.grid(row=0, column=2)

        global allow_eleven
        allow_eleven = tkinter.IntVar()
        allow_eleven.set(11 in config_data.grades)
        eleventh_checkbox = tkinter.Checkbutton(grades_layout, text="11th", variable=allow_eleven,
                                                command=set_allow_eleven)
        eleventh_checkbox.grid(row=0, column=3)

        global allow_twelve
        allow_twelve = tkinter.IntVar()
        allow_twelve.set(12 in config_data.grades)
        twelveth_checkbox = tkinter.Checkbutton(grades_layout, text="12th", variable=allow_twelve,
                                                command=set_allow_twelve)
        twelveth_checkbox.grid(row=0, column=4)

    edit_button = tkinter.Button(window, text="Edit teacher overrides 🗗", command=show_teachers_edit)
    edit_button.grid(sticky='WE')

    global file_in_text
    file_in_text = tkinter.StringVar()
    file_entry('Input Filename: ', window, file_in_text, file_in_open_file_dialog)

    lb_label = tkinter.Label(window, text='Select script to run:')
    lb_label.grid()

    lb = tkinter.Listbox(window, selectmode=tkinter.SINGLE)

    i = 0
    for script in scripts:
        lb.insert(i, script[0])
        i += 1

    lb.grid(sticky='NSWE')

    def run_script():
        try:
            in_file = file_in_text.get()

            if len(in_file) <= 0:
                raise Exception('Please specify a valid input file')
            if not os.path.exists(in_file):
                raise Exception('Failed to find file: "' + in_file + '"')

            for selection in lb.curselection():
                prev_file_key: str = scripts[selection][2]
                prev_file = config_data.get_prev_output_file(prev_file_key)
                out_file = platform.show_save_file(
                    'Save file for ' + scripts[selection][0],
                    csv_filetypes,
                    prev_file)

                if len(out_file) > 0:
                    out_file += '' if out_file.endswith('.csv') else '.csv'
                    config_data.set_prev_output_file(prev_file_key, out_file)
                    config_data.save()

                    func: Callable[[str, str], Any] = scripts[selection][1]
                    func(in_file, out_file)
                    tkinter.messagebox.showinfo('Success', scripts[selection][0] + ' ran successfully!')
                    platform.start_file(os.path.dirname(out_file))
        except BaseException as e:
            tkinter.messagebox.showerror('Error!', str(e))
            raise e

    btn = tkinter.Button(window, text="Run script", command=run_script)
    btn.grid(sticky='WE')

    window.columnconfigure('all', weight=1)
    window.rowconfigure(len(window.children) - 2, weight=1)
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


def set_is_boys():
    is_boys_school.set(1)
    is_girls_school.set(0)
    config_data.is_girls = False
    config_data.save()


def set_is_girls():
    is_girls_school.set(1)
    is_boys_school.set(0)
    config_data.is_girls = True
    config_data.save()


def set_semester():
    config_data.semester = int(semester_str.get())
    config_data.save()


def set_freshman_year():
    config_data.year = freshman_year.get()
    config_data.save()


def set_allow_nine():
    if allow_nine.get() > 0:
        if 9 not in config_data.grades:
            config_data.grades.append(9)
    else:
        if 9 in config_data.grades:
            config_data.grades.remove(9)

    config_data.save()


def set_allow_ten():
    if allow_ten.get() > 0:
        if 10 not in config_data.grades:
            config_data.grades.append(10)
    else:
        if 10 in config_data.grades:
            config_data.grades.remove(10)

    config_data.save()


def set_allow_eleven():
    if allow_eleven.get() > 0:
        if 11 not in config_data.grades:
            config_data.grades.append(11)
    else:
        if 11 in config_data.grades:
            config_data.grades.remove(11)

    config_data.save()


def set_allow_twelve():
    if allow_twelve.get() > 0:
        if 12 not in config_data.grades:
            config_data.grades.append(12)
    else:
        if 12 in config_data.grades:
            config_data.grades.remove(12)

    config_data.save()


def show_teachers_edit():
    window = tkinter.Toplevel()
    window.title('Edit teacher overrides')
    window.geometry('1100x600')

    row_getters = []

    frame = tkinter.Frame(window)
    frame.pack(anchor='n', fill='x')

    # In the config data, girls come first, but I put boys first in the UI b/c why not
    tkinter.Label(frame, text='____', relief='sunken').grid(row=0, column=0)
    tkinter.Label(frame, text='Name', relief='sunken').grid(row=0, column=1, sticky='WE')
    tkinter.Label(frame, text='Boy\'s School ID', relief='sunken').grid(row=0, column=2, sticky='WE')
    tkinter.Label(frame, text='Girl\'s School ID', relief='sunken').grid(row=0, column=3, sticky='WE')
    tkinter.Label(frame, text='Schoology Unique ID', relief='sunken').grid(row=0, column=4, sticky='WE')

    def add():
        teachers_edit_row(frame, {'name': '', 'girls_uuid': '', 'boys_uuid': '', 'schoology_uuid': ''}, row_getters)
        frame.rowconfigure('all', weight=1)
        frame.columnconfigure('all', weight=1)
        frame.columnconfigure(0, weight=0)

    def close():
        window.quit()
        window.destroy()

    def save():
        config_data.teacher_overrides.clear()

        for getter in row_getters:
            config_data.teacher_overrides.append(getter())

        config_data.save()

        close()

    for override in config_data.teacher_overrides:
        teachers_edit_row(frame, override, row_getters)

    frame.rowconfigure('all', weight=1)
    frame.columnconfigure('all', weight=1)
    frame.columnconfigure(0, weight=0)

    buttons_layout = tkinter.Frame(window)
    buttons_layout.pack(anchor='s', fill='x', side='bottom')

    add_button = tkinter.Button(buttons_layout, text='Add teacher override', command=add)
    add_button.grid(sticky='WE')

    dialog_buttons_layout = tkinter.Frame(buttons_layout)
    dialog_buttons_layout.grid(sticky='WE')

    tkinter.Label(dialog_buttons_layout, text=' ').grid(row=0, column=0, sticky='WE')
    cancel_button = tkinter.Button(dialog_buttons_layout, text='Cancel', command=close)
    cancel_button.grid(row=0, column=1)
    save_button = tkinter.Button(dialog_buttons_layout, text='Save', command=save)
    save_button.grid(row=0, column=2)

    dialog_buttons_layout.columnconfigure('all', pad=10)
    dialog_buttons_layout.columnconfigure(0, weight=1)
    buttons_layout.columnconfigure('all', weight=1)

    window.mainloop()


def teachers_edit_row(frame: tkinter.Frame, override: dict, row_getters: list):
    i = len(row_getters) + 1

    name_var = tkinter.StringVar()
    name_var.set(override['name'])
    girls_uuid_var = tkinter.StringVar()
    girls_uuid_var.set(override['girls_uuid'])
    boys_uuid_var = tkinter.StringVar()
    boys_uuid_var.set(override['boys_uuid'])
    schoology_uuid_var = tkinter.StringVar()
    schoology_uuid_var.set(override['schoology_uuid'])

    def getter():
        return {
            'name': name_var.get(),
            'girls_uuid': girls_uuid_var.get(),
            'boys_uuid': boys_uuid_var.get(),
            'schoology_uuid': schoology_uuid_var.get()
        }

    row_getters.append(getter)

    remove_button = tkinter.Button(frame, text='-')
    remove_button.grid(row=i, column=0)

    name_entry = tkinter.Entry(frame, textvariable=name_var)
    name_entry.grid(row=i, column=1, sticky='WE')
    boys_uuid_entry = tkinter.Entry(frame, textvariable=boys_uuid_var)
    boys_uuid_entry.grid(row=i, column=2, sticky='WE')
    girls_uuid_entry = tkinter.Entry(frame, textvariable=girls_uuid_var)
    girls_uuid_entry.grid(row=i, column=3, sticky='WE')
    schoology_uuid_entry = tkinter.Entry(frame, textvariable=schoology_uuid_var)
    schoology_uuid_entry.grid(row=i, column=4, sticky='WE')

    widgets = [remove_button, name_entry, girls_uuid_entry, boys_uuid_entry, schoology_uuid_entry]

    def remove():
        for widget in widgets:
            widget.grid_remove()
            widget.destroy()

        row_getters.remove(getter)

    remove_button.configure(command=remove)


def file_in_open_file_dialog():
    try:
        file_name = platform.show_open_file('Open csv file',
                                            csv_filetypes,
                                            in_default_folder)
        if os.path.exists(file_name):
            file_in_text.set(file_name)
    except BaseException as e:
        tkinter.messagebox.showerror('Error!', str(e))
        raise e
