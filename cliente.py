import os


def limpar_terminal():
    os.system("cls")


class Cliente:
    def __init__(self, id_cliente, nome, email, telefone):
        self.__id_cliente = id_cliente
        self.nome = nome
        self.email = email
        self.telefone = telefone

    @property
    def id_cliente(self):
        return self.__id_cliente

    @property
    def nome(self):
        return self.__nome

    @property
    def email(self):
        return self.__email

    @property
    def telefone(self):
        return self.__telefone

    @nome.setter
    def nome(self, nome):
        if not isinstance(nome, str):
            raise ValueError("Nome invalido")

        elif not nome.strip():
            raise ValueError("Nome vazio")

        elif not nome.replace(" ", "").isalpha():
            raise ValueError("Nome deve conter apenas letras")

        self.__nome = nome.strip()

    @email.setter
    def email(self, email):
        if not isinstance(email, str):
            raise ValueError("Email invalido")

        elif not email.strip():
            raise ValueError("Email vazio")

        self.__email = email.lower().strip().replace(" ", "")

    @telefone.setter
    def telefone(self, telefone):
        telefone_limpo = telefone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not isinstance(telefone_limpo, str):
            raise ValueError("Telefone invalido")

        elif not telefone_limpo.strip():
            raise ValueError("Telefone nao pode estar vazio")

        elif not telefone_limpo.isdigit():
            raise ValueError("Telefone deve conter apenas numeros")

        self.__telefone = telefone_limpo.strip()

    def dados_cliente(self):
        return f"ID: {self.id_cliente} --- Nome: {self.nome} --- Email: {self.email} --- Telefone: {self.telefone}"

    def alterar_cliente(self, nome, email, telefone):
        try:
            cliente_teste = Cliente(self.id_cliente, nome, email, telefone)
        except ValueError as err:
            print(err)
            return False

        self.nome = nome
        self.email = email
        self.telefone = telefone

        print(f"Dados do cliente de ID {self.id_cliente} modificados")
        return True


class SistemaCliente:
    def __init__(self):
        self.__clientes = {}
        self.__id_contador = 0

    @property
    def clientes(self):
        return self.__clientes

    @property
    def id_contador(self):
        return self.__id_contador

    @id_contador.setter
    def id_contador(self, id_contador):
        if not isinstance(id_contador, int):
            raise ValueError("ID invalido")

        if id_contador < 0:
            raise ValueError("ID tem q ser maior q zero")

        self.__id_contador = id_contador

    def pegar_id(self):
        if not self.clientes:
            self.id_contador = 0
        else:
            self.id_contador = list(self.clientes.keys())[-1] + 1

    def verifica_email_cliente(self, email):
        if not email.strip():
            return False
        for cliente in self.clientes.values():
            if cliente.email == email.lower().replace(" ", ""):
                return False
        return True

    def incluir_cliente(self, nome, email, telefone):
        email_verificacao = self.verifica_email_cliente(email)

        if not email_verificacao:
            print("Email ja cadastrado")
            return False

        try:
            cliente = Cliente(self.id_contador, nome, email, telefone)
        except ValueError as erro:
            print(erro)
            return False

        self.id_contador += 1
        self.clientes[cliente.id_cliente] = cliente
        return True

    def listar_clientes(self):
        if not self.clientes:
            print("Sem clientes para listar")
            return False

        for cliente in self.clientes.values():
            print(cliente.dados_cliente())

    def pedir_id(self):
        try:
            id_pedido = int(input("Digite o id do cliente: "))
        except ValueError:
            return None
        return id_pedido

    def procurar_cliente(self, id_pedido):
        if id_pedido not in self.clientes:
            print("ID invalido")
            return None
        else:
            return self.clientes[id_pedido]

    def alterar_cliente(self, id_pedido, nome, email, telefone):
        if id_pedido is None or id_pedido <= 0:
            print("ID invalido")
            return False

        cliente = self.procurar_cliente(id_pedido)

        if cliente is None:
            print("Cliente nao encontrado")
            return False

        if email.lower().strip().replace(" ", "") != cliente.email:
            email_verificacao = self.verifica_email_cliente(email)

            if not email_verificacao:
                print("Email ja cadastrado")
                return False
        try:
            resultado = cliente.alterar_cliente(nome, email, telefone)
        except ValueError:
            return False

        if not resultado:
            return False
        return True

    def excluir_cliente(self, id_pedido):

        if id_pedido is None or id_pedido <= 0:
            print("ID invalido")
            return False

        cliente = self.procurar_cliente(id_pedido)

        if cliente is None:
            print("Cliente nao encontrado")
            return False

        self.clientes.pop(cliente.id_cliente)
        return True

    def excluir_todos(self):
        self.clientes.clear()


def pegar_de_arquivo_cliente(s_cliente):
    try:
        with open("clientes.txt", encoding='utf-8') as arq:
            for linha in arq:
                if not linha.strip():
                    continue

                dados = linha.strip().split(";")
                if len(dados) != 4:
                    continue
                try:
                    cliente = Cliente(int(dados[0]), dados[1], dados[2], dados[3])
                    s_cliente.clientes[cliente.id_cliente] = cliente
                except ValueError:
                    pass
    except FileNotFoundError:
        with open("clientes.txt", "w") as arq:
            pass


def colocar_no_arquivo_cliente(s_cliente):
    with open("clientes.txt", "w", encoding='utf-8') as arq:
        for cliente in s_cliente.clientes.values():
            dados = (cliente.dados_cliente())
            arq.write(f"{cliente.id_cliente};{cliente.nome};{cliente.email};{cliente.telefone}\n")


def nomes_incluir_cliente(s_cliente):
    nome = input("Digite o nome do cliente: ")
    email = input("Digite o email do cliente: ")
    telefone = input("Digite o telefone do cliente: ")
    return s_cliente.incluir_cliente(nome, email, telefone)


def id_procurar_cliente(s_cliente):
    id_pedido = s_cliente.pedir_id()
    return s_cliente.procurar_cliente(id_pedido)


def nomes_alterar_cliente(s_cliente):
    nome = input("Digite o novo nome do cliente: ")
    email = input("Digite o novo email do cliente: ")
    telefone = input("Digite o novo telefone do cliente: ")
    return s_cliente.alterar_cliente(s_cliente.pedir_id(), nome, email, telefone)


def id_excluir_cliente(s_cliente):
    id_pedido = s_cliente.pedir_id()
    return s_cliente.excluir_cliente(id_pedido)


def confirmacao_excluir_todos(s_cliente):
    while True:
        validar = input("Confirme novamente para APAGAR "
                        "todos os dados(s/n): ").lower().strip()
        if validar in ('nao', 'n'):
            print("Exclusao cancelada")
            return False
        elif validar in ('sim', 's'):
            print("Continuando exclusao")
            s_cliente.excluir_todos()
            print("Exclusao concluida")
            return True
        else:
            print("Opção invalida, tente novamente")


def menu_clientes():
    s_cliente = SistemaCliente()
    pegar_de_arquivo_cliente(s_cliente)
    s_cliente.pegar_id()

    while True:
        print("\n=== MÓDULO CLIENTES ===")
        print("1. Incluir Novo Cliente")
        print("2. Listar Todos")
        print("3. Consultar por ID")
        print("4. Alterar Cliente")
        print("5. Excluir Cliente")
        print("6. Excluir TODOS os clientes")
        print("7. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            limpar_terminal()
            print("\n--- INCLUSÃO ---")
            resultado = nomes_incluir_cliente(s_cliente)
            if not resultado:
                print("Erro, nao foi possivel adicionar cliente")
            else:
                print("Cliente adicionado com sucesso")

        elif opcao == '2':
            limpar_terminal()
            s_cliente.listar_clientes()

        elif opcao == '3':
            limpar_terminal()
            cliente = id_procurar_cliente(s_cliente)
            if cliente is None:
                print("Cliente nao encontrado")
            else:
                print(cliente.dados_cliente())

        elif opcao == '4':
            limpar_terminal()
            print("\n--- ALTERAÇÃO ---")
            resultado = nomes_alterar_cliente(s_cliente)
            if not resultado:
                print("Erro, nao foi possivel alterar cliente")
            else:
                print("Cliente alterado com sucesso")

        elif opcao == '5':
            limpar_terminal()
            print("\n--- EXCLUSÃO DE CLIENTE ---")
            resultado = id_excluir_cliente(s_cliente)
            if not resultado:
                print("Erro, nao foi possivel remover cliente")
            else:
                print("Cliente removido com sucesso")

        elif opcao == '6':
            limpar_terminal()
            print("\n--- EXCLUSÃO TOTAL ---")
            confirmacao_excluir_todos(s_cliente)

        elif opcao == '7':
            limpar_terminal()
            colocar_no_arquivo_cliente(s_cliente)
            break

        else:
            input("Opção inválida. Aperte ENTER e tente novamente.")

        input('Aperte enter para passar')


if __name__ == "__main__":
    menu_clientes()
