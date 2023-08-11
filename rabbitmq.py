import pika

# Configurações do RabbitMQ
rabbitmq_server = 'seu_endereco_do_rabbitmq'
rabbitmq_port = 5672
rabbitmq_username = 'seu_usuario'
rabbitmq_password = 'sua_senha'
rabbitmq_exchange = 'nome_da_troca'
rabbitmq_routing_key = 'chave_de_rota'

# Conectando ao RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_username, 
                                    rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_server, 
                                                               port=rabbitmq_port, 
                                                               credentials=credentials))
channel = connection.channel()

# Enviando uma mensagem
message = 'Olá, RabbitMQ!'
channel.basic_publish(exchange=rabbitmq_exchange, 
                      routing_key=rabbitmq_routing_key,
                      body=message)
print(f'Mensagem enviada: {message}')

# Fechando a conexão
connection.close()
