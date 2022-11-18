from socket import *
import threading
import time 

SERVER_HOST = gethostbyname(gethostname())
SERVER_PORT = 5050



client = socket(AF_INET, SOCK_STREAM)
client.connect((SERVER_HOST, SERVER_PORT))

UDP_PORT =  client.getsockname()[1]+300

client_UDP = socket(AF_INET, SOCK_DGRAM) 
client_UDP.bind((SERVER_HOST, UDP_PORT)) 

client2 = socket(AF_INET, SOCK_STREAM)
client2.bind((SERVER_HOST, client.getsockname()[1] + 100))

peer_client = ''

# texts for displaying on screen.
WELCOME_MESSAGE = "********Welcome to Server!********\n1- Register\n2- Login"
REGISTER_MESSAGE = "********Register Screen!********"
LOGIN_MESSAGE = "********Login Screen!********"
APP_IN_MESSAGE = "********Welcome to Chat App!********"
SEARCH_MESSAGE = "********Search Screen!********"
CHAT_MESSAGE = "********Chat Screen!********"


def welcome_page():
    while True:
        selection = input("Please select an option(Press 'Q' to quit): ")
        # validation for selection.
        if selection != '1' and selection != '2' and selection != 'Q':
            print('Ooopss! Invalid option!')
        else:
            return selection


def registration_page():
    message = ""  # it will be sent to server.
    while True:
        username = input("Please type an username: ")
        # validation for username and password
        if len(username) == 0 or len(username.split()) == 2:
            print('Ooopss! Username length should be bigger than 0 or should not contain space!')
            continue
        while True:
            password = input("Please type a password: ")
            if len(password) == 0 or len(password.split()) == 2:
                print('Ooopss! Password length should be bigger than 0 or should not contain space!!')
                continue
            message = username + " " + password
            break
        break
    return message


def login_page():
    message = ""  # it will be sent to server.
    while True:
        username = input("Username: ")
        # validation for username and password
        if len(username) == 0 or len(username.split()) == 2:
            print('Ooopss! Username length should be bigger than 0 or should not contain space!')
            continue
        while True:
            password = input("Password: ")
            if len(password) == 0 or len(password.split()) == 2:
                print('Ooopss! Password length should be bigger than 0 or should not contain space!!')
                continue
            message = username + " " + password
            break
        break
    return message


def app_page():
    print("1- Search\n2- Chat\n3- Logout\n")
    while True:
        selection = input("Please select an option: ")
        # validation for selection.
        if selection != '1' and selection != '2' and selection != '3':
            print('Ooopss! Invalid option!')
        else:
            return selection


def search_page():
    while True:
        username = input("Type an username to search: ")
        # validation for username and password
        if len(username) == 0 or len(username.split()) == 2:
            print('Ooopss! Username length should be bigger than 0 or should not contain space!')
            continue
        return username


def chat_page():
    address = ()
    while True:
        ip = input("Please type an IP address: ")
        # validation for username and password
        if len(ip) == 0 or len(ip.split()) == 2:
            print('Ooopss! Username length should be bigger than 0 or should not contain space!')
            continue
        while True:
            port = input("Please type a Port number: ")
            if len(port) == 0 or len(port.split()) == 2:
                print('Ooopss! Password length should be bigger than 0 or should not contain space!!')
                continue
            break
        address = (ip, int(port))
        break
    return address


def handle_registration():
    print(REGISTER_MESSAGE)
    while True:
        message = registration_page()
        client.send('REG_REQ'.encode('ascii'))
        response = client.recv(20).decode('ascii')
        if response == 'REG_OK':
            client.send(message.encode('ascii'))
            result = client.recv(20).decode('ascii')
            if result == 'REG_SUCCESS':
                print('Your registration has been successfully completed! You can login now!')
                return
            else:
                print('Username is already taken! Please try another!')
                continue


def handle_login():
    print(LOGIN_MESSAGE)
    while True:
        message = login_page()
        client.send('LOG_REQ'.encode('ascii'))
        response = client.recv(20).decode('ascii')
        if response == 'LOG_OK':
            client.send(message.encode('ascii'))
            result = client.recv(20).decode('ascii')
            if result == 'LOG_SUCCESS':
                print('You are in now!')
                return
            elif result == 'USR_ERR':
                print('Invalid Username! Please Try Again!')
                continue
            else:
                print('Invalid Password! Please Try Again!')
                continue


def handle_search():
    print(SEARCH_MESSAGE)
    while True:
        username = search_page()
        client.send('SRC_REQ'.encode('ascii'))
        response = client.recv(20).decode('ascii')
        if response == 'SRC_OK':
            client.send(username.encode('ascii'))
            result = client.recv(20).decode('ascii')
            if result == 'SRC_SUCCESS':
                addr = client.recv(100).decode('ascii')
                print(f'Contact address of {username}: {addr}')
                return addr
            print(f'Not any contact address for {username} in the system!')
            return

def send_hello_message ():
    hello_message = 'HELLO ' + str(client)
    client_UDP.sendto(hello_message.encode('ascii'),(SERVER_HOST, 50060))
    # for hello message
    sendHello_thread = threading.Timer(60, send_hello_message)
    sendHello_thread.start()



'''def chat():


def handle_chat():
    print(CHAT_MESSAGE)
    address = chat_page()
    print(f'ADDRESS: {address}')
    client.setsockopt()
    client.send('CHAT_REQ'.encode('ascii'))
    response = client.recv(10).decode('ascii')
    if response == 'BUSY':
        print('User is busy!')

    elif response == 'CHAT_REJECT':
        print('User does not want to chat!')

    else:
        print("Let's Chat!")
        chat()
    client.connect((SERVER_HOST, SERVER_PORT))'''


def main():
    while True:
        print(WELCOME_MESSAGE)
        selection = welcome_page()
        if selection == '1':    # registration.
            handle_registration()
        elif selection == '2':  # login.
            handle_login()
            break
        else:
            print(f'{client.getsockname()} has left the server!')
            client.close()
            return

    # user in now.
    send_hello_message()
    while True:
        print(APP_IN_MESSAGE)
        selection = app_page()
        if selection == '1':    # search.
            handle_search()
        elif selection == '2':  # chat.
            break
            #handle_chat()
        else:                   # logout.
            print(f'{client.getsockname()} has left the server!')
            client.close()
            return


def chat_response(client_peer):
    global peer_client
    answer = input(f'{client_peer} wants to chat with u! Do you want? [Y/N]: ')
    if answer == 'Y':
        peer_client = client_peer
        client.send('CHAT_OK')
    else:
        client.send('CHT_REJECT')


def start_to_listen():
    global peer_client
    client2.listen()
    while True:
        client_peer, address = client2.accept()
        request = client2.recv(10).decode('ascii')
        if request == 'CHAT_REQ' and peer_client != '':
            client2.send('BUSY'.encode('ascii'))
        elif request == 'CHAT_REQ' and peer_client == '':
            chat_response(client_peer)

        print(f'{str(address)} connected to {client.getsockname()}!')
        break


# for server
listen_thread = threading.Thread(target=main)
listen_thread.start()



# for peer
peer_thread = threading.Thread(target=start_to_listen)
peer_thread.start()