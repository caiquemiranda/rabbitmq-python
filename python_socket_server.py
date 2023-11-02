import socket

HOST = '127.0.0.1'
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

print("Esperando conexão...")
conn, addr = s.accept()

data = conn.recv(1024)
print("Recebido:", data.decode())

conn.close()
s.close()
