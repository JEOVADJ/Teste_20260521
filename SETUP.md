Setup rápido do projeto de monitoramento IoT

1) Prepare MySQL
- Criar banco e tabelas: executar `backend/models.sql` no MySQL.

2) Configurar variáveis de ambiente
- Criar arquivo `.env` na pasta `backend` com as variáveis:

  MYSQL_HOST=localhost
  MYSQL_PORT=3306
  MYSQL_USER=root
  MYSQL_PASSWORD=senha
  MYSQL_DB=iot_monitor
  MQTT_BROKER=localhost
  MQTT_PORT=1883

3) Instalar dependências Python

```bash
python -m venv .venv
source .venv/bin/activate   # ou .\.venv\Scripts\activate no Windows
pip install -r backend/requirements.txt
```

4) Executar backend (inicia API + subscriber MQTT)

```bash
python backend/app.py
```

5) Abrir dashboard
- Acessar http://localhost:5000 no navegador.

6) Enviar amostra MQTT (exemplo usando mosquitto_pub)

JSON:
```bash
mosquitto_pub -h localhost -t devices/SistemaA/Dispositivo1 -m '{"system":"SistemaA","device_id":"Dispositivo1","value":23.5}'
```

Formato CSV simples: `value,device,system,ts`
