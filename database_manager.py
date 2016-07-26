
import sqlite3
from tabulate import tabulate

RESET_DATABASE = '''
DROP TABLE IF EXISTS Inventory;

CREATE TABLE Inventory (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    type TEXT,
    model TEXT,
    serial_number TEXT UNIQUE,
    import_date TEXT,
    location TEXT,
    status TEXT,
    owner TEXT
);
'''

ENTRY_DATA_TEMPLATE = {"type": "",
                       "model": "",
                       "serial_number": "",
                       "import_date": "",
                       "location": "",
                       "status": "",
                       "owner": ""}

QUERRY_COMMAND = "command"
QUERRY_ARGUMENTS = "arguments"

QUERRY_FRAME = {QUERRY_COMMAND: None,
                QUERRY_ARGUMENTS: None}

class DataBaseManager(object):
    """docstring for DataBaseManager"""
    def __init__(self):
        # temporary disconnect thread safe
        #TODO: adding threadsafe checking
        super(DataBaseManager, self).__init__()
        self.connection = sqlite3.connect('inventorydb.sqlite', check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        self.command_map = {
            "find": self.find
        }
        self.commands_available = self.command_map.keys()

    def data_pretty_print(self, data):
        """ convert data into table pretty print """
        data_str = tabulate(data, headers="keys", tablefmt="psql")
        return data_str

    def reset(self):
        """ Reset Database """
        self.cursor.executescript(RESET_DATABASE)

    def add_entry(self, new_data):
        """ Add new data entry, expected new data is stored as dictionary """
        if isinstance(new_data, dict):
            data_template = ENTRY_DATA_TEMPLATE
            for key, value in new_data.items():
                if data_template.has_key(key):
                    data_template[key] = value

            self.cursor.execute('''INSERT OR IGNORE INTO Inventory (
                type, model, serial_number, import_date, location, status, owner) 
                VALUES ( ?, ?, ?, ?, ?, ?, ? )''',
                (data_template["type"], data_template["model"],
                data_template["serial_number"], data_template["import_date"],
                data_template["location"], data_template["status"], data_template["owner"]))
            self.connection.commit()

    def find(self, args):
        """ Querry data from database for given conditions """
        r = self.cursor.execute("SELECT * FROM Inventory; ")
        result = r.fetchall()
        # convert to list of entry data stored by key/value pair
        item_list = [dict(x) for x in result]
        data_dict = dict()
        for item in item_list: # convert to dictionary of list value base on column name
            for key, value in item.items():
                try:
                    data_dict[key].append(value)
                except KeyError:
                    data_dict[key] = [value]
        data_str = self.data_pretty_print(data_dict)
        return data_str

    def execute(self, querry_frame):
        """ entry function to execute all command """
        if isinstance(querry_frame, dict) and querry_frame.has_key(QUERRY_COMMAND) \
                                            and querry_frame.has_key(QUERRY_ARGUMENTS):
            func_handler = self.command_map[querry_frame[QUERRY_COMMAND]]
            data = func_handler(querry_frame[QUERRY_ARGUMENTS])
            return True, data
        else:
            # invaid frame
            return False, None

handler = DataBaseManager()
