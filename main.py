import sys
import traceback
from report_writer import ReportWriter
from scraper import USPScraper
from utils import USPUtils

class USPDataRunner:
    def __init__(self, num_units_to_scrape=None):
        self.num_units_to_scrape = num_units_to_scrape
        self.scraper = USPScraper()
        self.all_scraped_data = []
        self.all_unique_disciplines = {}
        self.discipline_to_courses_map = {}

    def parse_command_line_args(self):
        if len(sys.argv) > 1:
            arg_value = sys.argv[1]
            try:
                if arg_value.lower() == "all":
                    self.num_units_to_scrape = None
                    print("Argumento 'all' detectado. coletará todas as unidades.")
                else:
                    self.num_units_to_scrape = int(arg_value)
                    if self.num_units_to_scrape < 1:
                        print(f"Aviso: O número de unidades para coletar ({self.num_units_to_scrape}) deve ser pelo menos 1. Usando valor padrão (todas as unidades).")
                        self.num_units_to_scrape = None
                    else:
                        print(f"Argumento '{self.num_units_to_scrape}' detectado. coletará {self.num_units_to_scrape} unidade(s).")
            except ValueError:
                print(f"Aviso: O argumento '{arg_value}' não é um número inteiro válido nem 'all'. Usando valor padrão (todas as unidades).")
                self.num_units_to_scrape = None
        else:
            print("Nenhum argumento fornecido. coletará todas as unidades por padrão.")

    def preprocess_data(self):
        for unidade in self.all_scraped_data:
            for curso in unidade.cursos:
                curso.unidade_nome = unidade.nome
                for disciplina in curso.disciplinas:
                    if disciplina.codigo not in self.discipline_to_courses_map:
                        self.discipline_to_courses_map[disciplina.codigo] = []
                    if curso not in self.discipline_to_courses_map[disciplina.codigo]:
                        self.discipline_to_courses_map[disciplina.codigo].append(curso)
                    if disciplina.codigo not in self.all_unique_disciplines:
                        self.all_unique_disciplines[disciplina.codigo] = disciplina

    def run(self):
        try:
            self.parse_command_line_args()
            utils = USPUtils()
            print(f"\nIniciando processo de extração. coletará {self.num_units_to_scrape if self.num_units_to_scrape else 'TODAS as'} unidades.")
            self.all_scraped_data = self.scraper.scrape(self.num_units_to_scrape)

            if self.all_scraped_data:
                print("\nProcesso de extração concluído com sucesso!")
                self.preprocess_data()

                print(f"[DEBUG MAIN] all_unique_disciplines (len): {len(self.all_unique_disciplines)}")
                print(f"[DEBUG MAIN] discipline_to_courses_map (len): {len(self.discipline_to_courses_map)}")

                utils.print_scraped_data_summary(self.all_scraped_data, self.all_unique_disciplines, self.discipline_to_courses_map)

                writer = ReportWriter()
                writer.write_unit_report_to_txt(self.all_scraped_data, self.all_unique_disciplines, self.discipline_to_courses_map)
            else:
                print("\nNenhum dado foi coletado ou ocorreu um erro crítico durante a extração.")

        except Exception as e:
            print(f"\nUm erro ocorreu no processo principal do main.py: {e}")
            traceback.print_exc()
        finally:
            self.scraper.driver.quit()
            print("Driver do navegador encerrado.")


def main():
    runner = USPDataRunner()
    runner.run()


if __name__ == "__main__":
    main()