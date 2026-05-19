from compras import menu_compra
from venda import menu_venda
from cliente import menu_clientes
from produtos import menu_produtos
from fornecedor import menu_fornecedor

def menu_principal():
    while True:
        print("\n╔══════════════════════════════╗")
        print("║   BEM-VINDO À RENNER S.A.    ║")
        print("╠══════════════════════════════╣")
        print("║ 1. Gerenciar Compras         ║")
        print("║ 2. Gerenciar Vendas          ║")
        print("║ 3. Gerenciar Fornecedores    ║")
        print("║ 4. Gerenciar Compras         ║")
        print("║ 5. Gerenciar Vendas          ║")
        print("║ 0. Sair do Sistema           ║")
        print("╚══════════════════════════════╝\n")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            menu_produtos()
        elif opcao == "3":
            menu_fornecedor()
        elif opcao == "4":
            menu_compra()
        elif opcao == "5":
            menu_venda()
        elif opcao == "0":
            print("\nSaindo do sistema. Até logo!\n")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()
