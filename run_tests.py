"""
Script para executar os testes com as configuracoes corretas
Carrega as variaveis de ambiente do arquivo .env.test antes de executar os testes
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variaveis de ambiente do arquivo .env.test
env_test_path = os.path.join(os.path.dirname(__file__), '.env.test')
if os.path.exists(env_test_path):
    load_dotenv(env_test_path)
    print(f"Variaveis de ambiente carregadas de: {env_test_path}")
    print(f"Token configurado: {os.getenv('FOCUSNFE_TOKEN')[:10]}...")
    print(f"Ambiente: {os.getenv('FOCUSNFE_AMBIENTE')}")
else:
    print(f"Aviso: Arquivo .env.test nao encontrado em {env_test_path}")

# Executa os testes usando pytest
import pytest

if __name__ == '__main__':
    # Argumentos passados ao pytest
    args = sys.argv[1:] if len(sys.argv) > 1 else ['-v', '--cov=EmissaoNFe', '--cov-report=term-missing']

    print("\n" + "="*60)
    print("Executando testes unitarios de Emissao de NFe")
    print("="*60 + "\n")

    # Executa pytest
    exit_code = pytest.main(args)

    sys.exit(exit_code)
