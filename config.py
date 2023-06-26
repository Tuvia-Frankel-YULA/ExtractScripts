import datetime
import json
import os
import sys


class Config:
    def __init__(self):
        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.config_file_path = os.path.join(script_directory, 'config', 'config.json')

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
            is_girls_val = config['is_girls']
            self.is_girls = isinstance(is_girls_val, bool) and is_girls_val \
                            or isinstance(is_girls_val, int) and is_girls_val > 0 \
                            or isinstance(is_girls_val, float) and is_girls_val > 0 \
                            or str(is_girls_val).lower() == 't' \
                            or str(is_girls_val).lower() == 'true'
            self.email_suffix = str(config['email']).strip()

    def save(self):
        config = {
            'year': self.year,
            'grades': self.grades,
            'is_girls': self.is_girls,
            'email': self.email_suffix,
        }

        with open(self.config_file_path, 'w') as config_file:
            json.dump(config, config_file)