"""
Gerador de dados de teste para o sistema IoT
Simula leituras de sensores
"""

import requests
import json
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:5000"

# Configuração de sensores simulados
SENSORS = [
    {"system": "SistemaA", "device": "temperatura_sala", "min": 15, "max": 30},
    {"system": "SistemaA", "device": "umidade_sala", "min": 30, "max": 80},
    {"system": "SistemaB", "device": "temperatura_externa", "min": 0, "max": 40},
    {"system": "SistemaB", "device": "pressao", "min": 900, "max": 1100},
]

def generate_reading(sensor):
    """Gera uma leitura simulada"""
    value = random.uniform(sensor['min'], sensor['max'])
    return {
        "system": sensor['system'],
        "device_id": sensor['device'],
        "value": round(value, 2),
        "timestamp": datetime.now().isoformat()
    }

def send_reading(reading):
    """Envia leitura para a API"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/readings",
            json=reading,
            timeout=5
        )
        if response.status_code in [200, 201]:
            print(f"✅ {reading['system']}/{reading['device_id']}: {reading['value']}")
            return True
        else:
            print(f"❌ Erro ao enviar {reading['device_id']}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 50)
    print("  Gerador de Dados de Teste IoT")
    print("=" * 50)
    print(f"Gerando dados para {len(SENSORS)} sensores\n")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n--- Ciclo {iteration} ({datetime.now().strftime('%H:%M:%S')}) ---")
            
            for sensor in SENSORS:
                reading = generate_reading(sensor)
                send_reading(reading)
            
            print("Aguardando 30 segundos para próximo ciclo...")
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n\n✅ Gerador parado")

if __name__ == "__main__":
    main()
