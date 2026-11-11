import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import criar_app  


class TesteApi(unittest.TestCase):
    def setUp(self):
        self.arquivo = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.arquivo.close()
        self.app = criar_app({"DATABASE": self.arquivo.name, "TESTING": True})
        self.c = self.app.test_client()
        self.admin = self.login("admin@vetcare.com", "admin123")

    def tearDown(self):
        os.unlink(self.arquivo.name)

    def login(self, email, senha):
        r = self.c.post("/api/login", json={"email": email, "senha": senha})
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        return {"Authorization": "Bearer " + r.get_json()["token"]}

    def novo_usuario(self, perfil, email):
        r = self.c.post("/api/usuarios", headers=self.admin,
                        json={"nome": perfil, "email": email, "perfil": perfil, "senha": "segredo1"})
        self.assertEqual(r.status_code, 201)
        return self.login(email, "segredo1")

    def novo_tutor(self, cpf="123.456.789-01"):
        r = self.c.post("/api/tutores", headers=self.admin, json={"nome": "Maria", "cpf": cpf})
        self.assertEqual(r.status_code, 201, r.get_data(as_text=True))
        return r.get_json()

    def test_login_invalido(self):
        r = self.c.post("/api/login", json={"email": "admin@vetcare.com", "senha": "errada"})
        self.assertEqual(r.status_code, 401)
        r = self.c.post("/api/login", json={"email": "ninguem@x.com", "senha": "123456"})
        self.assertEqual(r.status_code, 401)

    def test_rotas_exigem_token(self):
        self.assertEqual(self.c.get("/api/tutores").status_code, 401)
        r = self.c.get("/api/tutores", headers={"Authorization": "Bearer lixo"})
        self.assertEqual(r.status_code, 401)

    def test_crud_usuario_sem_expor_hash(self):
        r = self.c.post("/api/usuarios", headers=self.admin,
                        json={"nome": "Ana", "email": "ana@x.com", "perfil": "RECEPCIONISTA", "senha": "segredo1"})
        self.assertEqual(r.status_code, 201)
        u = r.get_json()
        self.assertNotIn("senha_hash", u)
        r = self.c.put(f"/api/usuarios/{u['id']}", headers=self.admin, json={"nome": "Ana Maria"})
        self.assertEqual(r.get_json()["nome"], "Ana Maria")
        self.login("ana@x.com", "segredo1")  
        self.assertEqual(self.c.delete(f"/api/usuarios/{u['id']}", headers=self.admin).status_code, 204)
        self.assertEqual(self.c.get(f"/api/usuarios/{u['id']}", headers=self.admin).status_code, 404)

    def test_usuario_validacoes(self):
        base = {"nome": "X", "email": "x@x.com", "perfil": "RECEPCIONISTA", "senha": "segredo1"}
        self.assertEqual(self.c.post("/api/usuarios", headers=self.admin, json={**base, "senha": "123"}).status_code, 400)
        self.assertEqual(self.c.post("/api/usuarios", headers=self.admin, json={**base, "perfil": "DONO"}).status_code, 400)
        self.assertEqual(self.c.post("/api/usuarios", headers=self.admin, json={**base, "email": "admin@vetcare.com"}).status_code, 409)

    def test_admin_nao_exclui_a_si_mesmo(self):
        eu = self.c.get("/api/me", headers=self.admin).get_json()
        self.assertEqual(self.c.delete(f"/api/usuarios/{eu['id']}", headers=self.admin).status_code, 409)

    def test_rbac(self):
        recep = self.novo_usuario("RECEPCIONISTA", "r@x.com")
        vet = self.novo_usuario("VETERINARIO", "v@x.com")
        self.assertEqual(self.c.get("/api/usuarios", headers=recep).status_code, 403)
        self.assertEqual(self.c.get("/api/veterinarios", headers=recep).status_code, 200)
        r = self.c.post("/api/veterinarios", headers=recep, json={"nome": "Dr", "crmv": "1"})
        self.assertEqual(r.status_code, 403)
        r = self.c.post("/api/tutores", headers=recep, json={"nome": "Jo", "cpf": "11122233344"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.c.get("/api/tutores", headers=vet).status_code, 200)
        r = self.c.post("/api/tutores", headers=vet, json={"nome": "Jo", "cpf": "99988877766"})
        self.assertEqual(r.status_code, 403)

    def test_tutor(self):
        t = self.novo_tutor()
        self.assertEqual(t["cpf"], "12345678901")  
        self.assertEqual(self.c.post("/api/tutores", headers=self.admin, json={"nome": "Z", "cpf": "123"}).status_code, 400)
        self.assertEqual(self.c.post("/api/tutores", headers=self.admin, json={"nome": "Z", "cpf": "12345678901"}).status_code, 409)
        r = self.c.put(f"/api/tutores/{t['id']}", headers=self.admin, json={"telefone": "7199999"})
        self.assertEqual(r.get_json()["telefone"], "7199999")
        self.assertEqual(r.get_json()["nome"], "Maria")

    def test_animal_e_vinculo_com_tutor(self):
        t = self.novo_tutor()
        dados = {"nome": "Rex", "especie": "Cão", "raca": "SRD", "sexo": "M",
                 "data_nascimento": "2020-05-10", "tutor_id": t["id"]}
        r = self.c.post("/api/animais", headers=self.admin, json=dados)
        self.assertEqual(r.status_code, 201, r.get_data(as_text=True))
        a = r.get_json()
        lista = self.c.get("/api/animais", headers=self.admin).get_json()
        self.assertEqual(lista[0]["tutor_nome"], "Maria")
        self.assertEqual(self.c.post("/api/animais", headers=self.admin, json={**dados, "tutor_id": 999}).status_code, 409)
        self.assertEqual(self.c.post("/api/animais", headers=self.admin, json={**dados, "sexo": "X"}).status_code, 400)
        self.assertEqual(self.c.post("/api/animais", headers=self.admin, json={**dados, "data_nascimento": "2999-01-01"}).status_code, 400)
        self.assertEqual(self.c.post("/api/animais", headers=self.admin, json={**dados, "data_nascimento": "10/05/2020"}).status_code, 400)
        self.assertEqual(self.c.delete(f"/api/tutores/{t['id']}", headers=self.admin).status_code, 409)
        self.assertEqual(self.c.delete(f"/api/animais/{a['id']}", headers=self.admin).status_code, 204)
        self.assertEqual(self.c.delete(f"/api/tutores/{t['id']}", headers=self.admin).status_code, 204)

    def test_veterinario(self):
        r = self.c.post("/api/veterinarios", headers=self.admin,
                        json={"nome": "Dra. Ana", "crmv": "BA-123", "especialidade": "Felinos"})
        self.assertEqual(r.status_code, 201)
        v = r.get_json()
        self.assertEqual(self.c.post("/api/veterinarios", headers=self.admin, json={"nome": "Outro", "crmv": "BA-123"}).status_code, 409)
        self.assertEqual(self.c.post("/api/veterinarios", headers=self.admin, json={"nome": "Sem CRMV"}).status_code, 400)
        self.assertEqual(self.c.delete(f"/api/veterinarios/{v['id']}", headers=self.admin).status_code, 204)

    def test_corpo_invalido(self):
        r = self.c.post("/api/tutores", headers=self.admin, data="nao e json", content_type="text/plain")
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
