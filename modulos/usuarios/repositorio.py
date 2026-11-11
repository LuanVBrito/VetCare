from transversal import db
from transversal.crud import Repositorio

repositorio = Repositorio("usuarios", ["nome", "email", "senha_hash", "perfil"])


def buscar_por_email(email):
    return db.consultar_um("SELECT * FROM usuarios WHERE email = ?", (email,))
