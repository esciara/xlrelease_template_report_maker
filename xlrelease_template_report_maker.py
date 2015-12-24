# -*- coding: utf-8 -*-
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.

from abc import ABCMeta, abstractmethod, abstractproperty
import requests
from openpyxl import Workbook
from requests.auth import HTTPBasicAuth
from collections import deque


class XLRJsonFetcher(object):
    def __init__(self, base_url, template_id, username, password):
        self.base_url = base_url
        self.template_id = template_id
        self.username = username
        self.password = password

    def fetch(self):
        url = self.build_url()
        resp = self.send_http_request_to_xlrelease(url)
        return resp.json()

    def build_api_base_url(self):
        return "%s/api/v1" % self.base_url

    def build_api_templates_base_url(self):
        return "%s/templates" % self.build_api_base_url()

    def build_url(self):
        return "%s/Applications/%s" % (self.build_api_templates_base_url(), self.template_id)

    def send_http_request_to_xlrelease(self, url):
        return requests.get(url, auth=HTTPBasicAuth(self.username, self.password))


class XLRObjectGraphBuilder(object):
    def __init__(self, json_data):
        self.json_data = json_data
        self.template = None

    def build(self):
        self.template = self.build_template_obj()
        self.template.phases.extend(self.build_phases_objs())
        return self.template

    def build_template_obj(self):
        return XLRTemplate(self.json_data)

    def build_phases_objs(self):
        return deque([XLRPhase(phase) for phase in self.json_data['phases']])


class WrongJsonNodeTypeError(Exception):
    pass


class XLRModelBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, json_data):
        if not self.verify_json_node_type(json_data):
            raise WrongJsonNodeTypeError()
        # verify type
        self.title = json_data['title']

    @classmethod
    def verify_json_node_type(cls, json_data):
        return json_data['type'] == cls.JSON_TYPE_NODE


class XLRTemplate(XLRModelBase):
    JSON_TYPE_NODE = 'xlrelease.Release'

    def __init__(self, json_data):
        super(XLRTemplate, self).__init__(json_data)
        self.phases = []


class XLRPhase(XLRModelBase):
    JSON_TYPE_NODE = 'xlrelease.Phase'

    def __init__(self, json_data):
        super(XLRPhase, self).__init__(json_data)


class XLRReportBuilder(object):
    def __init__(self, template):
        self.template = template
        self.workbook = Workbook()
        self.worksheet = self.workbook.active

    def build_report(self):
        self.populate_report_with_template()
        self.populate_report_with_phases()

    def populate_report_with_template(self):
        self.worksheet['A1'] = self.template.title

    def populate_report_with_phases(self):
        # TODO put le phases in a method "build_phase_info" or populate_phase_info
        for i in range(len(self.template.phases)):
            self.worksheet["A{0}".format(2 + i)] = self.template.phases[i].title

    def save_to_file(self, filename):
        self.workbook.save(filename)
