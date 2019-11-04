#from socket import AF_INET, socket, SOCK_STREAM
import socket
from threading import Thread
import sys

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    try:
        while True:
            #print("hello")
            client, client_address = SERVER.accept()
            print("%s:%s has connected." % client_address)
            client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
            addresses[client] = client_address
            Thread(target=handle_client, args=(client,client_address,)).start()
    except KeyboardInterrupt:
        print("Caught Keyboard Interrupt")
    finally:
        return


def handle_client(client,client_address):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    if not name:
        client.close()
        return
    elif name == "{quit}":
        client.send(bytes("{quit}", "utf8"))
        print("%s:%s has disconnected." % client_address)
        client.close()
        return
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"),client_address)
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if not msg:
            client.close()
            del clients[client]
            break
        elif msg != bytes("{quit}", "utf8"):
            broadcast(msg,client_address, name+": ")
        else:
            print("sup")
            client.send(bytes("{quit}", "utf8"))
            print("%s:%s has disconnected." % client_address)
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"),client_address)
            break


def broadcast(msg,client_address=None, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    invalid_clients=[]
    for sock in clients:
        try:
            sock.send(bytes(prefix, "utf8")+msg)
        except BrokenPipeError:
            invalid_clients.append(sock)
            continue
    for client in invalid_clients:
        print("%s:%s has disconnected." % client_address)
        client.close()
        del clients[client]
        broadcast(bytes("%s has left the chat." % name, "utf8"))

        
clients = {}
addresses = {}

HOST = '127.0.0.3'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

if __name__ == "__main__":
    try:
        SERVER.listen(5)
        print("Waiting for connection...")
        ACCEPT_THREAD = Thread(target=accept_incoming_connections,daemon=True)
        print("-----Enter {quit} to exit-----")
        ACCEPT_THREAD.start()
        while True:
            z = input()
            if z == "{quit}":
                print("Closing Server. Exitting....")
                SERVER.close()
                sys.exit(1)
        ACCEPT_THREAD.join()
        SERVER.close()
    except KeyboardInterrupt:
        print("Caught Keyboard Interrupt")
        for client in clients:
            client.send(bytes("*****Server Disconnected*******", "utf8"))
        
        for client in clients:
            client.send(bytes("{quit}", "utf8"))
        SERVER.close()
        sys.exit(1)
