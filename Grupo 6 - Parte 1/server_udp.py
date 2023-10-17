import socket 
from PIL import Image
import os

HOST = "127.0.0.1"
PORT = 5000
origin = (HOST, PORT)  # Endereço de origem do servidor
dest = (HOST, 3000)    # Endereço de destino para envio de volta ao cliente

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET).

serverSocket.bind(origin) # Liga o socket do servidor ao endereço de origem especificado.

#------------RECEBIMENTO DO ARQUIVO -----------------------------------

print("Server is ready!")
file_bytes = b""  # Variável para armazenar os bytes do arquivo recebido

file_name, clientAddress = serverSocket.recvfrom(1024)  # Recebe o nome do arquivo enviado pelo cliente
file_name = file_name.decode()
print(file_name)
file_name = "received_" + file_name  # Modifica o nome do arquivo para salvar no servidor
file = open(file_name, "wb")  # Abre um novo arquivo binário para escrita

dcount = 0  # Contador para contagem dos datagramas recebidos
while True:
    datagram, clientAddress = serverSocket.recvfrom(1024)
    dcount += 1
    print(f"datagram {dcount} recebido do cliente ({clientAddress})")

    if datagram == b"<END>":  # Usa "<END>" para indicar o fim do arquivo.
        dcount = 0
        break
    else:
        file_bytes += datagram
print("envio finalizado.")

file.write(file_bytes)
file.close()
# Recebe e reconstroi o arquivo enviado pelo cliente, escrevendo-o no disco.


#------DEVOLUCAO DO ARQUIVO----------------------------------------------------------
file = open(file_name, "rb")
serverSocket.sendto(file_name.encode(), clientAddress)  # Envia o nome do arquivo de volta ao cliente

while True:
    file_data = file.read(1024)
    if not file_data:
        serverSocket.sendto(b"<END>", clientAddress)  # Envia "<END>" para indicar o fim do envio.
        break
    serverSocket.sendto(file_data, clientAddress)
# Lê o arquivo reaberto e envia partes do arquivo de volta para o cliente.


file.close()
serverSocket.close()  # Fecha o arquivo e o socket do servidor.
