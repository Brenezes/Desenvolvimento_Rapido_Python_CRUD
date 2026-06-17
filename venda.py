import sqlite3
from datetime import date
from tkinter import *
from tkinter import messagebox, ttk

#  BANCO DE DADOS

DB = "db_sistema.db"

def conectar():
    return sqlite3.connect(DB)

def criar_tabela():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            data            TEXT    NOT NULL,
            cliente         TEXT    NOT NULL,
            produto         TEXT    NOT NULL,
            quantidade      INTEGER NOT NULL,
            preco_unitario  REAL    NOT NULL,
            total           REAL    NOT NULL,
            pagamento       TEXT    NOT NULL
        )
    """)
    con.commit()
    con.close()

def db_inserir(cliente, produto, quantidade, preco_unitario, pagamento):
    hoje  = date.today().strftime("%d/%m/%Y")
    total = quantidade * preco_unitario
    con   = conectar()
    cur   = con.cursor()
    cur.execute(
        "INSERT INTO vendas (data, cliente, produto, quantidade, preco_unitario, total, pagamento) VALUES (?,?,?,?,?,?,?)",
        (hoje, cliente, produto, quantidade, preco_unitario, total, pagamento)
    )
    con.commit()
    con.close()

def db_listar():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, data, cliente, produto, quantidade, preco_unitario, total, pagamento FROM vendas ORDER BY id")
    rows = cur.fetchall()
    con.close()
    return rows

def db_buscar_por_id(id_venda):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, data, cliente, produto, quantidade, preco_unitario, total, pagamento FROM vendas WHERE id=?", (id_venda,))
    row = cur.fetchone()
    con.close()
    return row

def db_alterar(id_venda, cliente, produto, quantidade, preco_unitario, pagamento):
    total = quantidade * preco_unitario
    con   = conectar()
    cur   = con.cursor()
    cur.execute("""
        UPDATE vendas
        SET cliente=?, produto=?, quantidade=?, preco_unitario=?, total=?, pagamento=?
        WHERE id=?
    """, (cliente, produto, quantidade, preco_unitario, total, pagamento, id_venda))
    con.commit()
    con.close()

def db_excluir(id_venda):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM vendas WHERE id=?", (id_venda,))
    con.commit()
    con.close()

def db_excluir_tudo():
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM vendas")
    con.commit()
    con.close()

def db_buscar(campo, termo):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        f"SELECT id, data, cliente, produto, quantidade, preco_unitario, total, pagamento FROM vendas WHERE {campo} LIKE ?",
        (f"%{termo}%",)
    )
    rows = cur.fetchall()
    con.close()
    return rows

#  TELA PRINCIPAL DE VENDAS

def abrir_tela_venda(janela_pai):
    criar_tabela()

    tela = Toplevel(janela_pai)
    tela.title("Gestão de Vendas")
    tela.attributes("-fullscreen", True)
    tela.configure(bg="#f0f0f0")

    # Título
    Label(tela, text="GESTÃO DE VENDAS", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=15)

    # Tabela
    frame_tabela = Frame(tela, bg="#f0f0f0")
    frame_tabela.pack(fill=BOTH, expand=True, padx=20, pady=5)

    colunas = ("ID", "Data", "Cliente", "Produto", "Qtd", "Preço Unit.", "Total", "Pagamento")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=18)

    larguras = [50, 100, 160, 160, 60, 110, 110, 130]
    for col, larg in zip(colunas, larguras):
        tabela.heading(col, text=col)
        tabela.column(col, width=larg, anchor=CENTER)

    scroll = Scrollbar(frame_tabela, orient=VERTICAL, command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    tabela.pack(side=LEFT, fill=BOTH, expand=True)
    scroll.pack(side=RIGHT, fill=Y)

    def carregar_tabela(rows=None):
        tabela.delete(*tabela.get_children())
        dados = rows if rows is not None else db_listar()
        for row in dados:
            id_, data, cliente, produto, qtd, preco, total, pag = row
            tabela.insert("", END, values=(
                id_, data, cliente, produto, qtd,
                f"R$ {preco:.2f}".replace(".", ","),
                f"R$ {total:.2f}".replace(".", ","),
                pag
            ))

    carregar_tabela()

    # Botões
    frame_btns = Frame(tela, bg="#f0f0f0")
    frame_btns.pack(pady=10)

    btn_cfg = {"font": ("Arial", 11), "width": 16, "pady": 5, "cursor": "hand2"}

    Button(frame_btns, text="Inserir",       bg="#4CAF50", fg="white", command=lambda: tela_inserir(tela, carregar_tabela),          **btn_cfg).grid(row=0, column=0, padx=8)
    Button(frame_btns, text="Atualizar",     bg="#2196F3", fg="white", command=lambda: carregar_tabela(),                            **btn_cfg).grid(row=0, column=1, padx=8)
    Button(frame_btns, text="Consultar",     bg="#FF9800", fg="white", command=lambda: tela_consultar(tela, carregar_tabela),        **btn_cfg).grid(row=0, column=2, padx=8)
    Button(frame_btns, text="Alterar",       bg="#9C27B0", fg="white", command=lambda: tela_alterar(tela, tabela, carregar_tabela),  **btn_cfg).grid(row=0, column=3, padx=8)
    Button(frame_btns, text="Excluir",       bg="#f44336", fg="white", command=lambda: acao_excluir(tabela, carregar_tabela),        **btn_cfg).grid(row=0, column=4, padx=8)
    Button(frame_btns, text="Excluir Tudo",  bg="#880000", fg="white", command=lambda: acao_excluir_tudo(carregar_tabela),           **btn_cfg).grid(row=0, column=5, padx=8)
    Button(frame_btns, text="Voltar",        bg="#607D8B", fg="white", command=tela.destroy,                                         **btn_cfg).grid(row=0, column=6, padx=8)

# Inserir 

def tela_inserir(pai, carregar_tabela):
    win = Toplevel(pai)
    win.title("Inserir Venda")
    win.geometry("420x380")
    win.resizable(False, False)
    win.configure(bg="#f0f0f0")
    win.grab_set()

    Label(win, text="Nova Venda", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)

    frame = Frame(win, bg="#f0f0f0")
    frame.pack(padx=30, pady=5, fill=X)

    v_cliente  = StringVar()
    v_produto  = StringVar()
    v_qtd      = StringVar()
    v_preco    = StringVar()
    v_pag      = StringVar()

    rotulos = ["Cliente", "Produto", "Quantidade", "Preco Unitario", "Pagamento"]
    variaveis = [v_cliente, v_produto, v_qtd, v_preco, v_pag]

    for i, (rot, var) in enumerate(zip(rotulos, variaveis)):
        Label(frame, text=rot + ":", font=("Arial", 11), bg="#f0f0f0", anchor=W).grid(row=i, column=0, sticky=W, pady=4)
        if rot == "Pagamento":
            opcoes = ["Dinheiro", "Cartao Debito", "Cartao Credito", "Pix", "Boleto"]
            cb = ttk.Combobox(frame, textvariable=var, values=opcoes, state="readonly", font=("Arial", 11), width=22)
            cb.grid(row=i, column=1, sticky=W, pady=4)
            cb.current(0)
        else:
            Entry(frame, textvariable=var, font=("Arial", 11), width=24).grid(row=i, column=1, sticky=W, pady=4)

    def salvar():
        cliente  = v_cliente.get().strip().title()
        produto  = v_produto.get().strip().title()
        pagamento = v_pag.get()
        try:
            qtd   = int(v_qtd.get())
            preco = float(v_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preco devem ser numeros.", parent=win)
            return
        if not cliente or not produto:
            messagebox.showerror("Erro", "Cliente e produto sao obrigatorios.", parent=win)
            return
        db_inserir(cliente, produto, qtd, preco, pagamento)
        carregar_tabela()
        messagebox.showinfo("Sucesso", "Venda registrada com sucesso!", parent=win)
        win.destroy()

    Button(win, text="Salvar", font=("Arial", 11), bg="#4CAF50", fg="white",
           width=14, command=salvar).pack(pady=15)

# Alterar

def tela_alterar(pai, tabela, carregar_tabela):
    selecionado = tabela.focus()
    if not selecionado:
        messagebox.showwarning("Atencao", "Selecione uma venda na tabela para alterar.")
        return

    valores = tabela.item(selecionado, "values")
    id_venda = int(valores[0])
    row = db_buscar_por_id(id_venda)
    if not row:
        messagebox.showerror("Erro", "Venda nao encontrada no banco.")
        return

    id_, data, cliente, produto, qtd, preco, total, pag = row

    win = Toplevel(pai)
    win.title(f"Alterar Venda ID {id_venda}")
    win.geometry("420x380")
    win.resizable(False, False)
    win.configure(bg="#f0f0f0")
    win.grab_set()

    Label(win, text=f"Alterar Venda - ID {id_venda}", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)

    frame = Frame(win, bg="#f0f0f0")
    frame.pack(padx=30, pady=5, fill=X)

    v_cliente  = StringVar(value=cliente)
    v_produto  = StringVar(value=produto)
    v_qtd      = StringVar(value=str(qtd))
    v_preco    = StringVar(value=str(preco))
    v_pag      = StringVar(value=pag)

    rotulos  = ["Cliente", "Produto", "Quantidade", "Preco Unitario", "Pagamento"]
    variaveis = [v_cliente, v_produto, v_qtd, v_preco, v_pag]

    for i, (rot, var) in enumerate(zip(rotulos, variaveis)):
        Label(frame, text=rot + ":", font=("Arial", 11), bg="#f0f0f0", anchor=W).grid(row=i, column=0, sticky=W, pady=4)
        if rot == "Pagamento":
            opcoes = ["Dinheiro", "Cartao Debito", "Cartao Credito", "Pix", "Boleto"]
            cb = ttk.Combobox(frame, textvariable=var, values=opcoes, state="readonly", font=("Arial", 11), width=22)
            cb.grid(row=i, column=1, sticky=W, pady=4)
        else:
            Entry(frame, textvariable=var, font=("Arial", 11), width=24).grid(row=i, column=1, sticky=W, pady=4)

    def salvar():
        try:
            nova_qtd   = int(v_qtd.get())
            novo_preco = float(v_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preco devem ser numeros.", parent=win)
            return
        db_alterar(id_venda, v_cliente.get().strip().title(), v_produto.get().strip().title(),
                   nova_qtd, novo_preco, v_pag.get())
        carregar_tabela()
        messagebox.showinfo("Sucesso", "Venda alterada com sucesso!", parent=win)
        win.destroy()

    Button(win, text="Salvar", font=("Arial", 11), bg="#9C27B0", fg="white",
           width=14, command=salvar).pack(pady=15)

# Excluir

def acao_excluir(tabela, carregar_tabela):
    selecionado = tabela.focus()
    if not selecionado:
        messagebox.showwarning("Atencao", "Selecione uma venda na tabela para excluir.")
        return
    valores  = tabela.item(selecionado, "values")
    id_venda = int(valores[0])
    confirma = messagebox.askyesno("Confirmar", f"Excluir a venda ID {id_venda}?")
    if confirma:
        db_excluir(id_venda)
        carregar_tabela()
        messagebox.showinfo("Sucesso", f"Venda ID {id_venda} excluida.")

def acao_excluir_tudo(carregar_tabela):
    confirma = messagebox.askyesno("Atencao", "Deseja excluir TODAS as vendas?\nEsta acao e irreversivel!")
    if confirma:
        db_excluir_tudo()
        carregar_tabela()
        messagebox.showinfo("Concluido", "Todas as vendas foram excluidas.")

# Consultar

def tela_consultar(pai, carregar_tabela):
    win = Toplevel(pai)
    win.title("Consultar Vendas")
    win.geometry("500x200")
    win.resizable(False, False)
    win.configure(bg="#f0f0f0")
    win.grab_set()

    Label(win, text="Consultar Vendas", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)

    frame = Frame(win, bg="#f0f0f0")
    frame.pack(padx=20, pady=5, fill=X)

    Label(frame, text="Campo:", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, sticky=W, pady=6)
    campos_busca = {"Cliente": "cliente", "Produto": "produto", "Pagamento": "pagamento"}
    v_campo = StringVar(value="Cliente")
    ttk.Combobox(frame, textvariable=v_campo, values=list(campos_busca.keys()),
                 state="readonly", font=("Arial", 11), width=18).grid(row=0, column=1, sticky=W, padx=10)

    Label(frame, text="Termo:", font=("Arial", 11), bg="#f0f0f0").grid(row=1, column=0, sticky=W, pady=6)
    v_termo = StringVar()
    Entry(frame, textvariable=v_termo, font=("Arial", 11), width=22).grid(row=1, column=1, sticky=W, padx=10)

    def buscar():
        campo_db = campos_busca[v_campo.get()]
        termo    = v_termo.get().strip()
        if not termo:
            messagebox.showwarning("Atencao", "Digite um termo para buscar.", parent=win)
            return
        rows = db_buscar(campo_db, termo)
        carregar_tabela(rows)
        messagebox.showinfo("Resultado", f"{len(rows)} venda(s) encontrada(s).", parent=win)
        win.destroy()

    def limpar():
        carregar_tabela()
        win.destroy()

    frame_btn = Frame(win, bg="#f0f0f0")
    frame_btn.pack(pady=12)
    Button(frame_btn, text="Buscar",       font=("Arial", 11), bg="#FF9800", fg="white", width=12, command=buscar).grid(row=0, column=0, padx=8)
    Button(frame_btn, text="Limpar filtro",font=("Arial", 11), bg="#607D8B", fg="white", width=14, command=limpar).grid(row=0, column=1, padx=8)


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    criar_tabela()
    abrir_tela_venda(root)
    root.mainloop()
