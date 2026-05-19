import os
import json
from datetime import date

ARQUIVO_VENDAS = "vendas.json"

class Venda:
    def __init__(self, id, data, cliente, produto, quantidade, preco_unitario, pagamento):
        self.id             = id
        self.data           = data
        self.cliente        = cliente
        self.produto        = produto
        self.quantidade     = int(quantidade)
        self.preco_unitario = float(preco_unitario)
        self.total          = self.quantidade * self.preco_unitario
        self.pagamento      = pagamento

    def recalcular_total(self):
        self.total = self.quantidade * self.preco_unitario

    def to_dict(self):
        return {
            "id":             self.id,
            "data":           self.data,
            "cliente":        self.cliente,
            "produto":        self.produto,
            "quantidade":     self.quantidade,
            "preco_unitario": self.preco_unitario,
            "total":          self.total,
            "pagamento":      self.pagamento,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id            = d["id"],
            data          = d["data"],
            cliente       = d["cliente"],
            produto       = d["produto"],
            quantidade    = d["quantidade"],
            preco_unitario= d["preco_unitario"],
            pagamento     = d["pagamento"],
        )

    def __str__(self):
        total_fmt = formatar_moeda(self.total)
        return (
            f"ID: {self.id:<4} | Data: {self.data:<12} | Cliente: {self.cliente:<20} | "
            f"Produto: {self.produto:<20} | Qtd: {self.quantidade:<6} | "
            f"Total: {total_fmt:<14} | Pagamento: {self.pagamento}"
        )

class RepositorioVendas:
    def __init__(self, arquivo=ARQUIVO_VENDAS):
        self.arquivo    = arquivo
        self.vendas     = []
        self._contador  = 0
        self._carregar()

    def _carregar(self):
        if not os.path.exists(self.arquivo):
            return
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.vendas    = [Venda.from_dict(d) for d in dados.get("vendas", [])]
            self._contador = dados.get("contador", 0)
        except (json.JSONDecodeError, KeyError):
            print(f"AVISO: arquivo '{self.arquivo}' corrompido — iniciando vazio.")
            self.vendas    = []
            self._contador = 0

    def _salvar(self):
        dados = {
            "contador": self._contador,
            "vendas":   [v.to_dict() for v in self.vendas],
        }
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def inserir(self, cliente, produto, quantidade, preco_unitario, pagamento):
        hoje   = date.today().strftime("%d/%m/%Y")
        venda  = Venda(self._contador, hoje, cliente, produto, quantidade, preco_unitario, pagamento)
        self.vendas.append(venda)
        self._contador += 1
        self._salvar()
        return venda

    def listar(self):
        return list(self.vendas)

    def buscar_por_id(self, id_venda):
        for v in self.vendas:
            if v.id == id_venda:
                return v
        return None

    def alterar(self, id_venda, novo_cliente=None, novo_produto=None,
                nova_quantidade=None, novo_preco=None, novo_pagamento=None):
        v = self.buscar_por_id(id_venda)
        if v is None:
            return None
        if novo_cliente:
            v.cliente = novo_cliente
        if novo_produto:
            v.produto = novo_produto
        if nova_quantidade:
            v.quantidade = int(nova_quantidade)
        if novo_preco:
            v.preco_unitario = float(novo_preco)
        if novo_pagamento:
            v.pagamento = novo_pagamento
        v.recalcular_total()
        self._salvar()
        return v

    def excluir(self, id_venda):
        v = self.buscar_por_id(id_venda)
        if v is None:
            return None
        self.vendas.remove(v)
        self._salvar()
        return v

    def excluir_tudo(self):
        self.vendas    = []
        self._contador = 0
        self._salvar()

    def buscar_por_cliente(self, termo):
        return [v for v in self.vendas if termo.lower() in v.cliente.lower()]

    def buscar_por_produto(self, termo):
        return [v for v in self.vendas if termo.lower() in v.produto.lower()]

    def buscar_por_pagamento(self, termo):
        return [v for v in self.vendas if termo.lower() in v.pagamento.lower()]

    def buscar_por_data(self, data):
        return [v for v in self.vendas if v.data == data]


def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def pausar():
    input("\nPressione Enter para continuar...")

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return "R$ 0,00"

def separador():
    print("-" * 90)

def menu_consultar(repo: RepositorioVendas):
    if not repo.listar():
        print("\n--- NENHUMA VENDA REGISTRADA. ---")
        pausar()
        return

    while True:
        limpar_terminal()
        print("\n─── CONSULTA DE VENDAS ───")
        print("1. Por ID")
        print("2. Por cliente")
        print("3. Por produto")
        print("4. Por forma de pagamento")
        print("5. Por data")
        print("0. Voltar\n")

        opcao = input("Opção: ").strip()

        limpar_terminal()

        if opcao == "1":
            try:
                id_v = int(input("ID da venda: "))
                v = repo.buscar_por_id(id_v)
                if v:
                    separador()
                    print(v)
                    separador()
                else:
                    print(f"Venda ID {id_v} não encontrada.")
            except ValueError:
                print("ID inválido.")

        elif opcao == "2":
            termo = input("Nome do cliente: ").strip()
            resultados = repo.buscar_por_cliente(termo)
            _exibir_lista(resultados, f"cliente '{termo}'")

        elif opcao == "3":
            termo = input("Nome do produto: ").strip()
            resultados = repo.buscar_por_produto(termo)
            _exibir_lista(resultados, f"produto '{termo}'")

        elif opcao == "4":
            print("Formas: Dinheiro | Cartão Débito | Cartão Crédito | Pix | Boleto")
            termo = input("Forma de pagamento: ").strip()
            resultados = repo.buscar_por_pagamento(termo)
            _exibir_lista(resultados, f"pagamento '{termo}'")

        elif opcao == "5":
            data = input("Data (dd/mm/aaaa): ").strip()
            resultados = repo.buscar_por_data(data)
            _exibir_lista(resultados, f"data '{data}'")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")

        pausar()

def _exibir_lista(lista, rotulo):
    if lista:
        separador()
        for v in lista:
            print(v)
        separador()
        print(f"Total encontrado: {len(lista)} venda(s).")
    else:
        print(f"Nenhuma venda encontrada para {rotulo}.")

def menu_venda():
    repo = RepositorioVendas()

    while True:
        limpar_terminal()
        print("\n╔══════════════════════╗")
        print("║    GESTÃO DE VENDAS  ║")
        print("╠══════════════════════╣")
        print("║ 1. Inserir venda     ║")
        print("║ 2. Listar vendas     ║")
        print("║ 3. Consultar venda   ║")
        print("║ 4. Alterar venda     ║")
        print("║ 5. Excluir venda     ║")
        print("║ 6. Excluir tudo      ║")
        print("║ 0. Sair              ║")
        print("╚══════════════════════╝\n")

        opcao = input("Opção: ").strip()
        limpar_terminal()

        if opcao == "1":
            print("─── REGISTRAR VENDA ───")
            cliente        = input("Nome do cliente: ").strip().title()
            produto        = input("Nome do produto: ").strip().title()
            try:
                quantidade     = int(input("Quantidade: "))
                preco_unitario = float(input("Preço unitário (R$): "))
                print("Formas: Dinheiro | Cartão Débito | Cartão Crédito | Pix | Boleto")
                pagamento = input("Forma de pagamento: ").strip().title()
                v = repo.inserir(cliente, produto, quantidade, preco_unitario, pagamento)
                print(f"\n✔ Venda registrada com sucesso!")
                print(f"  ID {v.id} | {v.produto} | Total: {formatar_moeda(v.total)}")
            except ValueError:
                print("ERRO: Quantidade e preço devem ser números válidos.")
            pausar()

        elif opcao == "2":
            vendas = repo.listar()
            if not vendas:
                print("Nenhuma venda registrada.")
            else:
                print(f"─── LISTA DE VENDAS ({len(vendas)} registro(s)) ───")
                separador()
                for v in vendas:
                    print(v)
                separador()
            pausar()

        elif opcao == "3":
            menu_consultar(repo)

        elif opcao == "4":
            if not repo.listar():
                print("Nenhuma venda registrada.")
                pausar()
                continue
            print("─── ALTERAR VENDA ───")
            try:
                id_v = int(input("ID da venda: "))
                v = repo.buscar_por_id(id_v)
                if v is None:
                    print(f"Venda ID {id_v} não encontrada.")
                    pausar()
                    continue
                print(f"\nVenda atual:\n{v}\n")
                print("(Deixe em branco para manter o valor atual)")
                novo_cliente   = input(f"Novo cliente [{v.cliente}]: ").strip().title() or None
                novo_produto   = input(f"Novo produto [{v.produto}]: ").strip().title() or None
                nova_qtd       = input(f"Nova quantidade [{v.quantidade}]: ").strip() or None
                novo_preco     = input(f"Novo preço unitário [{v.preco_unitario:.2f}]: ").strip() or None
                print("Formas: Dinheiro | Cartão Débito | Cartão Crédito | Pix | Boleto")
                novo_pag       = input(f"Nova forma de pagamento [{v.pagamento}]: ").strip().title() or None
                atualizada = repo.alterar(id_v, novo_cliente, novo_produto, nova_qtd, novo_preco, novo_pag)
                print(f"\n✔ Venda ID {id_v} atualizada. Novo total: {formatar_moeda(atualizada.total)}")
            except ValueError:
                print("ERRO: ID, quantidade e preço devem ser números válidos.")
            pausar()

        elif opcao == "5":
            if not repo.listar():
                print("Nenhuma venda registrada.")
                pausar()
                continue
            print("─── EXCLUIR VENDA ───")
            try:
                id_v = int(input("ID da venda para excluir: "))
                v = repo.buscar_por_id(id_v)
                if v is None:
                    print(f"Venda ID {id_v} não encontrada.")
                    pausar()
                    continue
                print(f"\n{v}")
                confirma = input("\nConfirmar exclusão? (s/n): ").strip().lower()
                if confirma == "s":
                    motivo = input("Motivo da exclusão: ").strip()
                    repo.excluir(id_v)
                    print(f"✔ Venda ID {id_v} excluída. Motivo: {motivo}")
                else:
                    print("Exclusão cancelada.")
            except ValueError:
                print("ERRO: O ID deve ser um número inteiro.")
            pausar()

        elif opcao == "6":
            total = len(repo.listar())
            if total == 0:
                print("Nenhuma venda registrada.")
                pausar()
                continue
            print(f"─── EXCLUIR TUDO ({total} venda(s)) ───")
            print("ATENÇÃO: esta ação é irreversível!")
            confirma = input("Digite CONFIRMAR para prosseguir: ").strip()
            if confirma == "CONFIRMAR":
                repo.excluir_tudo()
                print("✔ Todas as vendas foram excluídas.")
            else:
                print("Operação cancelada.")
            pausar()

        elif opcao == "0":
            print("Saindo do módulo de Vendas. Até logo!")
            break

        else:
            print("Opção inválida.")
            pausar()


if __name__ == "__main__":
    menu_venda()
