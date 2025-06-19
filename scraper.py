import os
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from parser import CourseParser
from unidade import Unidade

class USPScraper:
    def __init__(self, driver_path=None):
        self.driver_path = driver_path or "/home/vitor/drivers/chromedriver-137/chromedriver-linux64/chromedriver"
        self.url = "https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275"
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 120)

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.binary_location = '/mnt/c/Users/vitor/Downloads/chrome-linux64/chrome-linux64/chrome'
        chrome_options.add_argument("--headless=new") # Comente para rodar em modo headless (com janela do navegador)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"ChromeDriver não encontrado em {self.driver_path}.")

        service = Service(self.driver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def scrape(self, num_units_to_scrape=None):
        self.driver.get(self.url)
        time.sleep(3)
        all_units_data = {}

        try:
            initial_dropdown = Select(self.wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade"))))
            total_units = len(initial_dropdown.options)
            unit_count = 0
            for i in range(1, total_units):
                if num_units_to_scrape and unit_count >= num_units_to_scrape:
                    break

                try:
                    unit_dropdown = Select(self.wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade"))))
                    fresh_options = unit_dropdown.options
                    if i >= len(fresh_options):
                        break

                    unit_value = fresh_options[i].get_attribute('value')
                    unit_text = fresh_options[i].text.strip()

                    if not unit_value:
                        continue
                    print("=="*60)
                    print(f"Processando a unidade: {unit_text}")
                    current_unit = all_units_data.get(unit_text)
                    if not current_unit:
                        current_unit = Unidade(nome=unit_text, codigo=unit_value)
                        all_units_data[unit_text] = current_unit

                    unit_dropdown.select_by_index(i)

                except Exception:
                    self.driver.get(self.url)
                    continue

                try:
                    course_dropdown_element = self.wait.until(EC.visibility_of_element_located((By.ID, "comboCurso")))
                    self.wait.until(lambda d: len(Select(course_dropdown_element).options) > 1)
                except TimeoutException:
                    continue

                course_dropdown = Select(course_dropdown_element)
                course_data = [
                    (opt.get_attribute('value'), opt.text.strip())
                    for opt in course_dropdown.options
                    if opt.get_attribute('value') and opt.text.strip() != "Selecione"
                ]

                if not course_data:
                    continue

                for course_value, course_text in course_data:
                    try:
                        print()
                        print()
                        print(f"Lendo dados do curso {course_text} da Unidade {unit_text}")
                        unit_dropdown = Select(self.wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade"))))
                        unit_dropdown.select_by_index(i)
                        course_dropdown_element = self.wait.until(EC.visibility_of_element_located((By.ID, "comboCurso")))
                        self.wait.until(lambda d: len(Select(course_dropdown_element).options) > 1)
                        course_dropdown = Select(course_dropdown_element)
                        course_dropdown.select_by_value(course_value)

                        buscar_button = self.wait.until(EC.element_to_be_clickable((By.ID, "enviar")))
                        buscar_button.click()

                        grade_tab = self.wait.until(EC.element_to_be_clickable((By.ID, "step4-tab")))
                        grade_tab.click()
                        self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='gradeCurricular']//table")))

                        html = self.driver.page_source
                        course_parser = CourseParser(html)
                        course_obj = course_parser.parse()

                        if course_obj:
                            course_obj.unidade_nome = current_unit.nome
                            current_unit.add_curso(course_obj)

                        # Volta para a aba inicial
                        try:
                            tab_inicio = self.wait.until(EC.element_to_be_clickable((By.ID, "step1-tab")))
                            tab_inicio.click()
                            self.wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                        except TimeoutException:
                            self.driver.get(self.url)
                            time.sleep(3)
                            self.wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))

                    except Exception:
                        self.driver.get(self.url)
                        time.sleep(3)
                        self.wait.until(EC.visibility_of_element_located((By.ID, "comboUnidade")))
                        continue
                print()
                print()
                print("=="*60)
                unit_count += 1

        except Exception as e:
            print(f"ERRO CRÍTICO: {e}")
            return []

        return list(all_units_data.values())
