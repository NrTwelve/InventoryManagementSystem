import threading
import cPickle
import socket

import service_base as base
import database_manager as db


class ThreadHandler(base.ServiceBase, threading.Thread):
    """ ThreadHandler """
    def __init__(self, client_socket):
        """  """
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def parse_message(self, message):
        """ parse given command into valid query commands """
        template = db.QUERRY_FRAME
        arguments = message.split(" ")
        if arguments[0] in db.handler.commands_available:
            template[db.QUERRY_COMMAND] = arguments[0]
            template[db.QUERRY_ARGUMENTS] = arguments[1:]
            return True, template
        else:
            return False, None

    def execute_query(self, message):
        """  """
        status, query_fr = self.parse_message(message)
        if status:
            status, data = db.handler.execute(query_fr)
            if status:
                self.send_data_message(self.client_socket, data)
                return

        # fail on excuting query
        self.send_error_message(self.client_socket,
                        "Invalid commands for querring data!")

    def run(self):
        self.client_socket.sendall(base.ACCEPT_SERVICE_MESSAGE)
        while True:
            try:
                message = self.client_socket.recv(base.MESSAGE_CHUNK_SIZE)
                if message == base.EXIT_COMMAND:
                    break
                elif message:
                    self.execute_query(message)
            except socket.error:
                print 'Client socket terminates connection!'
                break

        self.client_socket.close()
