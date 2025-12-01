"""
Testes de integração para emissão de NFe
ATENÇÃO: Estes testes fazem chamadas REAIS à API de homologação da FocusNFe

Execute apenas quando quiser testar a integração completa com a API.
Use: pytest tests/test_integracao_nfe.py -m integration
"""

import unittest
import os
import sys
from datetime import datetime
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from emissao_nfe.focusnfe.main import emitir_nfe, consultar_nfe, cancelar_nfe
import pytest


@pytest.mark.integration
class TestIntegracaoNFe(unittest.TestCase):
    """
    Testes de integração que fazem chamadas reais à API

    IMPORTANTE:
    - Estes testes usam o ambiente de homologação
    - Certifique-se de que o token está configurado corretamente no .env.test
    - Os testes podem demorar alguns segundos devido às chamadas de API
    """

    @classmethod
    def setUpClass(cls):
        """Configuração antes de todos os testes da classe"""
        # Carrega variáveis de ambiente
        from dotenv import load_dotenv
        env_test_path = os.path.join(os.path.dirname(__file__), '..', '.env.test')
        if os.path.exists(env_test_path):
            load_dotenv(env_test_path)

        # Verifica se o token está configurado
        cls.token = os.getenv('FOCUSNFE_TOKEN')
        if not cls.token:
            raise ValueError("Token não configurado. Configure FOCUSNFE_TOKEN no .env.test")

    def test_01_emitir_nfe_integracao(self):
        """
        Teste de integração: Emite uma NFe no ambiente de homologação
        Este teste faz uma chamada real à API
        """
        # Referência única para este teste
        referencia = f"teste_int_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Dados mínimos para emissão de NFe de teste
        # Nota: Em homologação, alguns campos podem ser fictícios
        dados_nfe = {
            "natureza_operacao": "Venda para testes de integracao",
            "tipo_documento": "1",
            "finalidade_emissao": "1",
            "cnpj_emitente": "51916585000125",  # CNPJ de teste
            "nome_emitente": "Empresa de Testes LTDA",
            "nome_fantasia_emitente": "Testes",
            "logradouro_emitente": "Rua de Teste",
            "numero_emitente": "123",
            "bairro_emitente": "Centro",
            "municipio_emitente": "Sao Paulo",
            "uf_emitente": "SP",
            "cep_emitente": "01000000",
            "inscricao_estadual_emitente": "123456789012",
            "regime_tributario_emitente": "1",
            "cnpj_destinatario": "07504505000132",  # CNPJ de teste
            "nome_destinatario": "Cliente de Teste",
            "logradouro_destinatario": "Rua do Cliente",
            "numero_destinatario": "456",
            "bairro_destinatario": "Centro",
            "municipio_destinatario": "Rio de Janeiro",
            "uf_destinatario": "RJ",
            "cep_destinatario": "20000000",
            "inscricao_estadual_destinatario": "ISENTO",
            "items": [
                {
                    "numero_item": "1",
                    "codigo_produto": "PROD001",
                    "descricao": "Produto de Teste",
                    "cfop": "5102",
                    "unidade_comercial": "UN",
                    "quantidade_comercial": "1.00",
                    "valor_unitario_comercial": "100.00",
                    "valor_total_bruto": "100.00",
                    "ncm": "84714900",
                    "icms_origem": "0",
                    "icms_situacao_tributaria": "102"
                }
            ]
        }

        # Emite a NFe
        resultado = emitir_nfe(dados_nfe, referencia)

        # Verificações
        print(f"\nResultado da emissão: {resultado}")

        # Armazena a referência para outros testes
        self.__class__.referencia_teste = referencia

        # Verifica se foi enviada com sucesso
        # Nota: Em homologação, pode retornar diferentes status
        self.assertIn('codigo', resultado)
        self.assertIn('referencia', resultado)
        self.assertEqual(resultado['referencia'], referencia)

    @pytest.mark.skip(reason="Executar apenas se test_01 foi bem-sucedido")
    def test_02_consultar_nfe_integracao(self):
        """
        Teste de integração: Consulta uma NFe emitida
        Este teste depende do test_01 ter sido executado
        """
        if not hasattr(self.__class__, 'referencia_teste'):
            self.skipTest("Teste de emissão não foi executado")

        # Aguarda alguns segundos para processamento
        time.sleep(3)

        # Consulta a NFe
        resultado = consultar_nfe(self.__class__.referencia_teste)

        print(f"\nResultado da consulta: {resultado}")

        # Verificações
        self.assertIn('codigo', resultado)
        self.assertIn('referencia', resultado)

    def test_03_consultar_nfe_inexistente(self):
        """
        Teste de integração: Consulta uma NFe que não existe
        """
        referencia_inexistente = "REF_NUNCA_EXISTIU_12345"

        # Consulta NFe inexistente
        resultado = consultar_nfe(referencia_inexistente)

        print(f"\nResultado da consulta (inexistente): {resultado}")

        # Deve retornar erro 404
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 404)

    @pytest.mark.skip(reason="Cancelamento só funciona para NFe autorizadas")
    def test_04_cancelar_nfe_integracao(self):
        """
        Teste de integração: Cancela uma NFe

        NOTA: Este teste está marcado para skip porque cancelamento
        só funciona para NFe já autorizadas pela SEFAZ
        """
        if not hasattr(self.__class__, 'referencia_teste'):
            self.skipTest("Teste de emissão não foi executado")

        # Justificativa de cancelamento
        justificativa = "Cancelamento para teste de integracao do sistema"

        # Cancela a NFe
        resultado = cancelar_nfe(self.__class__.referencia_teste, justificativa)

        print(f"\nResultado do cancelamento: {resultado}")

        # Verificações
        self.assertIn('codigo', resultado)


if __name__ == '__main__':
    # Para executar apenas estes testes de integração:
    # python -m pytest tests/test_integracao_nfe.py -v -s -m integration
    unittest.main()
