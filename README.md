# Notifica Saúde 🚀

Automação para monitorização de atualizações nos portais do DATASUS e CNES.

## ✨ Funcionalidades
- **Monitorização Inteligente:** Deteta mudanças em sites estáticos e dinâmicos (Angular).
- **Notificação Visual:** Envia e-mails em HTML com tabelas comparativas.
- **Ação Rápida:** Botão de download direto para SCNES e links de acesso para sistemas FTP.
- **Eficiência:** Só notifica se houver uma alteração real detetada.

## 🛠️ Tecnologias
- Python 3
- Selenium (EdgeDriver)
- BeautifulSoup4
- SMTP (Gmail)

## 🚀 Configuração do Ambiente

Recomendo o uso de um ambiente virtual para manter as dependências isoladas.

### No Windows (PowerShell ou CMD)
1. **Criar o ambiente virtual:**
```powershell
  python -m venv venv
```

2. **Ativar o ambiente:**
```powershell
.\venv\Scripts\activate
```

3. **Instalar as dependências:**
```powershell
pip install -r requirements.txt
```

### No Linux (Ubuntu/Debian/Arch)

1. **Instalar suporte a venv (se necessário):**
   
  - *Ubuntu/Debian:* `sudo apt install python3-venv`

3. **Criar o ambiente virtual:**
  ```bash
  python3 -m venv venv
  ```

3. **Ativar o ambiente:**
  ```bash
  source venv/bin/activate
  ```

4. **Instalar as dependências:**
  ```bash
  pip install -r requirements.txt

  ```

> **Nota para Linux:** Para o SCNES (Selenium), certifique-se de ter o navegador instalado (Edge ou Chrome) e o driver correspondente no seu PATH. No Windows, o script já tenta gerenciar isso automaticamente.

---

### Por que usar isso?

* **No Linux:** Se você tentar usar o `pip` globalmente (sem o venv), muitas distribuições modernas (como o Ubuntu 23+ ou Arch) vão te dar um erro de "Externally Managed Environment". O ambiente virtual resolve isso.
* **No Windows:** Facilita muito se você precisar mover a pasta do script para outro PC. É só levar a pasta, ativar o venv e pronto.
