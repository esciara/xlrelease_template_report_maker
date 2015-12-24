# -*- coding: utf-8 -*-
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.

import requests
from openpyxl import Workbook
from requests.auth import HTTPBasicAuth


class XLReleaseJsonFetcher(object):
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


class ObjectModelBuilder(object):
    def __init__(self, json_data):
        self.json_data = json_data

    def build(self):
        return self.build_template_obj()

    def build_template_obj(self):
        return XLReleaseTemplate(self.json_data['title'])

        # class XLReleaseBaseClass(object):
        #     def __init__(self):
        #         pass

        # class XLReleaseTemplate(object):
        #     def __init__(self, title):
        #         self.title = title


class XLReleaseTemplate(object):
    def __init__(self, title):
        self.title = title


class ReportBuilder(object):
    def __init__(self, template):
        self.template = template
        self.workbook = Workbook()
        self.worksheet = self.workbook.active

    def build(self):
        self.build_template_info()

    def build_template_info(self):
        self.worksheet['A1'] = self.template.title

    def save_to_file(self, filename):
        self.workbook.save(filename)
