# server.py

import socket
import time

HOST = '127.0.0.1'
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

print(f"Servidor iniciado em {HOST}:{PORT}")
conn, addr = s.accept()

with conn:
    print('Conectado por', addr)
    while True:
        
        data = conn.recv(1024)
        if not data:
            break
        print('Dados recebidos:', data.decode('utf-8'))
        time.sleep(0.5)
