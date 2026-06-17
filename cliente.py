import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

conexao = sqlite3.connect("db_sistema.db")
cursor = conexao.cursor()

# Criaçao da tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS TB_CLIENTE(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL)
""")
conexao.commit()


class Cliente:
    def __init__(self, nome, email, telefone, id_cliente=None):
        self.__id_cliente = id_cliente
        self.nome = nome
        self.email = email
        self.telefone = telefone

    # Property para poder utilizar sem usar parenteses
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

    # Setter para poder modificar os dados e fazer validaçao de erro
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

        elif '@' not in email or '.' not in email:
            raise ValueError("Email invalido")

        self.__email = email.lower().strip().replace(" ", "")

    @telefone.setter
    def telefone(self, telefone):
        if not isinstance(telefone, str):
            raise ValueError("Telefone invalido")

        telefone_limpo = telefone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if not telefone_limpo.strip():
            raise ValueError("Telefone nao pode estar vazio")

        elif not telefone_limpo.isdigit():
            raise ValueError("Telefone deve conter apenas numeros")

        self.__telefone = telefone_limpo.strip()

    def __str__(self):
        return f"ID: {self.id_cliente} --- Nome: {self.nome} --- Email: {self.email} --- Telefone: {self.telefone}"


# Classe do banco de dados
class SistemaCliente:
    # Incluir os dados no banco de dados
    def incluir_cliente(self, cliente):
        try:
            cursor.execute(("INSERT INTO TB_CLIENTE(nome, email, telefone) VALUES (?, ?, ?)"),
                           (cliente.nome, cliente.email, cliente.telefone))
            conexao.commit()

        # Retorno usando tupla passar msg e validaçao
        except sqlite3.IntegrityError:
            return (False, "email duplicado")
        except sqlite3.OperationalError:
            return (False, "erro no banco de dados")
        except Exception:
            return (False, "erro desconhecido")

        return (True, "cliente inserido")

    # Pega todos os clientes do banco e retorna eles como uma lista
    def listar_clientes(self):
        try:
            cursor.execute("SELECT id, nome, email, telefone FROM TB_CLIENTE")
            resultado = cursor.fetchall()

            if not resultado:
                return (False, "nenhum cliente adicionado")

            clientes_listados = []
            for id_cliente, nome, email, telefone in resultado:
                clientes_listados.append(Cliente(nome, email, telefone, id_cliente=id_cliente))
            return (True, clientes_listados)
        except sqlite3.OperationalError:
            return (False, "erro no banco de dados")
        except Exception:
            return (False, "erro desconhecido")

    # encontra o cliente por id e e retorna como object
    def procurar_cliente(self, id_pedido):
        try:
            cursor.execute(("SELECT id, nome, email, telefone FROM TB_CLIENTE WHERE id = ?"), (id_pedido,))
            dados = cursor.fetchone()
            if not dados:
                return (False, "nenhum cliente encontrado")

            id_cliente, nome, email, telefone = dados

            cliente = Cliente(nome, email, telefone, id_cliente)
            return (True, cliente)

        except sqlite3.OperationalError:
            return (False, "erro no banco de dados")
        except Exception:
            return (False, "erro desconhecido")

    # Encontra cliente por id e dps muda os dados
    def alterar_cliente(self, id_pedido, cliente):
        try:
            cursor.execute(("UPDATE TB_CLIENTE SET nome = ?, email = ?, telefone = ? WHERE id = ?"),
                           (cliente.nome, cliente.email, cliente.telefone, id_pedido))

            if cursor.rowcount == 0:
                return (False, "nenhum cliente encontrado com esse id")
            conexao.commit()

        except sqlite3.IntegrityError:
            return (False, "email duplicado")
        except sqlite3.OperationalError:
            return (False, "erro no banco de dados")
        except Exception:
            return (False, "erro desconhecido")

        return (True, "Dados do cliente trocados")

    # Exclui o cliente por id
    def excluir_cliente(self, id_pedido):
        try:
            cursor.execute(("DELETE FROM TB_CLIENTE WHERE id = ?"),
                           (id_pedido,))
            if cursor.rowcount == 0:
                return (False, "nenhum cliente encontrado com esse id")
            conexao.commit()

        except sqlite3.IntegrityError:
            return (False, "cliente tem registros vinculados")
        except sqlite3.OperationalError:
            return (False, "erro no banco de dados")
        except Exception:
            return (False, "erro desconhecido")
        return (True, "cliente excluido")

    # Remove todos os clientes
    def excluir_todos(self):
        try:
            cursor.execute("DELETE FROM TB_CLIENTE")
            conexao.commit()
        except sqlite3.IntegrityError:
            return (False, "cliente tem registros vinculados")
        except sqlite3.OperationalError:
            return (False, "erro no banco de dados")
        except Exception:
            return (False, "erro desconhecido")
        return (True, "todos os clientes excluidos")


# Classe do tk
class InterfaceCliente:
    def __init__(self, janela_pai):
        self.__janela = tk.Toplevel(janela_pai)
        self.__banco_cliente = SistemaCliente()
        self.__contador = 0

    @property
    def janela(self):
        return self.__janela

    @property
    def banco_cliente(self):
        return self.__banco_cliente

    #Cria a janela principal do sistema
    def criar_janela(self):
        # Cria o titulo
        self.janela.title("Menu Cliente")
        self.janela.attributes("-fullscreen", True)
        barra_menu = tk.Menu(self.janela, font=("Arial", 14))

        # Cria o menu para ir para as outras tabelas
        menu_opcoes = tk.Menu(barra_menu, tearoff=0, font=("Arial", 14))
        menu_opcoes.add_command(label="Adicionar Cliente", command=self.adicionar_cliente_tk)
        menu_opcoes.add_command(label="Alterar Cliente", command=self.alterar_cliente_tk)
        menu_opcoes.add_command(label="Remover Cliente", command=self.excluir_cliente_tk)
        menu_opcoes.add_command(label="Encontrar Cliente", command=self.procurar_cliente_tk)
        menu_opcoes.add_separator()
        menu_opcoes.add_command(label="Sair", command=self.janela.destroy)

        # Coloca o menu opçoes na barra de menu
        barra_menu.add_cascade(label='Opções', menu=menu_opcoes)

        lbltitulo = tk.Label(self.janela, text='SISTEMA DE GERENCIAMENTO DE CLIENTES', font=("Arial", 16, "bold"))
        lbltitulo.pack(pady=40)

        # Define a barra de menu ma janela
        self.janela.config(menu=barra_menu)
        self.janela.mainloop()

    # Janela pra adicionar o cliente
    def adicionar_cliente_tk(self):
        janela_filha = tk.Toplevel(self.janela)
        janela_filha.title("Cadastro de Clientes")
        janela_filha.geometry("800x500")

        tk.Label(janela_filha, text="Nome:").grid(row=0, column=0, padx=10, pady=10)
        entrada_nome = tk.Entry(janela_filha, width=40)
        entrada_nome.grid(row=0, column=1)

        tk.Label(janela_filha, text="Email:").grid(row=1, column=0, padx=10, pady=10)
        entrada_email = tk.Entry(janela_filha, width=40)
        entrada_email.grid(row=1, column=1)

        tk.Label(janela_filha, text="Telefone:").grid(row=2, column=0, padx=10, pady=10)
        entrada_telefone = tk.Entry(janela_filha, width=40)
        entrada_telefone.grid(row=2, column=1)

        # Pega a tabela de clientes
        tabela = self.criar_tabela(janela_filha)
        self.atualizar_tabela_tk(tabela)

        # Botao para concluir
        tk.Button(
            janela_filha,
            text="Salvar Cliente",
            command=lambda: (self.salvar_cliente_tk(
                self.banco_cliente.incluir_cliente,
                entrada_nome,
                entrada_email,
                entrada_telefone,
                tabela),
                self.atualizar_tabela_tk(tabela)
            )).grid(row=3, column=0, pady=10)

        tk.Button(janela_filha, text="Voltar", command=janela_filha.destroy).grid(row=3, column=1, pady=10)

    # Cria a tabela de clientes
    def criar_tabela(self, janela):
        colunas = ("id", "nome", "email", "telefone")
        tabela = ttk.Treeview(janela, columns=colunas, show="headings")

        # Definindo os cabeçalhos da tabela
        tabela.heading("id", text="Id")
        tabela.heading("nome", text="Nome")
        tabela.heading("email", text="Email")
        tabela.heading("telefone", text="Telefone")

        # Definindo o tamanho das colunas
        tabela.column("id", width=40, anchor="center")
        tabela.column("nome", width=150, anchor="w")
        tabela.column("email", width=240, anchor="e")
        tabela.column("telefone", width=120, anchor="e")

        # Posiciona a tabela na janela
        tabela.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        return tabela

    # atualiza a tabela de clientes
    def atualizar_tabela_tk(self, tabela):
        # limpa tudo
        tabela.delete(*tabela.get_children())

        # busca no banco
        resultado, dados = self.banco_cliente.listar_clientes()

        if resultado:
            for cliente in dados:
                tabela.insert(
                    "",
                    "end",
                    values=(
                        cliente.id_cliente,
                        cliente.nome,
                        cliente.email,
                        cliente.telefone
                    )
                )

    # salva o cliente apos pegar os dados do usuario
    def salvar_cliente_tk(self, funcao, nome, email, telefone, tabela, id_cliente=None):
        try:
            cliente = Cliente(nome.get(), email.get(), telefone.get())
            if id_cliente is None:
                resultado, mensagem = funcao(cliente)
            else:
                resultado, mensagem = funcao(int(id_cliente.get()), cliente)

            if resultado:
                messagebox.showinfo("Sucesso", mensagem)

                nome.delete(0, tk.END)
                email.delete(0, tk.END)
                telefone.delete(0, tk.END)
                if id_cliente is not None:
                    id_cliente.delete(0, tk.END)

                self.atualizar_tabela_tk(tabela)

            else:
                messagebox.showerror("Erro", mensagem)

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    # Muda os dados do cliente
    def alterar_cliente_tk(self):
        janela_filha = tk.Toplevel(self.janela)
        janela_filha.title("Alteraçao de Clientes")
        janela_filha.geometry("800x500")

        tk.Label(janela_filha, text="ID: ").grid(row=0, column=0, padx=10, pady=10)
        entrada_id = tk.Entry(janela_filha, width=40)
        entrada_id.grid(row=0, column=1)

        tk.Label(janela_filha, text="Novo Nome:").grid(row=1, column=0, padx=10, pady=10)
        entrada_nome = tk.Entry(janela_filha, width=40)
        entrada_nome.grid(row=1, column=1)

        tk.Label(janela_filha, text="Novo Email:").grid(row=2, column=0, padx=10, pady=10)
        entrada_email = tk.Entry(janela_filha, width=40)
        entrada_email.grid(row=2, column=1)

        tk.Label(janela_filha, text="Novo Telefone:").grid(row=3, column=0, padx=10, pady=10)
        entrada_telefone = tk.Entry(janela_filha, width=40)
        entrada_telefone.grid(row=3, column=1)

        tabela = self.criar_tabela(janela_filha)
        self.atualizar_tabela_tk(tabela)

        tk.Button(
            janela_filha,
            text="Salvar Cliente",
            command=lambda: (self.salvar_cliente_tk(
                self.banco_cliente.alterar_cliente,
                entrada_nome,
                entrada_email,
                entrada_telefone,
                tabela,
                entrada_id), self.atualizar_tabela_tk(tabela))).grid(row=4, column=0, pady=10)

        tk.Button(janela_filha, text="Voltar", command=janela_filha.destroy).grid(row=4, column=1, pady=10)

        self.atualizar_tabela_tk(tabela)

    # Exclui o cliente com base no id ou exclui todos apos 3 cliques no botao
    def excluir_cliente_tk(self):
        janela_filha = tk.Toplevel(self.janela)
        janela_filha.title("Exclusão de Clientes")
        janela_filha.geometry("800x500")

        msg_excluirtodos = tk.Label(janela_filha, text="CLIQUE 3 VZS NO BOTAO COM A BARRA VAZIA PARA EXCLUIR TODOS", fg="red",  font=("Arial", 12, "bold", "italic"))
        msg_excluirtodos.grid(row=1, columnspan=3, padx=10, pady=10)

        tk.Label(janela_filha, text="ID que deseja excluir: ").grid(row=0, column=0, padx=10, pady=10)
        entrada_id = tk.Entry(janela_filha, width=40)
        entrada_id.grid(row=0, column=1)

        tabela = self.criar_tabela(janela_filha)
        self.atualizar_tabela_tk(tabela)

        tk.Button(
            janela_filha,
            text="Remover cliente",
            command=lambda: (self.remover_cliente_tk(
                entrada_id, tabela), self.atualizar_tabela_tk(tabela)
                )).grid(row=2, column=0, pady=10)

        tk.Button(janela_filha, text="Voltar", command=janela_filha.destroy).grid(row=2, column=1, pady=10)

    # Faz a exclusao no banco de dados
    def remover_cliente_tk(self, id_cliente, tabela):
        # Verifica quantas vzs o botao foi clicado
        id_entrada = id_cliente.get().strip()
        self.__contador += 1

        if self.__contador % 3 == 0 and not id_entrada:
            self.remover_todos_tk()
            self.__contador = 0
            self.atualizar_tabela_tk(tabela)
            return

        if not id_entrada:
            messagebox.showwarning("Campo vazio", "Digite um ID.")
            return

        try:
            id_entrada = int(id_entrada)
        except ValueError:
            messagebox.showwarning("Id invalido", "O id deve ser numerico")
            return

        resultado, msg = self.banco_cliente.excluir_cliente(id_entrada)

        if resultado:
            messagebox.showinfo("Sucesso", msg)

            id_cliente.delete(0, tk.END)
            self.atualizar_tabela_tk(tabela)
        else:
            messagebox.showerror("Falha", msg)

    # Pede confirmaçao para poder excluir todos
    def remover_todos_tk(self):
        confirmacao = messagebox.askyesno("CONFIRMAÇÂO", "Nenhum id foi informado, deseja excluir todos?")

        if confirmacao:
            resultado, msg = self.banco_cliente.excluir_todos()
            if resultado:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Falha", msg)

    # Encontra o cliente por id
    def procurar_cliente_tk(self):
        janela_filha = tk.Toplevel(self.janela)
        janela_filha.title("Pesquisa de Clientes")
        janela_filha.geometry("800x500")

        tk.Label(janela_filha, text="ID que deseja encontrar: ").grid(row=0, column=0, padx=10, pady=10)
        entrada_id = tk.Entry(janela_filha, width=40)
        entrada_id.grid(row=0, column=1)

        tabela = self.criar_tabela(janela_filha)
        self.atualizar_tabela_tk(tabela)

        tk.Button(
            janela_filha,
            text="Encontrar cliente",
            command=lambda: self.encontrar_cliente_tk(
                entrada_id, tabela
                )).grid(row=2, column=0, pady=10)

        tk.Button(janela_filha, text="Voltar", command=janela_filha.destroy).grid(row=2, column=2, pady=10)

    def encontrar_cliente_tk(self, id_cliente, tabela):
        id_pegar = id_cliente.get().strip()

        if not id_pegar:
            self.atualizar_tabela_tk(tabela)
            return

        try:
            id_pegar = int(id_pegar)
        except ValueError:
            messagebox.showwarning("Id invalido", "Id deve ser numerico")
            return

        resultado, dados = self.banco_cliente.procurar_cliente(id_pegar)

        if resultado:
            tabela.delete(*tabela.get_children())
            tabela.insert(
                "",
                "end",
                values=(dados.id_cliente, dados.nome, dados.email, dados.telefone))
        else:
            messagebox.showerror("Falha", dados)


if __name__ == '__main__':
    i_cliente = InterfaceCliente()
    i_cliente.criar_janela()
