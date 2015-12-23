# -*- coding: utf-8 -*-
from unittest import TestCase
from xlrelease_export_pipeline import *


class TestBuildUrls(TestCase):
    def setUp(self):
        self.base_url = "http://localhost"

    def test_should_return_base_url(self):
        self.assertEqual('http://localhost/api/vl', build_api_base_url(self.base_url))

    def test_should_return_api_config_base_url(self):
        self.assertEqual('http://localhost/api/vl/config', build_api_config_base_url(self.base_url))

    def test_should_return_api_phases_base_url(self):
        self.assertEqual('http://localhost/api/vl/phases', build_api_phases_base_url(self.base_url))

    def test_should_return_api_releases_base_url(self):
        self.assertEqual('http://localhost/api/vl/releases', build_api_releases_base_url(self.base_url))

    def test_should_return_api_tasks_base_url(self):
        self.assertEqual('http://localhost/api/vl/tasks', build_api_tasks_base_url(self.base_url))

    def test_should_return_api_templates_base_url(self):
        self.assertEqual('http://localhost/api/vl/templates', build_api_templates_base_url(self.base_url))
