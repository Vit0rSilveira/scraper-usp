import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import parser 
from unidade import Unidade  

# ====================================================================
# SUA FUNÇÃO INICIAR_DRIVER QUE COMPROVADAMENTE FUNCIONA
# ====================================================================
def iniciar_driver(driver_path=None):
    chrome_options = Options()
    chrome_options.binary_location = '/mnt/c/Users/vitor/Downloads/chrome-linux64/chrome-linux64/chrome'
    chrome_options.add_argument("--headless=new") # Descomente para rodar em modo headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    driver_path = driver_path or "/home/vitor/drivers/chromedriver-137/chromedriver-linux64/chromedriver"
    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"ChromeDriver não encontrado em {driver_path}. Por favor, verifique o caminho.")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
# ====================================================================


def scrape_data(driver, num_units_to_scrape=None):
    """
    Navega pela página da USP para raspar dados de unidades e cursos.

    Args:
        driver: O WebDriver do Selenium.
        num_units_to_scrape (int, optional): Número máximo de unidades para raspar.
                                             Se None, raspa todas.

    Returns:
        list[Unidade]: Uma lista de objetos Unidade populados com seus cursos e disciplinas.
    """
    url = "https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275" 
    driver.get(url)

    time.sleep(3) # Dá um tempo para a página carregar completamente
    print(f"DEBUG: scrape_data chamada com num_units_to_scrape={num_units_to_scrape} (tipo: {type(num_units_to_scrape)})")
    wait = WebDriverWait(driver, 60)

    all_units_data = {} # Dicionário para armazenar Unidades por nome, evitando duplicatas.

    try:
        print("Obtendo contagem inicial de unidades para definir o escopo do loop...")
        initial_unit_dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
        initial_unit_dropdown = Select(initial_unit_dropdown_element)
        total_unit_options_count = len(initial_unit_dropdown.options)
        print(f"Total inicial de {total_unit_options_count} opções de unidades encontradas.")

        unit_count = 0
        # Iterar pelo índice para sempre buscar a opção de unidade fresca
        # Começa de 1 para pular a opção "Selecione"
        for i in range(1, total_unit_options_count): 
            if num_units_to_scrape and unit_count >= num_units_to_scrape:
                print(f"Limite de {num_units_to_scrape} unidades processadas. Encerrando.")
                break

            unit_value = None
            unit_text = None
            
            try:
                # CRÍTICO: Re-localizar o dropdown de unidades e obter opções frescas para CADA UNIDADE
                print(f"--- Iniciando processamento para a Unidade na posição {i+1} ---")
                print("Re-localizando dropdown de unidades (comboUnidade) para a próxima iteração da unidade...")
                unit_dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                unit_dropdown = Select(unit_dropdown_element)
                fresh_unit_options = unit_dropdown.options # Obtém as opções mais recentes
                
                if i >= len(fresh_unit_options): # Verificação de segurança: se o número de opções mudou
                    print(f"AVISO: Índice de unidade {i} fora do alcance das opções atuais ({len(fresh_unit_options)}). Pode indicar mudança inesperada na página. Encerrando loop de unidades.")
                    break

                unit_option_element = fresh_unit_options[i]
                unit_value = unit_option_element.get_attribute('value')
                unit_text = unit_option_element.text.strip()

                if not unit_value: # Pula opções sem valor (como "Selecione" se for incluído por engano)
                    print(f"    Pulando opção inválida de unidade (valor vazio): '{unit_text}'")
                    continue
                
                print(f"--- Processando unidade: {unit_text} (Opção {i+1}/{total_unit_options_count}) ---")

                current_unit_obj = all_units_data.get(unit_text)
                if not current_unit_obj:
                    current_unit_obj = Unidade(nome=unit_text, codigo=unit_value) 
                    all_units_data[unit_text] = current_unit_obj

                # Seleciona a unidade atual
                unit_dropdown.select_by_index(i)
                print(f"    Unidade '{unit_text}' selecionada.")

            except (StaleElementReferenceException, TimeoutException) as e:
                print(f"❌ ERRO ao preparar a unidade {i+1} ('{unit_text}' - valor temporário): {e}. Recarregando a página e pulando para a próxima unidade.")
                driver.get(url)
                wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                continue # Pula para a próxima iteração da unidade
            except Exception as e:
                temp_unit_name = unit_text if unit_text is not None else "Valor Desconhecido"
                print(f"❌ ERRO INESPERADO ao preparar a unidade {i+1} ('{temp_unit_name}' - valor temporário): {e}. Recarregando a página e pulando para a próxima unidade.")
                driver.get(url)
                wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                continue # Pula para a próxima iteração da unidade

            # --- Início do processamento dos cursos para a unidade atual ---

            print("    Esperando dropdown de cursos (ID 'comboCurso')...")
            try:
                course_dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, "comboCurso")))
                # Espera até que o dropdown de cursos tenha mais de uma opção (ou seja, os cursos foram carregados)
                wait.until(lambda driver_instance: len(Select(course_dropdown_element).options) > 1)
                print("    Dropdown de cursos populado com opções além do 'Selecione'.")
            except TimeoutException:
                print(f"    ❌ TIMEOUT: O dropdown de cursos para a unidade '{unit_text}' não carregou cursos a tempo (apenas 'Selecione' encontrado). Pulando esta unidade.")
                continue 
            
            # Coleta os dados (value, text) dos cursos para evitar StaleElementReferenceException
            course_dropdown = Select(course_dropdown_element)
            course_options_data = [] 
            for opt in course_dropdown.options:
                value = opt.get_attribute('value')
                text = opt.text.strip()
                if value and text != "Selecione": # Garante que não é a opção "Selecione" ou vazia
                    course_options_data.append((value, text))
            
            print(f"    Total de opções no dropdown (incluindo 'Selecione'): {len(course_dropdown.options)}.")
            print(f"    Total de cursos válidos encontrados para '{unit_text}': {len(course_options_data)}.")

            if not course_options_data:
                print(f"    Nenhum curso válido encontrado para a unidade '{unit_text}'. Pulando para a próxima unidade.")
                continue 

            for course_value, course_text in course_options_data:
                print(f"\n      Processando curso: {course_text} da Unidade {unit_text}")

                try:
                    # 1. Re-localiza o dropdown de unidades e seleciona a unidade atual (sempre a partir do elemento fresco)
                    print("        Re-localizando comboUnidade para seleção do curso...")
                    unit_dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                    unit_dropdown = Select(unit_dropdown_element)
                    unit_dropdown.select_by_index(i) # 'i' é o índice da unidade atual do loop externo
                    print("        Unidade re-selecionada para garantir o contexto do curso.")

                    # 2. Espera e re-localiza o dropdown de cursos, esperando que ele seja populado
                    print("        Re-localizando comboCurso para seleção do curso...")
                    course_dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, "comboCurso")))
                    wait.until(lambda driver_instance: len(Select(course_dropdown_element).options) > 1) 
                    print("        ComboCurso re-populado.")

                    # 3. Cria o objeto Select e seleciona o curso
                    course_dropdown = Select(course_dropdown_element)
                    course_dropdown.select_by_value(course_value) # Seleciona pelo valor (que é imutável)
                    print(f"        Curso '{course_text}' selecionado pelo valor.")


                    buscar_button = wait.until(EC.element_to_be_clickable((By.ID, "enviar")))
                    print("        Clicando no botão 'Buscar' pelo ID 'enviar'...")
                    
                    buscar_button.click()

                    print("        Aguardando que a aba 'Grade curricular' (ID 'step4-tab') esteja visível e clicável, confirmando carregamento do conteúdo de detalhes...")
                    grade_curricular_tab = wait.until(EC.element_to_be_clickable((By.ID, "step4-tab")))
                    print("        Conteúdo de detalhes carregado. Aba 'Grade curricular' visível.")

                    print("        Tentando clicar na aba 'Grade curricular' pelo ID 'step4-tab' para exibir o conteúdo...")
                    grade_curricular_tab.click()
                    print("        Aba 'Grade curricular' clicada. Aguardando conteúdo...")

                    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='gradeCurricular']//table")))
                    print("        Conteúdo da Grade Curricular (tabela de disciplinas) visível.")
                    
                    html_content_with_grade = driver.page_source
                    
                    course_obj = parser.extract_course_details(html_content_with_grade)

                    if course_obj:
                        # ATENÇÃO: LINHA ADICIONADA AQUI para atribuir o nome da unidade ao curso
                        course_obj.unidade_nome = current_unit_obj.nome # <-- NOVA LINHA AQUI
                        current_unit_obj.add_curso(course_obj) # Adiciona o curso à unidade atual
                        print("        Dados da grade curricular coletados com sucesso.")
                    else:
                        print(f"        ERRO: O parser retornou None para o curso '{course_text}'")

                    # PASSO CRÍTICO: Voltar para a aba do formulário para selecionar o próximo curso
                    print("        Iniciando retorno à aba de seleção de cursos ('step1-tab') para o próximo curso...")
                    try:
                        # Assumindo que 'step1-tab' é a aba que contém os dropdowns.
                        initial_form_tab = wait.until(EC.element_to_be_clickable((By.ID, "step1-tab"))) 
                        initial_form_tab.click()
                        # Pequena espera para os elementos de dropdown ficarem visíveis e interageveis
                        wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade"))) 
                        print("        Aba de seleção de cursos clicada e dropdowns visíveis para próxima iteração.")
                    except TimeoutException:
                        print("        AVISO: Timeout ao clicar na aba inicial. Recarregando a página como fallback para garantir estado limpo.")
                        driver.get(url) # Fallback para recarga completa se o clique na aba falhar
                        wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade"))) # Espera pelo dropdown após recarga
                    print("        Retorno à aba inicial concluído.")
                    
                except TimeoutException as e:
                    print(f"❌ TIMEOUT: Elemento não encontrado ou não clicável para o curso '{course_text}': {e}. Recarregando a página e pulando para o próximo curso.")
                    # Em caso de timeout, um recarregamento completo da página é a recuperação mais segura.
                    driver.get(url)
                    wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                    continue # Continua para o próximo curso
                
                except StaleElementReferenceException as e:
                    print(f"        StaleElementReferenceException para o curso '{course_text}': {e}. Recarregando a página para tentar o próximo curso.")
                    driver.get(url)
                    wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                    continue # Continua para o próximo curso
                    
                except Exception as e:
                    print(f"        ERRO INESPERADO ao processar curso '{course_text}': {e}. Recarregando a página e tentando o próximo curso.")
                    driver.get(url)
                    wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                    continue

            unit_count += 1
            print(f"--- Unidade '{unit_text}' processada por completo. Preparando para a próxima unidade... ---") 

    except Exception as e:
        print(f"ERRO CRÍTICO no processo de raspagem (nível superior, fora dos loops internos): {e}")
        return [] 

    return list(all_units_data.values())