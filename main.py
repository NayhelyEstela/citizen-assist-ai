"""Citizen Assist AI: assistente de terminal para jovens no primeiro emprego."""

import os
from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")


def mostrar_boas_vindas(assistente):
    print("=" * 60)
    print(f" {assistente.nome}")
    print(" Orientações para jovens no primeiro emprego")
    print("=" * 60)
    print("Aviso: este assistente NÃO é um canal oficial.")
    print("Não digite nome, CPF, telefone ou e-mail.")


def mostrar_menu():
    print("\n--- Menu principal ---")
    print("1. Fazer uma pergunta")
    print("2. Navegar por categorias")
    print("3. Ver indicadores")
    print("0. Sair")


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    if not base.carregar():
        print(f"Não foi possível iniciar: {base.erro}")
        print("Confira se o arquivo data/base_conhecimento.json existe "
              "e está correto.")
        return
    if base.erro:   # carregou, mas ignorou alguns registros
        print(f"Aviso: {base.erro}")

    assistente = Assistente("Citizen Assist AI", base,
                            CAMINHO_HISTORICO, CAMINHO_CSV)
    mostrar_boas_vindas(assistente)

    try:
        while True:
            mostrar_menu()
            opcao = assistente.ler_opcao("Escolha uma opção: ", 3)
            if opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.exibir_indicadores()
            else:
                break
        assistente.encerrar()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: salva o que já foi feito e sai sem erro
        print("\n\nEncerrando o assistente. Seus atendimentos foram salvos.")
        assistente.salvar_historico()
        assistente.exportar_csv()


if __name__ == "__main__":
    main()