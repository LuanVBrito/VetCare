from transversal import db
from transversal.crud import Repositorio


class RepositorioAnimal(Repositorio):
    def listar(self):
        # inclui o nome do tutor para a listagem
        return db.consultar(
            "SELECT a.*, t.nome AS tutor_nome FROM animais a "
            "JOIN tutores t ON t.id = a.tutor_id ORDER BY a.nome"
        )


repositorio = RepositorioAnimal(
    "animais", ["nome", "especie", "raca", "sexo", "data_nascimento", "tutor_id"]
)
