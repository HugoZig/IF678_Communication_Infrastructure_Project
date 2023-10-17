from Rdt import * 

while True:
    msg = input("Boas vindas ao Chatinho!\n")
    if("hi " in msg):
        name = msg.split("hi ")
        User = Rdt(name[1])
        if User.isSender("SYN") == 24:
            print("nome já utilizado tente outro")
        else:
            User.waiting()
            break
    else:
        print("Comando invalido. Impossivel entrar no chat.")