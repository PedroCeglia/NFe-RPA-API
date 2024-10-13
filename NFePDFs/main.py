import pypdf as pyf
import tabula
import pandas as pd
import os

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def percorrer_lista_pdfs_diretorio(src):
    '''
    Percorre uma pasta e recupera todos os dados de nfe a partir de um pdf \n
    retorna um dicionario {codigo_nota:lista_itens_nfe} \n
    '''
    dfs_total = {}

    for arquivo in os.listdir(src):
        if arquivo.endswith(".pdf"):
            nfe = get_dados_nfe_by_pdf(f"{src}/{arquivo}")
            itens_nfe = nfe["itens"]
            codigo = str(nfe["codigo_nfe"])
            dfs_total.update({codigo:itens_nfe})

    return dfs_total

def percorrer_lista_pdfs(lista_pdfs):
    '''
    Percorre umalista de pdfs_nfe e recupera todos os dados de nfe a partir de um pdf \n
    retorna um dicionario {codigo_nota:lista_itens_nfe} \n
    '''
    dfs_total = {}

    for arquivo in lista_pdfs:
        if arquivo.filename.endswith('.pdf'):
            nfe = get_dados_nfe_by_pdf(arquivo)
            itens_nfe = nfe["itens"]
            codigo = str(nfe["codigo_nfe"])
            dfs_total.update({codigo:itens_nfe})

    return dfs_total

def get_dados_nfe_by_pdf(pdf_name):
    '''
    Recupera Tabelas de Produtos de um pdf
    '''
    # Recuperando lista de Paginas
    reader = pyf.PdfReader(pdf_name)
    paginas = len(reader.pages)

    # Cria o Dataframe Final 
    df_todos_os_produtos_nota = pd.DataFrame(columns=["CÓDIGO", "QTD."])

    for page in range(paginas):
        # Recuperando tabelas na pagina do pdf
        lista_de_tabelas = tabula.read_pdf(pdf_name, pages=page + 1, lattice=True)

        # Escolhendo a tabela que tem os dados dos produtos da nota   
        df_itens_nota = lista_de_tabelas[-2]

        # Limpando colunas vazias e trocando valores vazios para ""
        df_itens_nota = df_itens_nota.dropna(how="all", axis=0)
        df_itens_nota = df_itens_nota.dropna(how="all", axis=1)
        df_itens_nota.fillna("")

        df_todos_os_produtos_nota = pd.concat([
            df_todos_os_produtos_nota,
            df_itens_nota[["CÓDIGO", "QTD.", "DESCRIÇÃO DO PRODUTO/SERVIÇO"]]], 
            ignore_index=True)
    
    # Limpando o código do produto
    df_todos_os_produtos_nota["CÓDIGO"] = df_todos_os_produtos_nota["CÓDIGO"].map(lambda txt: str(txt).replace("\r", ""))
    
    df_todos_os_produtos_nota = df_todos_os_produtos_nota.rename(columns={
        "CÓDIGO":"Cod",
        "QTD.":"QTDD",
        "DESCRIÇÃO DO PRODUTO/SERVIÇO":"ITEM"
    })
    
    # Recuperando apenas o nome 
    df_todos_os_produtos_nota["ITEM"] = df_todos_os_produtos_nota["ITEM"].str.split(" - ").str[0]
    df_todos_os_produtos_nota["ITEM"] = df_todos_os_produtos_nota["ITEM"].str.split(r" -\r").str[0]
    df_todos_os_produtos_nota["ITEM"] = df_todos_os_produtos_nota["ITEM"].str.split(r"-\r").str[0]
    df_todos_os_produtos_nota["ITEM"] = df_todos_os_produtos_nota["ITEM"].str.split(r"\r").str[0]



    # Recuperando código da nota
    codigo_nota = recuperar_numero_nota(pdf_name)

    return {
        "itens":df_todos_os_produtos_nota, 
        "codigo_nfe": codigo_nota
    }

def formatar_df(txt):
    return str(txt).replace("\r", "")


def recuperar_numero_nota(pdf_name):
    '''
    Recupera o numero da nota a partir de um pdf
    '''
    reader = pyf.PdfReader(pdf_name)
    texto = reader.pages[0].extract_text().split("NOTA FISCAL: ")[1].split(" SÉRIE: ")[0]
    return texto

#recuperar_numero_nota("pdfs/nfe2.pdf")