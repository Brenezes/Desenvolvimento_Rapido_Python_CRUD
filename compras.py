import os
import json
from datetime import date

ARQUIVO_COMPRAS = "compras.json"

STATUS_VALIDOS = ["Pendente", "Aprovada", "Recebida", "Cancelada"]


# ══════════════════════════════════════════════
#  CLASSE COMPRA
# ══════════════════════════════════════════════

class Compra:
    def __init__(self, id, data, fornecedor, produto, quantidade, preco_unitario, status):
        self.id             = id
        self.data           = data
        self.fornecedor     = fornecedor
        self.produto        = produto
        self.quantidade     = int(quantidade)
        self.preco_unitario = float(preco_unitario)
        self.total          = self.quantidade * self.preco_unitario
        self.status         = status

    def recalcular_total(self):
        self.total = self.quantidade * self.preco_unitario

    def to_dict(self):
        return {
            "id":             self.id,
            "data":           self.data,
            "fornecedor":     self.fornecedor,
            "produto":        self.produto,
            "quantidade":     self.quantidade,
            "preco_unitario": self.preco_unitario,
            "total":          self.total,
            "status":         self.status,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id            = d["id"],
            data          = d["data"],
            fornecedor    = d["fornecedor"],
            produto       = d["produto"],
            quantidade    = d["quantidade"],
            preco_unitario= d["preco_unitario"],
            status        = d["status"],
        )

    def __str__(self):
        total_fmt = formatar_moeda(self.total)
        return (
            f"ID: {self.id:<4} | Data: {self.data:<12} | Fornecedor: {self.fornecedor:<20} | "
            f"Produto: {self.produto:<20} | Qtd: {self.quantidade:<6} | "
            f"Total: {total_fmt:<14} | Status: {self.status}"
        )


# ══════════════════════════════════════════════
#  CLASSE REPOSITÓRIO DE COMPRAS
# ══════════════════════════════════════════════

class RepositorioCompras:
    def __init__(self, arquivo=ARQUIVO_COMPRAS):
        self.arquivo   = arquivo
        self.compras   = []
        self._contador = 0
        self._carregar()

    # ── Persistência ──────────────────────────

    def _carregar(self):
        if not os.path.exists(self.arquivo):
            return
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.compras   = [Compra.from_dict(d) for d in dados.get("compras", [])]
            self._contador = dados.get("contador", 0)
        except (json.JSONDecodeError, KeyError):
            print(f"AVISO: arquivo '{self.arquivo}' corrompido — iniciando vazio.")
            self.compras   = []
            self._contador = 0

    def _salvar(self):
        dados = {
            "contador": self._contador,
            "compras":  [c.to_dict() for c in self.compras],
        }
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    # ── CRUD ──────────────────────────────────

    def inserir(self, fornecedor, produto, quantidade, preco_unitario, status):
        hoje   = date.today().strftime("%d/%m/%Y")
        compra = Compra(self._contador, hoje, fornecedor, produto, quantidade, preco_unitario, status)
        self.compras.append(compra)
        self._contador += 1
        self._salvar()
        return compra

    def listar(self):
        return list(self.compras)

    def buscar_por_id(self, id_compra):
        for c in self.compras:
            if c.id == id_compra:
                return c
        return None

    def alterar(self, id_compra, novo_fornecedor=None, novo_produto=None,
                nova_quantidade=None, novo_preco=None, novo_status=None):
        c = self.buscar_por_id(id_compra)
        if c is None:
            return None
        if novo_fornecedor:
            c.fornecedor = novo_fornecedor
        if novo_produto:
            c.produto = novo_produto
        if nova_quantidade:
            c.quantidade = int(nova_quantidade)
        if novo_preco:
            c.preco_unitario = float(novo_preco)
        if novo_status:
            c.status = novo_status
        c.recalcular_total()
        self._salvar()
        return c

    def excluir(self, id_compra):
        c = self.buscar_por_id(id_compra)
        if c is None:
            return None
        self.compras.remove(c)
        self._salvar()
        return c

    def excluir_tudo(self):
        self.compras   = []
        self._contador = 0
        self._salvar()

    # ── Consultas ─────────────────────────────

    def buscar_por_fornecedor(self, termo):
        return [c for c in self.compras if termo.lower() in c.fornecedor.lower()]

    def buscar_por_produto(self, termo):
        return [c for c in self.compras if termo.lower() in c.produto.lower()]

    def buscar_por_status(self, termo):
        return [c for c in self.compras if termo.lower() in c.status.lower()]

    def buscar_por_data(self, data):
        return [c for c in self.compras if c.data == data]


# ══════════════════════════════════════════════
#  FUNÇÕES AUXILIARES DE INTERFACE
# ══════════════════════════════════════════════

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
    print("-" * 100)


# ══════════════════════════════════════════════
#  SUBMENU: CONSULTAR
# ══════════════════════════════════════════════

def menu_consultar(repo: RepositorioCompras):
    if not repo.listar():
        print("\n--- NENHUMA COMPRA REGISTRADA. ---")
        pausar()
        return

    while True:
        limpar_terminal()
        print("\n─── CONSULTA DE COMPRAS ───")
        print("1. Por ID")
        print("2. Por fornecedor")
        print("3. Por produto")
        print("4. Por status")
        print("5. Por data")
        print("0. Voltar\n")

        opcao = input("Opção: ").strip()
        limpar_terminal()

        if opcao == "1":
            try:
                id_c = int(input("ID da compra: "))
                c = repo.buscar_por_id(id_c)
                if c:
                    separador()
                    print(c)
                    separador()
                else:
                    print(f"Compra ID {id_c} não encontrada.")
            except ValueError:
                print("ID inválido.")

        elif opcao == "2":
            termo = input("Nome do fornecedor: ").strip()
            resultados = repo.buscar_por_fornecedor(termo)
            _exibir_lista(resultados, f"fornecedor '{termo}'")

        elif opcao == "3":
            termo = input("Nome do produto: ").strip()
            resultados = repo.buscar_por_produto(termo)
            _exibir_lista(resultados, f"produto '{termo}'")

        elif opcao == "4":
            print(f"Status disponíveis: {' | '.join(STATUS_VALIDOS)}")
            termo = input("Status para consultar: ").strip()
            resultados = repo.buscar_por_status(termo)
            _exibir_lista(resultados, f"status '{termo}'")

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
        for c in lista:
            print(c)
        separador()
        print(f"Total encontrado: {len(lista)} compra(s).")
    else:
        print(f"Nenhuma compra encontrada para {rotulo}.")


# ══════════════════════════════════════════════
#  MENU PRINCIPAL DE COMPRAS
# ══════════════════════════════════════════════

def menu_compra():
    repo = RepositorioCompras()

    while True:
        limpar_terminal()
        print("\n╔═══════════════════════╗")
        print("║   GESTÃO DE COMPRAS   ║")
        print("╠═══════════════════════╣")
        print("║ 1. Inserir compra     ║")
        print("║ 2. Listar compras     ║")
        print("║ 3. Consultar compra   ║")
        print("║ 4. Alterar compra     ║")
        print("║ 5. Excluir compra     ║")
        print("║ 6. Excluir tudo       ║")
        print("║ 0. Sair               ║")
        print("╚═══════════════════════╝\n")

        opcao = input("Opção: ").strip()
        limpar_terminal()

        # ── 1. INSERIR ────────────────────────
        if opcao == "1":
            print("─── REGISTRAR COMPRA ───")
            fornecedor     = input("Nome do fornecedor: ").strip().title()
            produto        = input("Nome do produto: ").strip().title()
            try:
                quantidade     = int(input("Quantidade: "))
                preco_unitario = float(input("Preço unitário (R$): "))
                print(f"Status: {' | '.join(STATUS_VALIDOS)}")
                status = input("Status da compra: ").strip().title()
                c = repo.inserir(fornecedor, produto, quantidade, preco_unitario, status)
                print(f"\n✔ Compra registrada com sucesso!")
                print(f"  ID {c.id} | {c.produto} | Total: {formatar_moeda(c.total)}")
            except ValueError:
                print("ERRO: Quantidade e preço devem ser números válidos.")
            pausar()

        # ── 2. LISTAR ─────────────────────────
        elif opcao == "2":
            compras = repo.listar()
            if not compras:
                print("Nenhuma compra registrada.")
            else:
                print(f"─── LISTA DE COMPRAS ({len(compras)} registro(s)) ───")
                separador()
                for c in compras:
                    print(c)
                separador()
            pausar()

        # ── 3. CONSULTAR ──────────────────────
        elif opcao == "3":
            menu_consultar(repo)

        # ── 4. ALTERAR ────────────────────────
        elif opcao == "4":
            if not repo.listar():
                print("Nenhuma compra registrada.")
                pausar()
                continue
            print("─── ALTERAR COMPRA ───")
            try:
                id_c = int(input("ID da compra: "))
                c = repo.buscar_por_id(id_c)
                if c is None:
                    print(f"Compra ID {id_c} não encontrada.")
                    pausar()
                    continue
                print(f"\nCompra atual:\n{c}\n")
                print("(Deixe em branco para manter o valor atual)")
                novo_forn  = input(f"Novo fornecedor [{c.fornecedor}]: ").strip().title() or None
                novo_prod  = input(f"Novo produto [{c.produto}]: ").strip().title() or None
                nova_qtd   = input(f"Nova quantidade [{c.quantidade}]: ").strip() or None
                novo_preco = input(f"Novo preço unitário [{c.preco_unitario:.2f}]: ").strip() or None
                print(f"Status: {' | '.join(STATUS_VALIDOS)}")
                novo_stat  = input(f"Novo status [{c.status}]: ").strip().title() or None
                atualizada = repo.alterar(id_c, novo_forn, novo_prod, nova_qtd, novo_preco, novo_stat)
                print(f"\n✔ Compra ID {id_c} atualizada. Novo total: {formatar_moeda(atualizada.total)}")
            except ValueError:
                print("ERRO: ID, quantidade e preço devem ser números válidos.")
            pausar()

        # ── 5. EXCLUIR ────────────────────────
        elif opcao == "5":
            if not repo.listar():
                print("Nenhuma compra registrada.")
                pausar()
                continue
            print("─── EXCLUIR COMPRA ───")
            try:
                id_c = int(input("ID da compra para excluir: "))
                c = repo.buscar_por_id(id_c)
                if c is None:
                    print(f"Compra ID {id_c} não encontrada.")
                    pausar()
                    continue
                print(f"\n{c}")
                confirma = input("\nConfirmar exclusão? (s/n): ").strip().lower()
                if confirma == "s":
                    motivo = input("Motivo da exclusão: ").strip()
                    repo.excluir(id_c)
                    print(f"✔ Compra ID {id_c} excluída. Motivo: {motivo}")
                else:
                    print("Exclusão cancelada.")
            except ValueError:
                print("ERRO: O ID deve ser um número inteiro.")
            pausar()

        # ── 6. EXCLUIR TUDO ───────────────────
        elif opcao == "6":
            total = len(repo.listar())
            if total == 0:
                print("Nenhuma compra registrada.")
                pausar()
                continue
            print(f"─── EXCLUIR TUDO ({total} compra(s)) ───")
            print("ATENÇÃO: esta ação é irreversível!")
            confirma = input("Digite CONFIRMAR para prosseguir: ").strip()
            if confirma == "CONFIRMAR":
                repo.excluir_tudo()
                print("✔ Todas as compras foram excluídas.")
            else:
                print("Operação cancelada.")
            pausar()

        # ── 0. SAIR ───────────────────────────
        elif opcao == "0":
            print("Saindo do módulo de Compras. Até logo!")
            break

        else:
            print("Opção inválida.")
            pausar()


if __name__ == "__main__":
    menu_compra()
