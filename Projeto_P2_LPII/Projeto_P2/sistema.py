from datetime import datetime
from pathlib import Path
import socket
from threading import Thread

ARQUIVO_LOG = Path(__file__).with_name("acessos.txt")
usuarios = {}


class Usuario:
    def __init__(self, nome, senha, perfil="comum"):
        self.nome = nome
        self.__senha = senha
        self.perfil = perfil
        self.__ativo = True
        self.__tentativas = 0

    def bloquear(self):
        self.__ativo = False

    def ativar(self):
        self.__ativo = True
        self.__tentativas = 0

    def autenticar(self, senha_informada):
        if not self.__ativo:
            return False
        if self.__senha == senha_informada:
            self.__tentativas = 0
            return True
        self.__tentativas += 1
        if self.__tentativas >= 3:
            self.bloquear()
        return False

    def permissao(self):
        return "Consultar informações"

    @property
    def ativo(self):
        return self.__ativo

    @property
    def tentativas(self):
        return self.__tentativas


class Administrador(Usuario):
    def __init__(self, nome, senha):
        super().__init__(nome, senha, "administrador")

    def permissao(self):
        return "Gerenciar usuários e consultar registros"


def registrar_log(nome, evento):
    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nome_seguro = nome.replace(";", "_").replace("\r", "_").replace("\n", "_")
    try:
        with ARQUIVO_LOG.open("a", encoding="utf-8") as arquivo:
            arquivo.write(f"{horario};{nome_seguro};{evento}\n")
    except OSError as erro:
        print(f"Não foi possível gravar o log: {erro}")


def mostrar_logs():
    try:
        conteudo = ARQUIVO_LOG.read_text(encoding="utf-8")
        print(conteudo.rstrip() or "Nenhum registro.")
    except FileNotFoundError:
        print("Arquivo de logs ainda não foi criado.")
    except (OSError, UnicodeError) as erro:
        print(f"Não foi possível ler o log: {erro}")


def cadastrar():
    nome = input("Nome: ").strip()
    chave = nome.casefold()
    if not nome:
        print("Informe um nome.")
        return
    if chave in usuarios:
        print("Nome já cadastrado.")
        return

    perfil = input("Perfil (1 - comum, 2 - administrador): ").strip()
    if perfil not in ("1", "2"):
        print("Perfil inválido.")
        return
    if perfil == "2" and any(u.perfil == "administrador" for u in usuarios.values()):
        if not exigir_administrador():
            return

    senha = input("Senha fictícia: ")
    if not senha.strip():
        print("Informe uma senha.")
        return
    classe = Usuario if perfil == "1" else Administrador
    usuarios[chave] = classe(nome, senha)
    print("Cadastro realizado.")


def exibir_usuario(usuario):
    status = "ativo" if usuario.ativo else "bloqueado"
    print(f"{usuario.nome} | {usuario.perfil} | {status}")


def listar():
    if not usuarios:
        print("Nenhum usuário cadastrado.")
    for usuario in usuarios.values():
        exibir_usuario(usuario)


def consultar():
    nome = input("Nome para consulta: ").strip()
    usuario = usuarios.get(nome.casefold())
    if usuario:
        exibir_usuario(usuario)
        print("Permissão:", usuario.permissao())
    else:
        print("Usuário não encontrado.")


def autenticar(apenas_administrador=False):
    nome = input("Nome: ").strip()
    senha = input("Senha: ")
    usuario = usuarios.get(nome.casefold())

    if usuario is None or not usuario.ativo:
        print("Acesso negado. Usuário inexistente ou bloqueado.")
        registrar_log(nome, "acesso negado")
        return None

    if not usuario.autenticar(senha):
        print("Acesso negado.")
        registrar_log(usuario.nome, "acesso negado")
        if not usuario.ativo:
            print("Conta bloqueada após três erros consecutivos.")
            registrar_log(usuario.nome, "bloqueio automático")
        return None

    if apenas_administrador and usuario.perfil != "administrador":
        print("Acesso negado. Operação exclusiva de administrador.")
        registrar_log(usuario.nome, "acesso administrativo negado")
        return None

    print("Acesso permitido.", usuario.permissao())
    registrar_log(usuario.nome, "acesso permitido")
    return usuario


def exigir_administrador():
    print("Identifique-se como administrador.")
    return autenticar(apenas_administrador=True)


def alterar_estado():
    if not exigir_administrador():
        return
    nome = input("Nome do usuário a bloquear ou reativar: ").strip()
    usuario = usuarios.get(nome.casefold())
    if usuario is None:
        print("Usuário não encontrado.")
        return
    escolha = input("1 - Bloquear | 2 - Reativar: ").strip()
    if escolha == "1":
        usuario.bloquear()
        registrar_log(usuario.nome, "bloqueio administrativo")
    elif escolha == "2":
        usuario.ativar()
        registrar_log(usuario.nome, "reativação administrativa")
    else:
        print("Opção inválida.")
        return
    exibir_usuario(usuario)


def consultar_logs():
    if not ARQUIVO_LOG.exists():
        mostrar_logs()
    elif exigir_administrador():
        mostrar_logs()


def demonstrar_referencias():
    primeira = Usuario("Exemplo", "SenhaFicticia")
    segunda = primeira
    print("Ativo antes:", primeira.ativo, segunda.ativo)
    segunda.bloquear()
    print("Ativo após bloquear pela segunda referência:", primeira.ativo, segunda.ativo)
    print("primeira is segunda:", primeira is segunda)


def ler_mensagem(conexao):
    with conexao.makefile("rb") as fluxo:
        mensagem = fluxo.readline(1024)
    if not mensagem.endswith(b"\n"):
        raise OSError("Mensagem incompleta.")
    return mensagem.decode("utf-8").rstrip("\n")


def atender_cliente(servidor):
    try:
        conexao, _ = servidor.accept()
        with conexao:
            conexao.settimeout(3)
            print("Servidor recebeu:", ler_mensagem(conexao))
            conexao.sendall("Mensagem recebida!\n".encode("utf-8"))
    except (OSError, UnicodeError) as erro:
        print(f"Erro no servidor: {erro}")


def testar_rede():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.bind(("127.0.0.1", 0))
            servidor.listen(1)
            servidor.settimeout(3)
            tarefa = Thread(target=atender_cliente, args=(servidor,))
            tarefa.start()
            try:
                with socket.create_connection(servidor.getsockname(), timeout=3) as cliente:
                    cliente.sendall("Olá, servidor!\n".encode("utf-8"))
                    print("Cliente recebeu:", ler_mensagem(cliente))
            finally:
                tarefa.join()
    except (OSError, UnicodeError) as erro:
        print(f"Erro no teste de rede: {erro}")


def menu():
    operacoes = {
        "1": cadastrar, "2": listar, "3": consultar, "4": autenticar,
        "5": alterar_estado, "6": consultar_logs, "7": testar_rede,
        "8": demonstrar_referencias,
    }
    while True:
        print("""
========== CONTROLE DE ACESSOS ==========
1 - Cadastrar usuário
2 - Listar usuários
3 - Consultar usuário
4 - Autenticar (login)
5 - Bloquear / reativar usuário
6 - Consultar logs
7 - Testar comunicação em rede
8 - Demonstrar referências
0 - Sair
=========================================
""")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Programa encerrado.")
            return
        operacao = operacoes.get(opcao)
        if operacao:
            operacao()
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        menu()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado.")
