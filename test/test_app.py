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
            url="http://{var[ip]}:{var[port]}/status".format(var=os.environ),
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
            url="http://{var[ip]}:{var[port]}/add_user".format(var=os.environ),
            json=json_data,
        )
        if response.json()["code"] == "success":
            self.fail("Root user added again")

