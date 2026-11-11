from flask import g
from werkzeug.security import generate_password_hash

from modulos.usuarios.repositorio import repositorio
from transversal.crud import Servico
from transversal.erros import ErroNegocio
from transversal.seguranca import PERFIS


def _hash_da_senha(senha):
    if len(senha or "") < 6:
        raise ErroNegocio("A senha deve ter ao menos 6 caracteres", 400)
    return generate_password_hash(senha)


class ServicoUsuario(Servico):
    nome_entidade = "Usuário"
    obrigatorios = ("nome", "email", "perfil")

    def validar(self, dados):
        super().validar(dados)
        if "@" not in dados["email"]:
            raise ErroNegocio("E-mail inválido", 400)
        if dados["perfil"] not in PERFIS:
            raise ErroNegocio("Perfil deve ser um de: " + ", ".join(PERFIS), 400)

    def saida(self, registro):
        return {k: v for k, v in registro.items() if k != "senha_hash"}

    def criar(self, dados):
        return super().criar({**dados, "senha_hash": _hash_da_senha(dados.get("senha"))})

    def atualizar(self, id, dados):
        dados = dict(dados)
        senha = dados.pop("senha", None)
        dados.pop("senha_hash", None)  # nunca aceitar hash vindo do cliente
        if senha:
            dados["senha_hash"] = _hash_da_senha(senha)
        return super().atualizar(id, dados)

    def excluir(self, id):
        if id == g.usuario["id"]:
            raise ErroNegocio("Você não pode excluir o próprio usuário", 409)
        super().excluir(id)


servico = ServicoUsuario(repositorio)
