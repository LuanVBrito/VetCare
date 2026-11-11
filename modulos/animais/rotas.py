from flask import Blueprint

from modulos.animais.servico import servico
from transversal.crud import registrar_crud
from transversal.seguranca import ADMIN, PERFIS, RECEPCIONISTA

bp = Blueprint("animais", __name__, url_prefix="/api/animais")
registrar_crud(bp, servico, leitura=PERFIS, escrita=(ADMIN, RECEPCIONISTA))
