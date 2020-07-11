"""
TerEnv project.

Questo programma si occupa di prendere una lista di IP di switch, collegarsi in telnet su cadauno di essi e abilitare l'SSH.
La particolarità di questa funzione è che gestisce il multi-thread, quindi esegue le connessioni simultaneamente.

La lista di IP viene caricata da un file di testo "swlist.txt".

La funzione EnableSSHDell gestisce la connessione e anche eventuali errori di irragiungibilita' e/o di autenticazione

ES:
192.168.90.500 17:23:35.207441 ERROR - Telnet closed
10.150.99.10 17:23:45.468009 SSH turned ON
10.150.99.11 17:23:55.696083 SSH turned ON

ES:

192.168.90.100 17:26:22.478091 ERROR - Telnet closed
192.168.90.200 17:26:43.508912 ERROR - Telnet closed
192.168.90.300 17:26:43.513410 ERROR - Telnet closed
192.168.90.400 17:26:43.514410 ERROR - Telnet closed
192.168.90.500 17:26:43.514410 ERROR - Telnet closed
10.150.99.10 17:26:53.614486 ERROR - auth failed
10.150.99.11 17:27:03.721079 ERROR - auth failed
"""


from NetTool import EnableSSHDell
from threading import Thread
import os,datetime

print("inizio programma")

# List SW IP
try:
    print(os.path.join(os.path.dirname(os.path.abspath(__file__)),"swlist.txt"))
    SW_list = [line.rstrip('\n') for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"swlist.txt"))]
except:
    print("File swlist.txt non trovato")
    exit()


user = "admin"
password = "cippalippa"
#host = "10.150.99.11"
threads = []        #blank array for multi-threading

# definisco l'index e inizio il loop
i = 0
#----------------
while i < len(SW_list):
    t = Thread(target=EnableSSHDell(SW_list[i],user, password))     #thread gestisce il parallel processing
    t.start()
    threads.append(t)
    i += 1 # incremento l'indice del loop
for t in threads:
    t.join()                                # accodiamo processi

