"""
file: dbconnection.py
written by: Johan Solbakken, Morten Tobias Rinde Sunde
date: 10.10.2023

    Contains a class that can be used to connect to a MongoDB-server.
    
"""

from pymongo import MongoClient, version
import log

class DbConnector:
    """
    Connects to the MongoDB server on the Ubuntu virtual machine.
    Connector needs HOST, USER and PASSWORD to connect.

    Example:
    HOST = "tdt4225-00.idi.ntnu.no" // Your server IP address/domain name
    USER = "testuser" // This is the user you created and added privileges for
    PASSWORD = "test123" // The password you set for said user
    """

    def __init__(self,
                 DATABASE='nihaodb',
                 HOST="localhost",
                 USER="root",
                 PASSWORD="example"):
        uri = "mongodb://%s:%s@%s:27017" % (USER, PASSWORD, HOST)
        # Connect to the databases 🇪🇸🇪🇸🇪🇸🇪🇸🇪🇸🇪🇸🇪🇸🇪🇸🇪🇸🇪🇸
        try:
            self.client = MongoClient(uri)
            self.db = self.client[DATABASE]
        except Exception as e:
            log.error("(Database) Failed to connect to db:", e)

        # get database information
        log.info(f"(Database) You are connected to the database: {self.db.name}")

    def close_connection(self):
        # close the cursor
        # close the DB connection
        self.client.close()
        log.info(f"(Database) Connection to {self.db.name}-db is closed")
