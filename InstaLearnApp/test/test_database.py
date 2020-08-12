import unittest

from mysql.connector.connection import MySQLConnection

from InstaDataPackage import Instabase


class TestDBase(unittest.TestCase):
    def test_connection(self):
        connection = Instabase._connect_db()
        self.assertIsInstance(connection, MySQLConnection)
        connection.close()

    def test_entries(self):
        result = Instabase.show_all()
        self.assertIsInstance(result, list)
        if not result:
            self.fail("No Entries in traning table are apprearing")
