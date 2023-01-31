import hmac
import hashlib
import time
from requests.auth import AuthBase

class CBAdvAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        request.headers.update(get_auth_headers(timestamp, message, self.api_key, self.secret_key))
        return request

def get_auth_headers(timestamp, message, api_key, secret_key):
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    return {
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': api_key,
        }