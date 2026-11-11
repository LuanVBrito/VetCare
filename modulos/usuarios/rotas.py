from flask import Blueprint

from modulos.usuarios.servico import servico
from transversal.crud import registrar_crud
from transversal.seguranca import ADMIN

bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")
registrar_crud(bp, servico, leitura=(ADMIN,), escrita=(ADMIN,))
