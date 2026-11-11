from werkzeug.security import check_password_hash

from modulos.usuarios.repositorio import buscar_por_email
from transversal.erros import ErroNegocio
from transversal.seguranca import criar_token


def login(email, senha):
    usuario = buscar_por_email((email or "").strip())
    # mesma mensagem para e-mail inexistente e senha errada (não revela quais e-mails existem)
    if usuario is None or not check_password_hash(usuario["senha_hash"], senha or ""):
        raise ErroNegocio("E-mail ou senha inválidos", 401)
    return {
        "token": criar_token(usuario["id"]),
        "usuario": {"id": usuario["id"], "nome": usuario["nome"], "perfil": usuario["perfil"]},
    }
