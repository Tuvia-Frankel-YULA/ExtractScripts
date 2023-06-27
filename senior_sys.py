import csv
import os

import configdata


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

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter) -> {}:
        return {}


class TeacherInfoExtract(SeniorSysExtract):
    def __init__(self):
        super().__init__()
        self.out_file = 'TeacherInfo.csv'
        self.rows = ['First Name', 'Last Name', 'E-mail', 'User Unique ID']

    def process(self, row, config_data: configdata.Config, csv_writer: csv.DictWriter) -> {}:
        csv_writer.writerow({
            'First Name': row['First Name'],
            'Last Name': row['Last Name'],
            'E-mail': row['E-mail'],
            'User Unique ID': config_data.get_schoology_uuid(row['ID'])
        })


def run_teacher_extract(input_file: str, output_folder: str):
    TeacherInfoExtract().do(input_file, output_folder)
