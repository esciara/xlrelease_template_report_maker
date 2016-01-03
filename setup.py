from setuptools import setup

setup(
        name='xlrelease_template_report_maker',
        version='0.1.dev0',
        packages=['tests'],
        url='https://github.com/esciara/xlrelease_template_report_maker',
        license='GNU LGPL',
        author='Emmanuel Sciara',
        author_email='emmanuel.sciara@gmail.com',
        description="This module exports the data of a XebiaLabs' XLRelease's Template in an Excel report",
        keywords="odoo openerp xml-rpc xmlrpc",
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        install_requires=[
            'requests~=2.9',
            'openpyxl~=2.3',
        ],
        tests_require=[
            'mock~=1.0',
            'unittest2~=1.1',
        ],
        test_suite='unittest2.collector'
)
