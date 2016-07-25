class ThreadHandler(object):
    """docstring for ThreadHandler"""
    def __init__(self):
        pass

    def run(self, thread_nr, client_socket):
        client_socket.send('Thank you for connecting')
        while 1:
            message = client_socket.recv(1024)
            if message:
                if message == "end":
                    break
                else:
                    print "    info: ", thread_nr, " ", message
        client_socket.close()
