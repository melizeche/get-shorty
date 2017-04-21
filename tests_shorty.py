import os
import json
import getshorty
import unittest
import tempfile

URL = 'http://google.com'
URL_MOBILE = 'http://facebook.com'
URL_TABLET = 'https://yahoo.com'
BAD_URL = 'http//google.com'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
UA_MOBILE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
UA_TABLET = 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'


class GetShortyTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, getshorty.app.config['DATABASE'] = tempfile.mkstemp()
        getshorty.app.config['TESTING'] = True
        self.app = getshorty.app.test_client()
        with getshorty.app.app_context():
            getshorty.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(getshorty.app.config['DATABASE'])

    def test_empty_db(self):
        resp = self.app.get('/api/1.0/list')
        assert b'[]' in resp.data

    def test_bad_methods(self):
        resp = self.app.post('/api/1.0/list')
        resp2 = self.app.get('/api/1.0/create')
        assert resp.status_code == 405
        assert resp2.status_code == 405

    def test_create_empty(self):
        resp = self.app.post('/api/1.0/create', data='{}')
        assert b'"url parameter is mandatory' in resp.data

    def test_create_badurl(self):
        resp = self.app.post(
            '/api/1.0/create', data=json.dumps(dict(url=BAD_URL)))
        assert b'"invalid url"' in resp.data

    def test_create_single(self):
        resp = self.app.post(
            '/api/1.0/create', data=json.dumps(dict(url=URL)))
        assert resp.status_code == 201
        short_url = json.loads(resp.data.decode('utf-8'))['shorten']
        resp2 = self.app.get(short_url)
        assert resp2.status_code == 302

    def test_create_complete(self):
        resp = self.app.post(
            '/api/1.0/create', data='{"url":"%s","url-mobile":"%s","url-tablet":"%s"}' % (URL, URL_MOBILE, URL_TABLET))
        assert resp.status_code == 201
        short_url = json.loads(resp.data.decode('utf-8'))['shorten']
        resp_default = self.app.get(short_url, environ_base={'HTTP_USER_AGENT':UA})
        assert resp_default.status_code == 302
        assert resp_default.location == URL
        resp_mobile = self.app.get(short_url, environ_base={'HTTP_USER_AGENT':UA_MOBILE})
        assert resp_mobile.status_code == 302
        assert resp_mobile.location == URL_MOBILE
        resp_tablet = self.app.get(short_url, environ_base={'HTTP_USER_AGENT':UA_TABLET})
        assert resp_tablet.status_code == 302
        assert resp_tablet.location == URL_TABLET


if __name__ == '__main__':
    unittest.main()
