
const token = sessionStorage.getItem('token');
const usuario = JSON.parse(sessionStorage.getItem('usuario') || 'null');
if (!token || !usuario) location.href = '/login.html';

const PERFIS = ['ADMINISTRADOR', 'RECEPCIONISTA', 'VETERINARIO'];
const ADMIN = ['ADMINISTRADOR'];
const ADMIN_RECEP = ['ADMINISTRADOR', 'RECEPCIONISTA'];

const ENTIDADES = {
  tutores: {
    titulo: 'Tutores', leitura: PERFIS, escrita: ADMIN_RECEP,
    campos: [
      { n: 'nome', l: 'Nome', obrig: true },
      { n: 'cpf', l: 'CPF', obrig: true },
      { n: 'telefone', l: 'Telefone' },
      { n: 'email', l: 'E-mail', tipo: 'email' },
      { n: 'endereco', l: 'Endereço' },
    ],
  },
  animais: {
    titulo: 'Animais', leitura: PERFIS, escrita: ADMIN_RECEP,
    campos: [
      { n: 'nome', l: 'Nome', obrig: true },
      { n: 'especie', l: 'Espécie', obrig: true },
      { n: 'raca', l: 'Raça' },
      { n: 'sexo', l: 'Sexo', tipo: 'select', opcoes: [['', '—'], ['M', 'Macho'], ['F', 'Fêmea']] },
      { n: 'data_nascimento', l: 'Nascimento', tipo: 'date' },
      { n: 'tutor_id', l: 'Tutor', tipo: 'select', fonte: 'tutores', obrig: true, coluna: 'tutor_nome' },
    ],
  },
  veterinarios: {
    titulo: 'Veterinários', leitura: PERFIS, escrita: ADMIN,
    campos: [
      { n: 'nome', l: 'Nome', obrig: true },
      { n: 'crmv', l: 'CRMV', obrig: true },
      { n: 'especialidade', l: 'Especialidade' },
      { n: 'telefone', l: 'Telefone' },
    ],
  },
  usuarios: {
    titulo: 'Usuários', leitura: ADMIN, escrita: ADMIN,
    campos: [
      { n: 'nome', l: 'Nome', obrig: true },
      { n: 'email', l: 'E-mail', tipo: 'email', obrig: true },
      { n: 'perfil', l: 'Perfil', tipo: 'select', obrig: true, opcoes: PERFIS.map((p) => [p, p]) },
      { n: 'senha', l: 'Senha (mín. 6)', tipo: 'password', soNoForm: true },
    ],
  },
};

function el(tag, props = {}, ...filhos) {
  const e = Object.assign(document.createElement(tag), props); 
  e.append(...filhos);
  return e;
}

function sair() {
  sessionStorage.clear();
  location.href = '/login.html';
}

async function api(caminho, opcoes = {}) {
  const r = await fetch('/api' + caminho, {
    ...opcoes,
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
  });
  if (r.status === 401) { sair(); throw new Error('Sessão expirada'); }
  const corpo = r.status === 204 ? null : await r.json();
  if (!r.ok) throw new Error((corpo && corpo.erro) || 'Erro inesperado');
  return corpo;
}


let atual = null;

function montarMenu() {
  const menu = document.getElementById('menu');
  menu.replaceChildren();
  for (const [chave, ent] of Object.entries(ENTIDADES)) {
    if (!ent.leitura.includes(usuario.perfil)) continue;
    menu.append(el('button', { textContent: ent.titulo, id: 'menu-' + chave, onclick: () => mostrar(chave) }));
  }
}

async function mostrar(chave) {
  atual = chave;
  const ent = ENTIDADES[chave];
  document.querySelectorAll('nav button').forEach((b) => b.classList.toggle('ativo', b.id === 'menu-' + chave));
  const conteudo = document.getElementById('conteudo');
  const podeEscrever = ent.escrita.includes(usuario.perfil);

  const barra = el('div', { className: 'barra' }, el('h2', { textContent: ent.titulo }));
  if (podeEscrever) barra.append(el('button', { className: 'primario', textContent: 'Novo', onclick: () => abrirForm(chave) }));
  conteudo.replaceChildren(barra);

  try {
    const registros = await api('/' + chave);
    if (registros.length === 0) {
      conteudo.append(el('div', { className: 'vazio', textContent: 'Nenhum registro cadastrado.' }));
      return;
    }
    const colunas = ent.campos.filter((c) => !c.soNoForm);
    const cabecalho = el('tr', {}, ...colunas.map((c) => el('th', { textContent: c.l })));
    if (podeEscrever) cabecalho.append(el('th', { textContent: 'Ações' }));
    const corpo = el('tbody');
    for (const reg of registros) {
      const linha = el('tr', {}, ...colunas.map((c) => el('td', { textContent: reg[c.coluna || c.n] ?? '' })));
      if (podeEscrever) {
        linha.append(el('td', {},
          el('button', { textContent: 'Editar', onclick: () => abrirForm(chave, reg) }),
          el('button', { textContent: 'Excluir', className: 'perigo', onclick: () => excluir(chave, reg) })));
      }
      corpo.append(linha);
    }
    conteudo.append(el('table', {}, el('thead', {}, cabecalho), corpo));
  } catch (e) {
    conteudo.append(el('div', { className: 'erro', textContent: e.message }));
  }
}

async function excluir(chave, reg) {
  if (!confirm('Excluir "' + (reg.nome || reg.id) + '"?')) return;
  try {
    await api('/' + chave + '/' + reg.id, { method: 'DELETE' });
    mostrar(chave);
  } catch (e) {
    alert(e.message);
  }
}

const dialogo = document.getElementById('dialogo');
const form = document.getElementById('form');
let editando = null;

async function abrirForm(chave, reg = null) {
  const ent = ENTIDADES[chave];
  editando = reg;
  document.getElementById('titulo-form').textContent = (reg ? 'Editar ' : 'Novo(a) ') + ent.titulo.toLowerCase();
  document.getElementById('erro-form').textContent = '';
  const campos = document.getElementById('campos');
  campos.replaceChildren();

  for (const c of ent.campos) {
    let entrada;
    if (c.tipo === 'select') {
      let opcoes = c.opcoes;
      if (c.fonte) {
        const itens = await api('/' + c.fonte);
        opcoes = [['', 'Selecione...'], ...itens.map((i) => [i.id, i.nome])];
      }
      entrada = el('select', { name: c.n }, ...opcoes.map(([v, t]) => el('option', { value: v, textContent: t })));
    } else {
      entrada = el('input', { name: c.n, type: c.tipo || 'text' });
    }
    entrada.required = !!c.obrig && !(c.n === 'senha' && reg);
    if (reg && c.n !== 'senha') entrada.value = reg[c.n] ?? '';
    if (c.n === 'senha') entrada.required = !reg; 
    campos.append(el('label', {}, c.l + (c.obrig ? ' *' : ''), entrada));
  }
  dialogo.showModal();
}

document.getElementById('cancelar').onclick = () => dialogo.close();

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const dados = Object.fromEntries(new FormData(form));
  if (editando && !dados.senha) delete dados.senha; 
  try {
    const caminho = '/' + atual + (editando ? '/' + editando.id : '');
    await api(caminho, { method: editando ? 'PUT' : 'POST', body: JSON.stringify(dados) });
    dialogo.close();
    mostrar(atual);
  } catch (err) {
    document.getElementById('erro-form').textContent = err.message;
  }
});

document.getElementById('quem').textContent = usuario.nome + ' (' + usuario.perfil + ')';
document.getElementById('sair').onclick = sair;
montarMenu();
mostrar('tutores');
