import os
import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

def limpar_terminal():
    """Limpa a tela do terminal de acordo com o sistema operacional."""
   
    os.system("cls" if os.name == "nt" else "clear")

class Produto:
    """Representa a entidade de um produto do sistema, contendo regras de validacao para nome, preco e estoque."""

    def __init__(self, nome, preco, estoque, id_produto=None):
        """Inicializa um produto definindo o ID privado e disparando os setters de validacao para os outros atributos."""
        self.__id_produto = id_produto
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    @property
    def id_produto(self):
        """Retorna o ID privado do produto."""
        return self.__id_produto

    @property
    def nome(self):
        """Retorna o nome privado do produto."""
        return self.__nome

    @property
    def preco(self):
        """Retorna o preco privado do produto."""
        return self.__preco

    @property
    def estoque(self):
        """Retorna o estoque privado do produto."""
        return self.__estoque

    @nome.setter
    def nome(self, nome):
        """Valida se o nome e uma string valida e nao vazia antes de remover espacos extras e salvar."""
        if not isinstance(nome, str):
            raise ValueError("Nome inválido: deve ser uma string.")
        if not nome.strip():
            raise ValueError("Nome inválido: não pode ser vazio.")
        self.__nome = nome.strip()

    @preco.setter
    def preco(self, preco):
        """Converte a entrada para float e garante que o preco seja um numero maior ou igual a zero."""
        try:
            preco_val = float(preco)
        except (ValueError, TypeError):
            raise ValueError("Preço inválido: deve ser um número.")
        if preco_val < 0:
            raise ValueError("Preço inválido: deve ser maior ou igual a zero.")
        self.__preco = preco_val

    @estoque.setter
    def estoque(self, estoque):
        """Converte a entrada para int e garante que o estoque seja um numero inteiro maior ou igual a zero."""
        try:
            estoque_val = int(estoque)
        except (ValueError, TypeError):
            raise ValueError("Estoque inválido: deve ser um número inteiro.")
        if estoque_val < 0:
            raise ValueError("Estoque inválido: deve ser maior ou igual a zero.")
        self.__estoque = estoque_val

    def __str__(self):
        """Formata a visualizacao textual do objeto produto para exibicao legivel no terminal."""
        return (
            f"ID: {self.id_produto} --- "
            f"Produto: {self.nome} --- "
            f"Preço: R${self.preco:.2f} --- "
            f"Estoque: {self.estoque} un"
        )
    
class SistemaProduto:
    """Gerencia a conexao com o banco de dados SQLite e realiza as operacoes de CRUD para os produtos."""

    def __init__(self, db_name="db_sistema.db"):
        """Define o nome do arquivo do banco de dados, abre a conexao e cria a tabela inicial se necessario."""
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(pasta_atual, db_name)
        self.conectar()
        self.criar_tabela()

    def conectar(self):
        """Estabelece a conexao com o banco de dados SQLite e cria o cursor para execucao de comandos SQL."""
        self.conexao = sqlite3.connect(self.db_name)
        self.cursor = self.conexao.cursor()

    def fechar_conexao(self):
        """Fecha o cursor e a conexao ativa com o banco de dados de forma segura."""
        if self.cursor:
            self.cursor.close()  
        if self.conexao:
            self.conexao.close()

    def criar_tabela(self):
        """Cria a tabela TB_PRODUTO no banco de dados caso ela ainda nao exista."""
        with self.conexao:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS TB_PRODUTO (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome    TEXT    NOT NULL UNIQUE,
                    preco   REAL    NOT NULL,
                    estoque INTEGER NOT NULL
                )
            """)

    def incluir_produto(self, produto):
        """Insere um novo produto na tabela TB_PRODUTO e trata possiveis erros de duplicidade ou operacao."""
        try:
            with self.conexao:
                self.cursor.execute(
                    "INSERT INTO TB_PRODUTO (nome, preco, estoque) VALUES (?, ?, ?)",
                    (produto.nome, produto.preco, produto.estoque)
                )
            return (True, "Produto inserido com sucesso!")
        except sqlite3.IntegrityError:
            return (False, "Erro: já existe um produto com esse nome.")
        except sqlite3.OperationalError:
            return (False, "Erro operacional no banco de dados.")
        except Exception as e:
            return (False, f"Erro inesperado: {e}")

    def listar_produtos(self):
        """Busca todos os produtos registrados no banco de dados e retorna uma lista de objetos Produto."""
        try:
            self.cursor.execute("SELECT id, nome, preco, estoque FROM TB_PRODUTO")
            resultado = self.cursor.fetchall()

            if not resultado:
                return (False, "Nenhum produto cadastrado.")

            produtos = [
                Produto(nome, preco, estoque, id_produto)
                for id_produto, nome, preco, estoque in resultado
            ]
            return (True, produtos)
        except sqlite3.OperationalError:
            return (False, "Erro operacional no banco de dados.")
        except Exception as e:
            return (False, f"Erro inesperado: {e}")

    def procurar_produto(self, id_produto):
        """Busca um produto especifico no banco de dados utilizando o ID fornecido."""
        try:
            self.cursor.execute(
                "SELECT id, nome, preco, estoque FROM TB_PRODUTO WHERE id = ?",
                (id_produto,)
            )
            dados = self.cursor.fetchone()

            if not dados:
                return (False, "Nenhum produto encontrado com esse ID.")

            id_p, nome, preco, estoque = dados
            return (True, Produto(nome, preco, estoque, id_p))
        except sqlite3.OperationalError:
            return (False, "Erro operacional no banco de dados.")
        except Exception as e:
            return (False, f"Erro inesperado: {e}")

    def alterar_produto(self, id_produto, produto):
        """Atualiza os dados de um produto existente no banco com base no ID informado."""
        try:
            with self.conexao:
                self.cursor.execute(
                    "UPDATE TB_PRODUTO SET nome = ?, preco = ?, estoque = ? WHERE id = ?",
                    (produto.nome, produto.preco, produto.estoque, id_produto)
                )
            if self.cursor.rowcount == 0:
                return (False, "Nenhum produto encontrado com esse ID.")
            return (True, "Produto alterado com sucesso!")
        except sqlite3.IntegrityError:
            return (False, "Erro: já existe um produto cadastrado com esse nome.")
        except sqlite3.OperationalError:
            return (False, "Erro operacional no banco de dados.")
        except Exception as e:
            return (False, f"Erro inesperado: {e}")

    def excluir_produto(self, id_produto):
        """Remove um produto especifico do banco de dados utilizando o ID informado."""
        try:
            with self.conexao:
                self.cursor.execute(
                    "DELETE FROM TB_PRODUTO WHERE id = ?", (id_produto,)
                )
            if self.cursor.rowcount == 0:
                return (False, "Nenhum produto encontrado com esse ID.")
            return (True, "Produto excluído com sucesso!")
        except sqlite3.OperationalError:
            return (False, "Erro operacional no banco de dados.")
        except Exception as e:
            return (False, f"Erro inesperado: {e}")

    def excluir_todos(self):
        """Apaga todos os registros contidos na tabela TB_PRODUTO do banco de dados."""
        try:
            with self.conexao:
                self.cursor.execute("DELETE FROM TB_PRODUTO")
            return (True, "Todos os produtos foram excluídos com sucesso!")
        except sqlite3.OperationalError:
            return (False, "Erro operacional no banco de dados.")
        except Exception as e:
            return (False, f"Erro inesperado: {e}")

def coletar_dados_produto():
    """Solicita os dados do produto via terminal e tenta instanciar um objeto Produto validando as entradas."""
    try:
        nome = input("Digite o nome do produto: ")
        preco = input("Digite o preço do produto: ")
        estoque = input("Digite a quantidade em estoque: ")
        return (True, Produto(nome, preco, estoque))
    except ValueError as erro:
        return (False, str(erro))

def pedir_id_produto():
    """Solicita um ID numérico ao usuario no terminal e valida se ele e maior que zero."""
    try:
        id_pedido = int(input("Digite o ID do produto: "))
        if id_pedido <= 0:  
            print("ID inválido: deve ser um número inteiro positivo.")
            return None
        return id_pedido
    except ValueError:
        return None

def exibir_resultado(funcao, *args):
    """Executa uma funcao do sistema de produtos e formata a exibicao do resultado dependendo do tipo retornado."""
    sucesso, dados = funcao(*args)

    if isinstance(dados, list):
        """Se o retorno for uma lista de produtos, percorre a lista imprimindo um por um."""
        for produto in dados:
            print(produto)
    elif isinstance(dados, Produto):
        """Se o retorno for uma unica instancia de Produto, imprime os dados do produto diretamente."""
        print(dados)
    else:
        """Se o retorno for uma mensagem de texto (sucesso ou erro), exibe o texto puro."""
        print(dados)

def confirmar_e_excluir_todos(s_produto):
    """Solicita uma confirmacao adicional em loop para garantir a exclusao total dos dados do banco."""
    while True:
        validar = input(
            "Confirme novamente para APAGAR todos os dados (s/n): "
        ).lower().strip()

        if validar in ("nao", "n"):
            print("Exclusão cancelada.")
            return
        elif validar in ("sim", "s"):
            exibir_resultado(s_produto.excluir_todos) 
            return
        else:
            print("Opção inválida, tente novamente.")

def menu_produtos():
    """Gera a interface de menu interativa em loop no terminal para que o usuario selecione as operacoes do sistema."""
    s_produto = SistemaProduto()

    while True:
        print("\n=== MÓDULO PRODUTOS ===")
        print("1. Incluir Novo Produto")
        print("2. Listar Todos")
        print("3. Consultar por ID")
        print("4. Alterar Produto")
        print("5. Excluir Produto")
        print("6. Excluir TODOS os produtos")
        print("7. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            """Processa a inclusao coletando as entradas, validando a criacao do objeto e salvando no banco."""
            limpar_terminal()
            print("\n--- INCLUSÃO ---")
            sucesso, dados = coletar_dados_produto()
            if not sucesso:
                print(dados)
            else:
                exibir_resultado(s_produto.incluir_produto, dados)

        elif opcao == "2":
            """Chama diretamente o metodo de listagem e envia o resultado para a funcao de exibicao."""
            limpar_terminal()
            exibir_resultado(s_produto.listar_produtos)

        elif opcao == "3":
            """Solicita o ID do produto e, caso seja valido, efetua a busca direta na base de dados."""
            limpar_terminal()
            id_produto = pedir_id_produto()
            if id_produto is None:
                print("ID inválido.")
            else:
                exibir_resultado(s_produto.procurar_produto, id_produto)

        elif opcao == "4":
            """Verifica se o ID existe antes de permitir a coleta de novas informacoes para atualizar o produto."""
            limpar_terminal()
            print("\n--- ALTERAÇÃO ---")
            id_produto = pedir_id_produto()
            if id_produto is None:
                print("ID inválido.")
                continue

            sucesso, produto_existente = s_produto.procurar_produto(id_produto)
            if not sucesso:
                print(produto_existente)  
                continue

            sucesso, dados = coletar_dados_produto()
            if not sucesso:
                print(dados)
                continue

            exibir_resultado(s_produto.alterar_produto, id_produto, dados)

        elif opcao == "5":
            """Solicita o ID informado pelo usuario e executa a remocao do registro correspondente no banco."""
            limpar_terminal()
            print("\n--- EXCLUSÃO DE PRODUTO ---")
            id_produto = pedir_id_produto()
            if id_produto is None:
                print("ID inválido.")
                continue
            exibir_resultado(s_produto.excluir_produto, id_produto)

        elif opcao == "6":
            """Garante um processo de seguranca em duas etapas antes de limpar completamente a tabela de produtos."""
            limpar_terminal()
            print("\n--- EXCLUSÃO TOTAL ---")
            
            primeira_confirmacao = input(
                "Tem certeza que deseja apagar TODOS os produtos? (s/n): "
            ).lower().strip()

            if primeira_confirmacao in ("sim", "s"):
                confirmar_e_excluir_todos(s_produto)
            else:
                print("Exclusão cancelada.")

        elif opcao == "7":
            """Fecha o fluxo de operacoes do banco de dados e encerra a execucao do laco principal."""
            limpar_terminal()
            s_produto.fechar_conexao()
            print("Saindo do sistema... Até logo!")
            break

        else:
            """Trata opcoes invalidas digitadas no menu principal redirecionando o fluxo de volta ao inicio."""
            input("Opção inválida. Aperte ENTER e tente novamente.")
            continue 
        input("\nAperte ENTER para continuar...")

#  INTERFACE TKINTER PARA PRODUTOS
def abrir_tela_produto(janela_pai):
    s_produto = SistemaProduto()
    
    tela = Toplevel(janela_pai)
    tela.title("Gestão de Produtos")
    tela.geometry("800x600")
    
    Label(tela, text="GESTÃO DE PRODUTOS", font=("Arial", 16, "bold")).pack(pady=10)

    frame_form = Frame(tela)
    frame_form.pack(pady=10)

    Label(frame_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = Entry(frame_form, width=30)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    Label(frame_form, text="Preço:").grid(row=1, column=0, padx=5, pady=5)
    entry_preco = Entry(frame_form, width=30)
    entry_preco.grid(row=1, column=1, padx=5, pady=5)

    Label(frame_form, text="Estoque:").grid(row=2, column=0, padx=5, pady=5)
    entry_estoque = Entry(frame_form, width=30)
    entry_estoque.grid(row=2, column=1, padx=5, pady=5)

    colunas = ("ID", "Nome", "Preço", "Estoque")
    tabela = ttk.Treeview(tela, columns=colunas, show="headings", height=10)
    for col in colunas:
        tabela.heading(col, text=col)
    tabela.pack(fill=X, padx=20, pady=10)

    def carregar_tabela():
        tabela.delete(*tabela.get_children())
        sucesso, dados = s_produto.listar_produtos()
        if sucesso and isinstance(dados, list):
            for p in dados:
                tabela.insert("", END, values=(p.id_produto, p.nome, f"R$ {p.preco:.2f}", p.estoque))

    def salvar():
        try:
            prod = Produto(entry_nome.get(), entry_preco.get(), entry_estoque.get())
            sucesso, msg = s_produto.incluir_produto(prod)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=tela)
                carregar_tabela()
            else:
                messagebox.showerror("Erro", msg, parent=tela)
        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e), parent=tela)

    def excluir():
        selecionado = tabela.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.", parent=tela)
            return
        id_prod = int(tabela.item(selecionado, "values")[0])
        s_produto.excluir_produto(id_prod)
        carregar_tabela()

    frame_btns = Frame(tela)
    frame_btns.pack()
    Button(frame_btns, text="Salvar Produto", command=salvar, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
    Button(frame_btns, text="Excluir Selecionado", command=excluir, bg="#f44336", fg="white").grid(row=0, column=1, padx=10)

    carregar_tabela()

if __name__ == "__main__":
    """Garante que a aplicacao so inicializara o menu caso o script seja executado diretamente pelo interpretador."""
    menu_produtos()