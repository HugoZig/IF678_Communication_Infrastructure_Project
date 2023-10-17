from socket import *
import struct
import numpy as np
from random import *

HOST = "127.0.0.1"  # Endereço IP do servidor
PORT = 5000         # Porta do servidor
origin = (HOST, PORT) # Tupla com o endereço IP e a porta do servidor

receiverSocket = socket(AF_INET, SOCK_DGRAM) # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET)
receiverSocket.bind(origin)
bufferSize = 1024
addr = (0,0)
endFlag = 0

def sendAck(ack):
    global endFlag
    data = struct.pack('i', ack)
    #receiverSocket.sendto(data, addr)
    if randint(0,9):     #taxa de perda de 10%
        receiverSocket.sendto(data, addr) # Envia os dados para o destino
    else: 
        print('\x1b[1;31;40m' + 'Ack perdido' + '\x1b[0m')
        endFlag = 0


state = "waitSeq_0" # Variável de estado - Começa com o estado inicial "waitCall_0"
file = open("pikapikapika.png", "wb")
file_bytes = 0


while(True): # Loop principal da maquina de estados finitos do receptor
    
    if state == "waitSeq_0": # Estado de esperar pelo pacote 0
        print("Esperando numSeq=0")
        try:
            pckg, addr = receiverSocket.recvfrom(bufferSize) # Recebe o pacote se algum chegar
        except: 
            print('ocorreu uma execao (waitSeq_0)')
            pass # Enquanto nao houver pacote para receber, apenas espera
        else:
            print('\x1b[1;32;40m' + 'Pacote recebido' + '\x1b[0m')
            tam = len(pckg) - 4
            pckg = struct.unpack_from(f'i {tam}s', pckg)
            seq = pckg[0]
            payload = pckg[1:]

            if seq == 0:
                if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                    endFlag=1
                for i in payload:
                    file.write(i)

                action = "sendAck0"   # Ao receber pacote, se o número de sequência for zero manda ack correspondente
            else: 
                action = "sendAck1" # Se o pacote não é o correto, manda o ack de sequência 1, ao invés disso
                if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                    endFlag=1
        

    elif state == "waitSeq_1": # Estado de esperar pelo pacote 1
        print("Esperando numSeq=1")
        try:
            pckg, addr = receiverSocket.recvfrom(bufferSize) # Recebe o pacote se algum chegar
        except: 
            print('ocorreu uma execao (waitSeq_1)')
            pass  # Esperar ate um pacote chegar
        else:
            print('\x1b[1;32;40m' + 'Pacote recebido' + '\x1b[0m')
            tam = len(pckg) - 4
            pckg = struct.unpack_from(f'i {tam}s', pckg)
            seq = pckg[0]
            payload = pckg[1:]

            if seq == 1:
                action = "sendAck1" # Se seq do pacote for o esperado, manda o ack de sequencia 1, e deve mudar o estado
                if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                    endFlag=1
                for i in payload:
                    file.write(i)
            else: 
                action = "sendAck0" # Se seq pacote nao for o esperado, manda o ack de sequencia 0, e deve continuar no mesmo estado 
                if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                    endFlag=1
                    


    if action == "sendAck0":
        print('\x1b[1;34;40m' + 'Ack 0 enviado' + '\x1b[0m')
        sendAck(0)           # Manda o ack de sequência 0
        if endFlag: break
        state = "waitSeq_1"  # Muda de estado para waitSeq_1
        
    elif action == "sendAck1":
        print('\x1b[1;34;40m' + 'Ack 1 enviado' + '\x1b[0m')
        sendAck(1)          # Manda ack de sequencia 1
        if endFlag: break
        state = "waitSeq_0" # Muda o estado para waitSeq_0

print('\x1b[7;35;47m' + 'Fim do programa' + '\x1b[0m')
file.close()
receiverSocket.close()