from kivy.network.urlrequest import UrlRequest
import urllib

def success(req, result):
    print 'ok'
def fail(req, result):
    print 'fail'

params = urllib.urlencode({'@number': 12524, '@type': 'issue',
    '@action': 'show'})
headers = {'Content-type': 'application/x-www-form-urlencoded',
          'Accept': 'text/plain'}

UrlRequest('http://127.0.0.1:8000', on_success=success, on_failure=fail, on_error=fail, req_body=params, req_headers=headers)