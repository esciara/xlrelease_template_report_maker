# -*- coding: utf-8 -*-
import os
from xlrelease_template_report_maker import XLRJsonFetcher, XLRObjectGraphBuilder, XLRReportBuilder

if __name__ == '__main__':
    base_url = 'http://127.0.0.1:5516'
    template_id = 'Release6710832'
    username = 'admin'
    password = 'releqsepourlesmaous'

    fetcher = XLRJsonFetcher(base_url, template_id, username, password)
    json_data = fetcher.fetch()

    builder = XLRObjectGraphBuilder(json_data)
    template = builder.build()

    report_builder = XLRReportBuilder(template)
    report_builder.build_report()
    report_builder.save_to_file(os.path.join('output', 'xlrelease_template_report.xls'))


