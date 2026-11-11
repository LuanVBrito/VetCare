import datetime
from functools import wraps

import jwt
from flask import current_app, g, request

from transversal import db
from transversal.erros import ErroNegocio

ADMIN = "ADMINISTRADOR"
RECEPCIONISTA = "RECEPCIONISTA"
VETERINARIO = "VETERINARIO"
PERFIS = (ADMIN, RECEPCIONISTA, VETERINARIO)


def criar_token(usuario_id):
    expira = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, current_app.config["SECRET_KEY"], algorithm="HS256")


def exigir_perfil(*perfis_permitidos):

    def decorador(funcao):
        @wraps(funcao)
        def interna(*args, **kwargs):
            cabecalho = request.headers.get("Authorization", "")
            if not cabecalho.startswith("Bearer "):
                raise ErroNegocio("Não autenticado", 401)
            try:
                dados = jwt.decode(cabecalho[7:], current_app.config["SECRET_KEY"], algorithms=["HS256"])
                usuario = db.consultar_um("SELECT id, nome, perfil FROM usuarios WHERE id = ?", (int(dados["sub"]),))
            except (jwt.InvalidTokenError, ValueError, KeyError):
                raise ErroNegocio("Token inválido ou expirado", 401)
            if usuario is None:
                raise ErroNegocio("Usuário não existe mais", 401)
            if perfis_permitidos and usuario["perfil"] not in perfis_permitidos:
                raise ErroNegocio("Seu perfil não tem permissão para esta operação", 403)
            g.usuario = usuario
            return funcao(*args, **kwargs)

        return interna

    return decorador
