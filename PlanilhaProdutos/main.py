import pandas as pd

def recuperar_planilhas(planilha):
    """
    Recupera uma planilha de produtos a partir de um csv \n
    Verifica se as colunas são validas \n
    Verifica se Existem itens duplicados \n
    Formata o custo \n
    passa a coluna "Cod" para string \n
    Return {codigo, planilha}
    """
    isColumnValid = verificando_colunas_planilha(planilha)
    if isColumnValid["codigo"] == 200:
        planilha["CUSTO"] = planilha["CUSTO"].map(formatar_custo)
        planilha["Cod"] = planilha["Cod"].astype(str)
        return verificando_itens_duplicados(planilha)
    else:
        return isColumnValid
    

def formatar_custo(item):   

    return float("{:.2f}".format(float(item.replace(",",".")) / 100))

def verificando_itens_duplicados(planilha: pd.DataFrame):
    """
    Verifica se existem itens duplicados na coluna 'Cod'. \n
    Ordena os valores do itens duplicados caso eles existam. \n
    Caso existam retornam a lista de itens duplicados \n
    Caso nao existam retornam a planilha original \n
    """
    planilha_de_duplicados = planilha[planilha.duplicated('Cod', keep=False)]
    planilha_de_duplicados = planilha_de_duplicados.sort_values(by='Cod', ignore_index=True)

    validDict = {"codigo": 200, "planilha":planilha}
    erroDict =  {"codigo": 203, "planilha":planilha, "planilhaDuplicados":planilha_de_duplicados}

    return validDict if len(planilha_de_duplicados) == 0 else erroDict

def verificando_colunas_planilha(planilha:pd.DataFrame):
    """
    Verifica se existe as colunas ['Cod', 'CUSTO']
    """
    colunas_necessarias = ["Cod", "CUSTO"]

    colunas_faltantes = [col for col in colunas_necessarias if not col in planilha.columns]

    if colunas_faltantes:
        return {
            "codigo":404,
            "mensage": f"Error, as seguintes colunas não foram encontradas: {colunas_faltantes}",
            "planilha": "Error"

        }
    else:
        return {
            "codigo":200,
            "mensage":"Todas as colunas foram encontradas"
        }
        