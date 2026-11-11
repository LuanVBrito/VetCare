from flask import Blueprint

from modulos.tutores.servico import servico
from transversal.crud import registrar_crud
from transversal.seguranca import ADMIN, PERFIS, RECEPCIONISTA

bp = Blueprint("tutores", __name__, url_prefix="/api/tutores")
registrar_crud(bp, servico, leitura=PERFIS, escrita=(ADMIN, RECEPCIONISTA))
