"""
---------------------------------------    CONFIGURATIONER.PY by OGC - Aruba Techops Team    ------------------------------------------------------
Questa funzione prende in input un dizionario caricato dal file device.json e produce un file di configurazione (configfile.txt) da caricare sul device da configurare.
Questa funzione cerca all'interno del dizionario il percorso del template di configurazione che una volta trovato, usa per eseguire la sostituzione dei parametri
passati attraverso il dizionario.
ES.
FwEnv2# cat conf_template.txt
config system admin
edit "admin"
set password -PASSWORD-
next
end
DIVENTA:
FwEnv2# cat configfile.txt
config system admin
edit "admin"
set password mypsw123
next
end
"""
import os


#----------------------------------------------------------------------------------------------------------------------

def fix_configuration60E(specs):

    # load dirty template
   

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'') # return current directory ( regardless os )
    print(path+'\n')
    # preparo la configurazione a seconda si  NAT o Transparent
    if specs["Firewall"][0]["mode"] == 0:
        print("CONFIGURAZIONE IN NAT\n")
        try:
            template_fw = open(path + specs["Firewall"][0]["conf_NAT"])   # open conf_template
        except:
            print("template " + specs["Firewall"][0]["conf_NAT"] + "non trovato" )
    else:
        try:
            print("CONFIGURAZIONE IN TRANSPARENT\n")
            template_fw = open(path + specs["Firewall"][0]["conf_TRA"])   # open conf_template
        except:
            print("template " + specs["Firewall"][0]["conf_TRA"] + "non trovato" )
    
    try:
        conf = open(path + 'configfile.txt', 'w')       #create actual config file
    except:
        print("impossibile creare il file di configurazione, verificare i permessi di scrittura")
    
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