from modulos.tutores.repositorio import repositorio
from transversal.crud import Servico
from transversal.erros import ErroNegocio


class ServicoTutor(Servico):
    nome_entidade = "Tutor"
    obrigatorios = ("nome", "cpf")

    def validar(self, dados):
        super().validar(dados)
        cpf = "".join(c for c in str(dados["cpf"]) if c.isdigit())
        if len(cpf) != 11:
            raise ErroNegocio("CPF deve ter 11 dígitos", 400)
        dados["cpf"] = cpf


servico = ServicoTutor(repositorio)
