from netmiko import ConnectHandler
import time


def countdown(total,step=5):    #show contdown during the reboot
    index = 0
    timer = 0
    while(timer<total):
        time.sleep(step)
        index += 1
        timer = index * step
        print("wait "+ str(total - timer) + " seconds...")


def swsaver(myip,usr,psw,tftpsrv):
    try:
        ssh_c = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)   #stabilisco una connessione con l'IP passato alla funzione
        # outputx=ssh_c.send_command("dir | in Directory")
    except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()


    cmd_copy = "en\ncopy run tftp://"+ tftpsrv +"/" + "config_"+myip.replace(".","_") + ".txt\ny"
    cmd_save = "en\ncopy run start\ny"

    # tento un salvataggio
    #save_cmd = "en\ncopy run start\ny"
    try:# salvo una copia locale sulla postazione
        print("salvataggio configurazione in corso_assicurati di aver attivato il TFTP server sul tuo computer locale...")
        output = ssh_c.send_command_timing(cmd_copy)
        print(output)
        ssh_c.disconnect()
    except:
        print("errore durante il salvataggio TFTP")

    #salvo la running sullo switch
    try:
        ssh_c = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)   #stabilisco una connessione con l'IP passato alla funzione
        print("salvataggio configurazione in corso sullo switch")
        output2 = ssh_c.send_command_timing(cmd_save)
        print(output2)
        ssh_c.disconnect()
    except:
        print("errore durante il salvataggio sullo switch")




def update20xx(imagename,myip,usr,psw):

    try:
        ssh_c2 = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)   #stabilisco una connessione con l'IP passato alla funzione
        # outputx=ssh_c.send_command("dir | in Directory")
    except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    #1° step
    cmd_stop_app = "en\napplication stop hiveagent\ndelete user-apps/ah_ha.conf_s\ny\ndelete user-apps/hiveagent_pr_s\ny\ndelete user-apps/ah_ha.conf\ny\ndelete user-apps/hiveagent_pr\ny\ndelete user-apps/hiveagent\ny\n"
    try:
        output = ssh_c2.send_command_timing(cmd_stop_app)
        print(output)
    except:
        print("Errore durante lo stop di hiveagent")
        exit()
    #Attivare il boot dallo slot di backup
    cmd_boot_bkp = "en\nboot system backup\n"
    try:
        output = ssh_c2.send_command_timing(cmd_boot_bkp)
        print(output)
    except:
        print("Errore durante il set del boot system backup")
        exit()
    #primo riavvio dello switch
    print("primo reboot in corso")
    ssh_c2.send_command_timing("en\nreload\ny")
    ssh_c2.disconnect()
    countdown(100)
    #--------------------------------------------------------------------------------------------------------------------------------------------
    try:
        ssh_c2 = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)   #stabilisco una connessione con l'IP passato alla funzione
        # outputx=ssh_c.send_command("dir | in Directory")
    except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()

    #2° step

    #Aggiornare il bootcode
    cmd_bootcode = "en\nupdate bootcode\ny\n"
    try:
        output = ssh_c2.send_command_timing(cmd_bootcode)
        print(output)
    except:
        print("Errore durante l'update del bootcode\n")
        exit()
    #secondo riavvio dello switch    
    print("secondo reboot in corso")
    ssh_c2.send_command_timing("en\nreload\ny")
    ssh_c2.disconnect()
    countdown(100)
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    try:
        ssh_c2 = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)   #stabilisco una connessione con l'IP passato alla funzione
        # outputx=ssh_c.send_command("dir | in Directory")
    except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()
    #Aggiornare il cpld
    cmd_cpld = "en\nupdate cpld\ny\n"
    try:
        output = ssh_c2.send_command_timing(cmd_cpld)
        print(output)
    except:
        print("Errore durante l'update del cpld")
        exit()
    #secondo riavvio dello switch    
    print("ultimo reboot in corso - E' possibile disalimentare lo switch")
    ssh_c2.send_command_timing("en\nreload\ny")
    ssh_c2.disconnect()
    countdown(180)