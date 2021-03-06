# -*- coding: utf-8 -*-
import json
import os
from collections import deque
from unittest2 import TestCase

from mock import Mock

from xlrelease_template_report_maker import *

BASE_URL = 'http://127.0.0.1:5516'
TEMPLATE_ID = 'Release6710832'
USERNAME = 'admin'
PASSWORD = 'releqsepourlesmaous'
TEMPLATE_ID_PREFIX = 'Applications/'
FULLY_FORMED_URL = '%s/api/v1/templates/%s%s' % (BASE_URL, TEMPLATE_ID_PREFIX, TEMPLATE_ID)


#############################
# Testing XLR Json Fetcher
#############################

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


def check_on_test_directories_and_create_if_needed():
    current_path = os.getcwd()
    if 'test' not in current_path.split(os.sep)[-1]:
        extended_path = os.path.join(current_path, 'test')
        if not os.path.exists(extended_path):
            extended_path = os.path.join(current_path, 'tests')
            if not os.path.exists(extended_path):
                raise IOError(
                        "Directory 'test' or 'tests' not found in %r : "
                        "cannot reach 'data' and create 'output' directories needed for the tests" % current_path)
        current_path = extended_path
    data_path = os.path.join(current_path, 'data')
    output_path = os.path.join(current_path, 'output')
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return data_path, current_path


##################################
# Testing XLR Object Graph Builder
##################################

class TestXLRObjectGraphBuilder(TestCase):
    def setUp(self):
        data_path, output_path = check_on_test_directories_and_create_if_needed()
        with open(os.path.join(data_path, '%s.json' % TEMPLATE_ID)) as json_file:
            self.json_data = json.load(json_file)
            self.builder = XLRObjectGraphBuilder(self.json_data)

    def test_should_extract_template(self):
        template = self.builder.build_template_obj()
        self.assertIsNotNone(template)

    def test_should_extract_phases(self):
        phases = self.builder.build_phases_objs()
        self.assertEqual(3, len(phases))

    def test_should_extract_tasks(self):
        tasks = self.builder.build_tasks_objs(0)
        self.assertEqual(7, len(tasks))

    def test_should_build_model(self):
        template = self.builder.build()
        self.assertIsNotNone(template)
        phases = template.phases
        self.assertEqual(3, len(phases))
        tasks = phases[0].tasks
        self.assertEqual(7, len(tasks))
        tasks = phases[1].tasks
        self.assertEqual(1, len(tasks))
        tasks = phases[2].tasks
        self.assertEqual(4, len(tasks))


#######################
# Testing XLR Models
#######################


class TestXLRModelBase(TestCase):
    class XLRTestModel(XLRModelBase):
        JSON_TYPE_NODE = 'test.type'

        def __init__(self, json_data):
            super(TestXLRModelBase.XLRTestModel, self).__init__(json_data)

    def setUp(self):
        self.json_data = json.loads("{\"title\": \"any title\", \"type\": \"test.type\"}")
        self.json_data_wrong_type = json.loads("{\"title\": \"any title\", \"type\": \"any.other.test.type\"}")

    def test_should_verify_json_node_type(self):
        is_correct_type, msg = TestXLRModelBase.XLRTestModel.verify_json_node_type(self.json_data_wrong_type)
        self.assertFalse(is_correct_type)

    def test_should_Exception_when_wrong_json_node_type(self):
        with self.assertRaises(WrongJsonNodeTypeError):
            TestXLRModelBase.XLRTestModel(self.json_data_wrong_type)

    def test_should_extract_attributes(self):
        xlr_object = TestXLRModelBase.XLRTestModel(self.json_data)
        self.assertEqual(self.json_data['title'], xlr_object.title)


class TestXLRTemplate(TestCase):
    def setUp(self):
        self.json_node_type = "xlrelease.Release"
        self.json_data = json.loads("{\"title\": \"any title\", \"type\": \"%s\"}" % self.json_node_type)

    def test_should_have_correct_json_node_type(self):
        self.assertEqual(self.json_node_type, XLRTemplate.JSON_TYPE_NODE)

    def test_should_extract_attributes(self):
        xlr_object = XLRTemplate(self.json_data)
        self.assertEqual(self.json_data['title'], xlr_object.title)


class TestXLRPhase(TestCase):
    def setUp(self):
        self.json_node_type = "xlrelease.Phase"
        self.json_data = json.loads("{\"title\": \"any title\", \"type\": \"%s\"}" % self.json_node_type)

    def test_should_have_correct_json_node_type(self):
        self.assertEqual(self.json_node_type, XLRPhase.JSON_TYPE_NODE)

    def test_should_extract_attributes(self):
        xlr_object = XLRPhase(self.json_data)
        self.assertEqual(self.json_data['title'], xlr_object.title)


class TestXLRTask(TestCase):
    def setUp(self):
        self.json_node_type = ['xlrelease.GateTask', 'xlrelease.Task', 'xlrelease.NotificationTask',
                               'xlrelease.DeployitTask', 'xlrelease.ScriptTask', 'xlrelease.ParallelGroup',
                               'xlrelease.CustomScriptTask']
        self.json_data = json.loads("{\"title\": \"any title\", \"type\": \"xlrelease.Task\"}")

    def test_should_have_correct_json_node_type(self):
        self.assertEqual(self.json_node_type, XLRTask.JSON_TYPE_NODE)

    def test_should_extract_attributes(self):
        xlr_object = XLRTask(self.json_data)
        self.assertEqual(self.json_data['title'], xlr_object.title)


#############################
# Testing XLR Report Builder
#############################

class TestXLRReportBuilder(TestCase):
    def setUp(self):
        self.template = Mock(title='This is my title', phases=deque([]))
        self.template.phases.extend(deque([Mock(title='This is my title 1', tasks=[]),
                                           Mock(title='This is my title 2', tasks=[]),
                                           Mock(title='This is my title 3', tasks=[])]))
        self.template.phases[0].tasks.extend(deque([Mock(title='This is my title 1.1'),
                                                    Mock(title='This is my title 1.2')]))
        self.template.phases[1].tasks.extend(deque([Mock(title='This is my title 2.1'),
                                                    Mock(title='This is my title 2.2'),
                                                    Mock(title='This is my title 2.3')]))
        self.template.phases[2].tasks.extend(deque([Mock(title='This is my title 3.1'),
                                                    Mock(title='This is my title 3.2'),
                                                    Mock(title='This is my title 3.3'),
                                                    Mock(title='This is my title 3.4')]))
        self.builder = XLRReportBuilder(self.template)
        data_path, output_path = check_on_test_directories_and_create_if_needed()
        self.output_xlsx_filename = os.path.join(output_path, 'sample.xlsx')
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
        self.assertEqual(self.template.phases.popleft().title, self.builder.worksheet['A4'].value)
        self.assertEqual(self.template.phases.popleft().title, self.builder.worksheet['A7'].value)

    def test_should_populate_report_with_tasks(self):
        phase_position = 0
        offset = 2
        self.builder.populate_report_with_tasks_for_phase(phase_position=phase_position, offset=offset)
        self.assertEqual(self.template.phases[phase_position].tasks[0].title, self.builder.worksheet['B2'].value)
        self.assertEqual(self.template.phases[phase_position].tasks[1].title, self.builder.worksheet['B3'].value)
        phase_position = 1
        offset = 3
        self.builder.populate_report_with_tasks_for_phase(phase_position=phase_position, offset=offset)
        self.assertEqual(self.template.phases[phase_position].tasks[0].title, self.builder.worksheet['B4'].value)
        self.assertEqual(self.template.phases[phase_position].tasks[1].title, self.builder.worksheet['B5'].value)
        self.assertEqual(self.template.phases[phase_position].tasks[2].title, self.builder.worksheet['B6'].value)

    def test_should_build_report(self):
        self.builder.build_report()
        self.assertIsNotNone(self.builder.worksheet['A1'].value)

        self.assertIsNotNone(self.builder.worksheet['A2'].value)
        self.assertIsNotNone(self.builder.worksheet['B2'].value)
        self.assertIsNotNone(self.builder.worksheet['B3'].value)

        self.assertIsNotNone(self.builder.worksheet['A4'].value)
        self.assertIsNotNone(self.builder.worksheet['B4'].value)
        self.assertIsNotNone(self.builder.worksheet['B5'].value)
        self.assertIsNotNone(self.builder.worksheet['B6'].value)

        self.assertIsNotNone(self.builder.worksheet['A7'].value)
        self.assertIsNotNone(self.builder.worksheet['B7'].value)
        self.assertIsNotNone(self.builder.worksheet['B8'].value)
        self.assertIsNotNone(self.builder.worksheet['B9'].value)
        self.assertIsNotNone(self.builder.worksheet['B10'].value)

        self.assertIsNone(self.builder.worksheet['A11'].value)
        self.assertIsNone(self.builder.worksheet['B13'].value)

    def test_should_save_to_file(self):
        self.builder.save_to_file(self.output_xlsx_filename)
        self.assertTrue(os.path.exists(self.output_xlsx_filename), 'File does not exist')
