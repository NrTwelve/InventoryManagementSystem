import sys
import optparse
import threading
import socket

import thread_handler
import service_base as service
import database_manager as db

MAX_NUMBER_CONNECTION = 5
WELCOME_MESSAGE = "Welcome to the Inventory Manager System!\nConnection port is: %s"

class Gateway(object):
    """docstring for Gateway"""
    def __init__(self, server_port):
        self.server_socket = ""
        self.initialize_socket_server(server_port)

    def initialize_socket_server(self, server_port):
        """ Create a new socket server """
        try:
            self.server_socket = socket.socket()
            host = socket.gethostname()                       # Get local machine name
            self.server_socket.bind((host, server_port))      # Bind to the port
            print WELCOME_MESSAGE % (server_port)
        except socket.error:
            print "Unable to start server, please specify different socket port number!"
            sys.exit()

    def is_allowed_connection(self):
        """ Check current status of all thread, return True for allowing new connection """
        # check for the maximum connection + caller thread
        if threading.active_count() == MAX_NUMBER_CONNECTION + 1:
            return False
        return True

    def authenticate(self, client_socket, db_handler):
        info = service.receive_data_message(client_socket)
        result = db_handler.verify_user_info(info)
        service.send_data_message(client_socket, result)
        return result, info['username']

    def run(self, db_handler):
        """ Main function for gateway, listen to socket connection """
        if not db_handler.administrator_check():
            print "Administrator account is required! Please create ones ..."
            user_info = service.get_user_info()
            user_info['usertype'] = db.ADMINISTRATOR_TYPE
            print db_handler.add_user(user_info)

        while True:
            self.server_socket.listen(5)
            c, addr = self.server_socket.accept()     # Establish connection with client.
            if self.is_allowed_connection() is False:
                c.sendall(service.DENY_SERVICE_MESSAGE)
                c.close()
                continue
            c.sendall(service.WELCOME_SERVICE_MESSAGE)
            result, username = self.authenticate(c, db_handler)
            if result:
                handler = thread_handler.ThreadHandler(c, username, db_handler)
                handler.start()


if __name__ == '__main__':
    usage = "usage: python %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--port", default=service.SERVER_DEFAULT_PORT,
                        help="socket server listen port [default: %default]")
    (options, args) = parser.parse_args()

    db_handler = db.DataBaseManager()
    gateway = Gateway(options.port)
    gateway.run(db_handler)
