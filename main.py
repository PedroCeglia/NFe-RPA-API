from flask import Flask, request, jsonify
import pandas as pd
from analise_nfe.produtos.main import recuperar_planilhas
from analise_nfe.pdfs.main import percorrer_lista_pdfs
from analise_nfe.planilha.main import create_planilhas_by_danfe
from emissao_nfe.focusnfe.main import emitir_nfe, consultar_nfe, cancelar_nfe
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
#CORS(app, resources={r"/processar_arquivos": {"origins": "https://6z4wqd.csb.app"}})
CORS(app)


@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"mensage":"Hello World"}), 200

@app.route('/processar_arquivos', methods=['POST'])
def processar_arquivos():
    # Verifica se os arquivos estão presentes na requisição
    if 'pdfs' not in request.files or 'csv' not in request.files:
        return jsonify({"error": "Arquivos CSV ou PDF não encontrados"}), 400
    
    # Obtém o arquivo CSV
    csv_file = request.files['csv']
    if not csv_file.filename.endswith('.csv'):
        return jsonify({"error": "O arquivo CSV é inválido."}), 400
    
    # Lê o CSV usando o pandas
    try:
        planilha = pd.read_csv(csv_file)
        print(planilha)
        planilha_response = recuperar_planilhas(planilha)
    except Exception as e:
        return jsonify({"error": f"Erro ao ler o CSV: {str(e)}"}), 400

    # Caso a planilha não seje valida
    if planilha_response["codigo"] != 200 and planilha_response["codigo"] != 203:
        return jsonify({
            "error": planilha_response["mensage"], 
            "planilha": planilha_response["planilha"]
        }), planilha_response["codigo"] 
    
    planilha_duplicados = planilha_response["planilhaDuplicados"] if planilha_response["codigo"] == 203 else []
 
    # Obtém a lista de arquivos PDF
    pdf_files = request.files.getlist('pdfs')
    pdf_files_valid = [file for file in pdf_files if file.filename.endswith('.pdf')]
    
    if not pdf_files_valid:
        return jsonify({"error": "Nenhum arquivo PDF válido foi encontrado."}), 400

    # Você pode realizar outras operações com os PDFs aqui (ex: extração de texto, análise de conteúdo)
    nfe_pdfs_list = percorrer_lista_pdfs(pdf_files_valid)
    informacoes_nfe = create_planilhas_by_danfe(planilha_response["planilha"], nfe_pdfs_list)

    # RESPOSTA CORRIGIDA – TUDO COMO ARRAY JSON
    response = {
        "planilha_itens_nfe": (
            informacoes_nfe["planilha_itens_nfe"].to_dict(orient="records") 
            if isinstance(informacoes_nfe["planilha_itens_nfe"], pd.DataFrame) 
            else []
        ),
        "planilha_itens_nao_encontrados": (
            informacoes_nfe["planilha_itens_nao_encontrados"].to_dict(orient="records") 
            if isinstance(informacoes_nfe["planilha_itens_nao_encontrados"], pd.DataFrame) 
            else []
        ),
        "planilha_total_itens": (
            informacoes_nfe["planilha_total_itens"].to_dict(orient="records") 
            if isinstance(informacoes_nfe["planilha_total_itens"], pd.DataFrame) 
            else []
        ),
        "planilha_duplicados": (
            planilha_duplicados.to_dict(orient="records") 
            if isinstance(planilha_duplicados, pd.DataFrame) 
            else []
        )
    }
    
    return jsonify(response), 200


@app.route('/emitir_nfe', methods=['POST'])
def emitir_nota_fiscal():
    """
    Endpoint para emitir uma NFe via FocusNFe

    Body esperado (JSON):
    {
        "referencia": "opcional_ref_unica",
        "dados_nfe": {
            "natureza_operacao": "Venda de mercadoria",
            "tipo_documento": 1,
            "finalidade_emissao": 1,
            "cnpj_emitente": "...",
            ... (outros campos conforme doc FocusNFe)
        }
    }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type deve ser application/json"}), 400

    dados = request.get_json()

    if 'dados_nfe' not in dados:
        return jsonify({"error": "Campo 'dados_nfe' é obrigatório"}), 400

    dados_nfe = dados['dados_nfe']
    referencia = dados.get('referencia')

    # Emite a NFe
    resultado = emitir_nfe(dados_nfe, referencia)

    if resultado['sucesso']:
        return jsonify(resultado), resultado['codigo']
    else:
        return jsonify(resultado), resultado['codigo']


@app.route('/consultar_nfe/<referencia>', methods=['GET'])
def consultar_nota_fiscal(referencia):
    """
    Endpoint para consultar o status de uma NFe pela referência

    Parâmetros:
        referencia (str): Referência única da NFe
    """
    if not referencia:
        return jsonify({"error": "Referência é obrigatória"}), 400

    # Consulta a NFe
    resultado = consultar_nfe(referencia)

    if resultado['sucesso']:
        return jsonify(resultado), resultado['codigo']
    else:
        return jsonify(resultado), resultado['codigo']


@app.route('/cancelar_nfe', methods=['DELETE'])
def cancelar_nota_fiscal():
    """
    Endpoint para cancelar uma NFe

    Body esperado (JSON):
    {
        "referencia": "ref_da_nfe",
        "justificativa": "Motivo do cancelamento (mínimo 15 caracteres)"
    }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type deve ser application/json"}), 400

    dados = request.get_json()

    if 'referencia' not in dados or 'justificativa' not in dados:
        return jsonify({"error": "Campos 'referencia' e 'justificativa' são obrigatórios"}), 400

    referencia = dados['referencia']
    justificativa = dados['justificativa']

    # Cancela a NFe
    resultado = cancelar_nfe(referencia, justificativa)

    if resultado['sucesso']:
        return jsonify(resultado), resultado['codigo']
    else:
        return jsonify(resultado), resultado['codigo']


if __name__ == '__main__':
    app.run(debug=True, port=5000, ssl_context=('cert.pem', 'key.pem'))
