from datetime import date

from modulos.animais.repositorio import repositorio
from transversal.crud import Servico
from transversal.erros import ErroNegocio


class ServicoAnimal(Servico):
    nome_entidade = "Animal"
    obrigatorios = ("nome", "especie", "tutor_id")

    def validar(self, dados):
        super().validar(dados)
        dados["sexo"] = dados.get("sexo") or None
        if dados["sexo"] not in (None, "M", "F"):
            raise ErroNegocio("Sexo deve ser M ou F", 400)
        dados["data_nascimento"] = dados.get("data_nascimento") or None
        if dados["data_nascimento"]:
            try:
                nascimento = date.fromisoformat(dados["data_nascimento"])
            except ValueError:
                raise ErroNegocio("Data de nascimento inválida (use AAAA-MM-DD)", 400)
            if nascimento > date.today():
                raise ErroNegocio("Data de nascimento não pode ser futura", 400)


servico = ServicoAnimal(repositorio)
