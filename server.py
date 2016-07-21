import threading
import socket               # Import socket module


def client_run(thread_nr, client_socket):
    client_socket.send('Thank you for connecting')
    while 1:
        message = client_socket.recv(1024)
        if message:
            if message == "end":
                break
            else:
                print "    info: ", thread_nr, " ", message
    client_socket.close()


s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 60000                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.

threads = list()

while True:
   c, addr = s.accept()     # Establish connection with client.
   t = threading.Thread(target=client_run, args=(len(threads), c))
   threads.append(t)
   t.start()
