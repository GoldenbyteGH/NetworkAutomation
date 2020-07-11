from SwPusher import pushDellimage
from SwUpdater import swsaver, update20xx
import os.path
from pathlib import Path
import socket
import json


"""
---------------------------------------    MAIN.PY by OGC - Aruba Techops Team    ------------------------------------------------------
Questo programma esegue un backup della configurazione di uno switch  per poi procedere con procedura di update del firmware.
Gli eventuali reboot vengono gestiti da una funzione countdown, la quale resta in attesa fino al termine del reboot ( statisticamente lo SW torna UP dopo 
100 secondi).
Questo programma non richiede input da tastiera in quanto i parametri dei device vengono letti dal dizionario devices.json
"""


# inizio programma principale

tftpsrv = "10.150.99.247" # definisco il tftp server sul quale prendere le immagini e fare i backups

try:
    path = Path(Path(__file__).parent).parent   # restituisce la parent directory "NetworkAutomation" da dove viene caricato il file json
    devices_load = open(os.path.join(path, "devices.json"))
    device_dict = json.loads(devices_load.read())
    
except:
    print("File 'devices.json' non trovato")
    exit()


# check if tftp is open ##############################################################################################################################
a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

location = (tftpsrv, 69)
result_of_check = a_socket.connect_ex(location)

if result_of_check == 0:
    print("TFTP Port is open")
else:
    print("TFTP Port is not open")

######################################################################################################################################################


ipaddress = device_dict["Switch"][0]["mgt_ip"]
imagename = device_dict["Switch"][0]["firm_img"]
username =  device_dict["Switch"][0]["usr"]
password =  device_dict["Switch"][0]["psw"]
print("Working on "+ipaddress+":\n")
# save run and backup the config
swsaver(ipaddress,username,password,tftpsrv)
# push new firmware (by JSON)
pushDellimage(imagename,ipaddress,username,password,tftpsrv)
#update process
update20xx(imagename,ipaddress,username,password)
print("\nprogramma terminato")








