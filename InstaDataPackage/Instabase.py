import os
import sqlite3

import mysql.connector
import pandas as pd
from mysql.connector.errors import IntegrityError

# Have to use .commit on database connection to save changes made in script
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
        try:
            self.__cursor.execute(
                """INSERT INTO accounts VALUES('{info[0]}',{info[1]},{info[2]},
                {info[3]},{info[4]},{info[5]},{info[6]},{info[7]}) """.format(
                    info=data
                )
            )
        except sqlite3.IntegrityError:
            self.__cursor.execute(
                """ UPDATE accounts SET posts={d[1]}, followers={d[2]}, following={d[3]}, private={d[4]},
        		bio_tag={d[5]}, external_url={d[6]}, verified={d[7]} WHERE username='{d[0]}'""".format(
                    d=data
                )
            )
        finally:
            self.__connection.commit()

    def transfer(self):
        self.__cursor.execute("SELECT * FROM accounts")
        with DB_Session() as db:
            for info in self.__cursor:
                db.insert(info)
            print(db.size())
        self.__cursor.execute("DELETE FROM accounts")
        self.__connection.commit()
        self.__cursor.execute("vacuum")
        self.__connection.commit()

    def show(self):
        self.__cursor.execute("SELECT * FROM accounts")
        for output in self.__cursor:
            print(output)

    def size(self):
        self.__cursor.execute("SELECT COUNT(*) FROM accounts")
        for output in self.__cursor:
            print("Accounts: {}".format(output))
        self.__cursor.execute("SELECT COUNT(*) FROM users")
        for output in self.__cursor:
            print("Users: {}".format(output))


class DB_Session:
    def __init__(self):
        pass

    def __enter__(self):
        self.__connection = mysql.connector.connect(
            host="localhost",
            user=os.environ.get("DB_USER"),
            passwd=os.environ.get("DB_PASS"),
            auth_plugin="mysql_native_password",
            database="instabase",
        )
        self.__cursor = self.__connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.__cursor.close()
        self.__connection.close()

    # Description of table
    def _description(self):
        """Gives a description of the database table

        Returns:
            List[Table Attributes]: List of table attributes
        """
        self.__cursor.execute("DESCRIBE insta_train")
        description = [output for output in self.__cursor]
        return description

    def insert(self, data):
        """Inserts user data into the database table

        Args:
            data: Tuple(User Data): Processed user data
        """
        try:
            self.__cursor.execute(
                """INSERT INTO insta_train VALUES('{info[0]}',{info[1]},{info[2]},
            {info[3]},{info[4]},{info[5]},{info[6]},{info[7]}) """.format(
                    info=data
                )
            )
        except IntegrityError:
            self.__cursor.execute(
                """ UPDATE insta_train SET posts={d[1]}, followers={d[2]}, following={d[3]}, private={d[4]}, 
                bio_tag={d[5]}, external_url={d[6]}, verified={d[7]} WHERE username='{d[0]}'""".format(
                    d=data
                )
            )
        finally:
            self.__connection.commit()

    def size(self):
        """Returns the amount of rows in the database table

        Returns:
            Integer: Number of rows in database table
        """
        self.__cursor.execute("SELECT COUNT(*) FROM insta_train")
        for output in self.__cursor:
            rows = output[0]
        return rows

    def search(self, users):
        """Queries the database for users and returns their data

        Args:
            users (List[String]): List of usernames

        Returns:
            Pandas Dataframe: Table of all the users queried rows with data if found
        """
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
            self.__cursor.execute(
                "SELECT * FROM insta_train WHERE username='{:s}'".format(user)
            )
            s = None
            for output in self.__cursor:
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
        return df

    def query(self, users):
        """Searches the database table for users

        Args:
            users (List[String]): List of usernames to search for

        Returns:
            Pandas DataFrame: Table of whether the users are in the database table
        """
        df = pd.DataFrame(columns=["User", "Found"])
        for user in users:
            self.__cursor.execute(
                "SELECT * FROM insta_train WHERE username='{:s}'".format(user)
            )
            s = None
            for output in self.__cursor:
                s = output
            if s:
                df = df.append({"User": user, "Found": True}, ignore_index=True)
            else:
                df = df.append({"User": user, "Found": False}, ignore_index=True)
        return df

    def show(self):
        """Shows all the entries in the database table

        Returns:
            List[Tuple(User Data)]: A list of all user data within the table
        """
        self.__cursor.execute("SELECT * FROM insta_train")
        entries = [output for output in self.__cursor]
        return entries
