import os

def limpar_terminal():
    os.system("cls")

def pausar():
    input("\nPressione Enter para continuar...")

def pegar_de_arquivo_fornecedor(gerenciador):
        try:
            with open("fornecedores.txt", "r", encoding="utf-8") as arq:
                for linha in arq:
                    if not linha.strip():
                        continue
                    dados = linha.strip().split(";")
                    if len(dados) != 6:
                        continue
                    try:
                        forn = Fornecedor(int(dados[0]), dados[1], dados[2], dados[3], dados[4], dados[5])
                        gerenciador.fornecedores.append(forn)
                        gerenciador.ID_CONTADOR = forn.id + 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            with open("fornecedores.txt", "w", encoding="utf-8") as arq:
                pass

def colocar_no_arquivo_fornecedor(gerenciador):
    with open("fornecedores.txt", "w", encoding="utf-8") as arq:
        for forn in gerenciador.fornecedores:
                arq.write(f"{forn.id};{forn.nome};{forn.cnpj};{forn.setor};{forn.contato};{forn.telefone}\n")

class Fornecedor:
    def __init__(self, id_forn, nome, cnpj, setor, contato, telefone):
        self.id = id_forn
        self.nome = nome
        self.cnpj = cnpj
        self.setor = setor
        self.contato = contato
        self.telefone = telefone

    def exibir(self):
        print(f"ID: {self.id} | Nome: {self.nome:<20} | CNPJ: {self.cnpj:<18} | Setor: {self.setor:<15} | Contato: {self.contato:<15} | Telefone: {self.telefone}")

class GerenciadorFornecedor:
    def __init__(self):
        self.fornecedores = []
        self.ID_CONTADOR = 0

    def incluir_fornecedor(self, nome, cnpj, setor, contato, telefone):
        novo_forn = Fornecedor(self.ID_CONTADOR, nome, cnpj, setor, contato, telefone)
        for forn in self.fornecedores:
            if novo_forn.cnpj == forn.cnpj:
                print(f"ERRO: O CNPJ '{cnpj}' já está cadastrado para outro fornecedor.")
                pausar()
                return
  
        self.fornecedores.append(novo_forn)
        self.ID_CONTADOR += 1
        print(f"{nome} (ID: {novo_forn.id}) foi incluído com sucesso.")
        pausar()

    def listar_fornecedores(self):

        if not self.fornecedores:
            print("\n--- NENHUM FORNECEDOR CADASTRADO. ---")
            pausar()
            return

        print("\n--- LISTA DE FORNECEDORES CADASTRADOS ---")
        for forn in self.fornecedores:
            forn.exibir()
        print("------------------------------------\n")
        pausar()

    def consultar_fornecedor(self, id_forn):
        try:
            id_busca = int(id_forn)
            for forn in self.fornecedores:
                if forn.id == id_busca:
                    return forn
        except ValueError:
            print(f"Fornecedor com ID '{id_forn}' não encontrado. (ID inválido.)")
            return None

    def menu_consultar(self):
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
                    if  contato_busca in forn.contato.lower():
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

    def alterar_fornecedor(self,id_forn, novo_nome, novo_cnpj, novo_setor, novo_contato, novo_telefone):
        forn_encontrado = self.consultar_fornecedor(id_forn)

        if forn_encontrado is None:
            print(f"ERRO DE ALTERAÇÃO: fornecedor com ID {id_forn} não encontrado.")
            pausar()
            return

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

        print(f"Fornecedor ID {id_forn} atualizado com sucesso.")
        pausar()

    def excluir_fornecedor(self,id_forn):
        forn_para_remover = self.consultar_fornecedor(id_forn)


        if forn_para_remover:
            msg_confirmacao = (
                f"\nO ID {id_forn} é {forn_para_remover.nome}, do setor {forn_para_remover.setor} "
                f"com contato {forn_para_remover.contato} ({forn_para_remover.telefone}).\n"
                "Deseja seguir com a exclusão? (s/n): "
            )
            certeza = input(msg_confirmacao).lower()

            while True:
                if certeza == 's':
                    motivo = input("Por favor, informe o motivo da exclusão: ")
                    self.fornecedores.remove(forn_para_remover)
                    print(f"Fornecedor ID {id_forn} foi excluído com sucesso. Motivo: {motivo}")
                    break
                elif certeza == 'n':
                    print("\nExclusão cancelada pelo usuário.")
                    break
                else:
                    certeza = input("Entrada inválida. Responda 's' para sim ou 'n' para não: ").lower()
        else:
            print(f"ERRO DE EXCLUSÃO: fornecedor com ID {id_forn} não encontrado.")
        pausar()


def menu_fornecedor():
    gerenciador = GerenciadorFornecedor()
    pegar_de_arquivo_fornecedor(gerenciador)
    
    while True:
        limpar_terminal()
        print("\n=== Fornecedores ===")
        print("1. Incluir novo fornecedor")
        print("2. Listar todos")
        print("3. Consultar fornecedor")
        print("4. Alterar fornecedor")
        print("5. Excluir fornecedor")
        print("6. Excluir TODOS os fornecedores")
        print("7. Sair")

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

        elif opcao == '6':
            limpar_terminal()
            print("\n--- EXCLUSÃO TOTAL ---")
            validar = input("Confirme para APAGAR todos os fornecedores (s/n): ").lower().strip()
            if validar in ('s', 'sim'):
                gerenciador.fornecedores.clear()
                gerenciador.ID_CONTADOR = 0
                print("Todos os fornecedores foram excluídos.")
            else:
                print("Exclusão cancelada.")
            pausar()

        elif opcao == '7':
            limpar_terminal()
            colocar_no_arquivo_fornecedor(gerenciador)
            break


if __name__ == "__main__":
    menu_fornecedor()