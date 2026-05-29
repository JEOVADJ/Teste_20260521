# IoT Dashboard - Sistema Moderno de Monitoramento

Um sistema completo e profissional para monitoramento de dispositivos IoT em tempo real com dashboard interativo.

## 🎯 Características

- ✅ **Dashboard Interativo**: Interface moderna e responsiva
- ✅ **Gráficos em Tempo Real**: Visualização de dados com Chart.js
- ✅ **WebSocket**: Comunicação em tempo real via Socket.io
- ✅ **MQTT Integration**: Suporte a sensores e dispositivos MQTT
- ✅ **Banco de Dados Robusto**: MySQL com tabelas otimizadas
- ✅ **API RESTful**: Endpoints completos para integração
- ✅ **Tema Escuro**: Suporte a modo escuro/claro
- ✅ **Responsivo**: Funciona em desktop, tablet e mobile
- ✅ **Estatísticas**: Min, Max, Média das últimas 24h
- ✅ **Histórico**: Visualização e export de dados históricos

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- MySQL 5.7+ ou MariaDB
- Node.js (opcional, para desenvolvimento)
- MQTT Broker (mosquitto ou similar)

### Backend

1. **Instalar dependências Python**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configurar variáveis de ambiente**:
```bash
cp .env.example .env
# Editar .env com suas configurações
```

3. **Iniciar o servidor Flask**:
```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

### Frontend

O frontend já está incluído no projeto. Acesse `http://localhost:5000` em seu navegador.

## 📦 Estrutura do Projeto

```
project/
├── backend/
│   ├── app.py              # Aplicação Flask principal
│   ├── config.py           # Configurações
│   ├── db.py               # Operações com banco de dados
│   ├── mqtt_subscriber.py  # Subscriber MQTT
│   ├── requirements.txt    # Dependências Python
│   └── .env.example        # Exemplo de variáveis de ambiente
├── frontend/
│   ├── index.html          # HTML principal
│   ├── app.js              # JavaScript do dashboard
│   └── styles.css          # Estilos CSS
└── README.md               # Este arquivo
```

## 🔌 API Endpoints

### Sistemas
- `GET /api/systems` - Listar todos os sistemas
- `GET /api/health` - Verificar status do servidor

### Dispositivos
- `GET /api/devices` - Listar dispositivos
- `GET /api/devices?system_id=ID` - Listar dispositivos por sistema
- `GET /api/devices/<id>/latest` - Última leitura de um dispositivo

### Leituras
- `GET /api/readings?device_id=ID` - Listar leituras
- `GET /api/readings?device_id=ID&start=DATE&end=DATE` - Leituras com filtro de data
- `GET /api/readings/stats?device_id=ID&hours=24` - Estatísticas
- `POST /api/readings` - Adicionar nova leitura

## 📊 Formato de Dados MQTT

### JSON
```json
{
  "system": "SistemaA",
  "device_id": "sensor_temperatura",
  "value": 23.5,
  "timestamp": "2024-05-28T10:30:00Z"
}
```

### CSV
```
23.5,sensor_temperatura,SistemaA,2024-05-28T10:30:00Z
```

## 🎨 Personalização

### Variáveis CSS
Edit `frontend/styles.css`:
```css
:root {
  --primary: #667eea;      /* Cor primária */
  --secondary: #764ba2;    /* Cor secundária */
  --success: #48bb78;      /* Cor de sucesso */
  /* ... outras cores ... */
}
```

## 📱 Responsividade

O dashboard é totalmente responsivo:
- **Desktop**: Layout completo com sidebar
- **Tablet**: Menu retrátil
- **Mobile**: Interface otimizada

## 🔐 Segurança

Para produção:

1. Configure `SECRET_KEY` em `.env`
2. Use variáveis de ambiente para credenciais
3. Configure HTTPS/SSL
4. Ative autenticação no MQTT broker
5. Configure firewall adequadamente

## 🐛 Troubleshooting

### Conexão com banco de dados
```bash
# Verificar se MySQL está rodando
mysql -u root -p
```

### Erro de módulo Python
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### MQTT não conectando
```bash
# Verificar se mosquitto está rodando
mosquitto -v
```

## 📝 Log

Os logs são salvos no console. Para arquivo de log, configure em `config.py`.

## 🤝 Contribuindo

Contribuições são bem-vindas! Faça um fork, crie uma branch e envie um pull request.

## 📄 Licença

Este projeto está sob licença MIT.

## 📞 Suporte

Para questões ou problemas, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para monitoramento IoT moderno**
