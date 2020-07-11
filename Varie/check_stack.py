#!/usr/bin/env python3
"""
Questo script verifica se gli switch elencati nel file "swlist.txt" sono all'int                                                                                                                                                             erno di uno stack.

Se il file non viene trovato lo script da errore e si ferma.

"""


import paramiko
import cmd
import time
import sys
import re
import getpass

#inizializzazione buffer per la connessione in ssh
#buff = ''
resp = ''


# List SW IP
try:
    SW_list = [line.rstrip('\n') for line in open("swlist.txt")]
except:
    print("File swlist.txt non trovato")
    exit()

#recupero lo user da usare nel loop
user=input("Inserisci lo user (necessario privilege level di 15): ")
#recupreo la psw da usare nel loop
psw=getpass.getpass("Inserisci la password di priviledged degli switch: ")


# definisco l'index e inizio il loop
i = 0
#----------------
while i < len(SW_list):
    i += 1 # incremento l'indice del loop

    try:    # Proviamoci
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SW_list[i-1], username=user, password=psw)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #run command
        chan = ssh.invoke_shell()
        # turn off paging-------------------------------------------------#
        chan.send('terminal length 0\n')
        time.sleep(1)
        resp = chan.recv(9999)      # recv(nbytes)
                                #Receive data from the channel. The return value                                                                                                                                                              is a string representing the data received.
                                # The maximum amount of data to be received at o                                                                                                                                                             nce is specified by nbytes.
                                # If a string of length zero is returned, the ch                                                                                                                                                             annel stream has closed.
        output = resp.decode('ascii').split(',')
        #print (''.join(output))
        #-----------------------------------------------------------------#
                                                                                                                                                                                                                                             

        # Display output of first command
        chan.send('show  interface status')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #output = ''.join(output)
        #print(output)

        for line in output:
            #print(line)
            if "2/" in line:
                stack=True
                break
            else:
                stack=False                                                                                                                                                                                                                  

        # Display output of second command
        output=''   #reinizializzo output
        chan.send('sh ver')
        chan.send('\n')
        time.sleep(3)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')


        # stampo i risultati della ricerca nel seguente forumato:

        # XXX.XXX.XXX -> Lo switch <switch> Ã¨(o NON Ã¨) in uno sck


        #in base alla regulare expression '(.+)#' ricavo l'hostname (la stringa                                                                                                                                                              prima del # ) e quindi stampo l'hostname
        RE_compile = re.compile('(.+)#')
        RE_result = RE_compile.search(''.join(output))
        if RE_result:
            if stack == True:
                print('#'*150 + '\r')
                print(SW_list[i-1],"-> Lo switch "+(RE_result.group(1)+" e' in u                                                                                                                                                             no stack"))
                print('#'*150 + '\r')
            else:
                print('#'*150 + '\r')
                print(SW_list[i-1],"-> Lo switch "+(RE_result.group(1)+" NON e'                                                                                                                                                              in uno stack"))
                print('#'*150 + '\r')
        else:
            if stack == True:
                print('#'*150 + '\r')
                print(SW_list[i-1],"-> Lo switch Ã¨ in uno stack ma non sono riu                                                                                                                                                             scito a recuperare l'hostname ")
                print('#'*150 + '\r')
            else:
                print('#'*150 + '\r')
                print(SW_list[i-1],"-> Lo switch NON Ã¨ in uno stack e non sono                                                                                                                                                              riuscito a recuperare l'hostname ","\n",RE_result,''.join(output))
                print('#'*150 + '\r')


        #chiudo la connessione
        ssh.close()

    #se qualcosa va storto..
    except paramiko.AuthenticationException as error:
        print('#'*150 + '\r')
        print(SW_list[i-1],"-> Authentication failed")
        print('#'*150 + '\r')
        continue
    except:
        print('#'*150 + '\r')
        print(SW_list[i-1],"-> Connection failed")
        print('#'*150 + '\r')
        continue

