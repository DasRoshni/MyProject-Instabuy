import json
import os
import unittest
import sys

import webtest
from google.appengine.ext import testbed



USER_AGENTS = {
    'android': 'Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36',
    'browser': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
}

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        # Try to get your WSGI from the current_dir or the dir above if this
        # file is in tests
        if os.getcwd().split(os.sep)[-1] == 'tests':
            sys.path.append(os.path.dirname(os.getcwd()))
        else:
            sys.path.append(os.getcwd())
        # Change this to import the WSGI, wherever it is
        from main import app

        # Instantiate our WSGI
        self.testapp = webtest.TestApp(app)

        # Activate testbed to test different GAE extensions
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        # Activate the different GAE extensions
        # The different activateble stubs are listed here:
        # https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting
        self.testbed.init_blobstore_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def printResults(self, expect, actual):
        print '\n\nExpected: {0}\nActual: {1}\n'.format(expect, actual)

    def checkStatusCode(self, expect, actual):
        self.printResults(expect, actual)
        self.assertEquals(expect, actual)


    def test_main_page_browser(self):
        """Simulate browser GET request and expect HTML body back"""
        resp = self.testapp.get('/', headers={'user-agent': USER_AGENTS['browser']})

        self.checkStatusCode(200, resp.status_code)

        res = '<html>' in resp.body

        self.printResults(res, True)
        self.assertTrue(res)

    def test_main_page_android(self):
        """Simulate Android request and expect JSON"""
        resp = self.testapp.get('/', headers={'user-agent': USER_AGENTS['android']})

        self.checkStatusCode(200, resp.status_code)

        actual = json.loads(resp.body)
        expect = {'images': []}

        self.printResults(expect, actual)
        self.assertEquals(expect, actual)
