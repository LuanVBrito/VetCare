import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil     TEXT NOT NULL CHECK (perfil IN ('ADMINISTRADOR','RECEPCIONISTA','VETERINARIO'))
);
CREATE TABLE IF NOT EXISTS tutores (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT NOT NULL,
    cpf      TEXT NOT NULL UNIQUE,
    telefone TEXT,
    email    TEXT,
    endereco TEXT
);
CREATE TABLE IF NOT EXISTS veterinarios (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    crmv         TEXT NOT NULL UNIQUE,
    especialidade TEXT,
    telefone     TEXT
);
CREATE TABLE IF NOT EXISTS animais (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT NOT NULL,
    especie         TEXT NOT NULL,
    raca            TEXT,
    sexo            TEXT CHECK (sexo IN ('M','F')),
    data_nascimento TEXT,
    tutor_id        INTEGER NOT NULL REFERENCES tutores(id) ON DELETE RESTRICT
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def consultar(sql, parametros=()):
    return [dict(linha) for linha in get_db().execute(sql, parametros).fetchall()]


def consultar_um(sql, parametros=()):
    linha = get_db().execute(sql, parametros).fetchone()
    return dict(linha) if linha else None


def executar(sql, parametros=()):
    conexao = get_db()
    try:
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    return cursor.lastrowid


def init_db(app):
    with app.app_context():
        conexao = get_db()
        conexao.executescript(ESQUEMA)
        if conexao.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
            senha = os.environ.get("VETCARE_ADMIN_SENHA", "admin123")
            conexao.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
                ("Administrador", "admin@vetcare.com", generate_password_hash(senha), "ADMINISTRADOR"),
            )
            conexao.commit()
