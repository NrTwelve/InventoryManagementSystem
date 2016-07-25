import cPickle
import socket
import sys
import service_base as base

HOST = socket.gethostname()         # Get local machine name, or SERVER hostname or IP

class InventoryClient(base.ServiceBase):
    """ InventoryClient for connecting and query information from InventoryServer """
    def __init__(self):
        """  """
        self.client_socket = socket.socket()
        
    def run(self):
        """ running client process """
        self.client_socket.connect((HOST, base.SERVER_PORT))
        rev_data = self.client_socket.recv(base.MESSAGE_CHUNK_SIZE)
        print rev_data
        if rev_data == base.DENY_SERVICE_MESSAGE:
            return

        while True:
            try :
                msg = raw_input(base.CONSOLE_TERM)
                self.client_socket.sendall(msg)
                if msg == "end":
                    break
                else:
                    self.receive_data_message(self.client_socket)
            except socket.error:
                print 'Server failed'
                sys.exit()

        self.client_socket.close()   # Close the socket when done

if __name__ == '__main__':
    # create a Inventory client
    client = InventoryClient()
    client.run()
