# -*- coding: utf-8 -*-
import os
from xlrelease_template_report_maker import XLReleaseJsonFetcher, ObjectModelBuilder, ReportBuilder

if __name__ == '__main__':
    base_url = 'http://127.0.0.1:5516'
    template_id = 'Release6710832'
    username = 'admin'
    password = 'releqsepourlesmaous'

    fetcher = XLReleaseJsonFetcher(base_url, template_id, username, password)
    json_data = fetcher.fetch()

    builder = ObjectModelBuilder(json_data)
    template = builder.build()

    report_builder = ReportBuilder(template)
    report_builder.build()
    report_builder.save_to_file(os.path.join('output', 'xlrelease_template_report.xls'))


