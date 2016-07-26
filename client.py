import socket
import optparse
import service_base as base

class InventoryClient(base.ServiceBase):
    """ InventoryClient for connecting and query information from InventoryServer """
    def __init__(self):
        """ InventoryClient Constructor """
        super(InventoryClient, self).__init__()
        self.client_socket = socket.socket()

    def run(self, server_hostname, server_port):
        """ running client process """
        try:
            self.client_socket.connect((server_hostname, server_port))
        except socket.error:
            print "Invalid server hostname/port!"
            return

        rev_data = self.client_socket.recv(base.MESSAGE_CHUNK_SIZE)
        print rev_data
        if rev_data == base.DENY_SERVICE_MESSAGE:
            return

        while True:
            try:
                msg = raw_input(base.CONSOLE_TERM)
                self.client_socket.sendall(msg)
                if msg == base.EXIT_COMMAND:
                    break
                else:
                    self.receive_data_message(self.client_socket)
            except socket.error:
                print 'Server failed'
                return

        self.client_socket.close()   # Close the socket when done

if __name__ == '__main__':
    # create a Inventory client
    usage = "usage: python %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-s", "--server", help="the InventoryManagementSystem server hostname or IP address")
    parser.add_option("-p", "--port", default=base.SERVER_DEFAULT_PORT,
                        help="socket server listen port [default: %default]")
    (options, args) = parser.parse_args()
    if not options.server:
        print "Please specify Server IP Address or hostname!"
        parser.print_help()
    else:
        client = InventoryClient()
        client.run(options.server, options.port)
