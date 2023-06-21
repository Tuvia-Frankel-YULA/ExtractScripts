import csv
import json
import os
import sys


class TaskData:
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 email: str,
                 grade: int,
                 year: int,
                 is_girls: bool,
                 email_suffix: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.grade = grade
        self.year = year
        self.is_girls = is_girls
        self.email_suffix = email_suffix


class Task:
    def __init__(self):
        self.out_file = 'output.csv'
        self.rows = []

    def do(self, in_file: str, out_folder: str):
        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.makedirs(out_folder, exist_ok=True)
        with open(os.path.join(script_directory, 'config', 'config.json')) as config_file:
            config = json.load(config_file)
            year = int(str(config['year']).strip())
            grades = list(map(int, map(str, config['grades'])))
            is_girls_val = config['is_girls']
            is_girls = isinstance(is_girls_val, bool) and is_girls_val \
                or isinstance(is_girls_val, int) and is_girls_val > 0\
                or isinstance(is_girls_val, float) and is_girls_val > 0\
                or str(is_girls_val).lower() == 't' \
                or str(is_girls_val).lower() == 'true' \

            with open(in_file) as csv_in:
                csv_reader = csv.DictReader(csv_in)

                with open(os.path.join(out_folder, self.out_file), 'w') as csv_out:
                    csv_writer = csv.DictWriter(csv_out, self.rows)

                    self.pre_pre_process(csv_writer)
                    csv_writer.writeheader()
                    self.pre_process(csv_writer)

                    for row in csv_reader:
                        email_suffix = str(config['email']).strip()

                        last_name = str(row['Last Name']).strip()
                        first_name = str(row['Student Name']).strip().removesuffix(last_name).strip()
                        email = (first_name[0] + last_name + str(year) + email_suffix).lower()
                        grade = int(row['Grade'].strip())

                        if grade in grades:
                            csv_writer.writerow(self.process(row,
                                                             TaskData(first_name,
                                                                      last_name,
                                                                      email,
                                                                      grade,
                                                                      year,
                                                                      is_girls,
                                                                      email_suffix)))

        print('Task "' + self.__class__.__name__ + '" is done')

    def pre_pre_process(self, csv_writer: csv.DictWriter):
        pass

    def pre_process(self, csv_writer: csv.DictWriter):
        pass

    def process(self, row, data: TaskData):
        return {}


class GmailTask(Task):
    def __init__(self):
        super().__init__()
        self.out_file = 'gmail.csv'
        self.rows = ['First Name [Required]',
                     'Last Name [Required]',
                     'Email Address [Required]',
                     'Password [Required]',
                     'Password Hash Function [UPLOAD ONLY]',
                     'Org Unit Path [Required]',
                     'New Primary Email [UPLOAD ONLY]',
                     'Recovery Email',
                     'Home Secondary Email',
                     'Work Secondary Email',
                     'Recovery Phone [MUST BE IN THE E.164 FORMAT]',
                     'Work Phone',
                     'Home Phone',
                     'Mobile Phone',
                     'Work Address',
                     'Home Address',
                     'Employee ID',
                     'Employee Type',
                     'Employee Title',
                     'Manager Email',
                     'Department',
                     'Cost Center',
                     'Building ID',
                     'Floor Name',
                     'Floor Section',
                     'Change Password at Next Sign-In',
                     'New Status [UPLOAD ONLY]',
                     'Advanced Protection Program enrollment']

    def process(self, row, data: TaskData):
        return {
            'First Name [Required]': data.first_name,
            'Last Name [Required]': data.last_name,
            'Email Address [Required]': data.email,
            'Password [Required]': 'YULA' + str(data.year),
            'Org Unit Path [Required]': '/YULA ' + ('Girls' if data.is_girls else 'Boys') + '/' + str(data.year),
            'Change Password at Next Sign-In': 'TRUE',
            'Advanced Protection Program enrollment': 'FALSE'
        }


class AdobeTask(Task):
    def __init__(self):
        super().__init__()
        self.out_file = 'adobe.csv'
        self.rows = ['Identity Type',
                     'Username',
                     'Domain',
                     'Email',
                     'First Name',
                     'Last Name',
                     'Country Code',
                     'ID',
                     'Product Configurations',
                     'Admin Roles',
                     'Product Configurations Administered',
                     'User Groups',
                     'User Groups Administered',
                     'Products Administered',
                     'Developer Access']

    def process(self, row, data: TaskData):
        return {
            'Identity Type': 'Federated ID',
            'Username': data.email.upper(),
            'Email': data.email,
            'First Name': data.first_name,
            'Last Name': data.last_name,
            'Country Code': 'US',
            'Product Configurations': 'Adobe Creative Cloud - YULA High Schools',
            'User Groups': 'YULA ' + ('Girls' if data.is_girls else 'Boys')
        }


class MicrosoftTask(Task):
    def __init__(self):
        super().__init__()
        self.out_file = 'microsoft.csv'
        self.rows = ['Username',
                     'First name',
                     'Last name',
                     'Display name',
                     'Job title',
                     'Department',
                     'Office number',
                     'Office phone',
                     'Mobile phone',
                     'Fax',
                     'Alternate email address',
                     'Address',
                     'City',
                     'State or province',
                     'ZIP or postal code',
                     'Country or region']

    def process(self, row, data: TaskData):
        return {
            'Username': data.email,
            'First name': data.first_name,
            'Last name': data.last_name,
            'Display name': data.first_name + ' ' + data.last_name,
            'Department': str(data.year) + ' Student',
            'State or province': 'CA',
            'Country or region': 'United States'
        }


class MosyleTask(Task):
    def __init__(self):
        super().__init__()
        self.out_file = 'mosyle.csv'
        self.rows = ['#Full Name',
                     'Person ID',
                     'Email',
                     'Managed Apple ID',
                     'Location',
                     'Grade Level',
                     'Serial Number']

    def pre_pre_process(self, csv_writer: csv.DictWriter):
        csv_writer.writerow({
            '#Full Name': '#v2_students'
        })

    def pre_process(self, csv_writer: csv.DictWriter):
        csv_writer.writerow({
            '#Full Name': '#Required',
            'Person ID': 'Required - unique inside your school',
            'Email': 'Optional',
            'Managed Apple ID': 'Required if applicable',
            'Location': 'Required',
            'Grade Level': 'Required',
            'Serial Number': 'Optional'
        })
        csv_writer.writerow({
            '#Full Name': '#Start fill below here'
        })

    def process(self, row, data: TaskData):
        return {
            '#Full Name': data.first_name + ' ' + data.last_name,
            'Person ID': data.email.removesuffix(data.email_suffix),
            'Email': data.email,
            'Location': 'YULA Girls' if data.is_girls else 'YULA Boys',
            'Grade Level': str(data.grade) + 'th',
        }


def run_tasks(input_file: str, output_folder: str):
    tasks = [GmailTask(), AdobeTask(), MicrosoftTask(), MosyleTask()]

    for task in tasks:
        task.do(input_file, output_folder)
