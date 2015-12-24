# -*- coding: utf-8 -*-
import json
import os
from collections import deque
from unittest import TestCase

from mock import Mock

from xlrelease_template_report_maker import *

BASE_URL = 'http://127.0.0.1:5516'
TEMPLATE_ID = 'Release6710832'
USERNAME = 'admin'
PASSWORD = 'releqsepourlesmaous'
TEMPLATE_ID_PREFIX = 'Applications/'
FULLY_FORMED_URL = '%s/api/v1/templates/%s%s' % (BASE_URL, TEMPLATE_ID_PREFIX, TEMPLATE_ID)


class TestXLRJsonFetcher(TestCase):
    def setUp(self):
        # TODO put username and password in a config file (or mock the whole thing)
        self.fetcher = XLRJsonFetcher(BASE_URL, TEMPLATE_ID,
                                      USERNAME, PASSWORD)

    def test_should_build_api_base_url(self):
        self.assertEqual('%s/api/v1' % BASE_URL, self.fetcher.build_api_base_url())

    def test_should_build_api_templates_base_url(self):
        self.assertEqual('%s/api/v1/templates' % BASE_URL, self.fetcher.build_api_templates_base_url())

    def test_should_build_url(self):
        self.assertEqual(FULLY_FORMED_URL, self.fetcher.build_url())

        # def test_should_send_http_request_to_xlrelease(self):
        #     resp = self.fetcher.send_http_request_to_xlrelease(FULLY_FORMED_URL)
        #     self.assertEqual(200, resp.status_code)


class TestXLRObjectGraphBuilder(TestCase):
    def setUp(self):
        with open('data/%s.json' % TEMPLATE_ID) as json_file:
            self.json_data = json.load(json_file)
            self.builder = XLRObjectGraphBuilder(self.json_data)

    def test_should_extract_template(self):
        template = self.builder.build_template_obj()
        self.assertIsNotNone(template)

    def test_should_extract_phases(self):
        phases = self.builder.build_phases_objs()
        self.assertEqual(3, len(phases))

    def test_should_extract_template_with_phases(self):
        template = self.builder.build()
        self.assertIsNotNone(template)
        self.assertEqual(3, len(template.phases))


class TestXLRTemplate(TestCase):
    def setUp(self):
        self.json_data = json.loads("{\"title\": \"any title\", \"type\": \"xlrelease.Release\"}")
        self.json_data_wrong_type = json.loads("{\"title\": \"any title\", \"type\": \"any.other.type\"}")

    def test_should_verify_json_node_type(self):
        self.assertTrue(XLRTemplate.verify_json_node_type(self.json_data))
        self.assertFalse(XLRTemplate.verify_json_node_type(self.json_data_wrong_type))

    def test_should_Exception_when_wrong_json_node_type(self):
        with self.assertRaises(WrongJsonNodeTypeError):
            XLRTemplate(self.json_data_wrong_type)

    def test_should_extract_attributes(self):
        template = XLRTemplate(self.json_data)
        self.assertEqual(self.json_data['title'], template.title)

class TestXLRReportBuilder(TestCase):
    def setUp(self):
        self.template = Mock(title='This is my title', phases=deque([]))
        self.template.phases.extend(deque([Mock(title='This is my title 1'),
                                           Mock(title='This is my title 2'),
                                           Mock(title='This is my title 3')]))
        self.builder = XLRReportBuilder(self.template)
        self.output_xlsx_filename = os.path.join('output', 'sample.xlsx')
        if os.path.exists(self.output_xlsx_filename):
            os.remove(self.output_xlsx_filename)

    def tearDown(self):
        if os.path.exists(self.output_xlsx_filename):
            os.remove(self.output_xlsx_filename)

    def test_should_populate_report_with_template(self):
        self.builder.populate_report_with_template()
        self.assertEqual(self.template.title, self.builder.worksheet['A1'].value)

    def test_should_populate_report_with_phases(self):
        self.builder.populate_report_with_phases()
        self.assertEqual(self.template.phases.popleft().title, self.builder.worksheet['A2'].value)
        self.assertEqual(self.template.phases.popleft().title, self.builder.worksheet['A3'].value)
        self.assertEqual(self.template.phases.popleft().title, self.builder.worksheet['A4'].value)

    def test_should_build_report(self):
        self.builder.build_report()
        self.assertIsNotNone(self.builder.worksheet['A1'].value)
        self.assertIsNotNone(self.builder.worksheet['A2'].value)
        self.assertIsNotNone(self.builder.worksheet['A3'].value)
        self.assertIsNotNone(self.builder.worksheet['A4'].value)
        self.assertIsNone(self.builder.worksheet['A5'].value)

    def test_should_save_to_file(self):
        self.builder.save_to_file(self.output_xlsx_filename)
        self.assertTrue(os.path.exists(self.output_xlsx_filename), 'File does not exist')
