import requests
import os
from datetime import datetime
from requests.auth import HTTPBasicAuth

# URLs da API FocusNFe
API_URL_PRODUCAO = "https://api.focusnfe.com.br/v2/nfe"
API_URL_HOMOLOGACAO = "https://homologacao.focusnfe.com.br/v2/nfe"

def get_api_config():
    """
    Retorna a configuração da API (URL e token).
    Por padrão usa homologação. Para produção, defina FOCUSNFE_AMBIENTE=producao
    """
    ambiente = os.getenv('FOCUSNFE_AMBIENTE', 'homologacao')
    token = os.getenv('FOCUSNFE_TOKEN', '')

    if not token:
        raise ValueError("Token da FocusNFe não configurado. Defina a variável de ambiente FOCUSNFE_TOKEN")

    api_url = API_URL_PRODUCAO if ambiente == 'producao' else API_URL_HOMOLOGACAO

    return {
        'url': api_url,
        'token': token,
        'ambiente': ambiente
    }

def emitir_nfe(dados_nfe, referencia=None):
    """
    Emite uma NFe através da API FocusNFe

    Args:
        dados_nfe (dict): Dados da NFe conforme documentação FocusNFe
        referencia (str): Referência única para a NFe (opcional, será gerado se não informado)

    Returns:
        dict: Resposta da API com status e informações da NFe
    """
    try:
        config = get_api_config()

        # Gera referência se não informada
        if not referencia:
            referencia = f"nfe_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Endpoint com referência
        url = f"{config['url']}?ref={referencia}"

        # Headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Autenticação Basic Auth (token como usuário, senha vazia)
        auth = HTTPBasicAuth(config['token'], '')

        # Faz a requisição POST
        response = requests.post(url, json=dados_nfe, headers=headers, auth=auth)

        # Processa resposta
        if response.status_code in [200, 201, 202]:
            return {
                'sucesso': True,
                'codigo': response.status_code,
                'mensagem': 'NFe enviada com sucesso',
                'dados': response.json(),
                'referencia': referencia,
                'ambiente': config['ambiente']
            }
        else:
            return {
                'sucesso': False,
                'codigo': response.status_code,
                'mensagem': 'Erro ao emitir NFe',
                'erro': response.json() if response.text else 'Sem detalhes do erro',
                'referencia': referencia
            }

    except ValueError as ve:
        return {
            'sucesso': False,
            'codigo': 500,
            'mensagem': str(ve)
        }
    except Exception as e:
        return {
            'sucesso': False,
            'codigo': 500,
            'mensagem': 'Erro interno ao emitir NFe',
            'erro': str(e)
        }

def consultar_nfe(referencia):
    """
    Consulta o status de uma NFe pela referência

    Args:
        referencia (str): Referência da NFe

    Returns:
        dict: Status e informações da NFe
    """
    try:
        config = get_api_config()

        # Endpoint com referência
        url = f"{config['url']}/{referencia}"

        # Autenticação Basic Auth
        auth = HTTPBasicAuth(config['token'], '')

        # Faz a requisição GET
        response = requests.get(url, auth=auth)

        # Processa resposta
        if response.status_code == 200:
            return {
                'sucesso': True,
                'codigo': response.status_code,
                'mensagem': 'NFe consultada com sucesso',
                'dados': response.json(),
                'referencia': referencia,
                'ambiente': config['ambiente']
            }
        elif response.status_code == 404:
            return {
                'sucesso': False,
                'codigo': 404,
                'mensagem': 'NFe não encontrada',
                'referencia': referencia
            }
        else:
            return {
                'sucesso': False,
                'codigo': response.status_code,
                'mensagem': 'Erro ao consultar NFe',
                'erro': response.json() if response.text else 'Sem detalhes do erro',
                'referencia': referencia
            }

    except ValueError as ve:
        return {
            'sucesso': False,
            'codigo': 500,
            'mensagem': str(ve)
        }
    except Exception as e:
        return {
            'sucesso': False,
            'codigo': 500,
            'mensagem': 'Erro interno ao consultar NFe',
            'erro': str(e)
        }

def cancelar_nfe(referencia, justificativa):
    """
    Cancela uma NFe emitida

    Args:
        referencia (str): Referência da NFe
        justificativa (str): Justificativa do cancelamento (mínimo 15 caracteres)

    Returns:
        dict: Resposta da operação de cancelamento
    """
    try:
        if len(justificativa) < 15:
            return {
                'sucesso': False,
                'codigo': 400,
                'mensagem': 'Justificativa deve ter no mínimo 15 caracteres'
            }

        config = get_api_config()

        # Endpoint com referência
        url = f"{config['url']}/{referencia}"

        # Headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Autenticação Basic Auth
        auth = HTTPBasicAuth(config['token'], '')

        # Dados do cancelamento
        dados_cancelamento = {
            'justificativa': justificativa
        }

        # Faz a requisição DELETE
        response = requests.delete(url, json=dados_cancelamento, headers=headers, auth=auth)

        # Processa resposta
        if response.status_code in [200, 201, 202]:
            return {
                'sucesso': True,
                'codigo': response.status_code,
                'mensagem': 'NFe cancelada com sucesso',
                'dados': response.json() if response.text else {},
                'referencia': referencia,
                'ambiente': config['ambiente']
            }
        else:
            return {
                'sucesso': False,
                'codigo': response.status_code,
                'mensagem': 'Erro ao cancelar NFe',
                'erro': response.json() if response.text else 'Sem detalhes do erro',
                'referencia': referencia
            }

    except ValueError as ve:
        return {
            'sucesso': False,
            'codigo': 500,
            'mensagem': str(ve)
        }
    except Exception as e:
        return {
            'sucesso': False,
            'codigo': 500,
            'mensagem': 'Erro interno ao cancelar NFe',
            'erro': str(e)
        }
