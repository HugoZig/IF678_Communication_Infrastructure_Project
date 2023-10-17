from socket import *
import os
import struct
from random import *

HOST = "127.0.0.1"  # Endereço IP do servidor
PORT = 5000         # Porta do servidor
dest = (HOST, PORT)  
bufferSize = 1020 #1024 - seqNum = 1024 - sizeof(int)
time = 1.0

senderSocket = socket(AF_INET, SOCK_DGRAM) # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET)
senderSocket.settimeout(time) 

def sendPkt(payload, seqNum): # Converte os dados em uma representação de string e codifica em bytes
    tam = len(payload)
    data = bytearray(4 + tam)
    data = struct.pack(f'i {tam}s', seqNum, payload)
    print('\x1b[1;32;40m' + 'Pacote enviado' + '\x1b[0m')
    if randint(0,3):   #taxa de perda de 25%
        senderSocket.sendto(data, dest) # Envia os dados para o destino
    else:print('\x1b[1;31;40m' + 'Pacote perdido' + '\x1b[0m')



file_src = "pikachuzera.png"  # Nome do arquivo a ser enviado
file = open(file_src, "rb")    # Abre o arquivo em modo de leitura binária

state = "waitCall_0" # Variável de estado do remetente - Inicializa com o estado "waitCall_0"
fimPck = 0 
while(True): #Loop principal da máquina de estados finitos do remetente
    
    if state == "waitCall_0":
    # Estado de esperar para enviar o pacote de sequência 0
        print("No aguardo por uma chamada de NumSeq = 0")
        action = "sendPktSeq_0" # Manda o pacote de sequência 0

    elif state == "waitAck_0":
    # Estado de esperar recebimento do Ack 0 após o pacote 0 ter sido enviado
        print("No aguardo por um ACK=0")
        try:
            ack_pck = senderSocket.recv(bufferSize) # Se chegar um pacote Ack, recebe o Ack
        except timeout:
            print('\x1b[7;31;47m' +'Timeout no Transmissor' + '\x1b[0m')
            action = "ReSendPktSeq_0" # Se ocorrer um timeout, manda novamente o pacote de sequência 0
        else:
            ack_pck = struct.unpack_from('i', ack_pck) # Decodifica o pacote ACK
            ack = ack_pck[0]             # Obtém o campo ACK do pacote
            if ack == 0: 
                print('\x1b[1;34;40m' + 'Ack 0 recebido' + '\x1b[0m')
                action = "stopTimer_0" # Se o ACK for 0, reseta o timer
                if fimPck: 
                    break
            else: 
                action = "ReSendPktSeq_0" # Se o ack for tiver a sequência errada, manda novamente o pacote 0

    elif state == "waitCall_1":
    # Estado de esperar para enviar o pacote de sequência 1
        print("No aguardo por uma chamada de NumSeq = 1")
        action = "sendPktSeq_1" # Manda o pacote de sequência 1

    elif state == "waitAck_1":
     # Estado de esperar recebimento do Ack 1 após o pacote 1 ter sido enviado
        print("No aguardo por um ACK=1")
        try:
            ack_pck = senderSocket.recv(bufferSize) # Se chegar um pacote Ack, recebe o Ack
        except timeout:
            print('\x1b[7;31;47m' +'Timeout no Transmissor' + '\x1b[0m')
            action = "ReSendPktSeq_1" # Se ocorrer um timeout, manda novamente o pacote de sequência 1
        else:
            ack_pck = struct.unpack_from('i', ack_pck) # Decodifica o pacote ACK
            ack = ack_pck[0]             # Obtém o campo ACK do pacote
            if ack == 1:
                action = "stopTimer_1" # Se o ACK for 1, reseta o timer
                print('\x1b[1;34;40m' + 'Ack 1 recebido' + '\x1b[0m')
                if fimPck: # Envio encerrou e receiver recebeu tudo
                    break
            else:
                action = "ReSendPktSeq_1" # Se o ack for tiver a sequência errada, manda novamente o pacote 1

    if action == "sendPktSeq_0":
        data = file.read(bufferSize)  # Lê 1024 bytes do arquivo
        if not data:
            fimPck = 1
            sendPkt(b'FIM', 0)
        else:
            sendPkt(data, 0)
            
        state = "waitAck_0"

    elif action == "stopTimer_0":
        senderSocket.settimeout(time) #reseta timer
        state = "waitCall_1"

    elif action == "sendPktSeq_1":
        data = file.read(bufferSize)  # Lê 1024 bytes do arquivo
        if not data: 
            fimPck = 1
            sendPkt(b'FIM', 1)
        else: # ainda há pacotes para enviar
            sendPkt(data, 1)
        state = "waitAck_1"

    elif action == "stopTimer_1":
        senderSocket.settimeout(time) #reseta timer
        state = "waitCall_0"

    elif action == "ReSendPktSeq_0":
        print('\x1b[1;33;40m' + 'Reenviando Pacote (NumSeq=0)' + '\x1b[0m')

        if not data: 
            fimPck = 1
            sendPkt(b'FIM', 0)
        else: # ainda há pacotes para enviar
            sendPkt(data, 0)
        state = "waitAck_0"
    
    elif action == "ReSendPktSeq_1":
        print('\x1b[1;33;40m' + 'Reenviando Pacote (NumSeq=1)' + '\x1b[0m')
        if not data: 
            fimPck = 1
            sendPkt(b'FIM', 1)
        else: # ainda há pacotes para enviar
            sendPkt(data, 1)
        state = "waitAck_1"     
        
print('\x1b[7;35;47m' + 'Fim do envio' + '\x1b[0m')
file.close()
senderSocket.close()
