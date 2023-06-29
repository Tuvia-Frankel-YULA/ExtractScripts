import csv
import os

import configdata
import util


class SeniorSysExtract:
    def __init__(self):
        self.out_file = 'output.csv'
        self.rows = []

    def do(self, in_file: str, out_folder: str):
        os.makedirs(out_folder, exist_ok=True)

        config_data = configdata.Config()

        with open(in_file) as csv_in:
            csv_reader = csv.DictReader(csv_in)

            with open(os.path.join(out_folder, self.out_file), 'w') as csv_out:
                csv_writer = csv.DictWriter(csv_out, self.rows)

                self.pre_pre_process(csv_writer)
                csv_writer.writeheader()
                self.pre_process(csv_writer)

                for row in csv_reader:
                    self.process(row, config_data, csv_writer)

    def pre_pre_process(self, csv_writer: csv.DictWriter):
        pass

    def pre_process(self, csv_writer: csv.DictWriter):
        pass

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        pass


class TeacherInfoExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
        self.out_file = 'TeacherInfo.csv'
        self.rows = ['First Name', 'Last Name', 'E-mail', 'User Unique ID']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        csv_writer.writerow({
            'First Name': str(row['First Name']),
            'Last Name': str(row['Last Name']),
            'E-mail': str(row['E-mail']),
            'User Unique ID': config_data.get_teacher_schoology_uuid(str(row['ID']))
        })


def run_teacher_extract(input_file: str, output_folder: str):
    TeacherInfoExtract().do(input_file, output_folder)


class StudentInfoExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
        self.out_file = 'StudentInfo.csv'
        self.rows = ['First Name', 'Last Name', 'E-mail', 'User Unique ID', 'Grad Year']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        csv_writer.writerow({
            'First Name': str(row['First Name']),
            'Last Name': str(row['Last Name']),
            'E-mail': str(row['Student E-mail']),
            'User Unique ID': config_data.get_student_uuid_prefix() + str(row['ID']),
            'Grad Year': int(row['Class Year'])
        })


def run_student_extract(input_file: str, output_folder: str):
    StudentInfoExtract().do(input_file, output_folder)


class CourseInfoExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
        self.out_file = 'CourseInfo.csv'
        self.rows = ['Course Code', 'Course Name', 'Section Name', 'Section Code', 'Location', 'Grading Periods']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        semesters = []

        if util.is_true_complex(row['Meets Terms S1']):
            semesters.append(1)
        if util.is_true_complex(row['Meets Terms S2']):
            semesters.append(2)

        section_id = str(row['Section ID'])
        course_name = str(row['Course Name'])
        section_number = str(row['Section No'])
        room = str(row['Room'])

        for semester in semesters:
            course_code = util.course_code(section_id, config_data.get_course_code_prefix(), semester)

            csv_writer.writerow({
                'Course Code': course_code,
                'Course Name': course_name,
                'Section Name': section_id,
                'Section Code': section_number,
                'Location': room,
                'Grading Periods': 'S' + str(semester)
            })


def run_course_extract(input_file: str, output_folder: str):
    CourseInfoExtract().do(input_file, output_folder)


class StudentMembershipExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
        self.out_file = 'StudentMembership.csv'
        self.rows = ['Course Code', 'Section Code', 'Unique User ID']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        uuid = config_data.get_student_uuid_prefix() + str(row['Export ID'])

        i = 1
        while util.section_id_header(i) in row:
            section_id = str(row[util.section_id_header(i)])
            course_code = util.course_code(section_id,
                                           config_data.get_course_code_prefix(),
                                           config_data.semester)

            if section_id != '':
                section_number = row[util.section_number_header(i)]
                csv_writer.writerow({
                    'Course Code': course_code,
                    'Section Code': str(section_number),
                    'Unique User ID': uuid
                })

            i += 1


def run_student_membership_extract(input_file: str, output_folder: str):
    StudentMembershipExtract().do(input_file, output_folder)
