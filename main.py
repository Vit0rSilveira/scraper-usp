"""
    To run this project it's important install some libraries
    Run in terminal linux:
    1) sudo apt install chromium-chromedriver
    2) python3 -m venv venv
    3) source venv/bin/activate
    4) 
        pip install selenium
        pip install beautifulsoup4
        pip install webdriver-manager

"""
# ====================================================================
# FUNÇÕES DE RELATÓRIO E SUMÁRIO (NÃO MUDOU NESTA VERSÃO)
# ====================================================================

# A função sanitize_filename FOI REMOVIDA daqui, agora está em ReportWriter

# main.py
import scraper
import os
import time
import sys
import re # Mantenha o import 're' pois ele é usado na função print_scraped_data_summary
from report_writer import ReportWriter

# ====================================================================
# FUNÇÕES DE RELATÓRIO E SUMÁRIO
# (AGORA ACEITAM OS DADOS PRÉ-PROCESSADOS COMO PARÂMETROS)
# ====================================================================

# ATENÇÃO: ESTA FUNÇÃO FOI MODIFICADA PARA ACEITAR all_unique_disciplines E discipline_to_courses_map
def print_scraped_data_summary(all_units_data, all_unique_disciplines, discipline_to_courses_map):
    """
    Imprime um resumo detalhado dos dados raspados, incluindo listas de cursos,
    disciplinas e análises de disciplinas em múltiplos cursos.

    Args:
        all_units_data (list): Uma lista de objetos Unidade contendo todos os dados raspados.
        all_unique_disciplines (dict): Dicionário {codigo_disciplina: Disciplina_obj}.
        discipline_to_courses_map (dict): Dicionário {codigo_disciplina: [Curso_obj1, Curso_obj2, ...]}.
    """
    print("\n" + "="*80)
    print("                      --- Resumo Completo dos Dados Raspados ---")
    print("="*80)

    # --- Contadores Globais (agora baseados nos dados pré-processados) ---
    total_units = len(all_units_data)
    total_courses = sum(len(unit.cursos) for unit in all_units_data)
    total_disciplines_occurrence = sum(len(curso.disciplinas) for unit in all_units_data for curso in unit.cursos)
    
    # --- VISÃO GERAL ---
    print("\n" + "-"*80)
    print("                     VISÃO GERAL DOS DADOS RASPADOS")
    print("-" * 80)
    print(f"  Total de Unidades Processadas: {total_units}")
    print(f"  Total de Cursos Encontrados: {total_courses}")
    print(f"  Total de Disciplinas Únicas Encontradas: {len(all_unique_disciplines)}")
    print(f"  Total de Disciplinas (contando repetições em cursos): {total_disciplines_occurrence}")
    print("-" * 80)

    # 1. Lista de cursos por unidades (e 3. Dados de todos os cursos)
    print("\n" + "="*80)
    print("             1 & 3. LISTA DE CURSOS POR UNIDADE E SEUS DADOS DETALHADOS")
    print("=" * 80)
    if not all_units_data:
        print("  Nenhuma unidade encontrada nos dados raspados.")
    else:
        for unidade in all_units_data:
            print(f"\n--- Unidade: {unidade.nome} (Código: {unidade.codigo}) ---")
            if not unidade.cursos:
                print("  Nenhum curso encontrado para esta unidade.")
            else:
                for curso in unidade.cursos:
                    print(f"  > Curso: {curso.nome}")
                    print(f"    Total de Disciplinas: {len(curso.disciplinas)}")
                    if curso.disciplinas:
                        print("    Disciplinas:")
                        for disciplina in curso.disciplinas:
                            print(f"      - {disciplina.codigo}: {disciplina.nome} (Créditos A: {disciplina.creditos_aula}, T: {disciplina.creditos_trabalho})")
                    else:
                        print("    Nenhuma disciplina encontrada para este curso.")
            print("-" * 70) # Separador para unidades

    # 2. Dados de um determinado curso (Já coberto pela listagem detalhada acima)
    print("\n" + "="*80)
    print("             2. DADOS DE UM DETERMINADO CURSO (Detalhes acima)")
    print("   Os dados de cursos específicos podem ser consultados na seção '1 & 3' acima.")
    print("=" * 80)

    # 4. Dados de uma disciplina, inclusive quais cursos ela faz parte
    print("\n" + "="*80)
    print("              4. DETALHES DE DISCIPLINAS ÚNICAS E SEUS CURSOS")
    print("=" * 80)
    if not all_unique_disciplines:
        print("  Nenhuma disciplina única encontrada nos dados raspados.")
    else:
        for disc_codigo, disciplina_obj in all_unique_disciplines.items():
            print(f"\n--- Disciplina: {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) ---")
            print(f"  Créditos Aula: {disciplina_obj.creditos_aula}, Créditos Trabalho: {disciplina_obj.creditos_trabalho}")
            
            cursos_com_disciplina = discipline_to_courses_map.get(disc_codigo, [])
            if cursos_com_disciplina:
                print(f"  Presente em {len(cursos_com_disciplina)} curso(s):")
                for curso_na_lista in cursos_com_disciplina:
                    print(f"    - {curso_na_lista.nome} (Unidade: {curso_na_lista.unidade_nome})")
            else:
                print("  Não foi possível encontrar em quais cursos esta disciplina aparece no mapa (erro interno ou dados inconsistentes).")
            print("-" * 70) # Separador para disciplinas

    # 5. Disciplinas que são usadas em mais de um curso
    print("\n" + "="*80)
    print("            5. DISCIPLINAS UTILIZADAS EM MÚLTIPLOS CURSOS (> 1)")
    print("=" * 80)
    found_multi_use = False
    if not all_unique_disciplines:
        print("  Nenhuma disciplina única encontrada nos dados raspados.")
    else:
        for disc_codigo, cursos_list in discipline_to_courses_map.items():
            if len(cursos_list) > 1:
                found_multi_use = True
                disciplina_obj = all_unique_disciplines.get(disc_codigo)
                if disciplina_obj:
                    print(f"\n--- Disciplina: {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) ---")
                    print(f"  Presente em {len(cursos_list)} cursos:")
                    for curso_na_lista in cursos_list:
                        print(f"    - {curso_na_lista.nome} (Unidade: {curso_na_lista.unidade_nome})")
                else:
                    print(f"\n--- Disciplina com Código: {disc_codigo} --- (Nome não encontrado no mapa de únicas)")
                    print(f"  Presente em {len(cursos_list)} cursos:")
                    for curso_na_lista in cursos_list:
                        print(f"    - {curso_na_lista.nome} (Unidade: {curso_na_lista.unidade_nome})")
                print("-" * 70) # Separador
    
    if not found_multi_use:
        print("  Nenhuma disciplina encontrada que seja utilizada em múltiplos cursos.")
    print("=" * 80)
    
    # 6. Disciplinas mais comuns (em mais cursos)
    print("\n" + "="*80)
    print("                6. DISCIPLINAS MAIS COMUNS (PRESENTES EM MAIS CURSOS)")
    print("=" * 80)

    # A lógica de calculation de discipline_counts é movida para o main, mas aqui
    # ela é espelhada para o print, caso os dados já venham pré-processados.
    # No entanto, a forma como main.py chama print_scraped_data_summary já garante que
    # discipline_counts_global será passado (que é o mesmo que discipline_counts aqui).
    # Vamos recriar discipline_counts aqui para garantir que a saída do terminal seja exatamente como o esperado.
    discipline_counts = []
    for disc_code, courses_list in discipline_to_courses_map.items():
        count = len(courses_list)
        if count > 0: # Incluir apenas disciplinas que foram encontradas em pelo menos um curso
            discipline_obj = all_unique_disciplines.get(disc_code)
            if discipline_obj:
                discipline_counts.append((discipline_obj, count))

    # Ordenar em ordem decrescente pelo número de cursos
    discipline_counts.sort(key=lambda x: x[1], reverse=True)

    if not discipline_counts:
        print("  Nenhuma disciplina encontrada nos dados raspados.")
    else:
        # Imprimir o top N, ou todas se houver menos que N
        num_to_display = min(len(discipline_counts), 15) # Exibir o top 15, por exemplo
        print(f"  Top {num_to_display} Disciplinas (ordenadas pelo número de cursos em que aparecem):")
        for i, (disciplina_obj, count) in enumerate(discipline_counts[:num_to_display]):
            print(f"    {i+1}. {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) - Presente em {count} curso(s).")
    print("=" * 80)
    print("\nFim do Resumo Detalhado.")
    print("="*80 + "\n")


# ====================================================================
# FUNÇÃO PRINCIPAL
# ====================================================================
def main():
    driver = None
    try:
        driver = scraper.iniciar_driver()
        
        num_units_to_scrape = None 

        if len(sys.argv) > 1:
            arg_value = sys.argv[1]
            try:
                if arg_value.lower() == "all":
                    num_units_to_scrape = None
                    print("Argumento 'all' detectado. Raspará todas as unidades.")
                else:
                    num_units_to_scrape = int(arg_value)
                    if num_units_to_scrape < 1:
                        print(f"Aviso: O número de unidades para raspar ({num_units_to_scrape}) deve ser pelo menos 1. Usando valor padrão (todas as unidades).")
                        num_units_to_scrape = None
                    else:
                        print(f"Argumento numérico '{num_units_to_scrape}' detectado. Raspará {num_units_to_scrape} unidade(s).")
            except ValueError:
                print(f"Aviso: O argumento '{arg_value}' não é um número inteiro válido nem 'all'. Usando valor padrão (todas as unidades).")
                num_units_to_scrape = None
        else:
            print("Nenhum argumento fornecido. Raspará todas as unidades por padrão.")

        print(f"\nIniciando processo de raspagem. Raspará {num_units_to_scrape if num_units_to_scrape else 'TODAS as'} unidades.")
        
        all_scraped_data = scraper.scrape_data(driver, num_units_to_scrape=num_units_to_scrape)
        
        if all_scraped_data:
            print("\nProcesso de raspagem concluído com sucesso!")
            
            # --- Pré-processa os dados para os relatórios TXT e Console (CALCULADO UMA ÚNICA VEZ AQUI) ---
            discipline_to_courses_map = {}
            all_unique_disciplines = {}

            for unidade in all_scraped_data:
                for curso in unidade.cursos:
                    # Adiciona o nome da unidade ao objeto Curso para referência futura nos relatórios
                    curso.unidade_nome = unidade.nome 
                    for disciplina in curso.disciplinas:
                        if disciplina.codigo not in discipline_to_courses_map:
                            discipline_to_courses_map[disciplina.codigo] = []
                        # Evita adicionar o mesmo objeto curso múltiplas vezes para a mesma disciplina
                        if curso not in discipline_to_courses_map[disciplina.codigo]: 
                            discipline_to_courses_map[disciplina.codigo].append(curso)
                        
                        if disciplina.codigo not in all_unique_disciplines:
                            all_unique_disciplines[disciplina.codigo] = disciplina
            # ------------------------------------------------------------------------------------------

            # ADICIONADO PRINTS DE DEBUG AQUI NO MAIN PARA VERIFICAR OS DADOS ANTES DE PASSAR
            print(f"[DEBUG MAIN] all_unique_disciplines (len antes de passar para summary/writer): {len(all_unique_disciplines)}")
            print(f"[DEBUG MAIN] discipline_to_courses_map (len antes de passar para summary/writer): {len(discipline_to_courses_map)}")


            # CHAMA A FUNÇÃO DE RESUMO, PASSANDO OS DADOS PRÉ-PROCESSADOS
            print_scraped_data_summary(all_scraped_data, all_unique_disciplines, discipline_to_courses_map) 

            # --- AGORA USANDO A CLASSE ReportWriter PARA ESCREVER ARQUIVOS TXT ---
            writer = ReportWriter()
            # Passa os dados pré-processados para o writer também
            writer.write_unit_report_to_txt(all_scraped_data, all_unique_disciplines, discipline_to_courses_map)
            # ----------------------------------------------------------------------

        else:
            print("\nNenhum dado foi raspado ou ocorreu um erro crítico durante a raspagem.")

    except Exception as e:
        print(f"\nUm erro ocorreu no processo principal do main.py: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("Driver do navegador encerrado.")

if __name__ == "__main__":
    main()