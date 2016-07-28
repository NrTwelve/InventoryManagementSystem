import hashlib, binascii, os # password encryption library
import sqlite3
import threading
from tabulate import tabulate

DROP_INVENTORY_DATABASE = '''
DROP TABLE IF EXISTS Inventory;
'''

INIT_USERS_DATABASE ='''
CREATE TABLE IF NOT EXISTS Users (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    username TEXT UNIQUE,
    password_digest TEXT,
    usertype TEXT,
    salt TEXT
);
'''

INIT_INVENTORY_DATABASE = '''
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
CONDITION_KEY = "where"


ADMINISTRATOR_TYPE = 'admin'
GUEST_TYPE = 'guest'

class DataBaseManager(object):
    """docstring for DataBaseManager"""
    def __init__(self):
        # temporary disconnect thread safe
        #TODO: adding threadsafe checking
        self.lock = threading.Lock()
        super(DataBaseManager, self).__init__()
        self.connection = sqlite3.connect('inventorydb.sqlite', check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.QUERRY_COMMAND = QUERRY_COMMAND
        self.QUERRY_ARGUMENTS = QUERRY_ARGUMENTS
        self.QUERRY_FRAME = QUERRY_FRAME
        self.command_map = {
            ADMINISTRATOR_TYPE: {
                "find": self.find,
                "add": self.add_entry,
                "del": self.del_entry,
                "update": self.update_entry,
                "reset": self.reset,
                "new_user": self.add_user,
                "del_user": self.del_user
            },
            GUEST_TYPE: {
                "find": self.find
            }
        }
        self.initializing()

    def initializing(self):
        """ Check for tables existence, if not, just create them """
        self.cursor.executescript(INIT_USERS_DATABASE)
        self.cursor.executescript(INIT_INVENTORY_DATABASE)

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

    def reset(self, args):
        """ Reset Inventory Database """
        status = "Success!"
        try:
            self.cursor.executescript(DROP_INVENTORY_DATABASE)
            self.cursor.executescript(INIT_INVENTORY_DATABASE)
        except Exception, e:
            status = e
        return status

    def encrypt_user_info(self, password_hash):
        """ encrypt user information in order to store in database """
        salt = os.urandom(32) #get salt of a day
        pass_digest = binascii.hexlify(hashlib.pbkdf2_hmac('sha256',
                        password_hash, salt, 100000))
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

    def extract_inventory_keys(self, args, full_keys=False):
        """ Return a subset of input which contains only key in Inventory database """
        data = dict()
        available_keys = ENTRY_DATA_TEMPLATE.keys() + ["id"]
        for key in available_keys:
            if args.has_key(key):
                data[key] = args[key]
            else:
                if full_keys and key != "id":
                    data[key] = ENTRY_DATA_TEMPLATE[key]                
        return data

    def parse_command_argument(self, args_list):
        """ convert argument list into a key-value pair dictionary """
        args = dict()
        for each in args_list:
            items = each.split("=")
            if len(items) == 2:
                args[items[0]] = items[1]
        return args

    def parse_command_argument_and_condition(self, args_list):
        """ convert argument list into a key-value pair dictionary """
        conditions = dict()
        try:
            cond_idx = args_list.index(CONDITION_KEY)
        except Exception, e:
            cond_idx = None
        # Note, args is a list of string type: <key>=<value>
        args = args_list[:cond_idx]
        if cond_idx != None:
            conditions = self.parse_command_argument(args_list[cond_idx:])
        return args, conditions

    def parse_show_option(self, args):
        """ return a string of showed items in database, default is show all """
        showed_items = "*"
        if args.has_key("show"):
            input_items = args["show"].split(",")
            available_keys = ENTRY_DATA_TEMPLATE.keys() + ["id"]
            # checking for a valid items in database
            showed_items = ",".join(set(available_keys) & set(input_items))
        return showed_items

    def parse_command_conditions(self, args):
        """ parse the input args into WHERE clauses for available items in database """
        data_conditions = self.extract_inventory_keys(args)
        conditions = ""
        conditions_keys = [x+"=?" for x in data_conditions.keys()]
        if conditions_keys:
            conditions = "WHERE "
            conditions += " AND ".join(conditions_keys)
        return conditions, tuple(data_conditions.values())

    def add_user(self, args):
        """ Add new user to database """
        status = "Fail on adding new user!"
        if isinstance(args, dict):
            user_info = args
        else:
            user_info = self.parse_command_argument(args)

        try:
            if user_info.has_key('username') and user_info.has_key('password_hash'):
                pass_digest, salt = self.encrypt_user_info(user_info['password_hash'])
                self.cursor.execute('''
                    INSERT OR IGNORE INTO Users (username, password_digest, usertype, salt)
                    VALUES ( ?, ?, ?, ? )''', (user_info['username'], pass_digest,
                    user_info['usertype'], salt))
                self.connection.commit()
                status = "Success!"
        except Exception, e:
            status = e
        return status

    def del_user(self, args):
        """ Delete an user account in database """
        status = "Please specify username for deleting: username=<deleted_username>!"
        user_info = self.parse_command_argument(args)
        try:
            if user_info.has_key('username'):
                self.cursor.execute("DELETE FROM Users WHERE username=? ;",
                    (user_info['username'], ))
                self.connection.commit()
                status = "Success!"
        except Exception, e:
            status = e
        return status

    def add_entry(self, args):
        """ Add new data entry, expected new data is stored as dictionary """
        status = "Fail! Can not insert to database"
        entry_info = self.parse_command_argument(args)
        try:
            data_template = self.extract_inventory_keys(entry_info, True)
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

    def del_entry(self, args):
        """ Delete entries in database which satisfy conditions """
        status = "Fail! Please specify the conditions (by 'where' clause)\n"
        status +="    In case of deleting all records, use command 'reset', instead."
        entry_info, conditions = self.parse_command_argument_and_condition(args)
        try:
            if conditions:
                command_str = "DELETE FROM Inventory %s ;"
                conditions, conditions_value = self.parse_command_conditions(conditions)
                command_str = command_str % (conditions)
                self.cursor.execute(command_str, conditions_value)
                self.connection.commit()
                status = "Success!"
        except Exception, e:
            status = e
        return status

    def find(self, args):
        """ Querry data from database for given conditions """
        args_info = self.parse_command_argument(args)
        try:
            command_str = "SELECT %s FROM Inventory %s; "
            show_items = self.parse_show_option(args_info)
            conditions, conditions_value = self.parse_command_conditions(args_info)
            command_str = command_str % (show_items, conditions)

            r = self.cursor.execute(command_str, conditions_value)
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
        except Exception, e:
            return e

    def update_entry(self, args):
        """ Update information for an exist record """
        status = "Fail! Please enter the updated informations\n"
        status +="         and conditions(by 'where' clause).\nOtherwise, all records are updated"
        updated_info, conditions = self.parse_command_argument_and_condition(args)
        updated_info_cmd = ", ".join(updated_info)
        if conditions:
            conditions_cmd, conditions_value = self.parse_command_conditions(conditions)
        else:
            conditions_cmd = ""
            conditions_value = tuple()

        try:
            command_str = "UPDATE Inventory SET %s %s; "
            command_str = command_str % (updated_info_cmd, conditions_cmd)
            r = self.cursor.execute(command_str, conditions_value)
            self.connection.commit()
            status = "Success!"
        except Exception, e:
            status = e
        return status

    def execute(self, query_frame, username):
        """ entry function to execute all command """
        self.lock.acquire()
        status = False
        data = None
        if isinstance(query_frame, dict) and query_frame.has_key(QUERRY_COMMAND) \
                                        and query_frame.has_key(QUERRY_ARGUMENTS):            
            func_handler = self.get_command_handler(username, query_frame[QUERRY_COMMAND])
            if func_handler:
                data = func_handler(query_frame[QUERRY_ARGUMENTS])
                status = True
        self.lock.release()
        return status, data

