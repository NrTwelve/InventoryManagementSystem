import threading
import cPickle
import socket

import service_base as service
import database_manager as db


class ThreadHandler(threading.Thread):
    """ ThreadHandler """
    def __init__(self, client_socket, username):
        """  """
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.username = username

    def parse_message(self, message):
        """ parse given command into valid query commands """
        template = db.QUERRY_FRAME
        arguments = message.split(" ")
        if arguments[0]:
            template[db.QUERRY_COMMAND] = arguments[0]
            args = dict()
            for each in arguments[1:]:
                items = each.split("=")
                if len(items) == 2:
                    args[items[0]] = items[1]
            template[db.QUERRY_ARGUMENTS] = args
            return True, template
        else:
            return False, None

    def execute_query(self, message):
        """  """
        status, query_fr = self.parse_message(message)
        if status:
            status, data = db.handler.execute(query_fr, self.username)
            if status:
                service.send_data_message(self.client_socket, data)
                return
        # fail on excuting query
        service.send_error_message(self.client_socket,
                        "Invalid commands for querring data!")

    def run(self):
        """ entry function for starting thread """
        accept_message = service.ACCEPT_SERVICE_MESSAGE % (self.username)
        service.send_data_message(self.client_socket, accept_message)
        while True:
            try:
                message = self.client_socket.recv(service.MESSAGE_CHUNK_SIZE)
                if message == service.EXIT_COMMAND:
                    break
                elif message:
                    self.execute_query(message)
            except socket.error:
                print 'Client socket terminates connection!'
                break

        self.client_socket.close()
