
from flask import jsonify, request

from transversal import db
from transversal.erros import ErroNegocio
from transversal.seguranca import exigir_perfil


class Repositorio:
    def __init__(self, tabela, colunas, ordem="nome"):
        self.tabela, self.colunas, self.ordem = tabela, colunas, ordem

    def listar(self):
        return db.consultar(f"SELECT * FROM {self.tabela} ORDER BY {self.ordem}")

    def buscar(self, id):
        return db.consultar_um(f"SELECT * FROM {self.tabela} WHERE id = ?", (id,))

    def criar(self, dados):
        campos = ", ".join(self.colunas)
        marcas = ", ".join("?" for _ in self.colunas)
        return db.executar(
            f"INSERT INTO {self.tabela} ({campos}) VALUES ({marcas})",
            [dados.get(c) for c in self.colunas],
        )

    def atualizar(self, id, dados):
        atribuicoes = ", ".join(f"{c} = ?" for c in self.colunas)
        db.executar(
            f"UPDATE {self.tabela} SET {atribuicoes} WHERE id = ?",
            [dados.get(c) for c in self.colunas] + [id],
        )

    def excluir(self, id):
        db.executar(f"DELETE FROM {self.tabela} WHERE id = ?", (id,))


class Servico:
    nome_entidade = "Registro"
    obrigatorios = ()

    def __init__(self, repositorio):
        self.repo = repositorio

    def validar(self, dados):
        faltando = [c for c in self.obrigatorios if not str(dados.get(c) or "").strip()]
        if faltando:
            raise ErroNegocio("Campos obrigatórios: " + ", ".join(faltando), 400)

    def saida(self, registro):
        return registro

    def listar(self):
        return [self.saida(r) for r in self.repo.listar()]

    def obter(self, id):
        registro = self.repo.buscar(id)
        if registro is None:
            raise ErroNegocio(f"{self.nome_entidade} não encontrado", 404)
        return registro

    def criar(self, dados):
        self.validar(dados)
        return self.saida(self.obter(self.repo.criar(dados)))

    def atualizar(self, id, dados):
        atual = self.obter(id)
        completo = {**atual, **dados}
        self.validar(completo)
        self.repo.atualizar(id, completo)
        return self.saida(self.obter(id))

    def excluir(self, id):
        self.obter(id)
        self.repo.excluir(id)


def corpo_json():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroNegocio("Envie um corpo JSON válido", 400)
    return dados


def registrar_crud(bp, servico, leitura, escrita):

    @bp.get("")
    @exigir_perfil(*leitura)
    def listar():
        return jsonify(servico.listar())

    @bp.get("/<int:id>")
    @exigir_perfil(*leitura)
    def obter(id):
        return jsonify(servico.saida(servico.obter(id)))

    @bp.post("")
    @exigir_perfil(*escrita)
    def criar():
        return jsonify(servico.criar(corpo_json())), 201

    @bp.put("/<int:id>")
    @exigir_perfil(*escrita)
    def atualizar(id):
        return jsonify(servico.atualizar(id, corpo_json()))

    @bp.delete("/<int:id>")
    @exigir_perfil(*escrita)
    def excluir(id):
        servico.excluir(id)
        return "", 204
