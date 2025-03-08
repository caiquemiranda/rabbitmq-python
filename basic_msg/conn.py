import socket
import time

def enviar_mensagem(mensagem):
    # Configuração do socket
    HOST = 'localhost'
    PORT = 5000
    
    # Criar socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Conectar ao servidor
        s.connect((HOST, PORT))
        # Enviar mensagem
        s.sendall(mensagem.encode())

if __name__ == "__main__":
    while True:
        mensagem = input("Digite uma mensagem (ou 'sair' para encerrar): ")
        if mensagem.lower() == 'sair':
            break
        enviar_mensagem(mensagem)
        time.sleep(0.1)  # Pequeno delay para não sobrecarregar
