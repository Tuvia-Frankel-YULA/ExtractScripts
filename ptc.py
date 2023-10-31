import csv
import os
import tkinter.messagebox

import configdata
import gui
import platform_util
import util


class PtcError:
    def __init__(self, error: str, uid: str, first_name: str, last_name: str):
        self.error = error
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name


class PtcExtract:
    def __init__(self):
        self.rows = []
        self.errors: [PtcError] = []

    def do(self, in_file: str, out_file: str):
        config_data = configdata.Config()

        if not self.should_do(config_data):
            return

        os.makedirs(os.path.dirname(out_file), exist_ok=True)

        with open(in_file) as csv_in:
            csv_reader = csv.DictReader(csv_in)

            with open(out_file, 'w') as csv_out:
                csv_writer = csv.DictWriter(csv_out, self.rows)

                self.pre_pre_process(csv_writer)
                csv_writer.writeheader()
                self.pre_process(csv_writer)

                for row in csv_reader:
                    self.process(row, config_data, csv_writer)

                self.post_process(csv_writer)

        if len(self.errors) > 0:
            with open(out_file + '_errors.csv', 'w') as errors_out:
                errors_write = csv.DictWriter(errors_out, ["Error", "Id", "First Name", "Last Name"])
                errors_write.writeheader()
                for error in self.errors:
                    tkinter.messagebox.showerror('Error!:',
                                                 '"' + error.error + '". id: ' + error.uid + ' , name: ' + error.first_name + ' ' + error.last_name)
                    errors_write.writerow({"Error": error.error, "Id": error.uid, "First Name": error.first_name,
                                           "Last Name": error.last_name})

    def should_do(self, config_data: configdata.Config) -> bool:
        return True

    def pre_pre_process(self, csv_writer: csv.DictWriter):
        pass

    def pre_process(self, csv_writer: csv.DictWriter):
        pass

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        pass

    def post_process(self, csv_writer: csv.DictWriter):
        pass


class InfoExtract(PtcExtract):
    def __init__(self, is_teachers: bool):
        super().__init__()
        self.parent_email_map = {}

        self.is_teachers = is_teachers
        if is_teachers:
            self.rows = ['Teacher ID Number', 'Teacher First Name', 'Teacher Last Name', 'Password', 'Room', 'Email',
                         'Zoom Link']
        else:
            self.rows = ['Student ID Number', 'Student First Name', 'Student Last Name', 'Password', '2nd Password',
                         'Grade', 'Email']

    def should_do(self, config_data: configdata.Config) -> bool:
        if not self.is_teachers:
            if tkinter.messagebox.askokcancel("Important",
                                              "You will need to get the parent's emails from senior systems! After you do so, select that file in the next dialog."):
                file_name = platform_util.show_open_file("Open parent email csv.", gui.csv_filetypes,
                                                         gui.in_default_folder)

                if not file_name.strip():
                    return False
                if not os.path.exists(file_name):
                    tkinter.messagebox.showerror('Failed to find file!', 'Failed to find file "' + file_name + '"!')
                    return False

                with open(file_name) as file:
                    reader = csv.DictReader(file)

                    for row in reader:
                        uid = config_data.get_student_uuid_prefix() + row['ID']
                        email1 = row['E-mail (Father / Name 1)'].strip()
                        email2 = row['E-mail (Mother / Name 2)'].strip()
                        email = (email1 + ' ' + email2).strip()

                        if not email:
                            self.errors.append(
                                PtcError("Failed to get email for student", uid, row['First Name'], row['Last Name']))
                        else:
                            self.parent_email_map[uid] = email

                return True
        else:
            return True

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        role = row['Role']
        school = row['School Title']

        uid = row['Unique User ID']

        if uid in config_data.excluded_uuids:
            return

        first_name = row['First Name']
        last_name = row['Last Name']
        email = row['Email']
        grad_year = row['Graduation Year']

        if self.is_teachers:
            if role.lower() != 'teacher':
                return

            if not str(uid.strip()):
                self.errors.append(PtcError('Teacher with empty Unique User ID.', uid, first_name, last_name))
                return

            if '@' in uid:
                self.errors.append(
                    PtcError('Teacher uid is an email. It should be an actual id.', uid, first_name, last_name))
                return

            if 'girl' in school.lower():
                if not config_data.is_girls:
                    return
            if 'boy' in school.lower():
                if config_data.is_girls:
                    return
            else:
                self.errors.append(
                    PtcError('Teacher belongs no neither boys nor girls school!?', uid, first_name, last_name))
        else:
            if role.lower() != 'student':
                return

            if 'girl' in school.lower():
                if not config_data.is_girls:
                    return
            if 'boy' in school.lower():
                if config_data.is_girls:
                    return
            else:
                self.errors.append(
                    PtcError('Student belongs no neither boys nor girls school!?', uid, first_name, last_name))

            if not str(uid.strip()):
                self.errors.append(PtcError('Student with empty Unique User ID.', uid, first_name, last_name))
                return

            if int(grad_year) < 2000:
                self.errors.append(
                    PtcError('Student with invalid graduation year ' + grad_year + '.', uid, first_name, last_name))
                return

        password = '1234567'
        room = ''
        link = ''

        if self.is_teachers:
            csv_writer.writerow({
                'Teacher ID Number': uid,
                'Teacher First Name': first_name,
                'Teacher Last Name': last_name,
                'Password': password,
                'Room': room,
                'Email': email,
                'Zoom Link': link,
            })
        else:

            grade = (config_data.year - int(grad_year)) + 9

            if grade > 12:
                self.errors.append(
                    PtcError('Student with invalid graduation year ' + grad_year + '.', uid, first_name,
                             last_name))
                return

            if uid not in self.parent_email_map:
                self.errors.append(
                    PtcError('Student does not have a parent email.', uid, first_name,
                             last_name))
                return

            email = self.parent_email_map[uid]

            csv_writer.writerow({
                'Student ID Number': uid,
                'Student First Name': first_name,
                'Student Last Name': last_name,
                'Password': '',
                '2nd Password': password,
                'Grade': grade,
                'Email': email,
            })


class CourseInfoExtract(PtcExtract):
    def __init__(self):
        super().__init__()

        self.teacher_class_map = {}
        self.course_map = {}
        self.student_classes = []
        self.rows = ['Student ID Number', 'Course Title', 'Teacher ID Number']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        status = row['Status']

        if not status.strip() or int(status) == 5:
            return

        enrollment = row['Enrollment Type (1=Admin/2=Member)']

        uid = row['Unique User ID']
        course_code = row['Course Code']
        section = row['Section Name']

        course = course_code + section

        self.course_map[course] = course_code

        if int(enrollment) == 1:
            if uid:
                if course in self.teacher_class_map and self.teacher_class_map[course] and self.teacher_class_map[course] != uid:
                    self.errors.append(PtcError("Course already has a teacher with id " + self.teacher_class_map[
                        course] + " but we are trying to set it to " + uid, course, "N/A", "N/A"))
                else:
                    self.teacher_class_map[course] = uid
        else:
            if 'Teacher ID' in row and row['Teacher ID'].strip():
                self.student_classes.append((uid, course, row['Teacher ID']))
            else:
                self.student_classes.append((uid, course, ''))

    def post_process(self, csv_writer: csv.DictWriter):
        missing_teachers = []

        for (uid, course, teacher) in self.student_classes:
            if not teacher and course not in self.teacher_class_map:
                if course not in missing_teachers:
                    self.errors.append(PtcError("Class has no teacher!", course, "N/A", "N/A"))
                    missing_teachers.append(course)
                continue

            teacher = self.teacher_class_map[course] if not teacher else teacher
            course_code = self.course_map[course]

            csv_writer.writerow({
                'Student ID Number': uid,
                'Course Title': course_code,
                'Teacher ID Number': teacher,
            })


def run_student_info_extract(input_file: str, output_file: str):
    InfoExtract(False).do(input_file, output_file)
    pass


def run_teacher_info_extract(input_file: str, output_file: str):
    InfoExtract(True).do(input_file, output_file)


def run_course_info_extract(input_file: str, output_file: str):
    CourseInfoExtract().do(input_file, output_file)
    pass
