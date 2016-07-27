import socket
import optparse
import service_base as service

class InventoryClient(object):
    """ InventoryClient for connecting and query information from InventoryServer """
    def __init__(self):
        """ InventoryClient Constructor """
        super(InventoryClient, self).__init__()
        self.client_socket = socket.socket()

    def authenticate(self):
        """ check authorization for current session """
        user_info = service.get_user_info()
        service.send_data_message(self.client_socket, user_info)
        respone = service.receive_data_message(self.client_socket)
        if respone == True:
            return True
        return False

    def run(self, server_hostname, server_port):
        """ running client process """
        try:
            self.client_socket.connect((server_hostname, server_port))
        except socket.error:
            print "Invalid server hostname/port!"
            return

        rev_data = self.client_socket.recv(service.MESSAGE_CHUNK_SIZE)
        print rev_data
        if rev_data == service.DENY_SERVICE_MESSAGE:
            return
        elif not self.authenticate():
            return
        else:
            data = service.receive_data_message(self.client_socket)
            print data

        while True:
            try:
                msg = raw_input(service.CONSOLE_TERM)
                if msg:
                    
                    if msg == service.EXIT_COMMAND:
                        break
                    elif msg == service.NEW_USER_COMMAND:
                        msg = service.create_new_user()

                    self.client_socket.sendall(msg)
                    data = service.receive_data_message(self.client_socket)
                    print data
            except socket.error:
                print 'Server failed'
                return

        self.client_socket.close()   # Close the socket when done

if __name__ == '__main__':
    # create a Inventory client
    usage = "usage: python %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-s", "--server", help="the InventoryManagementSystem server hostname or IP address")
    parser.add_option("-p", "--port", default=service.SERVER_DEFAULT_PORT,
                        help="socket server listen port [default: %default]")
    (options, args) = parser.parse_args()
    if not options.server:
        print "Please specify Server IP Address or hostname!"
        parser.print_help()
    else:
        client = InventoryClient()
        client.run(options.server, options.port)
