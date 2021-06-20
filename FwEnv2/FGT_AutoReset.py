
"""

La funzione ResetFW resetta ,in fase di riavvio, i firewall Fortigate ricavando dalla connessione seriale le credenziali dell'utente maintainer.

"""

import serial.tools.list_ports
from pythonping import ping

from re import search
from time import sleep


def COM_Finder():
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
                Serial = "{}: {} [{}]".format(port, desc, hwid)
                if search("USB-to-Serial",Serial):
                        return Serial[0:4]
def ResetFW():

    found = False
    port = serial.Serial(COM_Finder(), baudrate=9600,parity="N",stopbits=1, bytesize=8,timeout=3.0)

    print(COM_Finder())
    print("Reset in corso\n")
    while True:
        try:
            rcv = port.read(2000)               #SE La COM non è disponibile o non collegata torno -1
        except:
            return "None"
        if search("Serial number:",str(rcv)):

            str_rcv = str(rcv.decode())
            found = search('.FGT.{13}',str_rcv)

        if found:
            Serial_FW = found.group(0).replace(" ","")
            Maintainer_psw = "bcpb" + Serial_FW
            if len(rcv)>0:
                print(rcv)
            if Serial_FW != "":
                if search("login", str(rcv)):
                    sleep(2)
                    port.write(('maintainer').encode())
                    sleep(2)
                    port.write(('\n').encode())
                    sleep(2)
                    port.write(Maintainer_psw.encode())
                    sleep(2)
                    port.write(('\n').encode())
                    sleep(2)
                    port.write(('execute factoryreset').encode())
                    sleep(2)
                    port.write(('\n').encode())
                    sleep(2)
                    port.write(('y').encode())
                    sleep(2)
                    port.write(('\n').encode())
                    print(port.read(2000))
                    print("RESET COMPLETATO")
                    break

def VerifyPing(delay):
    sleep(delay)
    while True:
        if ping('192.168.1.99').success(True):
            print("FW UP")
            break
