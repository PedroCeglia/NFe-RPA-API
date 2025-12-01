import pandas as pd

def create_planilhas_by_danfe(planilha_items:pd.DataFrame, itens_danfe:dict, title=""):
    """
    Percorre um dicionario de itens_danfe \n
    {codigo: df_itens_danfe} \n
    Recebe um dataframe com a planilha de custo \n
    Retorna um dicionario com os valores
    { \n
        planilha_total_itens: df_total_itens_nfe, \n
        planilha_itens_nao_encontrados: erros_by_nfe_dict, \n
        planilha_itens_nfe: itens_by_nfe_dict \n
    }
    """
    erros_by_nfe_dict = {}
    itens_by_nfe_dict = {}
    df_total_itens_nfe = pd.DataFrame(columns=["numeroDaNota", "total"])

    # Recupera os itens validos, não encontrados e o total da nota
    dict_danfe_infos = recupera_informacoes_sobre_as_nfe(planilha_items, itens_danfe, title)

    for codigo, danfe_infos in dict_danfe_infos.items():
        # Recupera informações da Danfe
        item_df, soma_total, erros_df = danfe_infos
        
        # Registra os erros e os itens
        erros_by_nfe_dict.update({codigo:erros_df.to_dict(orient="records")})
        itens_by_nfe_dict.update({codigo:item_df.to_dict(orient="records")})

        nova_linha_df_total = pd.DataFrame([[codigo, soma_total]], columns=["numeroDaNota", "total"])

        df_total_itens_nfe = pd.concat([ df_total_itens_nfe, nova_linha_df_total], ignore_index=True)
    
    return {
        "planilha_total_itens": df_total_itens_nfe, 
        "planilha_itens_nao_encontrados": erros_by_nfe_dict, 
        "planilha_itens_nfe": itens_by_nfe_dict
    }

def recupera_informacoes_sobre_as_nfe(planilha_items:pd.DataFrame, itens_danfe:dict, title=""):
    """
    Percorre um dicionario de NFe {codigo:df_itens_nfe}\n
    Retorna um dicionario com as seguintes informações sobre a nfe\n
    {codigo: [\n
        df_nfe_itens_validos,\n 
        soma_todos_itens_nfe, \n
        df_nfe_itens_nao_encontrados
    ]}
    """
    # Cria um dicionario vazio
    dict_danfe = {}

    # Percorre um dicionario de nfe {codigo:df_itens_danfe}
    for codigo, df_itens in itens_danfe.items():
        # Junta os dfs, df_itens_danfe e df_planilha_itens a partir do código dos itens
        df_nfe_itens_validos = pd.merge(df_itens, planilha_items, on='Cod', how='left')
        print(df_nfe_itens_validos)
        # Na coluna "QTDD" os itens com os valores '' serão trocados por 0
        df_nfe_itens_validos['QTDD'] = df_nfe_itens_validos['QTDD'].replace("", 0)

        # Recupera os itens da NFe que não possuem um custo na planilha
        df_nfe_itens_nao_encontrados = df_nfe_itens_validos[df_nfe_itens_validos["CUSTO"].isna() == True]
        
        # Recupera os itens da NFe que possuem um custo na planilha
        df_nfe_itens_validos = df_nfe_itens_validos[df_nfe_itens_validos["CUSTO"].isna() == False]
        
        # Caso tenha algum item da NFe sem um valor na coluna Custo
        if not df_nfe_itens_nao_encontrados.empty:
            print("ERROS", title, codigo)            
            print(df_nfe_itens_nao_encontrados[["Cod", "QTDD", "ITEM"]])
        
        # Caso não possua nenhum item da NFe com algum valor na coluna custo
        if len(df_nfe_itens_validos) == 0:
            continue
        
        # Cria a coluna "Total" para cada item valido da NFe
        df_nfe_itens_validos["TOTAL"] = df_nfe_itens_validos["QTDD"] * df_nfe_itens_validos["CUSTO"]
        
        # Define a ordem em que serão exibidas as colunas do dataframe
        # reset_index reinicia o index do dataframe
        # drop=True descarta o index original
        df_nfe_itens_validos = df_nfe_itens_validos.reindex(columns=["ITEM","Cod","CUSTO","QTDD","TOTAL"]).reset_index(drop=True)
        
        # Recupera o valor final da nota
        df_soma_total = df_nfe_itens_validos["TOTAL"].sum()
        soma_total_todos_itens = "{:.2f}".format(df_soma_total)

        dict_danfe.update({codigo: [df_nfe_itens_validos, soma_total_todos_itens, df_nfe_itens_nao_encontrados]})


    return dict_danfe