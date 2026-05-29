"""
Script de teste para o sistema IoT Dashboard
Testa conexões, APIs e funcionalidades básicas
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"
TIMEOUT = 5

def test_health():
    """Testa endpoint de saúde"""
    print("\n🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print(f"   Certifique-se de que o servidor está rodando em {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_api_systems():
    """Testa API de sistemas"""
    print("\n🔍 Testando /api/systems...")
    try:
        response = requests.get(f"{BASE_URL}/api/systems", timeout=TIMEOUT)
        if response.status_code == 200:
            systems = response.json()
            print(f"✅ Sistemas encontrados: {len(systems)}")
            for sys in systems:
                print(f"   - {sys['name']} (ID: {sys['id']})")
            return systems
        else:
            print(f"❌ Erro: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def test_api_devices(system_id=None):
    """Testa API de dispositivos"""
    print("\n🔍 Testando /api/devices...")
    try:
        url = f"{BASE_URL}/api/devices"
        if system_id:
            url += f"?system_id={system_id}"
        
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Dispositivos encontrados: {len(devices)}")
            for dev in devices[:5]:  # Mostrar apenas os 5 primeiros
                print(f"   - {dev['identifier']} (ID: {dev['id']})")
            return devices
        else:
            print(f"❌ Erro: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def test_api_readings(device_id):
    """Testa API de leituras"""
    print(f"\n🔍 Testando /api/readings (device_id={device_id})...")
    try:
        url = f"{BASE_URL}/api/readings?device_id={device_id}&limit=10"
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            readings = response.json()
            print(f"✅ Leituras encontradas: {len(readings)}")
            for reading in readings[:3]:  # Mostrar apenas as 3 primeiras
                print(f"   - {reading['ts']}: {reading['value']}")
            return readings
        elif response.status_code == 404:
            print("⚠️  Nenhuma leitura encontrada")
            return []
        else:
            print(f"❌ Erro: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def test_add_reading(device_id):
    """Testa adição de nova leitura"""
    print(f"\n🔍 Testando POST /api/readings...")
    try:
        # Simular uma leitura
        payload = {
            "device_id": device_id,
            "value": 25.5,
            "ts": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{BASE_URL}/api/readings",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            print("✅ Leitura adicionada com sucesso")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal de testes"""
    print("=" * 50)
    print("  TESTES DO SISTEMA IOT DASHBOARD")
    print("=" * 50)
    
    # Teste de conexão
    if not test_health():
        print("\n❌ Servidor não está respondendo")
        sys.exit(1)
    
    # Teste de sistemas
    systems = test_api_systems()
    if not systems:
        print("\n⚠️  Nenhum sistema encontrado. Criando dados de teste...")
        print("   Envie dados via MQTT ou pela API POST /api/readings")
    else:
        system_id = systems[0]['id']
        
        # Teste de dispositivos
        devices = test_api_devices(system_id)
        if devices:
            device_id = devices[0]['id']
            
            # Teste de leituras
            test_api_readings(device_id)
            
            # Teste de adição
            test_add_reading(device_id)
    
    print("\n" + "=" * 50)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 50)
    print("\nAcesse o dashboard em: http://localhost:5000")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
