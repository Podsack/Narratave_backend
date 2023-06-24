import requests


class HttpClient:
    instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        self.session = requests.Session()

    def get(self, url, params=None, headers=None):
        response = self.session.get(url, params=params, headers=headers)
        return response

    def post(self, url, data=None, headers=None):
        response = self.session.post(url, data=data, headers=headers)
        return response

    def close(self):
        self.session.close()
        self.instance = None
