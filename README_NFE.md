# Emissão de NFe via FocusNFe

Este documento descreve como usar os endpoints de emissão de Notas Fiscais Eletrônicas (NFe) através da API FocusNFe.

## Configuração

### 1. Obter Token da FocusNFe

Acesse [https://focusnfe.com.br/](https://focusnfe.com.br/) e obtenha seu token de autenticação.

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure suas credenciais:

```
FOCUSNFE_TOKEN=seu_token_aqui
FOCUSNFE_AMBIENTE=homologacao
```

**Importante:**
- Use `homologacao` para testes
- Use `producao` para emissão real de notas fiscais

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

## Endpoints Disponíveis

### 1. Emitir NFe

**POST** `/emitir_nfe`

Emite uma nova nota fiscal eletrônica.

#### Request Body (JSON)

```json
{
  "referencia": "minha_ref_unica_123",
  "dados_nfe": {
    "natureza_operacao": "Venda de mercadoria",
    "data_emissao": "2025-01-15T10:30:00",
    "tipo_documento": 1,
    "finalidade_emissao": 1,
    "cnpj_emitente": "07504505000132",
    "inscricao_estadual_emitente": "12345678",
    "nome_emitente": "Minha Empresa LTDA",
    "logradouro_emitente": "Rua Exemplo",
    "numero_emitente": "123",
    "bairro_emitente": "Centro",
    "municipio_emitente": "São Paulo",
    "uf_emitente": "SP",
    "cep_emitente": "01000000",
    "cnpj_destinatario": "51916585000125",
    "nome_destinatario": "Cliente LTDA",
    "logradouro_destinatario": "Rua Cliente",
    "numero_destinatario": "456",
    "bairro_destinatario": "Jardins",
    "municipio_destinatario": "São Paulo",
    "uf_destinatario": "SP",
    "cep_destinatario": "01400000",
    "items": [
      {
        "numero_item": "1",
        "codigo_produto": "PROD001",
        "descricao": "Produto Exemplo",
        "cfop": "5102",
        "quantidade_comercial": 10,
        "valor_unitario_comercial": 100.00,
        "codigo_ncm": "12345678",
        "icms_situacao_tributaria": "00",
        "pis_situacao_tributaria": "01",
        "cofins_situacao_tributaria": "01"
      }
    ],
    "valor_produtos": 1000.00,
    "valor_frete": 0.00,
    "valor_seguro": 0.00,
    "valor_total": 1000.00,
    "modalidade_frete": 0
  }
}
```

**Campos obrigatórios em `dados_nfe`:**
- `natureza_operacao`: Descrição da operação
- `data_emissao`: Data de emissão (formato ISO)
- `tipo_documento`: 0 (entrada) ou 1 (saída)
- `finalidade_emissao`: 1=normal, 2=complementar, 3=ajuste, 4=devolução
- Dados do emitente (CNPJ/CPF, IE, nome, endereço)
- Dados do destinatário (CNPJ/CPF, nome, endereço)
- `items`: Array de itens da nota
- Valores totais

**Campos opcionais:**
- `referencia`: Se não informado, será gerado automaticamente

#### Response (202 Accepted - Processando)

```json
{
  "sucesso": true,
  "codigo": 202,
  "mensagem": "NFe enviada com sucesso",
  "dados": {
    "cnpj_emitente": "07504505000132",
    "ref": "minha_ref_unica_123",
    "status": "processando_autorizacao"
  },
  "referencia": "minha_ref_unica_123",
  "ambiente": "homologacao"
}
```

#### Response (201 Created - Autorizada)

```json
{
  "sucesso": true,
  "codigo": 201,
  "mensagem": "NFe enviada com sucesso",
  "dados": {
    "status": "autorizado",
    "chave_nfe": "NFe41190607504505000132550010000000221923094166",
    "numero": "22",
    "serie": "1",
    "caminho_xml_nota_fiscal": "/arquivos.../nfe.xml",
    "caminho_danfe": "/arquivos.../danfe.pdf"
  },
  "referencia": "minha_ref_unica_123",
  "ambiente": "homologacao"
}
```

### 2. Consultar NFe

**GET** `/consultar_nfe/<referencia>`

Consulta o status de uma NFe pela referência.

#### Exemplo

```
GET /consultar_nfe/minha_ref_unica_123
```

#### Response

```json
{
  "sucesso": true,
  "codigo": 200,
  "mensagem": "NFe consultada com sucesso",
  "dados": {
    "status": "autorizado",
    "chave_nfe": "NFe41190607504505000132550010000000221923094166",
    "numero": "22",
    "serie": "1",
    "caminho_xml_nota_fiscal": "/arquivos.../nfe.xml",
    "caminho_danfe": "/arquivos.../danfe.pdf"
  },
  "referencia": "minha_ref_unica_123",
  "ambiente": "homologacao"
}
```

### 3. Cancelar NFe

**DELETE** `/cancelar_nfe`

Cancela uma nota fiscal eletrônica.

#### Request Body (JSON)

```json
{
  "referencia": "minha_ref_unica_123",
  "justificativa": "Cancelamento solicitado pelo cliente devido a erro no pedido"
}
```

**Campos obrigatórios:**
- `referencia`: Referência da NFe
- `justificativa`: Motivo do cancelamento (mínimo 15 caracteres)

#### Response

```json
{
  "sucesso": true,
  "codigo": 200,
  "mensagem": "NFe cancelada com sucesso",
  "dados": {
    "status": "cancelado",
    "mensagem_sefaz": "Cancelamento homologado"
  },
  "referencia": "minha_ref_unica_123",
  "ambiente": "homologacao"
}
```

## Status Possíveis da NFe

- `processando_autorizacao`: NFe enviada e aguardando processamento pela SEFAZ
- `autorizado`: NFe autorizada e válida
- `erro_autorizacao`: Erro na autorização pela SEFAZ
- `cancelado`: NFe cancelada
- `denegado`: NFe denegada pela SEFAZ

## Tratamento de Erros

Todos os endpoints retornam erros no seguinte formato:

```json
{
  "sucesso": false,
  "codigo": 400,
  "mensagem": "Descrição do erro",
  "erro": {
    "detalhes": "Informações adicionais sobre o erro"
  }
}
```

## Códigos HTTP

- `200`: Sucesso
- `201`: NFe criada e autorizada
- `202`: NFe aceita e em processamento
- `400`: Erro na requisição (dados inválidos)
- `404`: NFe não encontrada
- `500`: Erro interno do servidor

## Processamento Assíncrono

A API FocusNFe opera de forma **assíncrona**:

1. Ao emitir uma NFe, você receberá um status inicial (geralmente `202 - processando_autorizacao`)
2. A nota entra em fila para autorização na SEFAZ
3. Use o endpoint `/consultar_nfe/<referencia>` para verificar o status atualizado
4. Alternativamente, configure webhooks na FocusNFe para receber notificações automáticas

## Exemplo de Uso Completo

```bash
# 1. Emitir NFe
curl -X POST http://localhost:5000/emitir_nfe \
  -H "Content-Type: application/json" \
  -d @dados_nfe.json

# 2. Consultar status
curl -X GET http://localhost:5000/consultar_nfe/minha_ref_unica_123

# 3. Cancelar (se necessário)
curl -X DELETE http://localhost:5000/cancelar_nfe \
  -H "Content-Type: application/json" \
  -d '{
    "referencia": "minha_ref_unica_123",
    "justificativa": "Cancelamento por erro no pedido"
  }'
```

## Documentação Oficial

Para mais informações sobre os campos e regras de validação, consulte a documentação oficial da FocusNFe:
- [Documentação NFe](https://focusnfe.com.br/doc/#nfe)

## Suporte

Para dúvidas ou problemas:
1. Verifique se as variáveis de ambiente estão configuradas corretamente
2. Confirme se o token está ativo na FocusNFe
3. Revise a documentação oficial da FocusNFe
4. Entre em contato com o suporte da FocusNFe
