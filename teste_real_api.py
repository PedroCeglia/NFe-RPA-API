"""
Script para fazer uma chamada REAL à API FocusNFe de homologação
Este script irá registrar uma requisição no painel da FocusNFe
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('.env.test')

from emissao_nfe.focusnfe.main import emitir_nfe, consultar_nfe

print("="*70)
print("TESTE REAL - Chamada à API FocusNFe de Homologação")
print("="*70)

# Verifica configuração
token = os.getenv('FOCUSNFE_TOKEN')
ambiente = os.getenv('FOCUSNFE_AMBIENTE')

print(f"\nConfiguração:")
print(f"  Token: {token[:15]}...")
print(f"  Ambiente: {ambiente}")
print(f"  URL: https://homologacao.focusnfe.com.br/v2/nfe")

# Gera referência única
referencia = f"teste_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"\nReferência da NFe: {referencia}")

# Dados mínimos para teste
# Fonte: https://focusnfe.com.br/doc/#emissao_nfe
dados_nfe = {
    "natureza_operacao": "Venda de mercadoria - TESTE",
    "tipo_documento": "1",
    "data_emissao":"2025-11-27",
    "data_entrada_saida":"2025-11-27",
    "finalidade_emissao": "1",
    "cnpj_emitente": "60849324000120",
    "nome_emitente": "PEDRO SILVEIRA CEGLIA DESENVOLVIMENTO DE SOFTWARE LTDA",
    "nome_fantasia_emitente": "DevCeglia",
    "logradouro_emitente": "RUA PAIS LEME",
    "numero_emitente": "215",
    "bairro_emitente": "PINHEIROS",
    "municipio_emitente": "Sao Paulo",
    "uf_emitente": "SP",
    "cep_emitente": "05424-150",
    "inscricao_estadual_emitente": "16600367000293",
    "regime_tributario_emitente": "1",
    "cnpj_destinatario": "07504505000132",
    "nome_destinatario": "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL",
    "logradouro_destinatario": "Rua Cliente",
    "numero_destinatario": "456",
    "bairro_destinatario": "Centro",
    "municipio_destinatario": "Rio de Janeiro",
    "uf_destinatario": "RJ",
    "cep_destinatario": "20000000",
    "inscricao_estadual_destinatario": "ISENTO",
    "modalidade_frete":"0",
    "items": [
        {
            "numero_item": "1",
            "codigo_produto": "PROD001",
            "descricao": "NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL",
            "cfop": "5102",
            "unidade_comercial": "UN",
            "quantidade_comercial": "1.00",
            "valor_unitario_comercial": "100.00",
            "valor_unitario_tributavel": "100.00",
            "unidade_tributavel": "UN",
            "quantidade_tributavel": "1.00",
            "valor_total_bruto": "100.00",
            "ncm": "84714900",
            "icms_origem": "0",
            "icms_situacao_tributaria": "102",
            "codigo_ncm":"12345678"
        }
    ]
}

print("\n" + "="*70)
print("Enviando NFe para API FocusNFe...")
print("="*70)

# Faz a chamada REAL
resultado = emitir_nfe(dados_nfe, referencia)

print("\nRESPOSTA DA API:")
print("-"*70)
print(f"Sucesso: {resultado.get('sucesso')}")
print(f"Código HTTP: {resultado.get('codigo')}")
print(f"Mensagem: {resultado.get('mensagem')}")
print(f"Ambiente: {resultado.get('ambiente')}")
print(f"Referência: {resultado.get('referencia')}")

if 'dados' in resultado:
    print("\nDados retornados:")
    import json
    print(json.dumps(resultado['dados'], indent=2, ensure_ascii=False))

if 'erro' in resultado:
    print("\nErro retornado:")
    import json
    print(json.dumps(resultado['erro'], indent=2, ensure_ascii=False))

print("\n" + "="*70)
print("AGORA VERIFIQUE O PAINEL DA FOCUSNFE!")
print("="*70)
print(f"\nVocê deve ver uma requisição com a referência: {referencia}")
print("Acesse: https://homologacao.focusnfe.com.br/")
print("\nSe não aparecer, pode haver um problema com:")
print("  1. Token de homologação")
print("  2. Dados da NFe inválidos")
print("  3. Configuração da conta FocusNFe")
print("="*70)
