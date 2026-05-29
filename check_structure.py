#!/usr/bin/env python3
"""
Verificador de Estrutura do Projeto IoT Dashboard
Lista todos os arquivos e verifica integridade
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

FILES_STRUCTURE = {
    "Frontend": [
        "frontend/index.html",
        "frontend/app.js",
        "frontend/styles.css",
    ],
    "Backend": [
        "backend/app.py",
        "backend/config.py",
        "backend/db.py",
        "backend/mqtt_subscriber.py",
        "backend/requirements.txt",
        "backend/.env.example",
    ],
    "Testes": [
        "backend/test_api.py",
        "backend/test_data_generator.py",
    ],
    "Documentação": [
        "README.md",
        "SETUP.md",
        "GUIA_COMPLETO.md",
        "FULL_README.md",
        "RESUMO_PROJETO.md",
        "check_structure.py",
    ],
}

def check_structure():
    """Verifica a estrutura do projeto"""
    print("=" * 60)
    print("  IoT Dashboard - Verificador de Estrutura")
    print("=" * 60)
    
    total_files = 0
    found_files = 0
    
    for category, files in FILES_STRUCTURE.items():
        print(f"\n📁 {category}")
        print("-" * 60)
        
        for file in files:
            filepath = PROJECT_ROOT / file
            total_files += 1
            
            if filepath.exists():
                size = filepath.stat().st_size
                size_kb = size / 1024
                print(f"✅ {file:<35} ({size_kb:>7.1f} KB)")
                found_files += 1
            else:
                print(f"❌ {file:<35} (NÃO ENCONTRADO)")
    
    print("\n" + "=" * 60)
    print(f"Status: {found_files}/{total_files} arquivos encontrados")
    
    if found_files == total_files:
        print("✅ ESTRUTURA COMPLETA E VÁLIDA!")
    else:
        print(f"⚠️  Faltam {total_files - found_files} arquivos")
    
    print("=" * 60)
    
    return found_files == total_files

def get_statistics():
    """Calcula estatísticas do projeto"""
    print("\n📊 Estatísticas do Projeto")
    print("-" * 60)
    
    total_lines = 0
    total_size = 0
    
    for category, files in FILES_STRUCTURE.items():
        if category == "Documentação":
            continue
        
        for file in files:
            filepath = PROJECT_ROOT / file
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                
                size = filepath.stat().st_size
                total_size += size
    
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"Linhas de Código: {total_lines:,}")
    print(f"Tamanho Total: {total_size_mb:.2f} MB")
    print(f"Arquivos de Código: {sum(len(v) for k, v in FILES_STRUCTURE.items() if k != 'Documentação')}")
    print(f"Documentação: {len(FILES_STRUCTURE['Documentação'])} arquivos")

if __name__ == "__main__":
    check_structure()
    get_statistics()
    
    print("\n🚀 Para iniciar o projeto:")
    print("   1. python -m venv venv")
    print("   2. venv\\Scripts\\activate  (Windows) ou source venv/bin/activate")
    print("   3. pip install -r backend/requirements.txt")
    print("   4. cp backend\\.env.example backend\\.env")
    print("   5. python backend/app.py")
    print("   6. Abrir http://localhost:5000")
