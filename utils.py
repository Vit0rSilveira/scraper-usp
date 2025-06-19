from unidade import Unidade

class USPUtils:

    @staticmethod
    def list_courses_by_units(all_units: list[Unidade]):
        for unit in all_units:
            print(f"\nUnidade: {unit.nome} (Código: {unit.codigo})")
            if unit.cursos:
                for curso in unit.cursos:
                    print(f"  Curso: {curso.nome}")
            else:
                print("  Nenhum curso encontrado para esta unidade.")

    @staticmethod
    def find_course_by_name(units: list[Unidade], course_name_to_find: str):
        found_course = None
        for unit in units:
            for course in unit.cursos:
                if course.nome.lower() == course_name_to_find.lower():
                    found_course = course
                    break
            if found_course:
                break

        if found_course:
            print(f"\n--- Detalhes do Curso: {found_course.nome} ---")
            print(f"  Unidade: {found_course.unidade.nome if found_course.unidade else 'N/A'}")
            print(f"  Duração Ideal: {found_course.duracao_ideal} semestres")
            print(f"  Informações Específicas: {found_course.informacoes_especificas}")
            print(f"  Disciplinas Obrigatórias: {len(found_course.disciplinas_obrigatorias)}")
            for i, disc in enumerate(found_course.disciplinas_obrigatorias):
                if i < 5:
                    print(f"    - {disc.nome} ({disc.codigo})")
                else:
                    print("    ... (mais disciplinas obrigatórias)")
                    break
            print(f"  Disciplinas Optativas Eletivas: {len(found_course.disciplinas_optativas_eletivas)}")
            for i, disc in enumerate(found_course.disciplinas_optativas_eletivas):
                if i < 5:
                    print(f"    - {disc.nome} ({disc.codigo})")
                else:
                    print("    ... (mais disciplinas optativas eletivas)")
                    break
        else:
            print(f"\nCurso '{course_name_to_find}' não encontrado.")

    @staticmethod
    def print_scraped_data_summary(all_units_data, all_unique_disciplines, discipline_to_courses_map):
        print("\n" + "="*80)
        print("                      --- Resumo Completo dos Dados coletados ---")
        print("="*80)

        total_units = len(all_units_data)
        total_courses = sum(len(unit.cursos) for unit in all_units_data)
        total_disciplines_occurrence = sum(len(curso.disciplinas) for unit in all_units_data for curso in unit.cursos)

        print("\n" + "-"*80)
        print("                     VISÃO GERAL DOS DADOS coletados")
        print("-" * 80)
        print(f"  Total de Unidades Processadas: {total_units}")
        print(f"  Total de Cursos Encontrados: {total_courses}")
        print(f"  Total de Disciplinas Únicas Encontradas: {len(all_unique_disciplines)}")
        print(f"  Total de Disciplinas (contando repetições em cursos): {total_disciplines_occurrence}")
        print("-" * 80)

        print("\n" + "="*80)
        print("             1 & 3. LISTA DE CURSOS POR UNIDADE E SEUS DADOS DETALHADOS")
        print("=" * 80)
        if not all_units_data:
            print("  Nenhuma unidade encontrada nos dados coletados.")
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
                print("-" * 70)

        print("\n" + "="*80)
        print("             2. DADOS DE UM DETERMINADO CURSO (Detalhes acima)")
        print("   Os dados de cursos específicos podem ser consultados na seção '1 & 3' acima.")
        print("=" * 80)

        print("\n" + "="*80)
        print("              4. DETALHES DE DISCIPLINAS ÚNICAS E SEUS CURSOS")
        print("=" * 80)
        if not all_unique_disciplines:
            print("  Nenhuma disciplina única encontrada nos dados coletados.")
        else:
            for disc_codigo, disciplina_obj in all_unique_disciplines.items():
                print(f"\n--- Disciplina: {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) ---")
                print(f"  Créditos Aula: {disciplina_obj.creditos_aula}, Créditos Trabalho: {disciplina_obj.creditos_trabalho}")
                cursos_com_disciplina = discipline_to_courses_map.get(disc_codigo, [])
                if cursos_com_disciplina:
                    print(f"  Presente em {len(cursos_com_disciplina)} curso(s):")
                    for curso in cursos_com_disciplina:
                        print(f"    - {curso.nome} (Unidade: {curso.unidade_nome})")
                else:
                    print("  Não foi possível encontrar em quais cursos esta disciplina aparece.")
                print("-" * 70)

        print("\n" + "="*80)
        print("            5. DISCIPLINAS UTILIZADAS EM MÚLTIPLOS CURSOS (> 1)")
        print("=" * 80)
        found_multi_use = False
        for disc_codigo, cursos_list in discipline_to_courses_map.items():
            if len(cursos_list) > 1:
                found_multi_use = True
                disciplina_obj = all_unique_disciplines.get(disc_codigo)
                if disciplina_obj:
                    print(f"\n--- Disciplina: {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) ---")
                    print(f"  Presente em {len(cursos_list)} cursos:")
                    for curso in cursos_list:
                        print(f"    - {curso.nome} (Unidade: {curso.unidade_nome})")
                    print("-" * 70)
        if not found_multi_use:
            print("  Nenhuma disciplina encontrada que seja utilizada em múltiplos cursos.")
        print("=" * 80)

        print("\n" + "="*80)
        print("                6. DISCIPLINAS MAIS COMUNS (PRESENTES EM MAIS CURSOS)")
        print("=" * 80)
        discipline_counts = []
        for disc_code, courses_list in discipline_to_courses_map.items():
            count = len(courses_list)
            if count > 0:
                discipline_obj = all_unique_disciplines.get(disc_code)
                if discipline_obj:
                    discipline_counts.append((discipline_obj, count))
        discipline_counts.sort(key=lambda x: x[1], reverse=True)
        if not discipline_counts:
            print("  Nenhuma disciplina encontrada nos dados coletados.")
        else:
            num_to_display = min(len(discipline_counts), 15)
            print(f"  Top {num_to_display} Disciplinas:")
            for i, (disciplina_obj, count) in enumerate(discipline_counts[:num_to_display]):
                print(f"    {i+1}. {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) - Presente em {count} curso(s).")
        print("=" * 80)
        print("\nFim do Resumo Detalhado.")
        print("="*80 + "\n")
