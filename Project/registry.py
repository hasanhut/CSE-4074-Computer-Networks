from socket import *
import threading


# declare fields.
UDP_PORT = 50060
PORT = 5050
SERVER = gethostbyname(gethostname())
ADDR = (SERVER, PORT)

ACCOUNTS = {}       # keeps registered accounts. key: username, value: password.

ONLINE_USERS = {}   # keeps online users.   key: username, value: client
STILL_ONLINE = []


TCP_SOCKET = socket(AF_INET, SOCK_STREAM)
UDP_SOCKET = socket(AF_INET, SOCK_DGRAM)

TCP_SOCKET.bind(ADDR)
TCP_SOCKET.listen()

UDP_SOCKET.bind((SERVER,UDP_PORT)) 

global client_timer


def check_registration(client, credentials):
    username, password = credentials.split()
    if username in ACCOUNTS:
        return 'REG_FAIL'
    ACCOUNTS[username] = password
    print(f'Client: {client.getpeername()} registered to server as {username}!')
    return 'REG_SUCCESS'


def check_login(client, credentials):
    username, password = credentials.split()
    if username not in ACCOUNTS:
        return 'USR_ERR'
    elif password != ACCOUNTS[username]:
        print(ACCOUNTS[username])
        return 'PSW_ERR'
    ONLINE_USERS[username] = client
    print(f'{username} is online now!')
    return 'LOG_SUCCESS'


def check_search(client, username):
    contact_address = ''  # it will be contact address of searched user.
    if username in ONLINE_USERS:
        contact_address = str(ONLINE_USERS[username].getpeername())  # sends contact address.

    if len(contact_address):
        print(f'Server found contact address of {username} for {str(client.getpeername())}')
        return 'SRC_SUCCESS', contact_address

    else:
        print(f'Server could not find contact address of {username} for {str(client.getpeername())}')
        return 'SRC_ERR', contact_address


# main function for server thread of TCP.
def handle(client):
    while True:
        request = client.recv(20).decode('ascii')
        if request == 'REG_REQ':
            client.send('REG_OK'.encode('ascii'))
            data = client.recv(1024).decode('ascii')
            result = check_registration(client, data)
            client.send(result.encode('ascii'))
            continue

        elif request == 'LOG_REQ':
            client.send('LOG_OK'.encode('ascii'))
            data = client.recv(1024).decode('ascii')
            result = check_login(client, data)
            client.send(result.encode('ascii'))
            continue

        elif request == 'SRC_REQ':
            client.send('SRC_OK'.encode('ascii'))
            data = client.recv(1024).decode('ascii')
            result, addr = check_search(client, data)
            if result == 'SRC_SUCCESS':
                client.send(result.encode('ascii'))
                client.send(addr.encode('ascii'))
            else:
                client.send(result.encode('ascii'))
            continue


def find_username (client):
    for key in ONLINE_USERS.keys():
        checker = 'laddr=' + str(ONLINE_USERS[key].getpeername())
        client = client.split(', ')[4] + ', ' + client.split(', ')[5]
        if checker == client:
            return key


def checkUserIsOnline ():
    usernameList_toDelete =[]
    STILL_ONLINE.clear()
    hello_message = UDP_SOCKET.recvfrom(1024)
    hello_message = str(hello_message[0])
    if len(hello_message) > 0:
        hello, client = hello_message.split(' ', 1)
        username = find_username(client)
        STILL_ONLINE.append(username)
        timer_reset()
    for username in ONLINE_USERS.keys():
        if username not in STILL_ONLINE:
            print (username + " is became offline and removed from Online Users.")
            usernameList_toDelete.append(username)
    for username in usernameList_toDelete:
        ONLINE_USERS[username].close()
        del ONLINE_USERS[username]        
           
        
def timer_reset ():
    global client_timer
    client_timer.cancel()
    client_timer = threading.Timer(20, checkUserIsOnline)
    client_timer.start()



def listen():
    while True:
        client, address = TCP_SOCKET.accept()
        print(f'{str(address)} connected to server!')
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def listen_UDP():

    global client_timer
    client_timer = threading.Timer(200, checkUserIsOnline)
    client_timer.start()

print("Server is listening...")

# for server

listen_thread = threading.Thread(target=listen)
listen_thread.start()

listenUDP_thread = threading.Thread(target=listen_UDP)
listenUDP_thread.start()


