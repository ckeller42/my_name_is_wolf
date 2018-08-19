#!/usr/bin/python
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


import copy
import os

from jira import JIRA


class JiraWrapper:
    """
    Setting for connecting to JIRA
    """

    def __init__(self, params):
        # general settings
        self.params = params
        self.jira = None

        # Proxy settings

        if "HTTP_PROXY" not in os.environ:
            if params.get_http_proxy_url:
                os.environ["HTTP_PROXY"] = params.get_http_proxy_url

        if "HTTPS_PROXY" not in os.environ:
            if params.get_https_proxy_url:
                os.environ["HTTPS_PROXY"] = params.get_https_proxy_url

        # jira settings
        self.jira_url = self.params.get_jira_url
        self.jira_url = self.jira_url.strip("/")

        # see if we need to use a certificate
        if params.get_use_cert:
            self.jira_options = {
                "server": self.jira_url,
                "verify": True,
                "client_cert": ("mycert-dn.crt", "mycert-dn.key",)
            }
        else:
            self.jira_options = {
                "server": self.jira_url}

    # noinspection PyAttributeOutsideInit
    def connect(self, username, password: str):
        """
        Trigger the connection to jira
        :param username:
        :param password: user password for the connection
        :return: True on success
        """
        try:
            print('Connecting to Jira')
            self.jira = JIRA(options=self.jira_options, basic_auth=(username, password), max_retries=1)
            print('Connected')
            return True, None

        except Exception as e:
            print('Unable to connect')
            print(str(e))
            pass
            return False, e

    @property
    def get_components(self) -> list:
        """
        Get list of components available on the server
        :return: available compnents
        """

        components = self.jira.project_components(self.params.get_project)
        component_list = []
        for i in components:
            component_list.append(i.name)

        return component_list

    def create_components(self, components: list) -> list:
        """
        Create components if the do not already exist
        :param components: components to create
        :return: list of created components
        """
        components_avail = self.get_components
        components_todo = set(components) - set(components_avail)

        for i in components_todo:
            self.jira.create_component(i, self.params.get_project)

        return list(components_todo)

    def create_task_subtask(self, task_name: str, comment: str, reporter: str, parent_assignee: str,
                            sub_assignees: list, duedate: str,
                            labels: [str], priority: str):
        """
        Creat a task and all subtasks for the users
        :param reporter: who reports the bug
        :param priority:
        :param comment:
        :param task_name: Name of the task
        :param parent_assignee: Who is the owner of the parent task
        :param sub_assignees: List of people getting the subtasks. Needs to be jira userids
        :param duedate: what is the duedate for the parent task and the subtasks
        :param labels: Labels the tasks get added
        :return: url to the jira task for the webbrowser
        """

        # return values
        parent_url = None
        error_msg = None

        parent_component = None
        parent_assignee_id = None
        for i in sub_assignees:
            if parent_assignee == i[0]:
                parent_assignee_id = i[1]
                parent_component = i[2]
                break
        assert parent_assignee_id

        # TODO this only works if the reporter is part of the assignee list.
        reporter_id = ''
        for i in sub_assignees:
            if reporter == i[0]:
                reporter_id = i[1]
                break

        assert reporter_id

        # sub_assignees = self.get_users(sub_assignees)
        issue_dict = {
            'project': self.params.get_project,
            'summary': task_name,
            'description': comment,
            'issuetype': {'name': 'Task'},
            'assignee': {'name': parent_assignee_id},
            'duedate': duedate,
            'labels': labels,
            'priority': {'name': priority}
        }
        if parent_component:
            issue_dict['components'] = [{'name': parent_component}]

        # TODO allow change reporter
        if self.params.can_change_reporter:
            issue_dict['reporter'] = {'name': reporter_id}

        # print("Creating task")
        # print(sub_assignees)
        # print(issue_dict['assignee'])

        # for debugging set to false to no swap jira
        create = True
        parent_issue = None
        if create:
            try:
                parent_issue = self.jira.create_issue(fields=issue_dict)
                print("Created task: %s" % parent_issue.key)
            except Exception as e:
                print(e)
                parent_url = None
                error_msg = e.text
                pass

        # we were not able to create a issue. Connection error?
        if not parent_issue:
            return parent_url, error_msg

        # does your handle bulk create?
        can_bulk = True

        # now create the sub-task, linked to the parent task for all users
        child_issue_dict = []
        for val in sub_assignees:
            # val[3] is the bool if the task has to be created
            if val[3]:
                print('Creating Sub-tak for:', val[0])
                cur_issue_dict = copy.deepcopy(issue_dict)
                cur_issue_dict['summary'] = '(Subtask) ' + task_name
                cur_issue_dict['issuetype'] = {'name': 'Sub-task'}
                if create:
                    # noinspection PyUnresolvedReferences
                    # cur_issue_dict['parent'] = {"id": parent_issue.key}
                    cur_issue_dict['parent'] = {"id": parent_issue.id}
                cur_issue_dict['assignee'] = {'name': val[1]}

                # if componets for the user, add it
                if val[2]:
                    cur_issue_dict['components'] = [{'name': val[2]}]
                else:
                    cur_issue_dict['components'] = []

                if not can_bulk:
                    print('Slow call of Sub-task creation')
                    self.jira.create_issue(cur_issue_dict)
                else:
                    child_issue_dict.append(cur_issue_dict)

        if create and len(child_issue_dict) > 0:
            try:
                self.jira.create_issues(child_issue_dict)
            except Exception as e:
                print('Error creating Sub-Tasks. Message:')
                print(e)
                pass

        assert parent_issue

        parent_url = '%s/%s/%s' % (self.jira_url, 'browse', parent_issue.key)
        print(parent_url)
        return parent_url, error_msg

    def get_users(self, userlist):
        """
        For all the users in the self.full_assignee_list get the user ids from JIRA
        :return:
        """
        for i, val in enumerate(userlist):
            tmp = self.jira.search_assignable_users_for_projects(val[0], self.params.get_project)
            if not tmp:
                raise Exception('Could not find userid for %s' % val[0])

            userlist[i][1] = tmp[0].key
        return userlist


if __name__ == '__main__':

    from my_name_is_wolf import parameter_wrapper

    params = parameter_wrapper.ParameterWrapper()
    params.read()
    jirawrapper = JiraWrapper(params)
    username = 'ADDME'
    password = 'ADDME'

    connection_ok = jirawrapper.connect(username, password)
    if connection_ok:
        print('Connection successfull')
