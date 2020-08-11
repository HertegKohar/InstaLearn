import unittest

from mysql.connector.connection import MySQLConnection

from InstaDataPackage import Instabase


class TestDBase(unittest.TestCase):
    def test_connection(self):
        self.assertIsInstance(Instabase._connect_db(), MySQLConnection)

    def test_entries(self):
        self.assertIsInstance(Instabase.show_all(), list)
