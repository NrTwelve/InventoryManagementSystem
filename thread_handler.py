import threading
import service_base as service

class ThreadHandler(threading.Thread):
    """ ThreadHandler """
    def __init__(self, client_socket, username, db_handler):
        """  """
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.username = username
        self.db_handler = db_handler

    def parse_message(self, message):
        """ parse given command into valid query commands """
        template = self.db_handler.QUERRY_FRAME.copy()
        arguments = message.split(" ")
        if arguments[0]:
            template[self.db_handler.QUERRY_COMMAND] = arguments[0]
            template[self.db_handler.QUERRY_ARGUMENTS] = arguments[1:]
            return True, template
        else:
            return False, None

    def execute_query(self, message):
        """  """
        status, query_fr = self.parse_message(message)
        if status:
            status, data = self.db_handler.execute(query_fr, self.username)
            if status:
                service.send_data_message(self.client_socket, data)
                return
        # fail on excuting query
        service.send_error_message(self.client_socket,
                        "Invalid commands/permission!")

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
            except Exception, e:
                print 'Client socket terminates connection!'
                break

        self.client_socket.close()
