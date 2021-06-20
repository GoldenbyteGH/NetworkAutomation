#print("HTTP/1.0 200 OK\n")
#print("Content-Type: text/html\n\n\n")

"""

Questo programma esegue la configurazione in 'automagically mode' di un apparato di rete sfruttando un file contenente i parametri di default 
( e quindi anche il relativo template da usare come modello della configrazione)
Il programma sfrutta la libreria netmiko ( basata su paramiko), quindi è necessario avere installate entrambi per ovviare ad eventuali errori sulle librerie
Il programma non prende parametri in input e non produce file di output, sfrutta il file "devices.json" per far preparare la configurazone e "scaricarla" sul device con IP di management 
indicato sul medesmimo file ("mgt_ip").
Nel caso la connessione non vada a buon fine il programma termina indicando il relativo errore.
"""


from netmiko import ConnectHandler
from pathlib import Path
import cgi, cgitb 
import json
import os
import time


#-----------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------

def fix_configuration60E(specs):

    # load dirty template
   

    #path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'') # return current directory ( regardless os )
    path = Path(Path(__file__).parent).parent   # restituisce la parent directory
    #print(path+'\n')
    # preparo la configurazione a seconda si  NAT o Transparent
    if specs["Firewall"][0]["mode"] == 0:
        print("CONFIGURAZIONE IN NAT\n")
        try:
            #template_fw = open(path + specs["Firewall"][0]["conf_NAT"])   # open conf_template
            template_fw = open(os.path.join(path,os.path.join("configfiles",os.path.join("FGT", specs["Firewall"][0]["conf_NAT"]))))
        except:
            print("template " + specs["Firewall"][0]["conf_NAT"] + "non trovato" )
            exit()
    else:
        try:
            print("CONFIGURAZIONE IN TRANSPARENT\n")
            template_fw = open(os.path.join(path,os.path.join("configfiles",os.path.join("FGT", specs["Firewall"][0]["conf_TRA"]))))   # open conf_template
        except:
            print("template " + specs["Firewall"][0]["conf_TRA"] + "non trovato" )
            exit()
    
    try:
        conf = open(os.path.join(os.path.join(path,""),"configfile.txt"), 'w')       #create actual config file
    except:
        print(os.path.join(os.path.join(path,""),"configfile.txt"))
        print("impossibile creare il file di configurazione, verificare i permessi di scrittura")
        exit()
    
    for line in template_fw.readlines():
        # fix parameters:
        if "-USER-" in line:
            line = line.replace("-USER-", specs["Firewall"][0]["usr_new"] )
        if "-PASSWORD-" in line:
            line = line.replace("-PASSWORD-", specs["Firewall"][0]["psw_new"] )
        if "-WAN_IP-" in line:
            line = line.replace("-WAN_IP-", specs["Firewall"][0]["wan1_ip"] )
            if "-WAN_SM-" in line:
                line = line.replace("-WAN_SM-", specs["Firewall"][0]["wan1_sm"] )
        if "-LAN_IP-" in line:
            line = line.replace("-LAN_IP-", specs["Firewall"][0]["mgt_ip"] )
            if "-LAN_SM-" in line:
                line = line.replace("-LAN_SM-", specs["Firewall"][0]["mgt_sm"] )
        if "-GW_IP-" in line:
            line = line.replace("-GW_IP-", specs["Firewall"][0]["gw_ip"] )
        if "-VIP1_IP-" in line:
            line = line.replace("-VIP1_IP-", specs["Firewall"][0]["vip1_ip"] )
        if "-PRIV1_IP-" in line:
            line = line.replace("-PRIV1_IP-", specs["Firewall"][0]["priv1_ip"] )

        conf.write(line)

    conf.close()






#Let's start with the script
#--------------------------------carico il file json dal quale recupero i dati di default dell'appliance da configurare-------------
# apro il file
try:
    path = Path(Path(__file__).parent).parent   # restituisce la parent directory "NetworkAutomation" 
    devices_load = open(os.path.join(path,os.path.join("configfiles", "devices.json")))
    
    
except:
    print(path)
    print(os.path.join("configfiles",os.path.join(path, "devices.json")))
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
    conf_fixed = open(os.path.join(os.path.join(path,""),"configfile.txt"))
except:
    print("File di configurazione non trovato all'interno di " +os.path.join(os.path.join(path,""),"configfile.txt"))
    exit()


#let'go netmiko----
i = 0   # I need 2 loops, one to configure and another to remove admin user..
while i < 2:
    if i == 1:
        try:
            if(device_dict["Firewall"][0]["mode"] == 1):
                try:
                    c_ssh = ConnectHandler(device_type="fortinet",ip = device_dict["Firewall"][0]["mgt_ip_def"],username=device_dict["Firewall"][0]["usr_def"], password= device_dict["Firewall"][0]["psw_new"] )    #netmiko connection
                    cmdtpset = ['config system settings','set opmode transparent','set manageip ' + device_dict["Firewall"][0]["mgt_ip_def"] + ' ' + '255.255.255.0','end']
                    c_ssh.send_config_set(cmdtpset)
                    time.sleep(4)

                except:
                    
                    print('#'*150 + '\r')
                    print("Errore nella configurazione in TP")
                    print('#'*150 + '\r')
                    exit()
                
                

            print("Loop: " + str(i) + '\n') 
            print("Configurazione del firewall, attendere prego...")
            c_ssh = ConnectHandler(device_type="fortinet",ip = device_dict["Firewall"][0]["mgt_ip_def"],username=device_dict["Firewall"][0]["usr_def"], password= device_dict["Firewall"][0]["psw_new"] )    #netmiko connection
            output = c_ssh.send_config_from_file(os.path.join(os.path.join(path,""),"configfile.txt"))   #netmiko miracle..questo comando "fallisce" se viene configurato un cambio IP, in tal caso il programma prosegue
                                                            #nell'exception statement

            # se non scatta l'Exception significa che c'è stato un errore in fase di configurazione dell'appliance
            print("ERRORE - L'IP non e' cambiato, verifica i parametri inseriti (ATTENZIONE - l'IP 10.10.10.1 è assegnato alla dmz)")
            print('#'*150 + '\r')
            print("\n" + output)
            print('#'*150 + '\r')
            
      
            
        except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
            print('#'*150 + '\r')
            print(error_message)
            print('#'*150 + '\r')
            
    else:
    
        #we have first to change admin password...
        try:   
            print("Loop: " + str(i) + '\n')
            try: 
                c_ssh = ConnectHandler(device_type="fortinet",ip = device_dict["Firewall"][0]["mgt_ip_def"],username=device_dict["Firewall"][0]["usr_def"], password= psw_def )    #netmiko connection
            except Exception as error_psw: #se ottengo quì un errore, probabilmente o la password di default non è corretta 
                                            # o l'IP del server python non è compatibile con quello di default del firewall
                print(error_psw)
                exit()
                
            cmdpswset = ['config system admin','edit "admin"','set password ' + device_dict["Firewall"][0]["psw_new"],'next','end']
            c_ssh.send_config_set(cmdpswset)
            # da errore a causa del cambio password, è normale        
        except Exception as error_psw:
            print(error_psw)
            print("password cambiata\n")
    
    i +=1
#rimuovo il file di configurazione generato dal programma
conf_fixed.close()
os.remove(os.path.join(os.path.join(path,""),"configfile.txt"))



print('\n'+'#'*150 + '\r')
print("PROGRAMMA TERMINATO\n l'errore 'Timed-out reading channel, data not available.' e' da ignorare ( errore dovuto al cambio IP)")
print('#'*150 + '\r')
