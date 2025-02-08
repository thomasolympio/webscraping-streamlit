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


def raspagem_site(driver) -> None:


    driver

    try:
        # (1) LOGIN MANUAL
        driver.get(URL_LOGIN)
        st.info("Favor fazer login manualmente no navegador. Até 120s para concluir.")
        st.warning("Não feche o navegador; volte ao Streamlit após logar.")

        tempo_espera = 120
        while tempo_espera > 0:
            # Ajuste a condição que detecta login (ex.: "V2" na URL ou "home" etc.)
            if "V2" in driver.current_url:
                st.success("✅ Login detectado! Prosseguindo...")
                break
            time.sleep(5)
            tempo_espera -= 5

        if "V2" not in driver.current_url:
            st.error("❌ Tempo esgotado ou login não foi detectado.")
            return None

        # (2) IR PARA A TELA DE DADOS
        driver.get(URL_DADOS)
        time.sleep(5)

        # (3) CLICAR EM "LIMPAR" (opcional)
        try:
            limpar_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Limpar')]"))
            )
            limpar_btn.click()
            time.sleep(2)
        except Exception as e:
            st.warning(f"Botão 'Limpar' não encontrado ou falhou. Erro: {e}")

        # (4) PREENCHER FILTROS

        # (A) EMPRESA (Autocomplete MUI com ID="Empresa")
        empresa_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "Empresa"))
        )
        empresa_input.click()  # abre as opções
        time.sleep(1)

        # Tenta pegar a lista de <li role="option"> e clica na primeira
        try:
            opcoes = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[@role='option']"))
            )
            opcoes[0].click()
            time.sleep(1)
        except Exception as e:
            st.warning(f"Não encontrei opções em 'Empresa'. Erro: {e}")
            # Se quiser usar ARROW_DOWN + ENTER:
            # empresa_input.send_keys(Keys.ARROW_DOWN)
            # empresa_input.send_keys(Keys.ENTER)

        # (B) STATUS INCIAL
        status_inicial_input = driver.find_element(
            By.XPATH, "//p[contains(text(),'Status Incial')]/../../..//input"
        )
        # Limpar e digitar data inicial (hoje - 360 dias)
        status_inicial_input.send_keys(Keys.CONTROL + "a")
        status_inicial_input.send_keys(Keys.DELETE)
        data_inicial = (datetime.now() - timedelta(days=360)).strftime("%d/%m/%Y")
        status_inicial_input.send_keys(data_inicial)
        time.sleep(1)

        # (C) STATUS FINAL
        status_final_input = driver.find_element(
            By.XPATH, "//p[contains(text(),'Status Final')]/../../..//input"
        )
        status_final_input.send_keys(Keys.CONTROL + "a")
        status_final_input.send_keys(Keys.DELETE)
        data_final = datetime.now().strftime("%d/%m/%Y")
        status_final_input.send_keys(data_final)
        time.sleep(1)

        # (D) TIPO PRODUTO (Autocomplete MUI com ID="Tipo Produto")
        tipo_prod_input = driver.find_element(By.ID, "Tipo Produto")
        tipo_prod_input.click()
        time.sleep(1)
        # Escolhe a primeira opção usando ARROW_DOWN + ENTER
        tipo_prod_input.send_keys(Keys.ARROW_DOWN)
        tipo_prod_input.send_keys(Keys.ENTER)
        time.sleep(1)

        # (5) CLICAR EM "VISUALIZAR"
        # Use . para buscar qualquer nó de texto dentro do <button>
        visualizar_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Visualizar')]"))
        )
        visualizar_btn.click()
        time.sleep(5)

        # (6) CLICAR NA ABA "LOTE POR NOTA FISCAL"
        try:
            aba_lote_nf = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'LOTE POR NOTA FISCAL')]"))
            )
            aba_lote_nf.click()
            time.sleep(5)
        except Exception as e:
            st.error(f"Não encontrei a aba 'LOTE POR NOTA FISCAL'. Erro: {e}")
            return pd.DataFrame()

        # (7) RASPAR A TABELA (React Virtualized)
        # Cada linha está em <div class="css-1xen6pn" style="position:absolute; ...">
        row_divs = driver.find_elements(
            By.XPATH, "//div[contains(@class,'css-1xen6pn') and contains(@style,'position: absolute')]"
        )

        all_data = []
        for row in row_divs:
            # Cada coluna em <div class="MuiTableCell-root ...">
            cell_divs = row.find_elements(By.XPATH, ".//div[contains(@class,'MuiTableCell-root')]")
            row_data = [cell.text.strip() for cell in cell_divs]
            all_data.append(row_data)

        # Ajuste o nº e nome das colunas conforme a quantidade real
        columns = [
            "LOTE PAGAMENTO", "TIPO LOTE", "CONCESSIONÁRIA", "STATUS",
            "DATA STATUS", "QUANTIDADE PROCESSOS", "VALOR SERVIÇO",
            "VALOR PEÇA", "VALOR TERCEIROS", "VALOR TOTAL",
            "DATA GERAÇÃO", "EMPRESA", "DATA LIBERAÇÃO PAGAMENTO",
            "ÚLTIMO COMENTÁRIO"
        ]

        # Se não for sempre 14 colunas, ajuste. 
        # Se row_data tiver tamanho diferente, isso pode dar erro
        if all_data and len(all_data[0]) == len(columns):
            df = pd.DataFrame(all_data, columns=columns)
        else:
            # Se a contagem não bater, gere algo "genérico"
            df = pd.DataFrame(all_data)

        return df

    finally:
        print("Coletado com sucesso")
        # Se não quiser fechar o navegador a cada execução, comente a linha abaixo:
        # driver.quit()
        pass