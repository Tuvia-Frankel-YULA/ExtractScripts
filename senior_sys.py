import csv
import os

import configdata
import util


class SeniorSysExtract:
    def __init__(self):
        self.rows = []

    def do(self, in_file: str, out_file: str):
        os.makedirs(os.path.dirname(out_file), exist_ok=True)

        config_data = configdata.Config()

        with open(in_file) as csv_in:
            csv_reader = csv.DictReader(csv_in)

            with open(out_file, 'w') as csv_out:
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
        self.rows = ['First Name', 'Last Name', 'E-mail', 'User Unique ID']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        email = str(row['E-mail'])
        uuid = str(row['ID'])

        if not email.endswith(config_data.email_suffix):
            return

        if uuid in config_data.excluded_uuids:
            return

        csv_writer.writerow({
            'First Name': str(row['First Name']),
            'Last Name': str(row['Last Name']),
            'E-mail': email,
            'User Unique ID': config_data.get_teacher_schoology_uuid(uuid)
        })


def run_teacher_extract(input_file: str, output_file: str):
    TeacherInfoExtract().do(input_file, output_file)


class StudentInfoExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
        self.rows = ['First Name', 'Last Name', 'E-mail', 'User Unique ID', 'Grad Year']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        uuid = str(row['ID'])

        if uuid in config_data.excluded_uuids:
            return

        csv_writer.writerow({
            'First Name': str(row['First Name']),
            'Last Name': str(row['Last Name']),
            'E-mail': str(row['Student E-mail']),
            'User Unique ID': config_data.get_student_uuid_prefix() + uuid,
            'Grad Year': int(row['Class Year'])
        })


def run_student_extract(input_file: str, output_file: str):
    StudentInfoExtract().do(input_file, output_file)


class CourseInfoExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
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
            course_code = util.course_code(section_number,
                                           section_id,
                                           config_data.get_course_code_prefix(),
                                           semester,
                                           config_data.is_girls)

            csv_writer.writerow({
                'Course Code': course_code,
                'Course Name': course_name + ' Sem' + str(semester),
                'Section Name': 'Section ' + section_number,
                'Section Code': section_number,
                'Location': room,
                'Grading Periods': 'S' + str(semester)
            })


def run_course_extract(input_file: str, output_file: str):
    CourseInfoExtract().do(input_file, output_file)


class MembershipExtract(SeniorSysExtract):
    def __init__(self, is_teachers: bool):
        super().__init__()
        self.is_teachers = is_teachers
        self.rows = ['Course Code', 'Section Code', 'Unique User ID']

        self.added_sections: list[str] = []

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter):
        export_id = str(row['Export ID'])

        if export_id in config_data.excluded_uuids:
            return

        uuid = config_data.get_student_uuid_prefix() + export_id

        i = 1
        while util.section_id_header(i) in row:
            section_id = str(row[util.section_id_header(i)])
            section_number = str(row[util.section_number_header(i)])
            course_code = util.course_code(section_number,
                                           section_id,
                                           config_data.get_course_code_prefix(),
                                           config_data.semester,
                                           config_data.is_girls)

            faculty_id = str(row[util.faculty_id_primary_header(i)]) if self.is_teachers else 'N/A'

            if section_id != '' and course_code not in self.added_sections and len(faculty_id) > 0:
                if self.is_teachers:
                    self.added_sections.append(course_code)

                teacher_uuid = config_data.get_teacher_schoology_uuid(faculty_id)

                csv_writer.writerow({
                    'Course Code': course_code,
                    'Section Code': section_number,
                    'Unique User ID': teacher_uuid if self.is_teachers else uuid
                })

            i += 1


def run_student_membership_extract(input_file: str, output_file: str):
    MembershipExtract(False).do(input_file, output_file)


def run_teacher_membership_extract(input_file: str, output_file: str):
    MembershipExtract(True).do(input_file, output_file)
