# report_writer.py
import os
import re

class ReportWriter:
    def __init__(self, output_dir="relatorios_unidades"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def _sanitize_filename(name):
        s = name.replace(" ", "_")
        s = re.sub(r'[^\w.-]', '', s)
        s = s.strip()
        return s

    def write_unit_report_to_txt(self, all_units_data, all_unique_disciplines=None, discipline_to_courses_map=None):
        """
        Escreve os dados detalhados de cada unidade para arquivos de texto separados.
        Inclui análises sobre disciplinas únicas, aquelas em múltiplos cursos,
        e as mais comuns (globalmente).

        Args:
            all_units_data (list): Lista de objetos Unidade com os dados coletados.
            all_unique_disciplines (dict): Opcional. Dicionário {codigo_disciplina: Disciplina_obj}.
            discipline_to_courses_map (dict): Opcional. Dicionário {codigo_disciplina: [Curso_obj1, Curso_obj2, ...]}.
        """
        print(f"\n[ESCRITA TXT] Iniciando escrita de relatórios por unidade para a pasta: '{self.output_dir}'...")
        
        # --- DEBUG PRINTS INICIAIS DA FUNÇÃO PARA VERIFICAR OS PARÂMETROS RECEBIDOS ---
        print(f"all_units_data recebido (len): {len(all_units_data) if all_units_data else 0}")
        print(f"all_unique_disciplines recebido (len): {len(all_unique_disciplines) if all_unique_disciplines else 0}")
        print(f"discipline_to_courses_map recebido (len): {len(discipline_to_courses_map) if discipline_to_courses_map else 0}")
        # -----------------------------------------------------------------------------

        if not all_units_data:
            print("  Nenhuma unidade para escrever relatórios TXT.")
            return

        # Preparar dados para a seção de disciplinas mais comuns (global)
        discipline_counts_global = []
        if all_unique_disciplines and discipline_to_courses_map:
            for disc_code, courses_list in discipline_to_courses_map.items():
                count = len(courses_list)
                if count > 0:
                    discipline_obj = all_unique_disciplines.get(disc_code)
                    if discipline_obj:
                        discipline_counts_global.append((discipline_obj, count))
            discipline_counts_global.sort(key=lambda x: x[1], reverse=True)
        
        print(f"discipline_counts_global: {len(discipline_counts_global)}")

        for unidade in all_units_data:
            sanitized_unit_name = self._sanitize_filename(unidade.nome)
            file_name = f"{sanitized_unit_name}.txt"
            file_path = os.path.join(self.output_dir, file_name)

            try:
                print(f"Abrindo arquivo para escrita: {file_name}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write(f"  RELATÓRIO DE UNIDADE: {unidade.nome} (Código: {unidade.codigo})\n")
                    f.write("="*80 + "\n\n")

                    if not unidade.cursos:
                        f.write("Nenhum curso encontrado para esta unidade.\n")
                    else:
                        f.write("### 1 & 3. LISTA DE CURSOS E SEUS DETALHES ###\n\n")
                        for curso in unidade.cursos:
                            f.write(f"--- Curso: {curso.nome} ---\n")
                            f.write(f"  Total de Disciplinas: {len(curso.disciplinas)}\n")
                            if curso.disciplinas:
                                f.write("  Disciplinas:\n")
                                for disciplina in curso.disciplinas:
                                    f.write(f"    - {disciplina.codigo}: {disciplina.nome} (Créditos A: {disciplina.creditos_aula}, T: {disciplina.creditos_trabalho})\n")
                            else:
                                f.write("  Nenhuma disciplina encontrada para este curso.\n")
                            f.write("-" * 70 + "\n\n")
                    
                    # --- Seções de Disciplinas Detalhadas ---
                    if all_unique_disciplines and discipline_to_courses_map:
                        f.write("\n" + "="*80 + "\n")
                        f.write("### 4. DETALHES DE DISCIPLINAS ÚNICAS E SEUS CURSOS (Nesta Unidade) ###\n\n")
                        disciplinas_da_unidade_no_mapa = set()
                        
                        for curso_da_unidade in unidade.cursos:
                            for disciplina_do_curso in curso_da_unidade.disciplinas:
                                disciplinas_da_unidade_no_mapa.add(disciplina_do_curso.codigo)

                        if disciplinas_da_unidade_no_mapa:
                            for disc_codigo in sorted(list(disciplinas_da_unidade_no_mapa)):
                                disciplina_obj = all_unique_disciplines.get(disc_codigo)
                                if disciplina_obj:
                                    f.write(f"--- Disciplina: {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) ---\n")
                                    f.write(f"  Créditos Aula: {disciplina_obj.creditos_aula}, Créditos Trabalho: {disciplina_obj.creditos_trabalho}\n")
                                    
                                    cursos_com_disciplina_global = discipline_to_courses_map.get(disc_codigo, [])
                                    
                                    # Filtrar para mostrar apenas os cursos que pertencem a esta unidade
                                    cursos_desta_unidade = [c for c in cursos_com_disciplina_global if c.unidade_nome == unidade.nome]

                                    if cursos_desta_unidade:
                                        f.write(f"  Presente em {len(cursos_desta_unidade)} curso(s) NESTA unidade:\n")
                                        for curso_na_lista in cursos_desta_unidade:
                                            f.write(f"    - {curso_na_lista.nome}\n")
                                    else:
                                         f.write("  Não foi possível encontrar cursos específicos desta unidade para esta disciplina.\n")
                                else:
                                    f.write(f"--- Disciplina com Código: {disc_codigo} --- (Nome não encontrado no mapa de únicas)\n")
                                    f.write(f"  (Detalhes não disponíveis)\n")
                                f.write("-" * 70 + "\n\n")
                        else:
                            f.write("  Nenhuma disciplina detalhada encontrada para esta unidade.\n")
                        
                        f.write("\n" + "="*80 + "\n")
                        f.write("### 5. DISCIPLINAS UTILIZADAS EM MÚLTIPLOS CURSOS (> 1) DESSA UNIDADE ###\n\n")
                        
                        multi_use_disciplines_in_unit = []
                        for disc_codigo in disciplinas_da_unidade_no_mapa:
                            cursos_com_disciplina_global = discipline_to_courses_map.get(disc_codigo, [])
                            cursos_desta_unidade = [c for c in cursos_com_disciplina_global if c.unidade_nome == unidade.nome]
                            if len(cursos_desta_unidade) > 1:
                                multi_use_disciplines_in_unit.append((disc_codigo, cursos_desta_unidade))

                        if multi_use_disciplines_in_unit:
                            for disc_codigo, cursos_list_in_unit in multi_use_disciplines_in_unit:
                                disciplina_obj = all_unique_disciplines.get(disc_codigo)
                                if disciplina_obj:
                                    f.write(f"--- Disciplina: {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) ---\n")
                                    f.write(f"  Presente em {len(cursos_list_in_unit)} cursos NESTA unidade:\n")
                                    for curso_na_lista in cursos_list_in_unit:
                                        f.write(f"    - {curso_na_lista.nome}\n")
                                else:
                                    f.write(f"--- Disciplina com Código: {disc_codigo} --- (Nome não encontrado)\n")
                                    f.write(f"  Presente em {len(cursos_list_in_unit)} cursos NESTA unidade.\n")
                                f.write("-" * 70 + "\n\n")
                        else:
                            f.write("  Nenhuma disciplina utilizada em múltiplos cursos NESTA unidade.\n")

                        # --- Seção: 6. Disciplinas mais comuns (GLOBAL) ---
                        f.write("\n" + "#"*80 + "\n")
                        f.write("### 6. DISCIPLINAS MAIS COMUNS (GLOBALMENTE - Todos os Cursos coletados) ###\n\n")
                        f.write("  Esta seção mostra as disciplinas mais comuns em todos os cursos coletados, não apenas nesta unidade.\n\n")
                        
                        if not discipline_counts_global:
                            f.write("  Nenhuma disciplina encontrada nos dados coletados para esta análise global.\n")
                        else:
                            num_to_display = min(len(discipline_counts_global), 15)
                            f.write(f"  Top {num_to_display} Disciplinas (ordenadas pelo número de cursos em que aparecem):\n")
                            for i, (disciplina_obj, count) in enumerate(discipline_counts_global[:num_to_display]):
                                f.write(f"    {i+1}. {disciplina_obj.nome} (Código: {disciplina_obj.codigo}) - Presente em {count} curso(s).\n")
                        f.write("-" * 70 + "\n\n")


                    f.write("\n" + "="*80 + "\n")
                    f.write("Fim do Relatório da Unidade.\n")
                    f.write("="*80 + "\n")


                print(f"  Escrito: {file_path}")
            except IOError as e:
                print(f"ERRO ao escrever para {file_path}: {e}")
            except Exception as e:
                print(f"ERRO INESPERADO ao escrever para {file_path}: {e}")
                import traceback
                traceback.print_exc()
        print("[ESCRITA TXT] Escrita de arquivos de relatório por unidade concluída.\n")