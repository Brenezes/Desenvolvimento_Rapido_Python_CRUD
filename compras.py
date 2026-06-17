import sqlite3
from datetime import date
from tkinter import *
from tkinter import messagebox, ttk

DB = "db_sistema.db"

STATUS_VALIDOS = ["Pendente", "Aprovada", "Recebida", "Cancelada"]

#  BANCO DE DADOS

def conectar():
    return sqlite3.connect(DB)

def criar_tabela():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            data            TEXT    NOT NULL,
            fornecedor      TEXT    NOT NULL,
            produto         TEXT    NOT NULL,
            quantidade      INTEGER NOT NULL,
            preco_unitario  REAL    NOT NULL,
            total           REAL    NOT NULL,
            status          TEXT    NOT NULL
        )
    """)
    con.commit()
    con.close()

def db_inserir(fornecedor, produto, quantidade, preco_unitario, status):
    hoje  = date.today().strftime("%d/%m/%Y")
    total = quantidade * preco_unitario
    con   = conectar()
    cur   = con.cursor()
    cur.execute(
        "INSERT INTO compras (data, fornecedor, produto, quantidade, preco_unitario, total, status) VALUES (?,?,?,?,?,?,?)",
        (hoje, fornecedor, produto, quantidade, preco_unitario, total, status)
    )
    con.commit()
    con.close()

def db_listar():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, data, fornecedor, produto, quantidade, preco_unitario, total, status FROM compras ORDER BY id")
    rows = cur.fetchall()
    con.close()
    return rows

def db_buscar_por_id(id_compra):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, data, fornecedor, produto, quantidade, preco_unitario, total, status FROM compras WHERE id=?", (id_compra,))
    row = cur.fetchone()
    con.close()
    return row

def db_alterar(id_compra, fornecedor, produto, quantidade, preco_unitario, status):
    total = quantidade * preco_unitario
    con   = conectar()
    cur   = con.cursor()
    cur.execute("""
        UPDATE compras
        SET fornecedor=?, produto=?, quantidade=?, preco_unitario=?, total=?, status=?
        WHERE id=?
    """, (fornecedor, produto, quantidade, preco_unitario, total, status, id_compra))
    con.commit()
    con.close()

def db_excluir(id_compra):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM compras WHERE id=?", (id_compra,))
    con.commit()
    con.close()

def db_excluir_tudo():
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM compras")
    con.commit()
    con.close()

def db_buscar(campo, termo):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        f"SELECT id, data, fornecedor, produto, quantidade, preco_unitario, total, status FROM compras WHERE {campo} LIKE ?",
        (f"%{termo}%",)
    )
    rows = cur.fetchall()
    con.close()
    return rows

#  TELA PRINCIPAL DE COMPRAS

def abrir_tela_compra(janela_pai):
    criar_tabela()

    tela = Toplevel(janela_pai)
    tela.title("Gestao de Compras")
    tela.attributes("-fullscreen", True)
    tela.configure(bg="#f0f0f0")

    # Titulo
    Label(tela, text="GESTAO DE COMPRAS", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=15)

    # Tabela
    frame_tabela = Frame(tela, bg="#f0f0f0")
    frame_tabela.pack(fill=BOTH, expand=True, padx=20, pady=5)

    colunas = ("ID", "Data", "Fornecedor", "Produto", "Qtd", "Preco Unit.", "Total", "Status")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=18)

    larguras = [50, 100, 160, 160, 60, 110, 110, 110]
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
            id_, data, fornecedor, produto, qtd, preco, total, status = row
            tabela.insert("", END, values=(
                id_, data, fornecedor, produto, qtd,
                f"R$ {preco:.2f}".replace(".", ","),
                f"R$ {total:.2f}".replace(".", ","),
                status
            ))

    carregar_tabela()

    # Botoes
    frame_btns = Frame(tela, bg="#f0f0f0")
    frame_btns.pack(pady=10)

    btn_cfg = {"font": ("Arial", 11), "width": 16, "pady": 5, "cursor": "hand2"}

    Button(frame_btns, text="Inserir",      bg="#4CAF50", fg="white", command=lambda: tela_inserir(tela, carregar_tabela),         **btn_cfg).grid(row=0, column=0, padx=8)
    Button(frame_btns, text="Atualizar",    bg="#2196F3", fg="white", command=lambda: carregar_tabela(),                           **btn_cfg).grid(row=0, column=1, padx=8)
    Button(frame_btns, text="Consultar",    bg="#FF9800", fg="white", command=lambda: tela_consultar(tela, carregar_tabela),       **btn_cfg).grid(row=0, column=2, padx=8)
    Button(frame_btns, text="Alterar",      bg="#9C27B0", fg="white", command=lambda: tela_alterar(tela, tabela, carregar_tabela), **btn_cfg).grid(row=0, column=3, padx=8)
    Button(frame_btns, text="Excluir",      bg="#f44336", fg="white", command=lambda: acao_excluir(tabela, carregar_tabela),       **btn_cfg).grid(row=0, column=4, padx=8)
    Button(frame_btns, text="Excluir Tudo", bg="#880000", fg="white", command=lambda: acao_excluir_tudo(carregar_tabela),          **btn_cfg).grid(row=0, column=5, padx=8)
    Button(frame_btns, text="Voltar",       bg="#607D8B", fg="white", command=tela.destroy,                                        **btn_cfg).grid(row=0, column=6, padx=8)

# Inserir

def tela_inserir(pai, carregar_tabela):
    win = Toplevel(pai)
    win.title("Inserir Compra")
    win.geometry("420x380")
    win.resizable(False, False)
    win.configure(bg="#f0f0f0")
    win.grab_set()

    Label(win, text="Nova Compra", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)

    frame = Frame(win, bg="#f0f0f0")
    frame.pack(padx=30, pady=5, fill=X)

    v_forn  = StringVar()
    v_prod  = StringVar()
    v_qtd   = StringVar()
    v_preco = StringVar()
    v_stat  = StringVar()

    rotulos   = ["Fornecedor", "Produto", "Quantidade", "Preco Unitario", "Status"]
    variaveis = [v_forn, v_prod, v_qtd, v_preco, v_stat]

    for i, (rot, var) in enumerate(zip(rotulos, variaveis)):
        Label(frame, text=rot + ":", font=("Arial", 11), bg="#f0f0f0", anchor=W).grid(row=i, column=0, sticky=W, pady=4)
        if rot == "Status":
            cb = ttk.Combobox(frame, textvariable=var, values=STATUS_VALIDOS, state="readonly", font=("Arial", 11), width=22)
            cb.grid(row=i, column=1, sticky=W, pady=4)
            cb.current(0)
        else:
            Entry(frame, textvariable=var, font=("Arial", 11), width=24).grid(row=i, column=1, sticky=W, pady=4)

    def salvar():
        fornecedor = v_forn.get().strip().title()
        produto    = v_prod.get().strip().title()
        status     = v_stat.get()
        try:
            qtd   = int(v_qtd.get())
            preco = float(v_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preco devem ser numeros.", parent=win)
            return
        if not fornecedor or not produto:
            messagebox.showerror("Erro", "Fornecedor e produto sao obrigatorios.", parent=win)
            return
        db_inserir(fornecedor, produto, qtd, preco, status)
        carregar_tabela()
        messagebox.showinfo("Sucesso", "Compra registrada com sucesso!", parent=win)
        win.destroy()

    Button(win, text="Salvar", font=("Arial", 11), bg="#4CAF50", fg="white",
           width=14, command=salvar).pack(pady=15)

# Alterar

def tela_alterar(pai, tabela, carregar_tabela):
    selecionado = tabela.focus()
    if not selecionado:
        messagebox.showwarning("Atencao", "Selecione uma compra na tabela para alterar.")
        return

    valores   = tabela.item(selecionado, "values")
    id_compra = int(valores[0])
    row       = db_buscar_por_id(id_compra)
    if not row:
        messagebox.showerror("Erro", "Compra nao encontrada no banco.")
        return

    id_, data, fornecedor, produto, qtd, preco, total, status = row

    win = Toplevel(pai)
    win.title(f"Alterar Compra ID {id_compra}")
    win.geometry("420x380")
    win.resizable(False, False)
    win.configure(bg="#f0f0f0")
    win.grab_set()

    Label(win, text=f"Alterar Compra - ID {id_compra}", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)

    frame = Frame(win, bg="#f0f0f0")
    frame.pack(padx=30, pady=5, fill=X)

    v_forn  = StringVar(value=fornecedor)
    v_prod  = StringVar(value=produto)
    v_qtd   = StringVar(value=str(qtd))
    v_preco = StringVar(value=str(preco))
    v_stat  = StringVar(value=status)

    rotulos   = ["Fornecedor", "Produto", "Quantidade", "Preco Unitario", "Status"]
    variaveis = [v_forn, v_prod, v_qtd, v_preco, v_stat]

    for i, (rot, var) in enumerate(zip(rotulos, variaveis)):
        Label(frame, text=rot + ":", font=("Arial", 11), bg="#f0f0f0", anchor=W).grid(row=i, column=0, sticky=W, pady=4)
        if rot == "Status":
            cb = ttk.Combobox(frame, textvariable=var, values=STATUS_VALIDOS, state="readonly", font=("Arial", 11), width=22)
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
        db_alterar(id_compra, v_forn.get().strip().title(), v_prod.get().strip().title(),
                   nova_qtd, novo_preco, v_stat.get())
        carregar_tabela()
        messagebox.showinfo("Sucesso", "Compra alterada com sucesso!", parent=win)
        win.destroy()

    Button(win, text="Salvar", font=("Arial", 11), bg="#9C27B0", fg="white",
           width=14, command=salvar).pack(pady=15)

# Excluir

def acao_excluir(tabela, carregar_tabela):
    selecionado = tabela.focus()
    if not selecionado:
        messagebox.showwarning("Atencao", "Selecione uma compra na tabela para excluir.")
        return
    valores   = tabela.item(selecionado, "values")
    id_compra = int(valores[0])
    confirma  = messagebox.askyesno("Confirmar", f"Excluir a compra ID {id_compra}?")
    if confirma:
        db_excluir(id_compra)
        carregar_tabela()
        messagebox.showinfo("Sucesso", f"Compra ID {id_compra} excluida.")

def acao_excluir_tudo(carregar_tabela):
    confirma = messagebox.askyesno("Atencao", "Deseja excluir TODAS as compras?\nEsta acao e irreversivel!")
    if confirma:
        db_excluir_tudo()
        carregar_tabela()
        messagebox.showinfo("Concluido", "Todas as compras foram excluidas.")

# Consultar

def tela_consultar(pai, carregar_tabela):
    win = Toplevel(pai)
    win.title("Consultar Compras")
    win.geometry("500x200")
    win.resizable(False, False)
    win.configure(bg="#f0f0f0")
    win.grab_set()

    Label(win, text="Consultar Compras", font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=10)

    frame = Frame(win, bg="#f0f0f0")
    frame.pack(padx=20, pady=5, fill=X)

    Label(frame, text="Campo:", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, sticky=W, pady=6)
    campos_busca = {"Fornecedor": "fornecedor", "Produto": "produto", "Status": "status"}
    v_campo = StringVar(value="Fornecedor")
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
        messagebox.showinfo("Resultado", f"{len(rows)} compra(s) encontrada(s).", parent=win)
        win.destroy()

    def limpar():
        carregar_tabela()
        win.destroy()

    frame_btn = Frame(win, bg="#f0f0f0")
    frame_btn.pack(pady=12)
    Button(frame_btn, text="Buscar",        font=("Arial", 11), bg="#FF9800", fg="white", width=12, command=buscar).grid(row=0, column=0, padx=8)
    Button(frame_btn, text="Limpar filtro", font=("Arial", 11), bg="#607D8B", fg="white", width=14, command=limpar).grid(row=0, column=1, padx=8)


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    criar_tabela()
    abrir_tela_compra(root)
    root.mainloop()
