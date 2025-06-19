import re
from bs4 import BeautifulSoup
from disciplina import Disciplina
from curso import Curso

class CourseParser:
    def __init__(self, html_content):
        """
        Inicializa o parser com o conteúdo HTML da página do curso.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.course_name = self._extract_course_name()
        self.disciplinas = []

    def _extract_course_name(self):
        """
        Extrai o nome do curso a partir do HTML.
        """
        course_name_element = self.soup.find('span', class_='curso')
        return course_name_element.text.strip() if course_name_element else "Nome do Curso Não Encontrado"

    def _find_semester_rows(self):
        """
        Localiza as linhas de cabeçalho dos semestres no HTML.
        """
        semester_header_cells = self.soup.find_all(
            'td',
            string=re.compile(r'\d+º Semestre Ideal'),
            style=re.compile(r'background-color: rgb\(204, 204, 204\);?')
        )

        if not semester_header_cells:
            # print(r"Tentando encontrar cabeçalhos de semestre apenas por texto '\d+º Semestre Ideal' (sem filtro de estilo).")
            semester_header_cells = self.soup.find_all(
                'td', string=re.compile(r'\d+º Semestre Ideal')
            )

        semesters = [cell.find_parent('tr') for cell in semester_header_cells if cell.find_parent('tr')]

        return semesters

    def _parse_disciplines_from_table(self, table, semester_index):
        """
        Extrai disciplinas de uma tabela de um semestre específico.
        """
        discipline_rows = table.find_all('tr', style=re.compile(r'height: 20px;'))

        if not discipline_rows:
            all_trs_in_table = table.find_all('tr')
            discipline_rows = [
                row for row in all_trs_in_table
                if row.find('td') and not row.find('th') and any(col.get_text(strip=True) for col in row.find_all('td'))
            ]

        else:
            print(f"Encontradas {len(discipline_rows)} linhas de disciplina para o semestre {semester_index + 1}.")

        for disc_row in discipline_rows:
            cols = disc_row.find_all('td')
            if len(cols) >= 4:
                codigo_tag = cols[0].find('a', class_='disciplina')
                codigo = codigo_tag.get('data-coddis') if codigo_tag else 'N/A'
                nome = cols[1].text.strip()
                try:
                    aula = int(cols[2].text.strip()) if cols[2].text.strip() else 0
                except ValueError:
                    aula = 0
                try:
                    trabalho = int(cols[3].text.strip()) if cols[3].text.strip() else 0
                except ValueError:
                    trabalho = 0

                self.disciplinas.append(Disciplina(codigo, nome, aula, trabalho))

    def parse(self):
        """
        Executa o parsing completo e retorna um objeto Curso.
        """
        semesters = self._find_semester_rows()

        for idx, semester_row in enumerate(semesters):
            table = semester_row.find_next('table')
            if table:
                self._parse_disciplines_from_table(table, idx)
                
        return Curso(nome=self.course_name, disciplinas=self.disciplinas)
