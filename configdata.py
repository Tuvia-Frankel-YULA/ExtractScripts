import datetime
import json
import os
import sys

import util


class Config:
    def __init__(self):
        self.email_suffix = '@yula.org'
        self.student_uuid_prefix = {
            'boys': 'YHSBD',
            'girls': 'YHSGD'
        }

        self.course_code_prefix = {
            'boys': 'YHSBD_',
            'girls': 'YHSGD_'
        }

        self.excluded_uuids = [
            'WEBSV',
            'TESTGIR'
        ]

        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.config_folder_path = os.path.join(script_directory, 'config')
        self.config_file_path = os.path.join(self.config_folder_path, 'config.json')

        if not os.path.exists(self.config_file_path):
            self.year = int(datetime.datetime.today().year + 4)
            self.grades = [9]
            self.year_map = {
                9: self.year,
                10: self.year - 1,
                11: self.year - 2,
                12: self.year - 3
            }
            self.is_girls = False
            self.semester = 1
            self.teacher_overrides = []
            self.output_file_names = {}
            self.save()
        else:
            with open(self.config_file_path) as config_file:
                config = json.load(config_file)
                self.year = int(str(config['year']).strip())

                self.year_map = {
                    9: self.year,
                    10: self.year - 1,
                    11: self.year - 2,
                    12: self.year - 3
                }

                self.grades = list(map(int, map(str, config['grades'])))
                self.is_girls = util.is_true_complex(config['is_girls'])
                self.semester = int(config['semester'])
                self.teacher_overrides = list(config['teacher_overrides'])
                self.output_file_names = dict(config['output_file_names'])

    def save(self):
        os.makedirs(self.config_folder_path, exist_ok=True)
        config = {
            'year': self.year,
            'grades': self.grades,
            'is_girls': self.is_girls,
            'semester': self.semester,
            'teacher_overrides': self.teacher_overrides,
            'output_file_names': self.output_file_names,
        }

        with open(self.config_file_path, 'w') as config_file:
            json.dump(config, config_file)

    def get_prev_output_file(self, key: str) -> str:
        if key in self.output_file_names:
            return self.output_file_names[key]
        else:
            return ''

    def set_prev_output_file(self, key: str, out_file: str):
        self.output_file_names[key] = out_file

    def get_teacher_schoology_uuid(self, senior_sys_uuid: str) -> str:
        for override in self.teacher_overrides:
            key = 'girls_uuid' if self.is_girls else 'boys_uuid'
            if override[key] == senior_sys_uuid:
                return override['schoology_uuid']

        return senior_sys_uuid

    def _get_div_accessor_name(self):
        return 'girls' if self.is_girls else 'boys'

    def get_student_uuid_prefix(self) -> str:
        return self.student_uuid_prefix[self._get_div_accessor_name()]

    def get_course_code_prefix(self) -> str:
        return self.course_code_prefix[self._get_div_accessor_name()]
