
import sqlite3

RESET_DATABASE = """
DROP TABLE IF EXISTS Inventory;

CREATE TABLE Inventory (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    type TEXT
    model TEXT
    serial_number TEXT UNIQUE
    import_date TEXT
    location TEXT
    status TEXT
    owner TEXT
);
"""



class DataBaseManager(object):
    """docstring for DataBaseManager"""
    def __init__(self):
        conn = sqlite3.connect('inventorydb.sqlite')
        self.cursor = conn.cursor()

    def reset(self):
        """ Reset Database """
        self.cursor.executescript(RESET_DATABASE)

data_handler = DataBaseManager()