import os
import unittest

import requests


class TestApp(unittest.TestCase):
    def test_status(self):
        raise NotImplementedError
        json_data = {
            "username": os.environ["username"],
            "password": os.environ["password"],
        }
        response = requests.post(
            url="{var['ip']}:{var['port']}".format(var=os.environ), json=json_data
        )
