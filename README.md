# Manual de Configuração e Uso do Projeto de extração de Dados da USP

Este manual foi criado para guiar qualquer pessoa, mesmo sem conhecimento prévio do projeto, na configuração, execução e compreensão básica do sistema de extração de dados da USP. Ele detalha cada passo, desde a preparação do ambiente Python até a execução da extração e geração de relatórios.

## Sumário

1.  **Visão Geral do Projeto**
2.  **Requisitos Mínimos do Sistema**
3.  **Configuração do Ambiente de Desenvolvimento**
    a.  Instalando o Python (Se Necessário)
    b.  Criando e Ativando um Ambiente Virtual (RECOMENDADO!)
    c.  Instalando as Bibliotecas Python do Projeto
4.  **Configuração do Navegador Google Chrome para o Selenium**
    a.  Por Que o Chrome é Necessário?
    b.  Instalando o Navegador Google Chrome
    c.  Entendendo e Configurando o ChromeDriver (Gerenciado Automaticamente)
    d.  **ATENÇÃO: Configurando o Caminho do Executável do Chrome (`binary_location`)**
        i.   Cenário 1: Chrome Instalado em Local Padrão (Recomendado - Abordagem Adotada)
        ii.  Cenário 2: Chrome Instalado em Local Personalizado/Portátil (Como Configurar)
5.  **Executando o Projeto de extração de Dados**
    a.  Como Rodar o Script
    b.  Saída no Terminal
    c.  Relatórios Salvos em Pastas (Por Unidade)
6.  **Estrutura de Pastas e Arquivos do Projeto**
7.  **Solução de Problemas Comuns *FAQ***

---

## 1. Visão Geral do Projeto

Este projeto consiste em um script Python que utiliza a biblioteca Selenium para automatizar a navegação em um portal de informações da Universidade de São Paulo (USP) e extrair dados sobre os cursos e suas respectivas disciplinas. Os dados coletados são então processados e organizados em relatórios legíveis, facilitando a análise e consulta.

O objetivo principal é fornecer uma forma eficiente para coletar informações acadêmicas de forma estruturada, que de outra forma seriam de difícil acesso manual em larga escala.

## 2. Requisitos Mínimos do Sistema

Para executar este projeto, você precisará de:

* **Sistema Operacional:** Windows, macOS ou Linux (testado e otimizado para Windows via WSL/Linux e linux nativo).
* **Python:** Versão 3.8 ou superior.
* **Navegador Web:** Google Chrome instalado.
* **Conexão com a Internet:** Necessário para baixar dependências e para a extração de dados.

## 3. Configuração do Ambiente de Desenvolvimento

### a. Instalando o Python (Se Necessário)

Se você ainda não tem Python instalado, siga as instruções abaixo para o seu sistema operacional:

* **Windows:** Baixe o instalador em [python.org](https://www.python.org/downloads/windows/) e certifique-se de marcar a opção "Add Python to PATH" durante a instalação.
* **macOS:** O macOS geralmente vem com Python pré-instalado, mas é recomendado usar o `brew` para uma versão mais recente: `brew install python`.
* **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install python3 python3-pip`.

### b. Criando e Ativando um Ambiente Virtual

Ambientes virtuais isolam as dependências do seu projeto, evitando conflitos com outras instalações Python no seu sistema.

1.  **Navegue até a pasta do projeto:**
    ```bash
    cd /caminho/para/o/seu/projeto
    ```
2.  **Crie o ambiente virtual:**
    ```bash
    python3 -m venv venv
    ```
3.  **Ative o ambiente virtual:**
    * **Windows (CMD/PowerShell):**
        ```bash
        .\venv\Scripts\activate
        ```
    * **Linux/macOS (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```
    Você saberá que o ambiente está ativo quando `(venv)` aparecer no início da linha de comando.

### c. Instalando as Bibliotecas Python do Projeto

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install -i requeriments.txt
```
Observações para Linux (especialmente WSL/Ubuntu):

Se você estiver em um ambiente Linux (como WSL no Windows ou uma distribuição Linux nativa), pode ser necessário instalar importantes adicionais do sistema para o ChromeDriver funcionar corretamente, especialmente para headless mode.

```bash
sudo apt update
sudo apt install chromium-chromedriver # Ou google-chrome-stable se for o navegador completo
sudo apt install libglib2.0-0 libnss3 libxss1 libatk-bridge2.0-0 libgtk-3-0
```

## 4. Configuração do Navegador Google Chrome para o Selenium
a. Por Que o Chrome é Necessário?
O Selenium interage com um navegador web real para simular a navegação de um usuário. O Google Chrome é um dos navegadores mais populares e bem suportados pelo Selenium, e o projeto foi desenvolvido com ele em mente.

b. Instalando o Navegador Google Chrome
Certifique-se de ter o Google Chrome instalado em seu sistema.

Windows: Baixe em google.com/chrome.
macOS: Baixe em google.com/chrome.
Linux (Ubuntu/Debian):
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -f
```

c. Entendendo e Configurando o ChromeDriver (Gerenciado Automaticamente)
O ChromeDriver é uma ponte que permite ao Selenium se comunicar com o navegador Chrome. Antigamente, era preciso baixar o ChromeDriver manualmente e posicioná-lo em um local específico.

A boa notícia: Seu projeto já usa uma biblioteca chamada webdriver-manager. Esta biblioteca faz todo o trabalho pesado por você!

Na primeira vez que você rodar o script (e se a versão do seu Chrome mudar), o webdriver-manager irá:
Detectar a versão do seu Google Chrome instalado.
Baixar a versão correta e compatível do ChromeDriver automaticamente.
Armazenar o ChromeDriver em cache para uso futuro.
O que você precisa fazer: Apenas certificar-se de ter webdriver-manager instalado (como fizemos no Passo 3.b) e ter uma conexão com a internet na primeira execução.

d. ATENÇÃO: Configurando o Caminho do Executável do Chrome (binary_location)
Esta é a parte mais importante e comum de causar erros se não for configurada corretamente. O arquivo scraper.py tem uma linha que informa ao Selenium onde encontrar o navegador Chrome em si.

Abra o arquivo scraper.py no seu editor de texto (VS Code, Sublime Text, Bloco de Notas, etc.). Procure pela função iniciar_driver e a linha que começa com chrome_options.binary_location = ....

```python
# Trecho relevante do seu scraper.py:
def iniciar_driver(driver_path=None): # Note que 'driver_path' não é usado aqui para o chromedriver.
    chrome_options = Options()
    chrome_options.binary_location = '/mnt/c/Users/vitor/Downloads/chrome-linux64/chrome-linux64/chrome' # Exemplo de caminho
    chrome_options.add_argument("--headless=new") # Comente para rodar em modo headless (com janela do navegador)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0")
```

Você tem duas opções principais para definir este caminho:

i. Opção 1: Chrome Instalado em Local Padrão (Recomendado - Abordagem Adotada)
Esta é a abordagem altamente recomendada e geralmente a mais simples, pois o Chrome se instala em caminhos bem conhecidos nos sistemas operacionais. Se o seu Google Chrome estiver instalado em um dos locais padrão do sistema (como C:\Program Files\Google\Chrome\Application\chrome.exe no Windows, /Applications/Google Chrome.app/Contents/MacOS/Google Chrome no macOS, ou /usr/bin/google-chrome no Linux), você pode comentar ou remover a linha chrome_options.binary_location = ....

Como fazer:
Altere a linha do scraper.py de:
```python
chrome_options.binary_location = '/mnt/c/Users/vitor/Downloads/chrome-linux64/chrome-linux64/chrome'
```
para:
```
# chrome_options.binary_location = '/mnt/c/Users/vitor/Downloads/chrome-linux64/chrome-linux64/chrome' # Comente esta linha
# Ou simplesmente remova a linha, pois o webdriver-manager encontrará automaticamente o executável padrão.
```
Neste projeto, esta é a abordagem que o ajuda a adotar, assumindo que o Chrome está instalado em um local padrão e acessível pelo sistema. Isso simplifica a configuração para a maioria dos usuários, confiando na habilidade do Selenium de encontrar o binário automaticamente quando binary_location não é explicitamente definido.

ii. Opção 2: Chrome Instalado em Local Personalizado/Portátil (Como Configurar)
Se você instalou o Chrome em um diretório não padrão (por exemplo, em uma pasta portátil, em um diretório específico da sua máquina, ou em um ambiente WSL onde o caminho é diferente do Windows), então você precisará especificar o caminho exato para o executável do Chrome.

Como fazer:

Substitua o valor da linha chrome_options.binary_location pelo caminho completo e correto para o executável do seu Google Chrome.

Exemplos de Caminhos:

Windows:

```Python
chrome_options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
# OU (se for uma instalação portátil ou diferente)
# chrome_options.binary_location = 'D:\\MeuChrome\\chrome.exe'
Importante: Use barras duplas \\ ou barras simples / para caminhos no Windows para evitar problemas com caracteres de escape. Ex: C:/Program Files/Google/Chrome/Application/chrome.exe.
```
Linux (ou WSL no Windows, apontando para um executável Linux):

```python
chrome_options.binary_location = '/usr/bin/google-chrome' # Para instalação apt padrão
# OU (se tiver um Chrome portátil no Linux/WSL)
# chrome_options.binary_location = '/home/seu_usuario/Downloads/chrome-linux64/chrome-linux64/chrome'
# OU (se tiver um executável Windows acessado do WSL)
# chrome_options.binary_location = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
```

Atenção em WSL: Se o seu Chrome estiver instalado no Windows e você estiver executando o script do WSL, você precisará usar o caminho do Windows com a notação /mnt/c/ (ou a letra da unidade correspondente). O caminho atualmente presente no scraper.py (/mnt/c/Users/vitor/Downloads/chrome-linux64/chrome-linux64/chrome) sugere o projeto usa uma instalação portátil do Chrome no contexto Linux/WSL.

Verifique o Caminho do Seu Chrome:

Windows: Clique com o botão direito no atalho do Chrome, vá em "Propriedades" e copie o "Destino".
Linux: Use which google-chrome ou whereis google-chrome no terminal para encontrar o caminho padrão. Para instalações completas, você saberá onde o colocou.
Lembre-se de salvar o arquivo scraper.py após fazer a alteração!

## 5. Executando o Projeto de extração de Dados

### a. Como Rodar o Script

1.  **Certifique-se de que o ambiente virtual esteja ativado** (veja Passo 3.b).
2.  **Navegue até a pasta raiz do projeto** onde o arquivo `main.py` está localizado.
3.  **Execute o script principal:**
    Você pode executar o script main.py de duas maneiras, dependendo da sua necessidade:
    1. Coletar dados de todas as unidades da USP
    Para coletar informações de todas as unidades da USP, basta executar o script sem argumentos adicionais:    
    ```bash
    python main.py
    ```
    2. Coletar dados de um número específico de unidades
    Se você quiser limitar a coleta a uma quantidade específica de unidades, você pode passar o número desejado como um argumento. Por exemplo, para coletar dados de 5 unidades, use:
    ```bash
    python main.py 5
    ```
### b. Saída no Terminal

Durante a execução, o script exibirá informações no terminal sobre o progresso da extração de dados, incluindo:

* Mensagens de inicialização do driver.
* Processamento de cada unidade (Escola, Instituto).
* Processamento de cada curso dentro das unidades.
* Mensagens de depuração ("DEBUG") que podem ajudar a entender o fluxo.
* Um resumo final dos dados coletados (listas de unidades, cursos, disciplinas únicas, disciplinas em múltiplos cursos, e as mais comuns globalmente).

### c. Relatórios Salvos em Pastas (Por Unidade)

Além da saída no terminal, o projeto gera relatórios detalhados em arquivos de texto (`.txt`).

* Todos os relatórios são salvos em uma pasta chamada `relatorios_unidades` (ou o nome que você definir na classe `ReportWriter` no `report_writer.py`).
* Um arquivo `.txt` separado é criado para cada unidade processada (ex: `Escola_de_Artes_Ciencias_e_Humanidades__EACH_.txt`).
* Cada relatório de unidade contém:
    * Detalhes da unidade.
    * Lista de todos os cursos oferecidos pela unidade e suas disciplinas.
    * Uma lista de todas as disciplinas únicas encontradas **nesta unidade**.
    * Uma análise das disciplinas que aparecem em múltiplos cursos **desta unidade**.
    * Uma lista das disciplinas mais comuns (top 15) em **todos os cursos coletados globalmente**.

## 6. Estrutura de Pastas e Arquivos do Projeto

O projeto é organizado da seguinte forma:
```

seu_projeto/
├── venv/            # Ambiente virtual Python (gerado automaticamente)
├── main.py          # Ponto de entrada principal do script
├── scraper.py       # Contém a lógica de automação web com Selenium
├── parser.py        # Responsável por extrair e interpretar dados do HTML
├── models.py        # Define as classes de dados (Unidade, Curso, Disciplina)
├── report_writer.py # Lógica para escrever os relatórios em arquivos .txt
├── queries.py       # (Opcional) Funções de consulta e análise de dados em memória
├── relatorios_unidades/ # Pasta onde os relatórios .txt serão salvos (criada automaticamente)
│   ├── Escola_de_Artes_Ciencias_e_Humanidades__EACH_.txt
│   └── Outra_Unidade_Processada.txt
├── README.md        # Este manual
└── (outros arquivos de teste/configurações se houver)
```

## 7. Solução de Problemas Comuns (FAQ)

* **`WebDriverException: Message: 'chromedriver' executable needs to be in PATH.`**
    * **Causa:** Embora `webdriver-manager` cuide disso, pode haver um problema de permissão, um download corrompido, ou um cache antigo.
    * **Solução:** Certifique-se de que `webdriver-manager` está instalado (`pip install webdriver-manager`). Se o problema persistir, tente desinstalar e reinstalar `webdriver-manager`. Em último caso, pode ser um problema de cache do webdriver-manager; tente limpar o cache do `webdriver-manager` (geralmente em `~/.wdm/` ou `C:\Users\SEU_USUARIO\.wdm\`).

* **`selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start: exited abnormally.`**
    * **Causa:** O navegador Chrome não conseguiu iniciar corretamente. Isso pode ser devido a um caminho incorreto para o executável do Chrome, navegador travado, ou dependências faltando (especialmente no Linux).
    * **Solução:**
        1.  **Verifique `chrome_options.binary_location`** no `scraper.py` (Passo 4.d). Este é o motivo mais comum.
        2.  **Reinicie o computador** ou mate os processos do Chrome/ChromeDriver. Em Linux/macOS, você pode tentar matar processos do Chrome/ChromeDriver com `pkill chrome` e `pkill chromedriver` no terminal.
        3.  **Em Linux:** Verifique se as dependências do sistema (mencionadas no passo 3.c) estão instaladas.
        4.  **Descomente `--headless=new`** no `scraper.py` se você estiver em um servidor sem interface gráfica, ou se a janela do Chrome estiver causando problemas.

* **`ValueError: No such file or directory: '...'` (apontando para um caminho de arquivo)**
    * **Causa:** Você especificou um caminho incorreto para o executável do Chrome em `chrome_options.binary_location` ou para outro arquivo no seu código.
    * **Solução:** Revise o caminho no seu `scraper.py` (`chrome_options.binary_location`) e certifique-se de que o arquivo existe nesse local e que seu usuário tem permissão para acessá-lo.

* **`ImportError: cannot import name 'HTML' from 'weasyprint'` ou erros relacionados a `WeasyPrint` no Linux:**
    * **Causa:** A biblioteca `WeasyPrint` ou suas dependências de sistema não foram instaladas corretamente.
    * **Solução:** Revise o **Passo 3.c** e certifique-se de que todas as dependências do sistema (especialmente para Linux) foram instaladas com `sudo apt-get install ...` e que `pip install WeasyPrint` foi bem-sucedido.

* **O terminal mostra `(venv)` mas os comandos `pip` ou `python` não funcionam (ou instalam globalmente):**
    * **Causa:** O ambiente virtual não foi ativado corretamente ou você está usando um comando como `pip3` ou `python3` que pode estar apontando para a instalação global.
    * **Solução:** Certifique-se de que ativou o ambiente virtual com o comando correto para seu sistema (Passo 2.b). Depois de ativado, use apenas `pip` e `python` (sem o 3) para garantir que você está usando as versões dentro do ambiente virtual.