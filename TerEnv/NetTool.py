#!/usr/bin/env python3
"""

NetTool.py = Telnet python tools

Questa funzione prende in input IP e credenziali per connettersi in telnet ed abilitare l'ssh

//////////////////////////////////////////////////////////////////////////////////////////////////////////
codice esempio recupearato da CLN 
https://community.cisco.com/t5/automation-and-analytics/python-telnet/m-p/4081752#M3808

es telent library from CLN

import getpass
import telnetlib

HOST = "192.168.122.3"
user = input("Enter your telnet username: ")
// After this line of code has executed, you read user's input (including the newline char: \n)
// Meaning that your 'user' variable is something like user = "username\n"

// You need to remove the unwanted tailing \n by adding the following code
user = user.rstrip()

password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"username: ")

tn.write(user.encode('ascii') + b"\n")
//Otherwise, when your script passing the variable 'user' with your additional tailing b"\n"
//which will become "username\n\n"
//which mean you hit the enter twice, in other word, you enter an empty password to the switch.

if password:
tn.read_until(b"Password: ")
tn.write(password.encode('ascii') + b"\n")

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



"""
import telnetlib,socket,datetime


def EnableSSHDell(HOST, USER,PASSWORD):

    #check if port is open
    if portchecker(HOST,23):
        print(HOST+" "+str(datetime.datetime.now().time())+" ERROR - Telnet closed")
        return             # port closed
    # check if credentials work
    #ok the port is open but it is not enough...what about credentials?
    checker = ""        # variable for the "show version"
    try:
        tn = telnetlib.Telnet(HOST)
        tn.read_until(b"User: ",timeout=5)
        tn.write(USER.encode('ascii') + b"\n")
        if PASSWORD:
            tn.read_until(b"Password:",timeout=5)
            tn.write(PASSWORD.encode('ascii') + b"\n")
        else:
            tn.read_until(b"Password:",timeout=5)
            tn.write(b"\n")

        tn.write(b"show version"+ b"\n")
        tn.write(b"exit"+ b"\n")
        checker = tn.read_until(b"exit",timeout=5).decode('ascii')

        if len(checker) < 250 :                     # se lo show version funziona, la stringa restituita dall'output è all'incirca di 800 caratteri {quindi maggiore di 250}( sui Dell).
                                                    # in caso contrario ( qualora fosse <= 50 caratteri) c'è stato un errore di autenticazione
            print(HOST+" "+str(datetime.datetime.now().time())+" ERROR - auth failed")
            return     #   auth error

    # ok it works, let's do it

        tn = telnetlib.Telnet(HOST)
        tn.read_until(b"User: ",timeout=5)
        tn.write(USER.encode('ascii') + b"\n")
        if PASSWORD:
            tn.read_until(b"Password:",timeout=5)
            tn.write(PASSWORD.encode('ascii') + b"\n")
        else:
            tn.read_until(b"Password:",timeout=5)
            tn.write(b"\n")

        tn.write(b"en"+ b"\n")
        tn.write(b"configure"+ b"\n")
        tn.write(b"crypto key generate rsa"+ b"\n"+b"y")
        tn.write(b"crypto key generate dsa"+ b"\n"+b"y")
        tn.write(b"ip ssh server"+ b"\n")
    
    except Exception as error_message:                  # loggo un ipotetico errore
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()

    print(HOST+" "+str(datetime.datetime.now().time())+" SSH turned ON")

  
def portchecker(HOST,PORT):
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (HOST, PORT)
    try:
        result_of_check = a_socket.connect_ex(location)         #discover what is open
    except:
        return 1    # porta chiusa, errore via da quì

    if result_of_check:
        return 1        #porta chiusa
    else:
        return 0        # porta aperta 
    a_socket.close()


