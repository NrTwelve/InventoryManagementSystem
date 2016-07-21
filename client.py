import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 60000                # Reserve a port for your service.

s.connect((host, port))

print s.recv(1024)
while 1:
    try :
        msg = raw_input('enter input: ')
        s.sendall(msg)
        if msg == "end":
            break
    except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

s.close                     # Close the socket when done
