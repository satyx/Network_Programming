import sys
import socket
import selectors
import types

#exploiting github bug

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    print("Inside accept_wrapper()")
    conn,addr = sock.accept()
    print("Accpeted connection from",addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn,events,data=data)

def service_connection(key,mask):
    print("Inside servce_connection()")
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb+=recv_data
        else:
            print("Closing connection to",data.addr)
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Echoing,",repr(data.outb),"to",data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]



if len(sys.argv)!=3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host,port = sys.argv[1],int(sys.argv[2])
lsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
lsock.bind((host,port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock,selectors.EVENT_READ,data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key,mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key,mask)
except KeyboardInterrupt:
    print("Caught Keyboard Interrupt. Exitting")
finally:
    sel.close()