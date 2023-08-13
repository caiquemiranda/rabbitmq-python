import pika
import json

# Configurações do RabbitMQ
rabbitmq_server = 'seu_endereco_do_rabbitmq'
rabbitmq_port = 5672
rabbitmq_username = 'seu_usuario'
rabbitmq_password = 'sua_senha'
rabbitmq_exchange = 'nome_da_troca'
rabbitmq_routing_key = 'chave_de_rota'

# Dados da ordem de compra
order_data = {
    'symbol': 'EURUSD',
    'type': 'buy',
    'volume': 0.1,
    'price': 1.2000
}

# Conectando ao RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_server, port=rabbitmq_port, credentials=credentials))
channel = connection.channel()

# Enviando a ordem de compra
message = json.dumps(order_data)
channel.basic_publish(exchange=rabbitmq_exchange, routing_key=rabbitmq_routing_key, body=message)
print(f'Ordem de compra enviada: {message}')

# Fechando a conexão
connection.close()
