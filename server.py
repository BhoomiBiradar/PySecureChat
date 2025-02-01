import _thread
import socket
import ssl

print("Server running and listening...")

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = "10.1.0.233"
port = 50000

# Use ssl.wrap_socket to secure the socket
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.check_hostname = False
ssl_context.load_cert_chain(certfile="./server.pem", keyfile="./server.key")

s_ssl = ssl_context.wrap_socket(s, server_side=True)

s_ssl.bind((host, port))
s_ssl.listen(5)
clients = []
aliases = []


def connect_new_client(c, addr):
    global aliases
    name = c.recv(2048).decode('utf-8')
    aliases.append(name)
    c.send(('Welcome, ' + name + '! You are client ' + str(len(aliases))).encode('utf-8'))
    
    print(name + ' has joined the chat room')
    while True:
        try:
            msg = c.recv(2048)
            if not msg:
                remove_client(c)
                break
            num = aliases.index(name) + 1
            msg = str(num) + ':  (' + name + '):  ' + msg.decode('utf-8')
            send_to_all(msg, c)
        except ConnectionResetError:
            
            remove_client(c)
            break
        except Exception as e:
            print("Error in handling client {}: {}".format(name, str(e)))
            remove_client(c)


def send_to_all(msg, con):
    for client in clients:
        try:
            client.send(msg.encode('utf-8'))
        except Exception as e:
            print("Error sending message to a client: {}".format(str(e)))
            remove_client(client)


def remove_client(client):
    if client in clients:
        index = clients.index(client)
        name = aliases[index]
        print(name + ' has left the chat room')
        print('connection with '+name + ' has been closed...')
        aliases.remove(name)
        clients.remove(client)
        client.close()



while True:
    try:
        c, ad = s_ssl.accept()
        print('Connection Established')
        clients.append(c)
        _thread.start_new_thread(connect_new_client, (c, ad))
    except Exception as e:
        print("Error accepting connection: {}".format(str(e)))
