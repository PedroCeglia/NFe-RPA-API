# Testes Unitários - Emissão de NFe

Este documento descreve como executar os testes unitários para o módulo de emissão de NFe.

## Estrutura de Testes

```
NFe-RPA-API/
├── tests/
│   ├── __init__.py
│   └── test_emissao_nfe.py      # Testes unitários de emissão de NFe
├── .env.test                     # Variáveis de ambiente para testes
├── pytest.ini                    # Configuração do pytest
└── run_tests.py                  # Script para executar testes
```

## Pré-requisitos

Instale as dependências de teste:

```bash
pip install -r requirements.txt
```

Ou instale apenas as ferramentas de teste:

```bash
pip install pytest pytest-cov pytest-mock
```

## Configuração

O arquivo `.env.test` contém as configurações para o ambiente de homologação:

```env
FOCUSNFE_TOKEN=bOVX7lwkTQtLEHpzLRyqij4LOCzcCN1y
FOCUSNFE_AMBIENTE=homologacao
```

## Como Executar os Testes

### Opção 1: Usando o script run_tests.py (Recomendado)

Este script carrega automaticamente as variáveis de ambiente do `.env.test`:

```bash
python run_tests.py
```

Para executar com cobertura de código:

```bash
python run_tests.py --cov=EmissaoNFe --cov-report=html
```

### Opção 2: Usando pytest diretamente

```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar um arquivo específico
pytest tests/test_emissao_nfe.py

# Executar uma classe específica
pytest tests/test_emissao_nfe.py::TestEmissaoNFe

# Executar um teste específico
pytest tests/test_emissao_nfe.py::TestEmissaoNFe::test_emitir_nfe_sucesso
```

### Opção 3: Usando unittest

```bash
python -m unittest tests.test_emissao_nfe
```

## Cobertura de Código

Para gerar relatório de cobertura:

```bash
# Relatório no terminal
pytest --cov=EmissaoNFe --cov-report=term-missing

# Relatório HTML
pytest --cov=EmissaoNFe --cov-report=html
```

O relatório HTML será gerado em `htmlcov/index.html`.

## Testes Implementados

### TestEmissaoNFe
- `test_emitir_nfe_sucesso`: Testa emissão bem-sucedida de NFe
- `test_emitir_nfe_erro_validacao`: Testa erro de validação nos dados
- `test_emitir_nfe_sem_referencia`: Testa geração automática de referência
- `test_emitir_nfe_sem_token`: Testa erro quando token não está configurado

### TestConsultarNFe
- `test_consultar_nfe_sucesso`: Testa consulta de NFe existente
- `test_consultar_nfe_nao_encontrada`: Testa consulta de NFe inexistente
- `test_consultar_nfe_erro_servidor`: Testa tratamento de erro do servidor

### TestCancelarNFe
- `test_cancelar_nfe_sucesso`: Testa cancelamento bem-sucedido
- `test_cancelar_nfe_justificativa_curta`: Testa validação de justificativa
- `test_cancelar_nfe_nao_autorizada`: Testa erro ao cancelar NFe não autorizada

### TestGetApiConfig
- `test_get_api_config_homologacao`: Testa configuração de homologação
- `test_get_api_config_producao`: Testa configuração de produção
- `test_get_api_config_sem_token`: Testa erro quando token não está configurado

## Mocks e Simulações

Os testes utilizam mocks para simular as chamadas à API FocusNFe, evitando:
- Chamadas reais à API durante os testes
- Consumo de créditos ou limites de requisição
- Dependência de conectividade com a internet
- Criação de notas fiscais reais no ambiente de homologação

## Boas Práticas

1. **Execute os testes antes de fazer commit**: Garante que as mudanças não quebraram nada
2. **Mantenha alta cobertura de código**: Idealmente acima de 80%
3. **Use o ambiente de homologação**: Nunca use tokens de produção em testes
4. **Mocks são seus amigos**: Use mocks para simular APIs externas
5. **Testes devem ser independentes**: Cada teste deve funcionar sozinho

## Troubleshooting

### Erro: ModuleNotFoundError

Se você receber erro de módulo não encontrado:

```bash
# Adicione o diretório raiz ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou no Windows
set PYTHONPATH=%PYTHONPATH%;%cd%
```

### Testes falham com erro de token

Verifique se o arquivo `.env.test` existe e contém o token correto:

```bash
cat .env.test  # Linux/Mac
type .env.test  # Windows
```

### Importação de módulos

Se houver problemas de importação, verifique se está executando os testes do diretório raiz do projeto.

## Integração Contínua

Para integrar com CI/CD, adicione ao seu workflow:

```yaml
# Exemplo para GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    python run_tests.py
```

## Próximos Passos

- [ ] Adicionar testes de integração com ambiente de homologação real
- [ ] Implementar testes de carga
- [ ] Adicionar testes end-to-end nos endpoints da API Flask
- [ ] Configurar CI/CD para executar testes automaticamente
