# -*- coding: utf-8 -*-
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.

import httplib
import urllib2
import base64
import sys
import json

# Parameters to be changed
from pprint import pprint

username = "admin"
password = "releqsepourlesmaous"
baseUrl = "http://localhost:5516"  # Or HTTPS

numberByPage = 1000

# set these to a file path to use client auth, e.g. if XL Release is running using mutual SSL:
# pemFile = '/path/to/my/key.pern'
# clientCertFile = '/path/to/my/cert.pern'
pemFile = None
clientCertFile = None
forceSslv3 = False

# see https://stackoverflow.com/questions/17 9273 3 9/forcing-mechanize-to-use-sslv3
if forceSslv3:
    import ssl
    from ssl import PROTOCOL_SSLv23, PROTOCOL_SSLv3, CERT_NONE, SSLSocket


    def monkey_wrap_socket(sock, keyfile=None, certfile=None,
                           server_side=False, cert_reqs=CERT_NONE, ssl_version=PROTOCOL_SSLv23, ca_certs=None,
                           do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None):
        ssl_version = PROTOCOL_SSLv3
        # for Python 2.6 or lower, remove the "ciphers" argument
        return SSLSocket(sock, keyfile=keyfile, certfile=certfile,
                         server_side=server_side, cert_reqs=cert_reqs, ssl_version=ssl_version, ca_certs=ca_certs,
                         do_handshake_on_connect=do_handshake_on_connect, suppress_ragged_eofs=suppress_ragged_eofs,
                         ciphers=ciphers)
        ssl.wrap_socket = monkey_wrap_socket


# see http://www.osmonov.com/2009/04/client-certificates-with-urllib2.html


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def init(self, key, cert):
        urllib2.HTTPSHandler.init(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)


if pemFile is not None and clientCertFile is not None:
    cert_handler = HTTPSClientAuthHandler(pemFile, clientCertFile)
    opener = urllib2.build_opener(cert_handler)
    urllib2.install_opener(opener)


def build_api_base_url(base_url):
    return "%s/api/vl" % base_url


def build_api_config_base_url(base_url):
    return "%s/config" % build_api_base_url(base_url)


def build_api_phases_base_url(base_url):
    return "%s/phases" % build_api_base_url(base_url)


def build_api_releases_base_url(base_url):
    return "%s/releases" % build_api_base_url(base_url)


def build_api_tasks_base_url(base_url):
    return "%s/tasks" % build_api_base_url(base_url)


def build_api_templates_base_url(base_url):
    return "%s/templates" % build_api_base_url(base_url)


def get_template_details(template_id):
    print "Getting templates details for template %r" % template_id
    uri = "%s/Applications/%s" % (build_api_templates_base_url(baseUrl), template_id)
    print "Fully formed URI: %s" % uri
    req = urllib2.Request(uri, headers={'Content-Type': 'application/json'})
    req = add_authorisation_to_request(req, username, password)
    data = json.load(urllib2.urlopen(req))
    print "Resulting JSON:"
    pprint(data)
    return data


def releases_search_req(uri, username, password):
    print "."
    req = urllib2.Request(uri,
                          data='{"active": true, "onlyMine": false, "onlyFlagged": false, "planned": true, "completed": true, "filter": ""}',
                          headers={'Content - Type': 'application / json'})
    req = add_authorisation_to_request(req, username, password)
    return urllib2.urlopen(req)


def templates_search_req(uri, username, password):
    print "."
    req = urllib2.Request(uri, headers={'Content-Type': 'application/json'})
    req = add_authorisation_to_request(req, username, password)
    return urllib2.urlopen(req)


def add_authorisation_to_request(req, username, password):
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    req.add_header("Authorization", "Basic %s" % base64string)
    return req


def releases_resp_by_page(p):
    url = build_releases_resp_by_page_url(p)
    return releases_search_req(url, username, password).read()


def build_releases_resp_by_page_url(p):
    uri = build_api_releases_base_url(baseUrl) + "/search" + build_url_pagination_suffixe(numberByPage, p)
    return uri


def templates_resp_by_page(p):
    uri = "%s/releases/templates?numberbypage=%s&page=%s" % (baseUrl, numberByPage, p)
    return templates_search_req(uri, username, password).read()


def templates_resp_by_page2():
    uri = "%s/api/vl/templates" % (baseUrl)
    return templates_search_req(uri, username, password).read()


def count_results(respByPage):
    goOn = True
    page = 0
    amount = 0
    while goOn:
        j = json.loads(respByPage(page))
        amount += len(j['cis'])
        page += 1
        goOn = len(j['cis']) > 0
    return amount


def triggers(respByPage):
    j = json.loads(respByPage())
    for ci in j:
        if len(ci['releaseTriggers']) > 0:
            print "Template with id %s has : %s triggers" % (ci['id'],
                                                             len(ci['releaseTriggers']))
            print " Triggers are : "
            for trigger in ci['releaseTriggers']:
                print " %s trigger (enabled: %s)" % (trigger['type'], trigger['enabled'])
