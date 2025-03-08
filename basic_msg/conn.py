import socket
import time
from datetime import datetime

def enviar_mensagem(mensagem):
    HOST = 'localhost'
    PORT = 5000
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(mensagem.encode())
            print(f"✅ Mensagem enviada: {mensagem}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

def main():
    print("=== Sistema de Envio de Mensagens ===")
    print("Digite 'sair' para encerrar o programa")
    print("=====================================")
    
    while True:
        try:
            mensagem = input("\n➤ Digite sua mensagem: ")
            if mensagem.lower() == 'sair':
                print("\nEncerrando o programa...")
                break
            
            if mensagem.strip():  # Só envia se não estiver vazia
                enviar_mensagem(mensagem)
                time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nPrograma interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
