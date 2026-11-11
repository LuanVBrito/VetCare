import os
import sqlite3

from flask import Flask, jsonify, redirect

from modulos.animais.rotas import bp as animais_bp
from modulos.auth.rotas import bp as auth_bp
from modulos.tutores.rotas import bp as tutores_bp
from modulos.usuarios.rotas import bp as usuarios_bp
from modulos.veterinarios.rotas import bp as veterinarios_bp
from transversal.db import close_db, init_db
from transversal.erros import ErroNegocio

RAIZ = os.path.dirname(os.path.abspath(__file__))


def criar_app(config=None):
    app = Flask(__name__, static_folder=os.path.join(RAIZ, "frontend"), static_url_path="")
    app.config["DATABASE"] = os.path.join(RAIZ, "vetcare.db")
    app.config["SECRET_KEY"] = os.environ.get("VETCARE_SECRET", "troque-esta-chave-em-producao-0123456789")
    app.config.update(config or {})

    app.teardown_appcontext(close_db)
    init_db(app)

    for bp in (auth_bp, usuarios_bp, tutores_bp, animais_bp, veterinarios_bp):
        app.register_blueprint(bp)

    @app.errorhandler(ErroNegocio)
    def erro_negocio(erro):
        return jsonify({"erro": erro.mensagem}), erro.status

    @app.errorhandler(sqlite3.IntegrityError)
    def erro_integridade(erro):
        texto = str(erro)
        if "UNIQUE" in texto:
            mensagem = "Já existe um registro com esse valor (CPF, CRMV ou e-mail repetido)"
        elif "FOREIGN KEY" in texto:
            mensagem = "Vínculo inválido: tutor inexistente ou registro em uso por outro cadastro (ex.: tutor com animais)"
        else:
            mensagem = "Dados inválidos"
        return jsonify({"erro": mensagem}), 409

    @app.get("/")
    def inicio():
        return redirect("/index.html")

    return app


if __name__ == "__main__":
    criar_app().run(host="127.0.0.1", port=5000, debug=False)
