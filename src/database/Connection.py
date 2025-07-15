import os
# This is an abstract class. It is used to create the three connection objects used in the full workflow of
# EvoRecSys.

class Connection:

    # These values should be changed according to your network configurations.
    HOST = os.environ.get('MYSQL_HOST')
    USER = os.environ.get('MYSQL_USER')
    PASSWORD = os.environ.get('MYSQL_PASSWORD')
    DATA_BASE = os.environ.get('MYSQL_DATABASE')

    # Constructor
    def __init__(self):

        self.connector = None
