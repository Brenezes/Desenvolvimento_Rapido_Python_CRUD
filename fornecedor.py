import os
import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# Conecta ao banco de dados, se não existir ele cria automaticamente
conexao = sqlite3.connect("db_sistema.db")
cursor = conexao.cursor()

# Cria a tabela de fornecedores caso ela ainda não exista no banco
cursor.execute("""
CREATE TABLE IF NOT EXISTS TB_FORNECEDOR (
    forn_id INTEGER PRIMARY KEY,
    forn_nome TEXT NOT NULL,
    forn_cnpj TEXT NOT NULL,
    forn_setor TEXT NOT NULL,
    forn_contato TEXT NOT NULL,
    forn_telefone TEXT NOT NULL
)
""")
conexao.commit()

def limpar_terminal():
    # limpa a tela do terminal
    os.system("cls")

def pausar():
    # faz o programa esperar o usuario apertar enter
    input("\nPressione Enter para continuar...")

class Fornecedor:
    # classe que representa um fornecedor com todos seus dados
    def __init__(self, id_forn, nome, cnpj, setor, contato, telefone):
        self.id = id_forn
        self.nome = nome
        self.cnpj = cnpj
        self.setor = setor
        self.contato = contato
        self.telefone = telefone

    def exibir(self):
        # mostra os dados do fornecedor formatado no terminal
        print(f"ID: {self.id} | Nome: {self.nome:<20} | CNPJ: {self.cnpj:<18} | Setor: {self.setor:<15} | Contato: {self.contato:<15} | Telefone: {self.telefone}")

class GerenciadorFornecedor:
    # classe responsavel por gerenciar a lista de fornecedores e operacoes no banco
    def __init__(self):
        self.fornecedores = []  # lista que guarda os objetos fornecedor em memoria
        self.ID_CONTADOR = 0   # contador de ids

    def carregar_fornecedores(self):
        # carrega os fornecedores do banco quando o programa inicia
        # sem isso a lista ficaria vazia toda vez que abrisse o programa
        cursor.execute("SELECT * FROM TB_FORNECEDOR")

        for linha in cursor.fetchall():
            forn = Fornecedor(linha[0], linha[1], linha[2], linha[3], linha[4], linha[5])
            self.fornecedores.append(forn)

        if self.fornecedores:
            # pega o maior id existente pra continuar de onde parou
            self.ID_CONTADOR = max(forn.id for forn in self.fornecedores) + 1

    def incluir_fornecedor(self, nome, cnpj, setor, contato, telefone):
        # verifica se ja existe um fornecedor com esse cnpj
        for forn in self.fornecedores:
            if forn.cnpj == cnpj:
                print(f"ERRO: O CNPJ '{cnpj}' já está cadastrado para outro fornecedor.")
                return

        # insere o fornecedor no banco de dados
        cursor.execute("INSERT INTO TB_FORNECEDOR (forn_nome, forn_cnpj, forn_setor, forn_contato, forn_telefone) VALUES (?, ?, ?, ?, ?)",
                       (nome, cnpj, setor, contato, telefone))
        conexao.commit()

        # pega o id gerado pelo banco automaticamente
        self.ID_CONTADOR = cursor.lastrowid
        novo_forn = Fornecedor(self.ID_CONTADOR, nome, cnpj, setor, contato, telefone)
        self.fornecedores.append(novo_forn)
        print(f"{nome} (ID: {novo_forn.id}) foi incluído com sucesso.")

    def listar_fornecedores(self):
        if not self.fornecedores:
            print("\n--- NENHUM FORNECEDOR CADASTRADO. ---")
            pausar()
            return

        # busca todos os fornecedores direto do banco pra garantir dados atualizados
        cursor.execute("SELECT * FROM TB_FORNECEDOR")
        self.fornecedores = []

        for linha in cursor.fetchall():
            forn = Fornecedor(linha[0], linha[1], linha[2], linha[3], linha[4], linha[5])
            self.fornecedores.append(forn)

        print("\n--- LISTA DE FORNECEDORES CADASTRADOS ---")
        for forn in self.fornecedores:
            forn.exibir()
        print("------------------------------------\n")
        pausar()

    def consultar_fornecedor(self, id_forn):
        # busca um fornecedor especifico pelo id no banco
        try:
            id_busca = int(id_forn)
            cursor.execute("SELECT * FROM TB_FORNECEDOR WHERE forn_id = ?", (id_busca,))
            linha = cursor.fetchone()  # retorna só uma linha ou None se não achar

            if linha:
                return Fornecedor(linha[0], linha[1], linha[2], linha[3], linha[4], linha[5])
            return None

        except ValueError:
            print(f"Fornecedor com ID '{id_forn}' não encontrado. (ID inválido.)")
            return None

    def menu_consultar(self):
        # menu com varias opçoes de busca de fornecedor
        if not self.fornecedores:
            print("\n--- NENHUM FORNECEDOR CADASTRADO. ---")
            pausar()
            return

        while True:
            limpar_terminal()
            print("\n--- CONSULTA ---")
            print("1. Por nome")
            print("2. Por ID")
            print("3. Por setor")
            print("4. Por contato")
            print("5. Por CNPJ")
            print("0. Voltar ao Menu Anterior\n")

            opcao = input("Escolha uma opção de consulta: ")

            if opcao == '1':
                limpar_terminal()
                nome_busca = input("Nome do fornecedor para consultar: ").lower()
                encontrados = []
                for forn in self.fornecedores:
                    if nome_busca in forn.nome.lower():
                        encontrados.append(forn)
                if encontrados:
                    print(f"\nResultados para nome '{nome_busca}':")
                    for forn in encontrados:
                        forn.exibir()
                else:
                    print(f"Nenhum fornecedor encontrado com o nome '{nome_busca}'.")
                pausar()

            elif opcao == '2':
                limpar_terminal()
                id_forn = input("ID do fornecedor para consultar: ")
                forn = self.consultar_fornecedor(id_forn)
                if forn:
                    forn.exibir()
                else:
                    print(f"Nenhum fornecedor encontrado com o ID '{id_forn}'.")
                pausar()

            elif opcao == '3':
                limpar_terminal()
                setor_busca = input("Setor para consultar: ").lower()
                encontrados = []
                for forn in self.fornecedores:
                    if setor_busca in forn.setor.lower():
                        encontrados.append(forn)
                if encontrados:
                    print(f"\nResultados para setor '{setor_busca}':")
                    for forn in encontrados:
                        forn.exibir()
                else:
                    print(f"Nenhum fornecedor encontrado no setor '{setor_busca}'.")
                pausar()

            elif opcao == '4':
                limpar_terminal()
                contato_busca = input("Nome do contato para consultar: ").lower()
                encontrados = []
                for forn in self.fornecedores:
                    if contato_busca in forn.contato.lower():
                        encontrados.append(forn)
                if encontrados:
                    print(f"\nResultados para contato '{contato_busca}':")
                    for forn in encontrados:
                        forn.exibir()
                else:
                    print(f"Nenhum fornecedor encontrado com o contato '{contato_busca}'.")
                pausar()

            elif opcao == '5':
                limpar_terminal()
                cnpj_busca = input("CNPJ do fornecedor para consultar: ")
                encontrados = []
                for forn in self.fornecedores:
                    if cnpj_busca in forn.cnpj.lower():
                        encontrados.append(forn)
                if encontrados:
                    print(f"\nResultados para CNPJ '{cnpj_busca}':")
                    for forn in encontrados:
                        forn.exibir()
                else:
                    print(f"Nenhum fornecedor encontrado com o CNPJ '{cnpj_busca}'.")
                pausar()

            elif opcao == '0':
                break
            else:
                limpar_terminal()
                print("Opção inválida.")
                pausar()

    def alterar_fornecedor(self, id_forn, novo_nome, novo_cnpj, novo_setor, novo_contato, novo_telefone):
        # busca o fornecedor pelo id antes de alterar
        forn_encontrado = self.consultar_fornecedor(id_forn)

        if forn_encontrado is None:
            print(f"ERRO DE ALTERAÇÃO: fornecedor com ID {id_forn} não encontrado.")
            pausar()
            return

        # só atualiza os campos que foram preenchidos
        if novo_nome:
            forn_encontrado.nome = novo_nome
        if novo_cnpj:
            forn_encontrado.cnpj = novo_cnpj
        if novo_setor:
            forn_encontrado.setor = novo_setor
        if novo_contato:
            forn_encontrado.contato = novo_contato
        if novo_telefone:
            forn_encontrado.telefone = novo_telefone

        # atualiza todos os campos no banco de dados
        cursor.execute("""
            UPDATE TB_FORNECEDOR 
            SET forn_nome=?, forn_cnpj=?, forn_setor=?, forn_contato=?, forn_telefone=?
            WHERE forn_id=?
        """, (forn_encontrado.nome, forn_encontrado.cnpj, forn_encontrado.setor,
              forn_encontrado.contato, forn_encontrado.telefone, id_forn))
        conexao.commit()
        print(f"Fornecedor ID {id_forn} atualizado com sucesso.")
        pausar()

    def excluir_fornecedor(self, id_forn):
        forn_para_remover = self.consultar_fornecedor(id_forn)
        
        if forn_para_remover is None:
            print(f"ERRO DE EXCLUSÃO: fornecedor com ID {id_forn} não encontrado.")
            return
    
        cursor.execute("DELETE FROM TB_FORNECEDOR WHERE forn_id = ?", (id_forn,))
        conexao.commit()
        
        # remove da lista pelo ID em vez de pelo objeto
        self.fornecedores = [f for f in self.fornecedores if f.id != id_forn]
        print(f"Fornecedor ID {id_forn} foi excluído com sucesso.")

# cria o gerenciador e carrega os dados do banco antes de abrir o menu
gerenciador = GerenciadorFornecedor()
gerenciador.carregar_fornecedores()

def menu_fornecedor():
    while True:
        limpar_terminal()
        print("\n=== Fornecedores ===")
        print("1. Incluir novo fornecedor")
        print("2. Listar todos")
        print("3. Consultar fornecedor")
        print("4. Alterar fornecedor")
        print("5. Excluir fornecedor")
        print("0. Voltar ao Menu Principal\n")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            limpar_terminal()
            print("\n--- INCLUSÃO ---")
            nome = input("Nome da empresa: ").strip().title()
            cnpj = input("CNPJ: ").strip()
            setor = input("Setor (ex: Material, Tecnologia, Alimentação): ").strip().title()
            contato = input("Nome do contato responsável: ").strip().title()
            telefone = input("Telefone: ").strip()
            gerenciador.incluir_fornecedor(nome, cnpj, setor, contato, telefone)

        elif opcao == '2':
            limpar_terminal()
            gerenciador.listar_fornecedores()

        elif opcao == '3':
            limpar_terminal()
            gerenciador.menu_consultar()

        elif opcao == '4':
            limpar_terminal()
            if not gerenciador.fornecedores:
                print("\n--- NENHUM FORNECEDOR CADASTRADO. ---")
                pausar()
                continue
            print("\n--- ALTERAÇÃO ---")
            try:
                id_forn = int(input("ID do fornecedor para alterar: "))
                novo_nome = input("Novo nome da empresa (deixe em branco para manter): ").strip().title()
                novo_cnpj = input("Novo CNPJ (deixe em branco para manter): ").strip()
                novo_setor = input("Novo setor (deixe em branco para manter): ").strip().title()
                novo_contato = input("Novo contato (deixe em branco para manter): ").strip().title()
                novo_telefone = input("Novo telefone (deixe em branco para manter): ").strip()
                gerenciador.alterar_fornecedor(id_forn, novo_nome, novo_cnpj, novo_setor, novo_contato, novo_telefone)
            except ValueError:
                print("ERRO: O ID deve ser um número inteiro.")
                pausar()

        elif opcao == '5':
            limpar_terminal()
            if not gerenciador.fornecedores:
                print("\n--- NENHUM FORNECEDOR CADASTRADO. ---")
                pausar()
                continue
            print("\n--- EXCLUSÃO ---")
            try:
                id_forn = int(input("ID do fornecedor para excluir: "))
                gerenciador.excluir_fornecedor(id_forn)
            except ValueError:
                print("ERRO: O ID deve ser um número inteiro.")
                pausar()

        elif opcao == '0':
            limpar_terminal()
            break

        else:
            input("Opção inválida. Aperte ENTER e tente novamente.")

#  INTERFACE TKINTER
def abrir_tela_fornecedor(janela_pai):
    gerenciador.carregar_fornecedores()
    
    tela = Toplevel(janela_pai)
    tela.title("Gestão de Fornecedores")
    tela.geometry("900x600")

    Label(tela, text="GESTÃO DE FORNECEDORES", font=("Arial", 16, "bold")).pack(pady=10)

    frame_form = Frame(tela)
    frame_form.pack(pady=10)

    campos = ["Nome", "CNPJ", "Setor", "Contato", "Telefone"]
    entries = {}
    for i, campo in enumerate(campos):
        Label(frame_form, text=f"{campo}:").grid(row=i, column=0, sticky=W, padx=5, pady=2)
        ent = Entry(frame_form, width=40)
        ent.grid(row=i, column=1, padx=5, pady=2)
        entries[campo] = ent

    colunas = ("ID", "Nome", "CNPJ", "Setor", "Contato", "Telefone")
    tabela = ttk.Treeview(tela, columns=colunas, show="headings", height=10)
    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=120)
    tabela.pack(fill=BOTH, expand=True, padx=20, pady=10)

    def carregar_tabela():
        tabela.delete(*tabela.get_children())
        gerenciador.carregar_fornecedores() # Atualiza a lista em memoria
        for forn in gerenciador.fornecedores:
            tabela.insert("", END, values=(forn.id, forn.nome, forn.cnpj, forn.setor, forn.contato, forn.telefone))

    def salvar():
        gerenciador.incluir_fornecedor(
            entries["Nome"].get().title(),
            entries["CNPJ"].get(),
            entries["Setor"].get().title(),
            entries["Contato"].get().title(),
            entries["Telefone"].get()
        )
        carregar_tabela()
        messagebox.showinfo("Sucesso", "Fornecedor incluído/processado!", parent=tela)

    def excluir():
        selecionado = tabela.focus()
        if not selecionado:
            return
        id_forn = int(tabela.item(selecionado, "values")[0])
        gerenciador.excluir_fornecedor(id_forn)
        carregar_tabela()

    frame_btns = Frame(tela)
    frame_btns.pack(pady=10)
    Button(frame_btns, text="Salvar Fornecedor", command=salvar, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
    Button(frame_btns, text="Excluir Selecionado", command=excluir, bg="#f44336", fg="white").grid(row=0, column=1, padx=10)

    carregar_tabela()


if __name__ == "__main__":
    menu_fornecedor()