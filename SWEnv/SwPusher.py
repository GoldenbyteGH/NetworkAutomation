from netmiko import ConnectHandler


def pushDellimage(imagename,myip,usr,psw,tftpsrv):

    try:
        ssh_c = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)   #stabilisco una connessione con l'IP passato alla funzione
        # outputx=ssh_c.send_command("dir | in Directory")
    except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()

    # copy image firmware on dell switches
    cmd_copy = "en\ncopy tftp://"+ tftpsrv +"/" + imagename + " backup \ny"
    print(cmd_copy)
    try:
        # start copy
        output = ssh_c.send_command_timing(cmd_copy)
        flag = False         # serve per verificare se ha finito di copiare
        print(output)
      
    except Exception as error_message:                  # loggo l'errore dato dal comando precedente.
        print('#'*150 + '\r')
        print(error_message)
        print('#'*150 + '\r')
        exit()
    
    #check if file has been loaded
    print("Caricamento in corso, attendere..")

    #search only for the firmware version number
    imagename = imagename.replace("N2000Stdv","")
    imagename = imagename.replace(".stk","")

    #check if the image has been loaded
    while(flag == False):
        try:
            # open a new ssh connection for check process 
            check = ConnectHandler(device_type="dell_force10",ip=myip,username=usr,password=psw)
            c_output = ssh_c.send_command("show version")
            print(c_output)
            if imagename in c_output:
                print("Immagine caricata con successo:\n")
                print(c_output)
                flag = True     # ok, immagine caricata
            check.disconnect()
        except:
            print("errore nella verifica dell'immagine")
            exit()
    ssh_c.disconnect()