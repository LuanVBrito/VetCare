from flask import Blueprint, g, jsonify

from modulos.auth import servico
from transversal.crud import corpo_json
from transversal.seguranca import exigir_perfil

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.post("/login")
def login():
    dados = corpo_json()
    return jsonify(servico.login(dados.get("email"), dados.get("senha")))


@bp.get("/me")
@exigir_perfil()
def me():
    return jsonify(g.usuario)
