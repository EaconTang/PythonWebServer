import socket

HOST, PORT = '', 8888
ADDRESS = (HOST, PORT)

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind(ADDRESS)
listen_socket.listen(1)

print 'Servin HTTP on port %s...'%str(PORT)
while 1:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    print 'Received from client: %s...'%request

    response = """
        HTTP/1.1 200 OK
        Saluton!
            """
    client_connection.sendall(response)
    client_connection.close()