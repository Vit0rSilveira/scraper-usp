import re
from bs4 import BeautifulSoup
from disciplina import Disciplina
from curso import Curso

def extract_course_details(html_content):
    """
    Extrai detalhes de um curso específico de uma string HTML.
    
    Args:
        html_content (str): A string contendo o código HTML da página de detalhes do curso.

    Returns:
        Curso: Um objeto Curso populado com o nome do curso e suas disciplinas.
               Retorna um Curso com lista de disciplinas vazia se nenhuma for encontrada.
    """
    # Cria o objeto BeautifulSoup a partir da string HTML fornecida
    soup = BeautifulSoup(html_content, 'html.parser')

    # Encontra o nome do curso (esta parte já está funcionando)
    course_name_element = soup.find('span', class_='curso')
    course_name = course_name_element.text.strip() if course_name_element else "Nome do Curso Não Encontrado"

    disciplinas = [] # Lista para armazenar as disciplinas encontradas

    # Buscando cabeçalhos de semestre por texto e estilo (esta parte está funcionando)
    semester_header_cells = soup.find_all('td', 
                                         string=re.compile(r'\d+º Semestre Ideal'), 
                                         style=re.compile(r'background-color: rgb\(204, 204, 204\);?'))
    
    if not semester_header_cells:
        print("DEBUG: Parser - Tentando encontrar cabeçalhos de semestre apenas por texto '\d+º Semestre Ideal' (sem filtro de estilo).")
        semester_header_cells = soup.find_all('td', string=re.compile(r'\d+º Semestre Ideal'))

    semesters = [cell.find_parent('tr') for cell in semester_header_cells if cell.find_parent('tr')]
    
    if not semesters:
        print("DEBUG: Parser - Nenhum cabeçalho de semestre (linha cinza com 'Semestre Ideal') encontrado na página.")
    else:
        print(f"DEBUG: Parser - Encontrados {len(semesters)} cabeçalhos de semestre (linhas cinzas com 'Semestre Ideal').")

    # Itera sobre cada cabeçalho de semestre encontrado
    for sem_idx, semester_row in enumerate(semesters):
        # >>> ALTERAÇÃO AQUI: USANDO find_next() EM VEZ DE find_next_sibling() <<<
        # find_next() procura o próximo elemento <<table>> em qualquer lugar após o semester_row
        discipline_table = semester_row.find_next('table')

        if discipline_table: # Se uma tabela de disciplinas foi encontrada
            print(f"DEBUG: Parser - Tabela de disciplinas encontrada para o semestre {sem_idx+1}.")

            # Tenta encontrar todas as linhas de disciplina dentro da tabela com o estilo específico
            discipline_rows = discipline_table.find_all('tr', style=re.compile(r'height: 20px;'))
            
            # NOVO FALLBACK: Se nenhuma linha foi encontrada com o estilo, tenta um método mais genérico
            if not discipline_rows:
                print(f"DEBUG: Parser - Nenhuma linha de disciplina (com 'height: 20px;') encontrada na tabela após o semestre {sem_idx+1}. Tentando encontrar todas as 'tr' e filtrar por conteúdo.")
                
                all_trs_in_table = discipline_table.find_all('tr')
                discipline_rows = [
                    row for row in all_trs_in_table 
                    if row.find('td') # A linha deve ter pelo menos uma célula de dados
                    and not row.find('th') # A linha não deve ser uma linha de cabeçalho (que teria <th>)
                    and any(col.get_text(strip=True) for col in row.find_all('td')) # Pelo menos uma célula deve ter texto
                ]
                
                if not discipline_rows:
                     print(f"DEBUG: Parser - Ainda nenhuma linha de disciplina válida encontrada para o semestre {sem_idx+1} após o fallback.")
                else:
                    print(f"DEBUG: Parser - Encontradas {len(discipline_rows)} linhas de disciplina para o semestre {sem_idx+1} após o fallback.")
            else:
                print(f"DEBUG: Parser - Encontradas {len(discipline_rows)} linhas de disciplina para o semestre {sem_idx+1} usando filtro de estilo inicial.")

            # Itera sobre cada linha de disciplina encontrada e extrai os dados
            for disc_row in discipline_rows:
                cols = disc_row.find_all('td')
                if len(cols) >= 4: # Garante que a linha tem colunas suficientes para os dados esperados
                    codigo_disciplina_tag = cols[0].find('a', class_='disciplina')
                    codigo_disciplina = codigo_disciplina_tag.get('data-coddis') if codigo_disciplina_tag else 'N/A'
                    
                    nome_disciplina = cols[1].text.strip()
                    
                    try:
                        creditos_aula = int(cols[2].text.strip()) if cols[2].text.strip() else 0
                    except ValueError:
                        creditos_aula = 0
                    try:
                        creditos_trabalho = int(cols[3].text.strip()) if cols[3].text.strip() else 0
                    except ValueError:
                        creditos_trabalho = 0

                    disciplinas.append(Disciplina(codigo_disciplina, nome_disciplina, creditos_aula, creditos_trabalho))
        else:
            print(f"DEBUG: Parser - Nenhuma tabela de disciplinas encontrada após o cabeçalho do semestre {sem_idx+1} usando find_next('table').")
    
    return Curso(nome=course_name, disciplinas=disciplinas)