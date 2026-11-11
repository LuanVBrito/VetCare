from flask import Blueprint

from modulos.veterinarios.servico import servico
from transversal.crud import registrar_crud
from transversal.seguranca import ADMIN, PERFIS

bp = Blueprint("veterinarios", __name__, url_prefix="/api/veterinarios")
registrar_crud(bp, servico, leitura=PERFIS, escrita=(ADMIN,))
