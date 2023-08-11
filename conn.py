"""import psutil

def listar_conexoes():
    # Obtém as conexões de rede ativas
    conexoes = psutil.net_connections(kind='inet')

    print("Endereços IP e portas em uso:")
    for conexao in conexoes:
        endereco_local = conexao.laddr
        endereco_remoto = conexao.raddr
        status = conexao.status
        print(f"Endereço local: {endereco_local.ip}:{endereco_local.port} | "
              f"Endereço remoto: {endereco_remoto.ip if endereco_remoto else 'N/A'}:{endereco_remoto.port if endereco_remoto else 'N/A'} | "
              f"Status: {status}")

if __name__ == "__main__":
    listar_conexoes()
"""
import psutil
import csv

def gerar_csv(conexoes, nome_arquivo):
    with open(nome_arquivo, 'w', newline='') as arquivo_csv:
        campos = ['Endereco_Local', 'Porta_Local', 'Endereco_Remoto', 'Porta_Remota', 'Status']
        escritor_csv = csv.writer(arquivo_csv)
        escritor_csv.writerow(campos)

        for conexao in conexoes:
            endereco_local = f"{conexao.laddr.ip}:{conexao.laddr.port}"
            endereco_remoto = f"{conexao.raddr.ip if conexao.raddr else 'N/A'}:{conexao.raddr.port if conexao.raddr else 'N/A'}"
            status = conexao.status
            linha = [endereco_local, endereco_remoto, status]
            escritor_csv.writerow(linha)

def main():
    conexoes = psutil.net_connections(kind='inet')
    nome_arquivo = 'conexoes_3.csv'

    gerar_csv(conexoes, nome_arquivo)
    print(f"Arquivo CSV '{nome_arquivo}' gerado com sucesso!")

if __name__ == "__main__":
    main()
