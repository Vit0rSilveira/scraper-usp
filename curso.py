class Curso:
    def __init__(self, nome, disciplinas=None, unidade_nome=None):
        self.nome = nome
        self.disciplinas = disciplinas if disciplinas is not None else []
        self.unidade_nome = unidade_nome