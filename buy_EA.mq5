#include <RabbitMqMql.mqh>

CRabbitMq mq;

input string RabbitMQ_Server = "seu_endereco_do_rabbitmq";
input int RabbitMQ_Port = 5672;
input string RabbitMQ_Username = "seu_usuario";
input string RabbitMQ_Password = "sua_senha";
input string RabbitMQ_Exchange = "nome_da_troca";
input string RabbitMQ_Queue = "nome_da_fila";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Inicialize a conexão com o RabbitMQ
   if (!mq.Init(RabbitMQ_Server, RabbitMQ_Port, RabbitMQ_Username, RabbitMQ_Password))
   {
      Print("Erro ao inicializar a conexão com o RabbitMQ");
      return(INIT_FAILED);
   }

   // Declare a fila
   mq.DeclareQueue(RabbitMQ_Queue);

   // Inicie a assinatura de mensagens
   mq.Subscribe(RabbitMQ_Queue);

   // Execute o loop de negociação
   EventSetMillisecondTimer(1000); // Defina um temporizador para verificar periodicamente

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Libere a conexão com o RabbitMQ
   mq.Deinit();
}

//+------------------------------------------------------------------+
//| Timer function to receive and interpret messages                |
//+------------------------------------------------------------------+
void OnTimer()
{
   // Receba mensagens do RabbitMQ
   string receivedMessage;
   if (mq.ReceiveMessage(RabbitMQ_Queue, receivedMessage))
   {
      Print("Mensagem recebida: ", receivedMessage);
      
      // Interprete a mensagem e execute uma ordem de compra
      if (StringFind(receivedMessage, "comprar") >= 0)
      {
         double price = MarketInfo("EURUSD", MODE_ASK);
         double lotSize = 0.1;
         OrderSend("EURUSD", OP_BUY, lotSize, price, 2, 0, 0, "", 0, clrNONE);
         Print("Ordem de compra executada: ", lotSize, " lotes a ", price);
      }
   }
   else
   {
      Print("Erro ao receber mensagem: ", mq.ErrorDescription());
   }
}

//+------------------------------------------------------------------+
