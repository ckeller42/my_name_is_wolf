# -*- coding: utf-8; -*-
"""
Gui implementation for gui created via qt-designer.
"""
__author__ = "Christoph G. Keller"
__copyright__ = "Copyright 2017"
__credits__ = [""]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Christoph G. Keller"
__email__ = "christoph.g.keller@gmail.com"
__status__ = "Production"

import configparser
import csv
import os


class ParameterWrapper:
    def __init__(self):
        self.conf_fname = 'my_name_is_wolf.ini'
        # create a default config
        self.conf = configparser.ConfigParser()

        self.conf.add_section('login')
        self.conf.set('login', 'use_cert', 'False')

        # JIRA
        self.conf.add_section('jira')
        self.conf.set('jira', 'project', '')
        self.conf.set('jira', 'jira_url', 'https://ckeller.atlassian.net/')
        self.conf.set('jira', 'can_change_reporter', 'True')

        # PROXY
        self.conf.add_section('proxy')
        self.conf.set('proxy', 'use_proxy', 'False')
        self.conf.set('proxy', 'http_proxy_url', '')
        self.conf.set('proxy', 'https_proxy_url', '')

        # LABELS
        self.conf.add_section('labels')
        self.conf.set('labels', 'default', '')

        # ASSIGNEE file
        self.conf.add_section('assignees')
        self.conf.set('assignees', 'default', 'users.csv')

    def save(self):
        f = open(self.conf_fname, 'w')
        self.conf.write(f)
        f.close()

    def read(self):
        if os.path.isfile(self.conf_fname):
            f = open(self.conf_fname, 'r')
            self.conf.read_file(f)
            f.close()
            return True
        else:
            return False

    @property
    def get_use_cert(self):
        value = self.conf.getboolean('login', 'use_cert')
        return value

    def set_use_cert(self, user_cert):
        self.conf.set('login', 'use_cert', str(user_cert))

    @property
    def can_change_reporter(self):
        value = self.conf.getboolean('jira', 'can_change_reporter')
        return value

    def set_can_change_reporter(self, can_change):
        self.conf.set('jira', 'can_change_reporter', str(can_change))

    @property
    def get_use_proxy(self):
        value = self.conf.getboolean('proxy', 'use_proxy')
        return value

    def set_use_proxy(self, useproxy):
        self.conf.set('proxy', 'use_proxy', str(useproxy))

    @property
    def get_http_proxy_url(self):
        http_proxy_url = self.conf.get('proxy', 'http_proxy_url')
        return http_proxy_url

    def set_http_proxy_url(self, http_proxy_url):
        self.conf.set('proxy', 'http_proxy_url', http_proxy_url)

    @property
    def get_https_proxy_url(self):
        https_proxy_url = self.conf.get('proxy', 'https_proxy_url')
        return https_proxy_url

    def set_https_proxy_url(self, https_proxy_url):
        self.conf.set('proxy', 'https_proxy_url', https_proxy_url)

    @property
    def get_config(self):
        labels = self.conf.get('labels', 'default')
        labels = labels.split(',')
        labels = [item.strip() for item in labels]
        assignee_fname = self.conf.get('assignees', 'default')
        assert isinstance(assignee_fname, str)
        return labels, assignee_fname

    @property
    def get_project(self):
        project = self.conf.get('jira', 'project')
        return project

    def set_project(self, project):
        self.conf.set('jira', 'project', project)

    @property
    def get_jira_url(self):
        jira_url = self.conf.get('jira', 'jira_url')
        assert jira_url
        return jira_url

    def set_jira_url(self, url):
        self.conf.set('jira', 'jira_url', url)

    @property
    def get_labels(self):
        all_labels, assignees_fname = self.get_config
        return list(set(all_labels))

    def add_label(self, new_label):
        labels = self.conf.get('labels', 'default')
        if len(labels) > 0:
            labels += ', %s' % new_label
        else:
            labels = '%s' % new_label

        self.conf.set('labels', 'default', labels)

    @property
    def get_assignee_fname(self):
        return self.conf.get('assignees', 'default')

    @property
    def get_assignees(self):
        full_assignees = self.load_users()
        return full_assignees

    def load_users(self):
        userfile = self.get_assignee_fname
        full_assignees = []
        if os.path.isfile(userfile):
            with open(userfile, 'r', encoding='utf-8') as csvfile:
                userreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in userreader:
                    if row:
                        full_assignees.append([row[0].strip(), '', row[1].strip()])
                    else:
                        print("Empty row do you want that?")
        else:
            print('File does not exist. Starting with empty user list.')
        return full_assignees

    def write_users(self, full_assignees):
        with open(self.get_assignee_fname, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [writer.writerow([r[0], r[2]]) for r in full_assignees]


if __name__ == '__main__':
    # open the configuratoin file
    params = ParameterWrapper()
    # example = []
    # example.append(['Christoph Keller', 'Test'])
    # example.append(['Christoph Keller', 'Test2'])

    example = params.load_users()
    print(example)
    params.write_users(example)
