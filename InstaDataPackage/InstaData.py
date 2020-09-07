# Imports
import concurrent.futures
import logging
import os
import pickle
import sys
import time
import traceback
from datetime import datetime
from random import choice

import instaloader
import requests
from instaloader import Profile
from instaloader.exceptions import (
    ProfileNotExistsException,
    QueryReturnedNotFoundException,
    ConnectionException,
    QueryReturnedBadRequestException,
)
from notify_run import Notify
from pytz import timezone
from .Instabase import DB_Session, DB_Session_Local
from .Wheel_Linked import Wheel

# from Wheel_Linked import Wheel
# from Instabase import *


class Instabot:
    # Initialize basic logger
    logging.basicConfig(
        filename="logging.txt",
        filemode="w",
        format="%(levelname)s %(asctime)s - %(message)s",
        level=logging.DEBUG,
    )
    __LOGGER = logging.getLogger()
    # Set the timezone and intialize notification to send messages during execution
    __EST = timezone("Canada/Eastern")
    __NOTIFICATION = Notify()

    def __init__(
        self, username=os.environ.get("IG_USER"), password=os.environ.get("IG_PASS")
    ):
        # Create an Instaloader instance
        self.__I_session = instaloader.Instaloader(max_connection_attempts=1)
        self.__I_session.login(username, password)
        self.users = Wheel()
        self.date_stamp = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day, 0, 0
        )
        self.add_users()
        self.cooldown = False

    # Time wrapper to get the execution time of a function
    def timer(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            exec_time = time.time() - start_time
            Instabot.__LOGGER.debug(
                f"{func.__name__} took {exec_time} seconds to execute"
            )
            Instabot.__NOTIFICATION.send(
                f"{func.__name__} took {exec_time} seconds to execute"
            )
            return result

        return wrapper

    @timer
    def test_notification(self):
        """Tests the notification channel
        """
        Instabot.__LOGGER.debug("Testing notification")
        Instabot.__NOTIFICATION.send("Testing Notification")

    def add_users(self):
        """Adds the followers of the account and changes the date stamp to the most recent post
        """
        users = Profile.from_username(
            self.__I_session.context, os.environ.get("IG_USER")
        ).get_followees()
        if not self.users.is_empty():
            self.users.clear()
        for user in users:
            self.users.add(user.username)
            Instabot.__LOGGER.debug(f"Added User {user.username}")
            date_stamp = self.set_date_user(user)
            if date_stamp > self.date_stamp:
                self.date_stamp = date_stamp
        Instabot.__LOGGER.debug(f"New Date Stamp: {date_stamp}")
        if self.cooldown:
            self.reset_cooldown()
        self.stop_date = None
        self.save_bot()

    def set_date_user(self, profile: Profile):
        """Obtains the latest post of the profile given and returns the date stamp of the post in UTC

        Args:
            profile (Profile): The profile to find the latest post of 

        Returns:
            datetime: The UTC date stamp of the profiles latest post
        """
        date_stamp = next(profile.get_posts()).date_utc
        return date_stamp

    # Reset cooldown
    def reset_cooldown(self):
        self.cooldown = not self.cooldown

    # Find the most recent post and take it's date
    def set_date_stamp(self):
        self.date_stamp = next(self.__I_session.get_feed_posts()).date_utc

    # Used to reset after a 429
    def reset(self):
        self.reset_cooldown()
        self.set_date_stamp()

    # Load the bot from a pickle file
    @staticmethod
    def load_bot():
        """Loads the saved Instabot object from the pickle file

        Returns:
            Instabot: Saved Instabot object from pickle file
        """
        with open("bot.pickle", "rb") as pickle_in:
            bot = pickle.load(pickle_in)
        Instabot.__LOGGER.debug("Loaded Bot")
        return bot

    # Save the bot to a pickle file
    def save_bot(self):
        """Saves the Instabot object to the pickle file for next use
        """
        with open("bot.pickle", "wb") as pickle_out:
            pickle.dump(self, pickle_out, protocol=pickle.HIGHEST_PROTOCOL)
        Instabot.__LOGGER.debug("Exported to pickle file")

    # Calculate the file size of the csv in MegaBytes
    def file_size(self):
        file_stats = os.stat("InstaData.csv")
        size = file_stats.st_size / (1024 * 1024)
        return size

    def get_profile(self, user: str):
        """Returns the profile of the given username

        Args:
            user (str): The username of the profile to be returned

        Returns:
            instaloader.Profile: The profile of the username given
        """
        return Profile.from_username(self.__I_session.context, user)

    def monitor_user(self, user: str):
        """Checks to see if the date stamp of the users most recent post is greater than the current
        held date stamp, if so then the data of the commenters of the post will be collected

        Args:
            user (str): The username of the profile to be accessed
        """
        try:
            profile = self.get_profile(user)
            post = next(profile.get_posts())
            if post.date_utc > self.date_stamp:
                Instabot.__NOTIFICATION.send("New Post")
                Instabot.__LOGGER.debug("New Post Found")
                self.date_stamp = post.date_utc
                self.commenters(post.get_comments())
                self.save_bot()
            else:
                Instabot.__LOGGER.debug("No new posts")
                self.save_bot()

        # If the post is unavailable send a notification and save the bot
        except QueryReturnedNotFoundException as err:
            Instabot.__NOTIFICATION.send("404 Error Code")
            Instabot.__LOGGER.warning(f"{err}")

        except QueryReturnedBadRequestException as err:
            Instabot.__LOGGER.warning(f"{err}")
            Instabot.__NOTIFICATION.send(
                f"Verification needed to access Instagram {datetime.now(Instabot.__EST)}"
            )
            self.cooldown = True
            self.stop_date = datetime.now(Instabot.__EST)
            self.save_bot()
            self.stop_scrape()

        # If too many requests has been sent reset cooldown and save
        except ConnectionException as err:
            Instabot.__NOTIFICATION.send(
                f"Can't get info on post need to cool down, {datetime.now(Instabot.__EST)}"
            )
            Instabot.__LOGGER.warning(f"{err}")
            self.cooldown = True
            self.stop_date = datetime.now(Instabot.__EST)
            self.save_bot()
            self.stop_scrape()
        # Except an unexpected error and exit the program
        except Exception as err:
            Instabot.__LOGGER.error(traceback.format_exc())
            Instabot.__NOTIFICATION.send(
                f"{traceback.format_exc()},{datetime.now(Instabot.__EST)}"
            )

    def stop_scrape(self):
        """Sends a request to stop the cronjob the local machine
        """
        try:
            json_data = {
                "username": os.environ.get("username"),
                "password": os.environ.get("password"),
            }
            response = requests.post(
                f"http://localhost:{os.environ.get('port')}/stop", json=json_data,
            )
            Instabot.__LOGGER.debug(
                f"Local Request Status Code: {response.status_code}"
            )
            Instabot.__NOTIFICATION.send(
                f"Local Request Status Code: {response.status_code}"
            )
        except Exception as _:
            Instabot.__LOGGER.error(traceback.format_exc())
            Instabot.__NOTIFICATION.send(
                f"{traceback.format_exc()},{datetime.now(Instabot.__EST)}"
            )

    def monitor_users(self):
        """Goes the saved followers usernames and rotates each time to see the date stamp of their
        most recent post
        """
        if not self.cooldown:
            user = self.users.get_next()
            Instabot.__LOGGER.debug(f"Monitoring {user}")
            self.monitor_user(user)
        else:
            Instabot.__LOGGER.warning("429 Need to cooldown")

    @timer
    def commenters(self, comments, limit=20):
        """Create a ThreadPoolExecutor instance in order to create seperate request for each user's information
		Pass the extract_data function into the executor and loop through the results 
		Take the processed information and insert into local database

        Args:
            comments (Iterator[PostCommentAnswer]): A generator of comments for a post 
            limit (int, optional): The amount of commenters to extract data from. Defaults to 20.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            shared_data_list = []
            try:
                for _ in range(limit):
                    shared_data_list.append(
                        executor.submit(self.extract_data, next(comments).owner)
                    )
            except StopIteration:
                Instabot.__LOGGER.debug("End of comment generator")
            finally:
                with DB_Session_Local() as db:
                    for shared_data in concurrent.futures.as_completed(
                        shared_data_list
                    ):
                        try:
                            db.insert(shared_data.result())
                            Instabot.__LOGGER.debug("Inserted User into database")
                        except ProfileNotExistsException:
                            Instabot.__LOGGER.debug("Profile not available")

    def extract_data(self, profile: Profile):
        """Helper method to extract the data from the given profile

        Args:
            profile (Profile): The given profile to extract data from

        Returns:
            tuple: A tuple of the processed info from the profile
        """
        info = (
            profile.username,
            profile.mediacount,
            profile.followers,
            profile.followees,
            int(profile.is_private),
            int("@" in str(profile.biography.encode("utf-8"))),
            int(profile.external_url is not None),
            int(profile.is_verified),
        )
        return info

    def export_to_file(self, filename, shared_data_list):
        with open(filename, "a") as fv:
            for shared_data in shared_data_list:
                info = str(shared_data)[1:-1].replace("'", "")
                info = info.replace(" ", "")
                fv.write(info + "\n")
        Instabot.__NOTIFICATION.send(
            f"Exported commenters to file, {datetime.now(Instabot.__EST)}"
        )

    def collect_file_data(self, filename):
        with open(filename, "r") as fv:
            fv.seek(0)
            h_map = {}
            shared_data_list = []
            for line in fv:
                info = line.split(",")
                if info[0] not in h_map:
                    shared_data_list.append(tuple(info))
                    h_map[info[0]] = None
        with DB_Session() as db:
            for shared_data in shared_data_list:
                db.insert(shared_data)
            print(db.size())

    def collect_data(self):
        with DB_Session_Local() as db:
            db.transfer()

    def collect_users_data(self, users):
        shared_data_list = [self.extract_data(user) for user in users]
        with DB_Session() as db:
            for shared_data in shared_data_list:
                db.insert(shared_data)

    def show_users_data(self, users):
        h_map = {}
        i = 0
        while i < len(users):
            if users[i] in h_map:
                users.pop(i)
            else:
                h_map[users[i]] = None
                i += 1
        with DB_Session() as db:
            print(db.query(users))

    # Query the database to see if a user is within it
    def query(self, users):
        with DB_Session() as db:
            print(db.query_found(users))
