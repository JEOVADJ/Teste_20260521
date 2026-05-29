# 🚀 IoT Dashboard - Guia de Configuração Completo

> Sistema moderno de monitoramento IoT com dashboard interativo em tempo real

## 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Instalação](#instalação)
3. [Configuração](#configuração)
4. [Inicialização](#inicialização)
5. [Testes](#testes)
6. [Troubleshooting](#troubleshooting)

---

## ✅ Pré-requisitos

### Componentes Necessários
- **Python**: 3.8 ou superior
- **MySQL**: 5.7+ ou MariaDB 10.3+
- **MQTT Broker**: mosquitto ou similar (opcional)
- **Git**: Para versionamento (opcional)

### Verificar Instalações

```bash
# Python
python --version

# MySQL
mysql --version

# mosquitto (opcional)
mosquitto --version
```

---

## 📦 Instalação

### Passo 1: Preparar Ambiente

```bash
# Abrir PowerShell como Administrador (Windows) ou terminal (Linux/Mac)
cd /caminho/do/projeto

# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Passo 2: Instalar Dependências

```bash
# Navegar até backend
cd backend

# Instalar packages Python
pip install --upgrade pip
pip install -r requirements.txt

# Voltar ao diretório raiz
cd ..
```

### Passo 3: Configurar Banco de Dados

#### MySQL

```sql
-- Abrir MySQL
mysql -u root -p

-- Criar banco de dados
CREATE DATABASE iot_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário (opcional)
CREATE USER 'iot_user'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON iot_monitor.* TO 'iot_user'@'localhost';
FLUSH PRIVILEGES;

-- Verificar
SHOW DATABASES;
USE iot_monitor;
SHOW TABLES;
```

---

## ⚙️ Configuração

### Arquivo .env

```bash
# Copiar arquivo de exemplo
cp backend/.env.example backend/.env

# Editar arquivo .env
# Windows: notepad backend\.env
# Linux/Mac: nano backend/.env
```

### Exemplo de .env

```ini
# ============ DATABASE ============
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=iot_user
MYSQL_PASSWORD=senha_segura
MYSQL_DB=iot_monitor

# ============ MQTT ============
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=devices/#

# ============ FLASK ============
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui

# ============ LOGGING ============
LOG_LEVEL=INFO
```

### Configurar MQTT (Opcional)

```bash
# Instalar mosquitto (Windows)
# Download: https://mosquitto.org/download/

# Ou via chocolatey:
choco install mosquitto

# Iniciar mosquitto
mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf"

# Linux/Mac com Homebrew:
brew install mosquitto
mosquitto
```

---

## 🎯 Inicialização

### Iniciar o Servidor

```bash
# Ativar ambiente virtual (se não estiver ativo)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Navegar ao backend
cd backend

# Iniciar Flask
python app.py
```

### Saída Esperada

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
```

### Acessar o Dashboard

- **URL**: http://localhost:5000
- **Porta**: 5000
- **Protocolo**: HTTP (HTTPS em produção)

---

## 🧪 Testes

### Teste 1: Verificar Saúde do Sistema

```bash
# Em outro terminal
cd backend

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Rodar teste de API
python test_api.py
```

Resultado esperado:
```
✅ Health check OK
✅ Sistemas encontrados: 0
```

### Teste 2: Gerar Dados de Teste

```bash
# Terminal 1: Servidor rodando (como acima)

# Terminal 2: Gerar dados
cd backend
python test_data_generator.py
```

Este script vai:
- Criar 4 sensores simulados
- Enviar leituras a cada 30 segundos
- Mostrar dados no dashboard em tempo real

### Teste 3: Verificar via cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Listar sistemas
curl http://localhost:5000/api/systems

# Listar dispositivos
curl http://localhost:5000/api/devices
```

---

## 📊 Exemplo de Fluxo Completo

### 1. Iniciar o Servidor
```bash
cd backend
python app.py
```

### 2. Em Outro Terminal - Gerar Dados
```bash
cd backend
python test_data_generator.py
```

### 3. Acessar Dashboard
- Abra http://localhost:5000 no navegador
- Selecione um sistema e dispositivo
- Veja os dados em tempo real!

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"

```bash
# Certificar que está no ambiente virtual
venv\Scripts\activate

# Reinstalar dependências
pip install -r backend/requirements.txt
```

### Erro: "Access denied for user 'root'@'localhost'"

```bash
# Verificar credenciais MySQL em .env
# Ou conectar ao MySQL e verificar permissões
mysql -u root -p

# Mostrar usuários
SELECT user, host FROM mysql.user;

# Verificar permissões
SHOW GRANTS FOR 'seu_usuario'@'localhost';
```

### Erro: "MQTT connection refused"

```bash
# Se MQTT é obrigatório, iniciar mosquitto
mosquitto

# Se não é obrigatório, o sistema continua funcionando
# sem dados de sensores
```

### Porta 5000 já está em uso

```bash
# Mudar porta em .env
FLASK_PORT=5001

# Ou liberar a porta
# Windows (PowerShell como Admin):
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

### Erro de Conexão ao Banco de Dados

```bash
# Verificar se MySQL está rodando
# Windows: Services -> MySQL
# Linux: sudo systemctl status mysql
# Mac: brew services list

# Ou via terminal
mysql -u root -p -e "SELECT 1"
```

---

## 🔒 Segurança - Checklist para Produção

- [ ] Mudar `SECRET_KEY` em `.env`
- [ ] Configurar HTTPS/SSL
- [ ] Usar senha forte para MySQL
- [ ] Configurar autenticação MQTT
- [ ] Limitar acesso por firewall
- [ ] Fazer backup regular do banco de dados
- [ ] Monitorar logs de erro
- [ ] Usar ambiente virtual em produção
- [ ] Configurar log de auditoria

---

## 📚 Recursos Adicionais

### Documentação
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MQTT Protocol](https://mqtt.org/)
- [Chart.js Documentation](https://www.chartjs.org/)

### Comandos Úteis

```bash
# Ver versões de pacotes
pip freeze

# Atualizar um pacote
pip install --upgrade flask

# Gerar arquivo requirements
pip freeze > requirements.txt

# Ver conectados ao MySQL
mysql -u root -p -e "SHOW PROCESSLIST;"

# Exportar banco de dados
mysqldump -u root -p iot_monitor > backup.sql

# Importar banco de dados
mysql -u root -p iot_monitor < backup.sql
```

---

## ✨ Próximos Passos

1. **Customizar Dashboard**: Editar `frontend/styles.css` e `frontend/app.js`
2. **Adicionar Autenticação**: Implementar login de usuários
3. **Integrar Mais Sensores**: Configurar novos tópicos MQTT
4. **Deploy**: Usar Docker ou servidor em nuvem
5. **Alertas**: Implementar sistema de notificações

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique este guia de troubleshooting
2. Consulte os logs do terminal
3. Verifique o arquivo `.env`
4. Teste a conectividade de cada componente

---

**Desenvolvido com ❤️ para IoT moderno**

Versão: 1.0.0
Última atualização: 28 de maio de 2026
