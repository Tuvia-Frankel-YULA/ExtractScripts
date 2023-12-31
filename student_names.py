import csv
import os

import configdata


class TaskData:
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 email: str,
                 grade: int,
                 year: int,
                 config_data: configdata.Config):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.grade = grade
        self.year = year
        self.config_data = config_data


class Task:
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
                    grade = int(row['Grade'].strip())
                    year = config_data.year_map[grade]

                    first_name = str(row['First Name']).strip()
                    last_name = str(row['Last Name']).strip()
                    # first_name = str(row['Student Name']).strip().removesuffix(last_name).strip()
                    email = str(row['Email'])
                    # (first_name[0] + last_name + str(year) + config_data.email_suffix).lower()

                    if grade in config_data.grades:
                        csv_writer.writerow(self.process(row,
                                                         TaskData(first_name,
                                                                  last_name,
                                                                  email,
                                                                  grade,
                                                                  year,
                                                                  config_data)))

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
            'Password [Required]': 'YULA' + str(data.year) + '!',
            'Org Unit Path [Required]': '/YULA ' + ('Girls' if data.config_data.is_girls else 'Boys') + '/' + str(
                data.year),
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
            'User Groups': 'YULA ' + ('Girls' if data.config_data.is_girls else 'Boys')
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
            'Person ID': data.email.removesuffix(data.config_data.email_suffix),
            'Email': data.email,
            'Location': 'Girls-YULA' if data.config_data.is_girls else 'YULA Boys',
            'Grade Level': str(data.year),
        }


def run_tasks(input_file: str, output_file: str):
    output_folder = os.path.dirname(output_file)
    tasks = [GmailTask(), AdobeTask(), MicrosoftTask(), MosyleTask()]

    for task in tasks:
        task.do(input_file, output_folder)
