import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib3
import json
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

# --- CONFIGURAÇÕES ---
EMAIL_REMETENTE = "preencha para seu contexto"
EMAIL_SENHA = "preencha para seu contexto"
EMAIL_DESTINATARIO = "preencha para seu contexto"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ESTADO = os.path.join(CAMINHO_ATUAL, "monitor_estado.json")

def enviar_email(assunto, corpo_html):
    msg = MIMEMultipart()
    msg['Subject'] = assunto
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO
    msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
        print("E-mail com links ajustados enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def obter_soup(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, verify=False, timeout=30, headers=headers)
        return BeautifulSoup(r.text, 'html.parser')
    except:
        return None

def obter_dados_scnes():
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    try:
        driver = webdriver.Edge(options=options)
        driver.get("https://cnes.datasus.gov.br/pages/downloads/aplicativos.jsp")
        versao = ""
        link_final = "https://cnes.datasus.gov.br/pages/downloads/aplicativos.jsp"
        
        for _ in range(15):
            try:
                elemento = driver.find_element(By.ID, "testeOutstanding-title")
                texto = elemento.text.strip()
                if re.search(r'\d+', texto):
                    versao = texto
                    link_tag = driver.find_element(By.XPATH, "//a[contains(@href, 'ATUALIZACAO.ZIP')]")
                    link_final = link_tag.get_attribute('href')
                    break
            except: pass
            time.sleep(2)
        return versao, link_final
    except: return None, None
    finally:
        try: driver.quit()
        except: pass

def monitorar():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r', encoding='utf-8') as f:
            estado_antigo = json.load(f)
    else:
        estado_antigo = {}

    novo_estado = {}
    alertas_html = ""

    def montar_linha(label, chave, valor_novo, link, direto=False):
        valor_antigo = estado_antigo.get(chave, "Nenhum dado")
        if valor_antigo != valor_novo:
            texto_botao = "BAIXAR AGORA" if direto else "ABRIR PÁGINA"
            cor_botao = "#28a745" if direto else "#1f5dc2"
            
            btn_html = f'<a href="{link}" target="_blank" style="background-color: {cor_botao}; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block;">{texto_botao}</a>'
            
            return f"""
            <tr>
                <td style="padding: 12px; border: 1px solid #ddd;"><b>{label}</b></td>
                <td style="padding: 12px; border: 1px solid #ddd; color: #666;">{valor_antigo}</td>
                <td style="padding: 12px; border: 1px solid #ddd; color: #d9534f; font-weight: bold;">{valor_novo}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{btn_html}</td>
            </tr>
            """
        return ""

    soup_sia = obter_soup("https://sia.datasus.gov.br/principal/index.php")
    if soup_sia:
        tabela = next((t for t in soup_sia.find_all('table') if "COMPETÊNCIA" in t.text), None)
        if tabela:
            v = tabela.find_all('tr')[1].get_text(" ", strip=True)
            alertas_html += montar_linha("SIA Competência", "sia_comp", v, "https://sia.datasus.gov.br/principal/index.php")
            novo_estado['sia_comp'] = v

    links_ftp = {
        'BPA': ("https://sia.datasus.gov.br/versao/listar_ftp_bpa.php", "BPAMAG"),
        'FPO': ("https://sia.datasus.gov.br/versao/listar_ftp_fpo.php", "FPOMAG_Atualiza"),
        'RAAS': ("https://sia.datasus.gov.br/versao/listar_ftp_raas.php", "RAAS_"),
        'SIA_EXE': ("https://sia.datasus.gov.br/versao/listar_ftp_sia.php", "BDSIA")
    }

    for chave, (url_pagina, prefixo) in links_ftp.items():
        soup = obter_soup(url_pagina)
        if soup:
            link_tag = soup.find('a', string=lambda t: t and prefixo in t)
            if link_tag:
                nome = link_tag.get_text(strip=True)
                data = link_tag.find_parent('td').find_next_sibling('td').get_text(strip=True)
                info = f"{nome} ({data})"
                alertas_html += montar_linha(chave, chave, info, url_pagina, direto=False)
                novo_estado[chave] = info

    v_scnes, l_scnes = obter_dados_scnes()
    if v_scnes and "{{" not in v_scnes:
        alertas_html += montar_linha("SCNES", "scnes", v_scnes, l_scnes, direto=True)
        novo_estado['scnes'] = v_scnes
    else:
        novo_estado['scnes'] = estado_antigo.get('scnes')

    if alertas_html:
        corpo_final = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 750px; margin: auto; background: white; border-radius: 8px; border: 1px solid #ddd; overflow: hidden;">
                <div style="background: #1f5dc2; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin:0; font-size: 22px;">Atualização de Sistemas DATASUS</h1>
                </div>
                <div style="padding: 20px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding:10px; border:1px solid #ddd; text-align:left;">Sistema</th>
                                <th style="padding:10px; border:1px solid #ddd; text-align:left;">Anterior</th>
                                <th style="padding:10px; border:1px solid #ddd; text-align:left;">Nova Versão / Data</th>
                                <th style="padding:10px; border:1px solid #ddd;">Ação</th>
                            </tr>
                        </thead>
                        <tbody>{alertas_html}</tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        enviar_email("🔔 ALERTA: Atualização DATASUS", corpo_final)

    with open(ARQUIVO_ESTADO, 'w', encoding='utf-8') as f:
        json.dump(novo_estado, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    monitorar()