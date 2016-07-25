import threading
import socket               # Import socket module
from thread_handler import ThreadHandler


MAX_NUMBER_CONNECTION = 5
CONNECTION_PORT = 60000

class Gateway(object):
    """docstring for Gateway"""
    def __init__(self):
        self.thread_handlers = list()
        self.server_socket = ""
        self.initialize_socket_server()

    def initialize_socket_server(self):
        """ Create a new socket server """
        self.server_socket = socket.socket()
        host = socket.gethostname()          # Get local machine name
        self.server_socket.bind((host, CONNECTION_PORT))      # Bind to the port

    def is_allowed_connection(self):
        """ Check current status of all thread, return True for allowing new connection """
        self.thread_handlers = [t for t in self.thread_handlers if not t.handled]
        if len(self.thread_handlers) > MAX_NUMBER_CONNECTION: # check for the maximum connection
            return False
        return True

    def run(self):
        """ Main function for gateway, listen to socket connection """
        while True:
            self.server_socket.listen(5)
            c, addr = self.server_socket.accept()     # Establish connection with client.
            if not is_allowed_connection:
                c.send("Reach to maximum number of connections.")
                c.close()
                continue

            handler = ThreadHandler()
            t = threading.Thread(target=handler.run, args=(len(self.thread_handlers), c))
            self.thread_handlers.append(t)
            t.start()


if __name__ == '__main__':
    gateway = Gateway()
    gateway.run()
