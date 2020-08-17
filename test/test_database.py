import unittest
from sqlite3 import Connection, ProgrammingError

from mysql.connector.connection import MySQLConnection
from mysql.connector.errors import OperationalError

from InstaDataPackage.Instabase import DB_Session, DB_Session_Local


class TestDBase(unittest.TestCase):
    def test_connection(self):
        with DB_Session() as db:
            self.assertIsInstance(db._DB_Session__connection, MySQLConnection)
        with self.assertRaises(OperationalError):
            db._DB_Session__connection.cursor()

    def test_connection_local(self):
        with DB_Session_Local() as db:
            self.assertIsInstance(db._DB_Session_Local__connection, Connection)
        with self.assertRaises(ProgrammingError):
            db._DB_Session_Local__connection.cursor()

    def test_entries(self):
        with DB_Session() as db:
            result = db.show()
            self.assertIsInstance(result, list)
        if not result:
            self.fail("No entries in training table are apprearing")
