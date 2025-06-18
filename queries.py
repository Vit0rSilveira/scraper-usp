# queries.py
from unidade import  Unidade
def list_courses_by_units(all_units: list[Unidade]):
    # ... (código anterior) ...
    for unit in all_units:
        # ... (print da unidade) ...
        if unit.cursos: # Garante que há cursos para iterar
            for curso in unit.cursos: # <--- ESTE LOOP DEVE ITERAR POR TODOS OS CURSOS
                print(f"  Curso: {curso.nome}")
                # ... (outras informações do curso) ...
        else:
            print(f"  Nenhum curso encontrado para esta unidade.")

# Exemplo de função adicional para consultas
def find_course_by_name(units, course_name_to_find):
    """Encontra e imprime detalhes de um curso específico pelo nome."""
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
            if i < 5: # Limita para não imprimir muitas
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