# -*- coding: utf-8 -*-
import json
import os
from collections import deque
from unittest import TestCase

from mock import Mock

from xlrelease_template_report_maker import XLReleaseJsonFetcher, ObjectModelBuilder, ReportBuilder

BASE_URL = 'http://127.0.0.1:5516'
TEMPLATE_ID = 'Release6710832'
USERNAME = 'admin'
PASSWORD = 'releqsepourlesmaous'
TEMPLATE_ID_PREFIX = 'Applications/'
FULLY_FORMED_URL = '%s/api/v1/templates/%s%s' % (BASE_URL, TEMPLATE_ID_PREFIX, TEMPLATE_ID)


class TestXLReleaseJsonFetcher(TestCase):
    def setUp(self):
        # TODO put username and password in a config file (or mock the whole thing)
        self.fetcher = XLReleaseJsonFetcher(BASE_URL, TEMPLATE_ID,
                                                                            USERNAME, PASSWORD)

    def test_should_build_api_base_url(self):
        self.assertEqual('%s/api/v1' % BASE_URL, self.fetcher.build_api_base_url())

    def test_should_build_api_templates_base_url(self):
        self.assertEqual('%s/api/v1/templates' % BASE_URL, self.fetcher.build_api_templates_base_url())

    def test_should_build_url(self):
        self.assertEqual(FULLY_FORMED_URL, self.fetcher.build_url())

    def test_should_send_http_request_to_xlrelease(self):
        resp = self.fetcher.send_http_request_to_xlrelease(FULLY_FORMED_URL)
        self.assertEqual(200, resp.status_code)


class TestObjectModelBuilder(TestCase):
    def setUp(self):
        with open('data/%s.json' % TEMPLATE_ID) as json_file:
            self.json_data = json.load(json_file)
            self.builder = ObjectModelBuilder(self.json_data)

    def test_should_extract_template_with_title(self):
        template = self.builder.build_template_obj()
        self.assertEqual('Test template for Excel Export', template.title)

    def test_should_find_phases(self):
        def get_all_phases(data):
            return deque([phase for phase in data['phases']])

        phases = get_all_phases(self.json_data)
        self.assertEqual('Phase 1', phases.popleft()['title'])
        self.assertEqual('Phase 2', phases.popleft()['title'])
        self.assertEqual('Phase 3', phases.popleft()['title'])


class TestReportBuilder(TestCase):
    def setUp(self):
        self.template = Mock(title='This is my title')
        self.builder = ReportBuilder(self.template)
        self.output_xlsx_filename = os.path.join('output', 'sample.xlsx')
        if os.path.exists(self.output_xlsx_filename):
            os.remove(self.output_xlsx_filename)

    def tearDown(self):
        if os.path.exists(self.output_xlsx_filename):
            os.remove(self.output_xlsx_filename)

    def test_should_write_excel_file(self):
        # write template info
        self.builder.build_template_info()
        # Data can be assigned directly to cells
        self.assertEqual(self.template.title, self.builder.worksheet['A1'].value)

    def test_should_save_to_file(self):
        self.builder.save_to_file(self.output_xlsx_filename)
        self.assertTrue(os.path.exists(self.output_xlsx_filename), 'File does not exist')
