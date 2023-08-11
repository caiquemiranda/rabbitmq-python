import socket

def main():
    # Endereço IP do computador
    #endereco_ip = '127.0.0.1'  # Pode ser alterado para o IP desejado
    endereco_ip = '35.207.24.140'
    #porta = 12345  # Porta que será escutada
    porta = 443

    # Cria um socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Liga o socket ao endereço IP e porta especificados
    server_address = (endereco_ip, porta)
    sock.bind(server_address)

    # Começa a escutar por conexões
    sock.listen(1)
    print(f"Aguardando uma conexão em {endereco_ip}:{porta}")

    # Aceita a conexão
    connection, client_address = sock.accept()
    print(f"Conexão estabelecida com {client_address}")

    try:
        while True:
            data = connection.recv(1024)  # Recebe os dados da conexão
            if not data:
                break
            print(f"Dados recebidos: {data.decode('utf-8')}")
    finally:
        # Encerra a conexão
        connection.close()

if __name__ == "__main__":
    main()
