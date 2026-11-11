from modulos.veterinarios.repositorio import repositorio
from transversal.crud import Servico


class ServicoVeterinario(Servico):
    nome_entidade = "Veterinário"
    obrigatorios = ("nome", "crmv")


servico = ServicoVeterinario(repositorio)
