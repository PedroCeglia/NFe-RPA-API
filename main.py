from flask import Flask, request, jsonify
import pandas as pd
from PlanilhaProdutos.main import recuperar_planilhas
from NFePDFs.main import percorrer_lista_pdfs
from NFePlanilhaFinal.main import create_planilhas_by_danfe
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/processar_arquivos": {"origins": "https://6z4wqd.csb.app"}})


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

    # Monta a resposta JSON
    response = {
        "planilha_itens_nfe": informacoes_nfe["planilha_itens_nfe"],
        "planilha_itens_nao_encontrados": informacoes_nfe["planilha_itens_nao_encontrados"],
        "planilha_total_itens": informacoes_nfe["planilha_total_itens"].to_json(orient="records"),
        "planilha_duplicados":planilha_duplicados.to_json(orient="records")
    }

    # Retorna o JSON com as informações
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
