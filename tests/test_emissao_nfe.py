"""
Testes unitários para o módulo de emissão de NFe
Utiliza mocks para simular chamadas à API FocusNFe
"""

import unittest
from unittest.mock import patch, Mock
import os
import sys

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from emissao_nfe.focusnfe.main import emitir_nfe, consultar_nfe, cancelar_nfe, get_api_config


class TestEmissaoNFe(unittest.TestCase):
    """Testes para a função emitir_nfe"""

    def setUp(self):
        """Configuração antes de cada teste"""
        # Define variáveis de ambiente para teste
        os.environ['FOCUSNFE_TOKEN'] = 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y'
        os.environ['FOCUSNFE_AMBIENTE'] = 'homologacao'

    @patch('emissao_nfe.focusnfe.main.requests.post')
    def test_emitir_nfe_sucesso(self, mock_post):
        """Testa emissão de NFe com sucesso"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'autorizado',
            'chave_nfe': '12345678901234567890123456789012345678901234',
            'numero': '000000001',
            'serie': '1'
        }
        mock_post.return_value = mock_response

        # Dados da NFe
        dados_nfe = {
            'natureza_operacao': 'Venda de mercadoria',
            'tipo_documento': 1,
            'finalidade_emissao': 1,
            'cnpj_emitente': '12345678000190'
        }

        # Executa a função
        resultado = emitir_nfe(dados_nfe, 'REF_TESTE_001')

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 200)
        self.assertEqual(resultado['referencia'], 'REF_TESTE_001')
        self.assertEqual(resultado['ambiente'], 'homologacao')
        self.assertIn('dados', resultado)
        self.assertEqual(resultado['dados']['status'], 'autorizado')

    @patch('emissao_nfe.focusnfe.main.requests.post')
    def test_emitir_nfe_erro_validacao(self, mock_post):
        """Testa emissão de NFe com erro de validação"""
        # Mock da resposta da API com erro
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            'erro': 'erro_validacao',
            'mensagem': 'CNPJ do emitente é obrigatório'
        }
        mock_response.text = '{"erro":"erro_validacao"}'
        mock_post.return_value = mock_response

        # Dados da NFe inválidos
        dados_nfe = {
            'natureza_operacao': 'Venda de mercadoria'
        }

        # Executa a função
        resultado = emitir_nfe(dados_nfe, 'REF_TESTE_002')

        # Verificações
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 422)
        self.assertIn('erro', resultado)

    @patch('emissao_nfe.focusnfe.main.requests.post')
    def test_emitir_nfe_sem_referencia(self, mock_post):
        """Testa emissão de NFe sem fornecer referência (deve ser gerada automaticamente)"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'autorizado'}
        mock_post.return_value = mock_response

        dados_nfe = {'natureza_operacao': 'Venda de mercadoria'}

        # Executa sem referência
        resultado = emitir_nfe(dados_nfe)

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertIn('referencia', resultado)
        self.assertTrue(resultado['referencia'].startswith('nfe_'))

    def test_emitir_nfe_sem_token(self):
        """Testa emissão de NFe sem token configurado"""
        # Remove o token
        os.environ.pop('FOCUSNFE_TOKEN', None)

        dados_nfe = {'natureza_operacao': 'Venda de mercadoria'}

        # Executa a função
        resultado = emitir_nfe(dados_nfe, 'REF_TESTE_003')

        # Verificações
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 500)
        self.assertIn('Token', resultado['mensagem'])

        # Restaura o token
        os.environ['FOCUSNFE_TOKEN'] = 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y'


class TestConsultarNFe(unittest.TestCase):
    """Testes para a função consultar_nfe"""

    def setUp(self):
        """Configuração antes de cada teste"""
        os.environ['FOCUSNFE_TOKEN'] = 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y'
        os.environ['FOCUSNFE_AMBIENTE'] = 'homologacao'

    @patch('emissao_nfe.focusnfe.main.requests.get')
    def test_consultar_nfe_sucesso(self, mock_get):
        """Testa consulta de NFe existente"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'autorizado',
            'chave_nfe': '12345678901234567890123456789012345678901234',
            'numero': '000000001'
        }
        mock_get.return_value = mock_response

        # Executa a função
        resultado = consultar_nfe('REF_TESTE_001')

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 200)
        self.assertEqual(resultado['referencia'], 'REF_TESTE_001')
        self.assertIn('dados', resultado)

    @patch('emissao_nfe.focusnfe.main.requests.get')
    def test_consultar_nfe_nao_encontrada(self, mock_get):
        """Testa consulta de NFe que não existe"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Executa a função
        resultado = consultar_nfe('REF_INEXISTENTE')

        # Verificações
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 404)
        self.assertEqual(resultado['mensagem'], 'NFe não encontrada')

    @patch('emissao_nfe.focusnfe.main.requests.get')
    def test_consultar_nfe_erro_servidor(self, mock_get):
        """Testa consulta com erro no servidor"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'erro': 'Erro interno do servidor'}
        mock_response.text = '{"erro":"..."}'
        mock_get.return_value = mock_response

        # Executa a função
        resultado = consultar_nfe('REF_TESTE_002')

        # Verificações
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 500)


class TestCancelarNFe(unittest.TestCase):
    """Testes para a função cancelar_nfe"""

    def setUp(self):
        """Configuração antes de cada teste"""
        os.environ['FOCUSNFE_TOKEN'] = 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y'
        os.environ['FOCUSNFE_AMBIENTE'] = 'homologacao'

    @patch('emissao_nfe.focusnfe.main.requests.delete')
    def test_cancelar_nfe_sucesso(self, mock_delete):
        """Testa cancelamento de NFe com sucesso"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'cancelado',
            'mensagem': 'NFe cancelada com sucesso'
        }
        mock_response.text = '{"status":"cancelado"}'
        mock_delete.return_value = mock_response

        # Executa a função
        resultado = cancelar_nfe('REF_TESTE_001', 'Cancelamento para teste unitário')

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 200)
        self.assertEqual(resultado['referencia'], 'REF_TESTE_001')
        self.assertIn('dados', resultado)

    def test_cancelar_nfe_justificativa_curta(self):
        """Testa cancelamento com justificativa menor que 15 caracteres"""
        # Executa a função
        resultado = cancelar_nfe('REF_TESTE_002', 'Curta')

        # Verificações
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 400)
        self.assertIn('15 caracteres', resultado['mensagem'])

    @patch('emissao_nfe.focusnfe.main.requests.delete')
    def test_cancelar_nfe_nao_autorizada(self, mock_delete):
        """Testa cancelamento de NFe não autorizada ainda"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'erro': 'NFe ainda não foi autorizada'
        }
        mock_response.text = '{"erro":"..."}'
        mock_delete.return_value = mock_response

        # Executa a função
        resultado = cancelar_nfe('REF_TESTE_003', 'Cancelamento para teste unitário')

        # Verificações
        self.assertFalse(resultado['sucesso'])
        self.assertEqual(resultado['codigo'], 400)


class TestGetApiConfig(unittest.TestCase):
    """Testes para a função get_api_config"""

    def setUp(self):
        """Configuração antes de cada teste"""
        os.environ['FOCUSNFE_TOKEN'] = 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y'
        os.environ['FOCUSNFE_AMBIENTE'] = 'homologacao'

    def test_get_api_config_homologacao(self):
        """Testa configuração para ambiente de homologação"""
        config = get_api_config()

        self.assertEqual(config['ambiente'], 'homologacao')
        self.assertEqual(config['url'], 'https://homologacao.focusnfe.com.br/v2/nfe')
        self.assertEqual(config['token'], 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y')

    def test_get_api_config_producao(self):
        """Testa configuração para ambiente de produção"""
        os.environ['FOCUSNFE_AMBIENTE'] = 'producao'
        config = get_api_config()

        self.assertEqual(config['ambiente'], 'producao')
        self.assertEqual(config['url'], 'https://api.focusnfe.com.br/v2/nfe')

        # Restaura ambiente de homologação
        os.environ['FOCUSNFE_AMBIENTE'] = 'homologacao'

    def test_get_api_config_sem_token(self):
        """Testa configuração sem token"""
        os.environ.pop('FOCUSNFE_TOKEN', None)

        with self.assertRaises(ValueError) as context:
            get_api_config()

        self.assertIn('Token', str(context.exception))

        # Restaura o token
        os.environ['FOCUSNFE_TOKEN'] = 'bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y'


if __name__ == '__main__':
    unittest.main()
