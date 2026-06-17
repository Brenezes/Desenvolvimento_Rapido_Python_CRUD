from tkinter import *
from tkinter import PhotoImage
from venda import abrir_tela_venda
from compras import abrir_tela_compra
from produtos import abrir_tela_produto
from fornecedor import abrir_tela_fornecedor
from cliente import InterfaceCliente

def main():
    janela = Tk()
    janela.title("StyloGest - Sistema de Gestão")
    janela.attributes("-fullscreen", True)

    # Funções de chamada
    def chamar_vendas(): abrir_tela_venda(janela)
    def chamar_compras(): abrir_tela_compra(janela)
    def chamar_produtos(): abrir_tela_produto(janela)
    def chamar_fornecedores(): abrir_tela_fornecedor(janela)
    def chamar_clientes(): 
        # Instancia a interface de cliente passando a janela principal como pai
        app_cliente = InterfaceCliente(janela)
        app_cliente.criar_janela()

    def sair():
        janela.destroy()

    # Barra de Menus Superior
    barra_menu = Menu(janela, font=("Arial", 14))

    menu_cadastros = Menu(barra_menu, tearoff=0, font=("Arial", 14))
    menu_cadastros.add_command(label="Clientes", command=chamar_clientes)
    menu_cadastros.add_command(label="Fornecedores", command=chamar_fornecedores)
    menu_cadastros.add_command(label="Produtos", command=chamar_produtos)
    menu_cadastros.add_separator()
    menu_cadastros.add_command(label="Sair", command=sair)

    menu_operacoes = Menu(barra_menu, tearoff=0, font=("Arial", 14))
    menu_operacoes.add_command(label="Vendas", command=chamar_vendas)
    menu_operacoes.add_command(label="Compras", command=chamar_compras)

    barra_menu.add_cascade(label="Cadastros", menu=menu_cadastros)
    barra_menu.add_cascade(label="Operações", menu=menu_operacoes)
    
    janela.config(menu=barra_menu)

    # Título Central
    Label(janela, text="StyloGest", font=("Arial", 30, "bold"), fg="#c8102e").pack(pady=(100, 10))
    Label(janela, text="Sistema de Gestão Comercial", font=("Arial", 16), fg="#666").pack()

    # Painel de Botões Rápidos no centro da tela
    frame_botoes = Frame(janela)
    frame_botoes.pack(pady=50)

    btn_config = {"font": ("Arial", 14), "width": 20, "pady": 15, "bg": "#e0e0e0", "cursor": "hand2"}

    Button(frame_botoes, text="🛒 Módulo de Vendas", command=chamar_vendas, **btn_config).grid(row=0, column=0, padx=20, pady=20)
    Button(frame_botoes, text="📦 Módulo de Compras", command=chamar_compras, **btn_config).grid(row=0, column=1, padx=20, pady=20)
    Button(frame_botoes, text="👥 Clientes", command=chamar_clientes, **btn_config).grid(row=1, column=0, padx=20, pady=20)
    Button(frame_botoes, text="🚚 Fornecedores", command=chamar_fornecedores, **btn_config).grid(row=1, column=1, padx=20, pady=20)
    Button(frame_botoes, text="🏷️ Produtos", command=chamar_produtos, **btn_config).grid(row=2, column=0, columnspan=2, padx=20, pady=20)

    janela.mainloop()

if __name__ == "__main__":
    main()