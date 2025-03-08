import streamlit as st
import socket
import threading
import time
from datetime import datetime
import json
import os

# Configuração da página Streamlit
st.set_page_config(page_title="Receptor de Mensagens", page_icon="📨")

# Configuração do layout
st.title("📨 Receptor de Mensagens")

# Variáveis globais
HOST = 'localhost'
PORT = 5001
TEMP_FILE = "mensagens_temp.json"

# Função para limpar todas as mensagens
def limpar_mensagens():
    """Limpa todas as mensagens do sistema"""
    # Limpar todos os estados relacionados a mensagens
    for key in list(st.session_state.keys()):
        if key in ['mensagens', 'fila_mensagens']:
            del st.session_state[key]
    
    # Limpar arquivo temporário
    try:
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
        # Criar arquivo vazio
        with open(TEMP_FILE, 'w') as f:
            json.dump([], f)
        print("Sistema de mensagens reinicializado")
    except Exception as e:
        print(f"Erro ao limpar mensagens: {e}")

# Inicialização do estado
if 'mensagens' not in st.session_state:
    st.session_state['mensagens'] = []
if 'status' not in st.session_state:
    st.session_state['status'] = "🟢 Servidor ativo"
if 'ultima_limpeza' not in st.session_state:
    st.session_state['ultima_limpeza'] = time.time()

def carregar_mensagens_temp():
    """Carrega mensagens do arquivo temporário"""
    try:
        if os.path.exists(TEMP_FILE):
            with open(TEMP_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        return []
    return []

def salvar_mensagem_temp(msg):
    """Salva mensagem no arquivo temporário"""
    try:
        mensagens = carregar_mensagens_temp()
        if msg not in mensagens:  # Evita duplicatas
            mensagens.append(msg)
            with open(TEMP_FILE, 'w') as f:
                json.dump(mensagens, f)
    except Exception as e:
        print(f"Erro ao salvar mensagem: {e}")

def adicionar_mensagem(msg):
    """Adiciona mensagem ao sistema"""
    if msg != "teste_conexao":  # Ignora mensagens de teste de conexão
        timestamp = datetime.now().strftime("%H:%M:%S")
        mensagem_formatada = f"[{timestamp}] {msg}"
        salvar_mensagem_temp(mensagem_formatada)
        print(f"Mensagem salva: {mensagem_formatada}")

def receber_mensagens():
    """Função que roda em thread separada para receber mensagens"""
    print("Iniciando servidor de socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((HOST, PORT))
        sock.listen(1)
        print(f"Servidor escutando em {HOST}:{PORT}")
        
        while True:
            try:
                conn, addr = sock.accept()
                print(f"Conexão recebida de {addr}")
                with conn:
                    data = conn.recv(1024)
                    if data:
                        mensagem = data.decode('utf-8')
                        print(f"Mensagem recebida: {mensagem}")
                        adicionar_mensagem(mensagem)
            except Exception as e:
                print(f"Erro na conexão: {e}")
                time.sleep(0.1)
    except Exception as e:
        print(f"Erro fatal no servidor: {e}")
        st.session_state['status'] = f"🔴 Erro no servidor: {str(e)}"
    finally:
        sock.close()

# Status do servidor
st.write(st.session_state.get('status', ""))

# Processar mensagens pendentes
if time.time() - st.session_state['ultima_limpeza'] > 0.5:  # Evita processamento muito frequente
    mensagens_temp = carregar_mensagens_temp()
    if mensagens_temp:
        st.session_state['mensagens'] = mensagens_temp.copy()  # Usa cópia direta do arquivo
    st.session_state['ultima_limpeza'] = time.time()

# Container para mensagens com scroll
with st.container():
    # Área de mensagens
    if len(st.session_state['mensagens']) == 0:
        st.info("Aguardando mensagens... (Servidor na porta 5001)")
    else:
        for msg in reversed(st.session_state['mensagens']):
            st.text(msg)

# Botões de controle em colunas
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar Mensagens"):
        limpar_mensagens()
        st.session_state['mensagens'] = []  # Garante que as mensagens sejam limpas
        time.sleep(0.1)  # Pequena pausa para garantir a limpeza
        st.rerun()
with col2:
    if st.button("🔄 Atualizar"):
        st.rerun()

# Iniciar thread de recebimento
if 'receiver_thread' not in st.session_state:
    receiver_thread = threading.Thread(target=receber_mensagens, daemon=True)
    receiver_thread.start()
    st.session_state['receiver_thread'] = receiver_thread

# Atualização automática mais frequente
time.sleep(0.1)
st.rerun() 