import webScrap

import streamlit as st
import time
import pandas as pd
from datetime import datetime, timedelta


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Se usar .env para carregar URLs, importe e use load_dotenv. Exemplo:
# from dotenv import load_dotenv
import os
from dotenv import load_dotenv

load_dotenv()

URL_LOGIN = os.getenv("URL_LOGIN")
URL_DADOS = os.getenv("URL_DADOS")



def get_driver():
    # Verifica se já temos um driver rodando
    if "driver" not in st.session_state or st.session_state.driver is None:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        st.session_state.driver = webdriver.Chrome(options=chrome_options)
    return st.session_state.driver

def autenticar_e_coletar():

    """
    1) Abre o navegador e aguarda o login manual até 120s.
    2) Navega até a página com o filtro.
    3) Preenche os campos: Empresa, Status Incial, Status Final, Tipo Produto.
    4) Clica em "Visualizar" e raspa a tabela.
    5) Clica em "Limpar" (exemplo) para resetar.
    6) Retorna os dados raspados em um DataFrame.
    """
    driver = get_driver()

    try:
        webScrap.raspagem_site(driver=driver)

    finally:
        # Fechar o navegador ao terminar (ou comentar se quiser manter aberto)
        st.info("coletando dados")
        pass


# ========== STREAMLIT APP ==========

def main():
    st.title("Exemplo Streamlit: Reutilizar WebDriver")
    if st.button("Iniciar / Reutilizar Driver"):
        df = autenticar_e_coletar()
        if df is not None:
            st.dataframe(df)

    if st.button("Fechar Driver"):
        if "driver" in st.session_state and st.session_state.driver is not None:
            st.session_state.driver.quit()
            st.session_state.driver = None
        st.info("Driver fechado.")

if __name__ == "__main__":
    main()