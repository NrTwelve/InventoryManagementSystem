import hashlib, binascii, os # password encryption library
import sqlite3
from tabulate import tabulate

RESET_DATABASE = '''
DROP TABLE IF EXISTS Inventory;
DROP TABLE IF EXISTS Users;
'''
INIT_DATABASE = '''
CREATE TABLE IF NOT EXISTS Inventory (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    type TEXT,
    model TEXT,
    serial_number TEXT UNIQUE,
    import_date TEXT,
    location TEXT,
    status TEXT,
    owner TEXT
);

CREATE TABLE IF NOT EXISTS Users (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    username TEXT,
    password_digest TEXT,
    usertype TEXT,
    salt TEXT
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

ADMINISTRATOR_TYPE = 'admin'
GUEST_TYPE = 'guest'



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
            ADMINISTRATOR_TYPE: {
                "find": self.find,
                "add": self.add_entry
            },
            GUEST_TYPE: {
                "find": self.find
            }
        }
        self.initializing()

    def initializing(self):
        """ Check for tables existence, if not, just create them """
        self.cursor.executescript(INIT_DATABASE)

    def administrator_check(self):
        """ Check an administrator account existence """
        r = self.cursor.execute("SELECT usertype FROM Users WHERE usertype= ?;",
            (ADMINISTRATOR_TYPE,))
        result = r.fetchone()
        if result:
            return True
        return False

    def data_pretty_print(self, data):
        """ convert data into table pretty print """
        data_str = tabulate(data, headers="keys", tablefmt="psql")
        return data_str

    def reset(self):
        """ Reset Database """
        self.cursor.executescript(RESET_DATABASE)
        self.cursor.executescript(INIT_DATABASE)

    def encrypt_user_info(self, info):
        """ encrypt user information in order to store in database """
        salt = os.urandom(32) #get salt of a day
        pass_digest = binascii.hexlify(hashlib.pbkdf2_hmac('sha256',
                        info["password_hash"], salt, 100000))
        salt = binascii.hexlify(salt) # convert byte to string
        return pass_digest, salt

    def verify_user_info(self, info):
        """ check user information with the stored info in database """
        if info.has_key('username') and info.has_key('password_hash'):
            r = self.cursor.execute("SELECT salt,password_digest FROM Users WHERE username= ?;",
                    (info['username'], ))
            result = r.fetchone()
            if result:
                salt = binascii.unhexlify(result['salt'])
                if result['password_digest'] == binascii.hexlify(hashlib.pbkdf2_hmac(
                            'sha256', info["password_hash"], salt, 100000)):
                    return True
        return False

    def get_usertype(self, username):
        """  """
        r = self.cursor.execute("SELECT usertype FROM Users WHERE username= ?;",(username, ))
        result = r.fetchone()
        if result:
            return result['usertype']
        return None

    def get_command_handler(self, username, command):
        """  """
        usertype = self.get_usertype(username)
        try:
            handler = self.command_map[usertype][command]
            return handler
        except:
            # invalid command for a particular username
            return None

    def add_user(self, user_info, usertype):
        """ Add new user to database """
        if isinstance(user_info, dict):
            if user_info.has_key('username') and user_info.has_key('password_hash'):
                pass_digest, salt = self.encrypt_user_info(user_info)
                self.cursor.execute('''INSERT OR IGNORE INTO Users (username, password_digest, usertype, salt)
                    VALUES ( ?, ?, ?, ? )''', (user_info['username'], pass_digest, usertype, salt))
                self.connection.commit()

    def add_entry(self, new_data):
        """ Add new data entry, expected new data is stored as dictionary """
        status = "Fail! Can not insert to database"
        try:
            if isinstance(new_data, dict):
                data_template = ENTRY_DATA_TEMPLATE
                for key, value in new_data.items():
                    if data_template.has_key(key):
                        data_template[key] = value

                self.cursor.execute('''INSERT INTO Inventory (
                    type, model, serial_number, import_date, location, status, owner)
                    VALUES ( ?, ?, ?, ?, ?, ?, ? )''',
                    (data_template["type"], data_template["model"],
                    data_template["serial_number"], data_template["import_date"],
                    data_template["location"], data_template["status"], data_template["owner"]))
                self.connection.commit()
                status = "Success!"
        except Exception, e:
            status = e
        return status

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
        if data_dict:
            return self.data_pretty_print(data_dict)
        else:
            return ""

    def execute(self, query_frame, username):
        """ entry function to execute all command """
        if isinstance(query_frame, dict) and query_frame.has_key(QUERRY_COMMAND) \
                                            and query_frame.has_key(QUERRY_ARGUMENTS):            
            func_handler = self.get_command_handler(username, query_frame[QUERRY_COMMAND])
            if func_handler:
                data = func_handler(query_frame[QUERRY_ARGUMENTS])
                return True, data
        # invaid frame/command
        return False, None

handler = DataBaseManager()
