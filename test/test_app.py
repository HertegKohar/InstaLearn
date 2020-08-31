import os
import unittest

import requests


class TestApp(unittest.TestCase):
    def test_status(self):
        json_data = {
            "username": os.environ["username"],
            "password": os.environ["password"],
        }
        response = requests.post(
            url=f"http://{os.environ.get('ip')}:{os.environ.get('port')}/status",
            json=json_data,
        )
        if response.json()["code"] == "fail":
            self.fail("Unable to get status")

    def test_add_user(self):
        json_data = {
            "username": os.environ.get("username"),
            "password": os.environ.get("password"),
        }
        response = requests.post(
            url=f"http://{os.environ.get('ip')}:{os.environ.get('port')}/add_user",
            json=json_data,
        )
        if response.json()["code"] == "success":
            self.fail("Root user added again")

