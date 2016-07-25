import threading
import socket               # Import socket module
import thread_handler
import service_base as base

MAX_NUMBER_CONNECTION = 5

class Gateway(object):
    """docstring for Gateway"""
    def __init__(self):
        self.server_socket = ""
        self.initialize_socket_server()

    def initialize_socket_server(self):
        """ Create a new socket server """
        self.server_socket = socket.socket()
        host = socket.gethostname()          # Get local machine name
        self.server_socket.bind((host, base.SERVER_PORT))      # Bind to the port

    def is_allowed_connection(self):
        """ Check current status of all thread, return True for allowing new connection """
        if threading.active_count() == MAX_NUMBER_CONNECTION + 1: # check for the maximum connection + caller thread
            return False
        return True

    def run(self):
        """ Main function for gateway, listen to socket connection """
        while True:
            self.server_socket.listen(5)
            c, addr = self.server_socket.accept()     # Establish connection with client.
            if self.is_allowed_connection() == False:
                c.sendall(base.DENY_SERVICE_MESSAGE)
                c.close()
                continue

            handler = thread_handler.ThreadHandler(c)
            handler.start()


if __name__ == '__main__':
    gateway = Gateway()
    gateway.run()
