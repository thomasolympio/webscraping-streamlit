import streamlit as st
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os


# Carregar variáveis de ambiente
load_dotenv()

# URL do sistema da Yamaha
URL_LOGIN = os.getenv('URL_LOGIN')
URL_DADOS = os.getenv('URL_DADOS')



# Configuração do WebDriver
chrome_options = Options()
# Comente a linha abaixo durante os testes para visualizar o navegador
# chrome_options.add_argument("--headless")  # Executar sem interface gráfica
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)


def autenticar_e_coletar():
    """ O usuário faz login manual e depois os dados são raspados automaticamente """
    driver.get(URL_LOGIN)
    st.info("🔑 Faça o login manualmente no site da Yamaha.")
    st.warning("⚠️ Após o login, **NÃO FECHE O NAVEGADOR**. Volte ao Streamlit para prosseguir.")

    # Aguarda a autenticação manual (Usuário tem 2 minutos para logar)
    tempo_espera = 120
    while tempo_espera > 0:
        if "V2" in driver.current_url:
            st.success("✅ Login detectado! Iniciando a raspagem automaticamente...")
            break
        time.sleep(5)
        tempo_espera -= 5

    if "V2" not in driver.current_url:
        st.error("❌ Tempo esgotado. Faça login e tente novamente.")
        return

    dados_totais = []

    try:
        driver.get(URL_DADOS)
        time.sleep(10)

        # 1️⃣ Clicar no botão "Visualizar"
        visualizar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visualizar')]"))
        )
        visualizar_btn.click()
        time.sleep(5)

        # 2️⃣ Identificar todas as empresas no filtro
        empresas = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//select[@id='empresa-select']/option"))
        )

        for empresa in empresas:
            empresa_nome = empresa.text.strip()
            empresa.click()
            time.sleep(3)  # Aguarde o carregamento

            # 3️⃣ Identificar todos os produtos disponíveis para essa empresa
            produtos = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//select[@id='produto-select']/option"))
            )

            for produto in produtos:
                produto_nome = produto.text.strip()
                produto.click()
                time.sleep(3)

                # 4️⃣ Clicar na aba "Lote por Nota Fiscal"
                aba_lote_nf = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'LOTE POR NOTA FISCAL')]"))
                )
                aba_lote_nf.click()
                time.sleep(5)

                # 5️⃣ Raspar os dados da tabela
                tabela = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                linhas = tabela.find_elements(By.TAG_NAME, "tr")

                for linha in linhas[1:]:  # Pulando o cabeçalho
                    colunas = linha.find_elements(By.TAG_NAME, "td")
                    if len(colunas) > 1:
                        numero_nf = colunas[1].text.strip()  # Segunda coluna (Número Nota Fiscal)
                        data_pagamento = colunas[4].text.strip()  # Quinta coluna (Data Pagamento)
                        dados_totais.append([empresa_nome, produto_nome, numero_nf, data_pagamento])

        # Criando DataFrame Pandas
        df = pd.DataFrame(dados_totais, columns=["Empresa", "Produto", "Número Nota Fiscal", "Data Pagamento"])
        return df

    except Exception as e:
        st.error(f"Erro ao coletar os dados: {e}")
        return None

    finally:
        driver.quit()

# Interface no Streamlit
st.title("🔍 Consulta de Notas Fiscais - Yamaha")

if st.button("🔑 Autenticação Manual"):
    st.info("Aguarde enquanto processamos...")
    df = autenticar_e_coletar()
    if df is not None:
        st.success("✅ Dados coletados com sucesso!")
        import ace_tools as tools
        tools.display_dataframe_to_user(name="Dados de Notas Fiscais", dataframe=df)
    else:
        st.error("❌ Falha ao coletar os dados.")
