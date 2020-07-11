
"""
---------------------------------------    FW_CONFIGURATOR.PY by OGC - Aruba Techops Team    ------------------------------------------------------
Questo programma esegue la configurazione in 'automagically mode' di un apparato di rete sfruttando un file contenente i parametri di default 
( e quindi anche il relativo template da usare come modello della configrazione)
Il programma sfrutta la libreria netmiko ( basata su paramiko), quindi è necessario avere installate entrambi per ovviare ad eventuali errori sulle librerie
Il programma non prende parametri in input e non produce file di output, sfrutta il file "devices.json" per far preparare la configurazone e "scaricarla" sul device con IP di management 
indicato sul medesmimo file ("mgt_ip").
Nel caso la connessione non vada a buon fine il programma termina indicando il relativo errore.
"""

from configurationer import fix_configuration60E
from netmiko import ConnectHandler
from pathlib import Path
import json
import os


#-----------------------------------------------------------------------------------------------------------------------------------


#Let's do it
#--------------------------------carico il file json dal quale recupero i dati di default dell'appliance da configurare-------------
# apro il file
try:
    path = Path(Path(__file__).parent).parent   # restituisce la parent directory "NetworkAutomation" da dove viene caricato il file json
    devices_load = open(os.path.join(path, "devices.json"))
    
    
except:
    print("File 'devices.json' non trovato")
    exit()

# Create dictionary from JSON
device_dict = json.loads(devices_load.read())

#------------------------------------------------------------------------------------------------------------------------------------------
#Let's fix configuration
fix_configuration60E(device_dict) # generate actual configuration ( configfile.txt)
#if default password is NULL make it empty
if device_dict["Firewall"][0]["psw_def"].upper() == "NULL":
    psw_def = ""
else:
    psw_def = device_dict["Firewall"][0]["psw_def"]
#----------------------------------------------------------------------------------
try:
    conf_fixed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"configfile.txt"))
except:
    print("File di configurazione non trovato all'interno di " + os.path.dirname(os.path.abspath(__file__)))
    exit()


#let'go netmiko----
i = 0   # I need 2 loops, one to configure and another to remove admin user..
while i < 2:
    if i == 1:
        try:
            print("Loop: " + str(i) + '\n') 
            print("Configurazione del firewall, attendere prego...")
            c_ssh = ConnectHandler(device_type="fortinet",ip = device_dict["Firewall"][0]["mgt_ip_def"],username=device_dict["Firewall"][0]["usr_def"], password= device_dict["Firewall"][0]["psw_new"] )    #netmiko connection
            c_ssh.send_config_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"configfile.txt"))   #netmiko miracle..questo comando "fallisce" se viene configurato un cambio IP, in tal caso il programma prosegue
                                                            #nell'exception statement
            
      
            
        except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
            print('#'*150 + '\r')
            print(error_message)
            print('#'*150 + '\r')
            
    else:
    
        #we have first to change admin password...
        try:   
            print("Loop: " + str(i) + '\n')
            c_ssh = ConnectHandler(device_type="fortinet",ip = device_dict["Firewall"][0]["mgt_ip_def"],username=device_dict["Firewall"][0]["usr_def"], password= psw_def )    #netmiko connection
            cmdpswset = ['config system admin','edit "admin"','set password ' + device_dict["Firewall"][0]["psw_new"],'next','end']
            c_ssh.send_config_set(cmdpswset)
            # da errore a causa del cambio password, è normale        
        except Exception as error_psw:
            print(error_psw)
            print("password cambiata\n")
    
    i +=1
#rimuovo il file di configurazione generato dal programma
conf_fixed.close()
os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),"configfile.txt"))


print('\n'+'#'*150 + '\r')
print("PROGRAMMA TERMINATO\n l'errore 'Timed-out reading channel, data not available.' e' da ignorare ( nel caso venga cambiato IP)")
print('#'*150 + '\r')
