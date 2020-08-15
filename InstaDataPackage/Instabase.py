import mysql.connector
import pandas as pd
from mysql.connector.errors import IntegrityError
import os
import sqlite3


class DB_Session_Local:
    def __init__(self):
        pass

    def __enter__(self):
        self.__connection = sqlite3.connect("instabase.db")
        self.__cursor = self.__connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.__cursor.close()
        self.__connection.close()

    def insert(self, data):
        self.__cursor.execute(
            """INSERT INTO accounts VALUES('{info[0]}',{info[1]},{info[2]},
            {info[3]},{info[4]},{info[5]},{info[6]},{info[7]}) """.format(
                info=data
            )
        )
        self.__connection.commit()

    def show(self):
        self.__cursor.execute("SELECT * FROM accounts")
        for output in self.__cursor:
            print(output)


# Have to use .commit on database connection to save changes made in script
# Create a connection instance in order to communicate with the database
def _connect_db():
    """Creates a database connection to the MySQL server

    Returns:
        MySQL Connector: The connection to the MySQL server
    """
    db_connection = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        passwd=os.environ.get("DB_PASS"),
        auth_plugin="mysql_native_password",
        database="instabase",
    )
    return db_connection


# Description of table
def _description():
    """Gives a description of the database table

    Returns:
        List[Table Attributes]: List of table attributes
    """
    connection = _connect_db()
    cursor = connection.cursor()
    cursor.execute("DESCRIBE insta_train")
    description = [output for output in cursor]
    cursor.close()
    connection.close()
    return description


def insert_db(data):
    """Inserts user data into the database table

    Args:
        data (List[Tuple(User Data)]): List of user data
    """
    connection = _connect_db()
    cursor = connection.cursor()
    for info in data:
        try:
            cursor.execute(
                """INSERT INTO insta_train VALUES('{info[0]}',{info[1]},{info[2]},
            {info[3]},{info[4]},{info[5]},{info[6]},{info[7]}) """.format(
                    info=info
                )
            )
        except IntegrityError:
            cursor.execute(
                """ UPDATE insta_train SET posts={d[1]}, followers={d[2]}, following={d[3]}, private={d[4]}, 
				bio_tag={d[5]}, external_url={d[6]}, verified={d[7]} WHERE username='{d[0]}'""".format(
                    d=info
                )
            )
        finally:
            connection.commit()
    cursor.close()
    connection.close()


def size():
    """Returns the amount of rows in the database table

    Returns:
        Integer: Number of rows in database table
    """
    connection = _connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM insta_train")
    for output in cursor:
        rows = output[0]
    cursor.close()
    connection.close()
    return rows


def search_db(users):
    """Queries the database for users and returns their data

    Args:
        users (List[String]): List of usernames

    Returns:
        Pandas Dataframe: Table of all the users queried rows with data if found
    """
    connection = _connect_db()
    cursor = connection.cursor()
    pd.set_option("display.max_columns", None)
    df = pd.DataFrame(
        columns=[
            "User",
            "Posts",
            "Followers",
            "Following",
            "Private",
            "Bio_Tag",
            "External_Url",
            "Verified",
        ]
    )
    for user in users:
        cursor.execute("SELECT * FROM insta_train WHERE username='{:s}'".format(user))
        s = None
        for output in cursor:
            s = output
        if s:
            df_temp = {
                "User": s[0],
                "Posts": s[1],
                "Followers": s[2],
                "Following": s[3],
                "Private": bool(s[4]),
                "Bio_Tag": bool(s[5]),
                "External_Url": bool(s[6]),
                "Verified": bool(s[7]),
            }
            df = df.append(df_temp, ignore_index=True)
        else:
            df = df.append({"User": user}, ignore_index=True)
    cursor.close()
    connection.close()
    return df


def query_db(users):
    """Searches the database table for users

    Args:
        users (List[String]): List of usernames to search for

    Returns:
        Pandas DataFrame: Table of whether the users are in the database table
    """
    connection = _connect_db()
    cursor = connection.cursor()
    df = pd.DataFrame(columns=["User", "Found"])
    for user in users:
        cursor.execute("SELECT * FROM insta_train WHERE username='{:s}'".format(user))
        s = None
        for output in cursor:
            s = output
        if s:
            df = df.append({"User": user, "Found": True}, ignore_index=True)
        else:
            df = df.append({"User": user, "Found": False}, ignore_index=True)
    cursor.close()
    connection.close()
    return df


def show_all():
    """Shows all the entries in the database table

    Returns:
        List[Tuple(User Data)]: A list of all user data within the table
    """
    connection = _connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM insta_train")
    entries = [output for output in cursor]
    cursor.close()
    connection.close()
    return entries
