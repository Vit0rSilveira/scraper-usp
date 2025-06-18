from curso import Curso
class Unidade:
    def __init__(self, nome, codigo, cursos=None):
        self.nome = nome
        self.codigo = codigo
        self.cursos = cursos if cursos is not None else []

    def add_curso(self, curso):
        """Adiciona um objeto Curso à lista de cursos desta Unidade."""
        if isinstance(curso, Curso):
            self.cursos.append(curso)
        else:
            print(f"AVISO: Tentativa de adicionar um objeto que não é Curso à Unidade: {curso}")