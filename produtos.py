import os

def limpar_terminal():
    os.system("cls")

class Produto:
    def __init__(self, id_produto, nome, preco, estoque):
        self.__id_produto = id_produto
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    @property
    def id_produto(self):
        return self.__id_produto

    @property
    def nome(self):
        return self.__nome

    @property
    def preco(self):
        return self.__preco

    @property
    def estoque(self):
        return self.__estoque

    @nome.setter
    def nome(self, nome):
        if not isinstance(nome, str):
            raise ValueError("Nome invalido")
        elif not nome.strip():
            raise ValueError("Nome vazio")
        self.__nome = nome.strip()

    @preco.setter
    def preco(self, preco):
        try:
            preco_val = float(preco)
        except (ValueError, TypeError):
            raise ValueError("Preco invalido")
        if preco_val < 0:
            raise ValueError("Preco deve ser maior ou igual a zero")
        self.__preco = preco_val

    @estoque.setter
    def estoque(self, estoque):
        try:
            estoque_val = int(estoque)
        except (ValueError, TypeError):
            raise ValueError("Estoque invalido")
        if estoque_val < 0:
            raise ValueError("Estoque deve ser maior ou igual a zero")
        self.__estoque = estoque_val

    def dados_produto(self):
        return f"{self.id_produto};{self.nome};{self.preco};{self.estoque}\n"

    def exibir_produto(self):
        return f"ID: {self.id_produto} --- Produto: {self.nome} --- Preço: R${self.preco:.2f} --- Estoque: {self.estoque} un"

    def alterar_produto(self, nome, preco, estoque):
        try:
            Produto(self.id_produto, nome, preco, estoque)
        except ValueError as err:
            print(err)
            return False
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        print(f"Dados do produto de ID {self.id_produto} modificados")
        return True


class SistemaProduto:
    def __init__(self):
        self.__produtos = {}
        self.__id_contador = 0

    @property
    def produtos(self):
        return self.__produtos

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
        if not self.produtos:
            self.id_contador = 0
        else:
            self.id_contador = list(self.produtos.keys())[-1] + 1

    def verifica_nome_produto(self, nome):
        if not nome.strip():
            return False
        for produto in self.produtos.values():
            if produto.nome.lower() == nome.lower().strip():
                return False
        return True

    def incluir_produto(self, nome, preco, estoque):
        nome_verificacao = self.verifica_nome_produto(nome)
        if not nome_verificacao:
            print("Produto ja cadastrado")
            return False
        try:
            produto = Produto(self.id_contador, nome, preco, estoque)
        except ValueError as erro:
            print(erro)
            return False
        self.produtos[produto.id_produto] = produto
        self.id_contador += 1
        return True

    def listar_produtos(self):
        if not self.produtos:
            print("Sem produtos para listar")
            return False
        for produto in self.produtos.values():
            print(produto.exibir_produto())

    def pedir_id(self):
        try:
            id_pedido = int(input("Digite o id do produto: "))
        except ValueError:
            return None
        return id_pedido

    def procurar_produto(self, id_pedido):
        if id_pedido not in self.produtos:
            print("ID invalido")
            return None
        return self.produtos[id_pedido]

    def alterar_produto(self, id_pedido, nome, preco, estoque):
        if id_pedido is None or id_pedido <= 0:
            print("ID invalido")
            return False
        produto = self.procurar_produto(id_pedido)
        if produto is None:
            print("Produto nao encontrado")
            return False
        if nome.lower().strip() != produto.nome.lower():
            nome_verificacao = self.verifica_nome_produto(nome)
            if not nome_verificacao:
                print("Produto ja cadastrado com esse nome")
                return False
        try:
            resultado = produto.alterar_produto(nome, preco, estoque)
        except ValueError:
            return False
        return resultado

    def excluir_produto(self, id_pedido):
        if id_pedido is None or id_pedido <= 0:
            print("ID invalido")
            return False
        produto = self.procurar_produto(id_pedido)
        if produto is None:
            print("Produto nao encontrado")
            return False
        self.produtos.pop(produto.id_produto)
        return True

    def excluir_todos(self):
        self.produtos.clear()


def pegar_de_arquivo_produto(s_produto):
    try:
        with open("produtos.txt", "r", encoding='utf-8') as arq:
            for linha in arq:
                if not linha.strip():
                    continue
                dados = linha.strip().split(";")
                if len(dados) != 4:
                    continue
                try:
                    produto = Produto(int(dados[0]), dados[1], float(dados[2]), int(dados[3]))
                    s_produto.produtos[produto.id_produto] = produto
                except ValueError:
                    pass
    except FileNotFoundError:
        with open("produtos.txt", "w", encoding='utf-8') as arq:
            pass

def colocar_no_arquivo_produto(s_produto):
    with open("produtos.txt", "w", encoding='utf-8') as arq:
        for produto in s_produto.produtos.values():
            dados = produto.dados_produto()
            arq.write(dados)

def nomes_incluir_produto(s_produto):
    nome = input("Digite o nome do produto: ")
    preco = input("Digite o preco do produto: ")
    estoque = input("Digite a quantidade em estoque: ")
    return s_produto.incluir_produto(nome, preco, estoque)

def id_procurar_produto(s_produto):
    id_pedido = s_produto.pedir_id()
    return s_produto.procurar_produto(id_pedido)

def nomes_alterar_produto(s_produto):
    id_pedido = s_produto.pedir_id()
    produto = s_produto.procurar_produto(id_pedido)
    if produto is None:
        return False
    nome = input(f"Digite o novo nome do produto (Atual: {produto.nome}): ")
    preco = input(f"Digite o novo preco do produto (Atual: {produto.preco}): ")
    estoque = input(f"Digite a nova quantidade em estoque (Atual: {produto.estoque}): ")
    return s_produto.alterar_produto(id_pedido, nome, preco, estoque)

def id_excluir_produto(s_produto):
    id_pedido = s_produto.pedir_id()
    return s_produto.excluir_produto(id_pedido)

def confirmacao_excluir_todos(s_produto):
    while True:
        validar = input("Confirme novamente para APAGAR todos os dados(s/n): ").lower().strip()
        if validar in ('nao', 'n'):
            print("Exclusao cancelada")
            return False
        elif validar in ('sim', 's'):
            print("Continuando exclusao")
            s_produto.excluir_todos()
            print("Exclusao concluida")
            return True
        else:
            print("Opção invalida, tente novamente")

def menu_produtos():
    s_produto = SistemaProduto()
    pegar_de_arquivo_produto(s_produto)
    s_produto.pegar_id()

    while True:
        print("\n=== MÓDULO PRODUTOS ===")
        print("1. Incluir Novo Produto")
        print("2. Listar Todos")
        print("3. Consultar por ID")
        print("4. Alterar Produto")
        print("5. Excluir Produto")
        print("6. Excluir TODOS os produtos")
        print("7. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            limpar_terminal()
            print("\n--- INCLUSÃO ---")
            resultado = nomes_incluir_produto(s_produto)
            if not resultado:
                print("Erro, nao foi possivel adicionar produto")
            else:
                print("Produto adicionado com sucesso")

        elif opcao == '2':
            limpar_terminal()
            s_produto.listar_produtos()

        elif opcao == '3':
            limpar_terminal()
            produto = id_procurar_produto(s_produto)
            if produto is None:
                print("Produto nao encontrado")
            else:
                print(produto.exibir_produto())

        elif opcao == '4':
            limpar_terminal()
            print("\n--- ALTERAÇÃO ---")
            resultado = nomes_alterar_produto(s_produto)
            if not resultado:
                print("Erro, nao foi possivel alterar produto")
            else:
                print("Produto alteredo com sucesso")

        elif opcao == '5':
            limpar_terminal()
            print("\n--- EXCLUSÃO DE PRODUTO ---")
            resultado = id_excluir_produto(s_produto)
            if not resultado:
                print("Erro, nao foi possivel remover produto")
            else:
                print("Produto removido com sucesso")

        elif opcao == '6':
            limpar_terminal()
            print("\n--- EXCLUSÃO TOTAL ---")
            confirmacao_excluir_todos(s_produto)

        elif opcao == '7':
            limpar_terminal()
            colocar_no_arquivo_produto(s_produto)
            break

        else:
            input("Opção inválida. Aperte ENTER e tente novamente.")

        input('Aperte enter para passar')

if __name__ == "__main__":
    menu_produtos()