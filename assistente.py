import csv
import json
import os
import re
import time
from datetime import datetime
from base_conhecimento import normalizar

LIMITE_ALTA = 6    # 6 pontos ou mais  -> confiança ALTA
LIMITE_MEDIA = 3   # de 3 a 5 pontos   -> confiança MÉDIA

PADROES_DADO_PESSOAL = [
    r"\b(cpf|rg|telefone|celular|whatsapp|zap|cep|conta)\b\D{0,15}\d{3,}",
    r"\barroba\b",
    r"\bponto com\b",
    r"\bmeu nome (e|eh|completo)\b",
    r"\bme chamo\b",
    r"\bmeu sobrenome (e|eh)\b",
    r"\bmeu endereco\b",
    r"\bminha rua\b",
    r"\bmoro (na|no) (rua|avenida|av|bairro|travessa)\b",
    r"(\b(zero|um|dois|tres|quatro|cinco|seis|sete|oito|nove)\b\s*){5,}",
]

CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "id_orientacao",
              "encontrou", "ajudou", "tentativas", "tempo_segundos",
              "confianca", "nota_facilidade"]


def entrada(texto):
    """Lê uma linha do teclado, sem espaços nas pontas."""
    return input(texto).strip()


class Assistente:
    """Faz o atendimento, guarda o histórico e calcula os indicadores."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base                          # BaseConhecimento (composição)
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historico = self.carregar_historico()  # atendimentos de todas as sessões

    # ------------------------------------------------------------------
    # Regras auxiliares
    # ------------------------------------------------------------------
    def nivel_confianca(self, pontos):
        """Traduz pontos em nível de confiança. None = 'não encontrei'."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None

    def tem_dado_pessoal(self, texto):
        """True se o texto parece conter dado pessoal."""

        digitos = sum(1 for letra in texto if letra.isdigit())
        if digitos >= 8 or "@" in texto:
            return True

        texto_norm = normalizar(texto)
        for padrao in PADROES_DADO_PESSOAL:
            if re.search(padrao, texto_norm):
                return True
        return False

    def ler_opcao(self, texto, maximo, minimo=0):
        """Pede um número de 'minimo' a 'maximo' e repete até ser válido."""
        while True:
            valor = entrada(texto)
            if valor.isdigit() and minimo <= int(valor) <= maximo:
                return int(valor)
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")

    def ler_sim_nao(self, texto):
        """Pede s ou n e repete até ser válido. Devolve True para 's'."""
        while True:
            valor = entrada(texto).lower()
            if valor in ("s", "n"):
                return valor == "s"
            print("Resposta inválida. Digite s ou n.")

    # ------------------------------------------------------------------
    # Histórico (historico.json)
    # ------------------------------------------------------------------
    def carregar_historico(self):
        """Lê o historico.json. Ausente ou corrompido não trava o programa."""
        try:
            with open(self.caminho_historico, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return [item for item in dados if isinstance(item, dict)]
            raise ValueError("histórico não é uma lista")
        except FileNotFoundError:
            return []
        except (ValueError, OSError):   # JSONDecodeError e UnicodeDecodeError são ValueError
            print("Aviso: histórico ilegível. Começando um novo "
                  "(o antigo foi guardado com a extensão .corrompido).")
            try:
                os.replace(self.caminho_historico,
                           self.caminho_historico + ".corrompido")
            except OSError:
                pass
            return []

    def salvar_historico(self):
        """Grava o histórico em historico.json."""
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
            return True
        except OSError:
            print("Aviso: não consegui salvar o histórico.")
            return False

    def registrar(self, origem, pergunta, id_orientacao, encontrou,
                  ajudou, tentativas, tempo, confianca=None):
        """Guarda um atendimento no histórico e já salva no arquivo."""
        self.historico.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,                 # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "confianca": confianca,
            "nota_facilidade": None,          # preenchida ao sair
        })
        self.salvar_historico()

    # ------------------------------------------------------------------
    # Atendimento por pergunta
    # ------------------------------------------------------------------
    def perguntar(self):
        """Responde dúvidas em texto livre usando a busca com pontuação."""
        tentativas = 0
        inicio = time.time()

        while True:
            texto = entrada("\nDigite sua dúvida (0 para voltar): ")

            if texto == "0":
                return
            if not texto:
                print("Atenção: você não digitou nada. Escreva sua dúvida.")
                continue
            if self.tem_dado_pessoal(texto):
                # Recusa e NÃO registra (nem entra na contagem de tentativas)
                print("Atenção: parece que sua mensagem tem dado pessoal "
                      "(CPF, telefone, e-mail, nome ou endereço).")
                print("Por segurança, ela não foi registrada. "
                      "Reescreva a dúvida sem esses dados.")
                continue

            tentativas += 1
            resultados = self.base.buscar(texto)    # [(pontos, orientacao), ...]
            pontos, melhor = resultados[0] if resultados else (0, None)
            nivel = self.nivel_confianca(pontos)

            if nivel is None:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (ex.: o nome do documento) "
                      "ou use a navegação por categorias.")
                self.registrar("pergunta", texto, None, False, False,
                               tentativas, round(time.time() - inicio, 1))
                continue

            print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)")
            melhor.exibir()

            alternativas = [(p, o) for p, o in resultados[1:3]
                            if p >= LIMITE_MEDIA]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} [{o.categoria}] ({p} pontos)")

            ajudou = self.ler_sim_nao(
                "\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("pergunta", texto, melhor.id, True, ajudou,
                           tentativas, round(time.time() - inicio, 1), nivel)

            if ajudou:               # dúvida resolvida: começa um novo atendimento
                tentativas = 0
                inicio = time.time()

    # ------------------------------------------------------------------
    # Atendimento por categorias
    # ------------------------------------------------------------------
    def navegar(self):
        """Mostra as categorias e deixa a pessoa escolher uma orientação."""
        categorias = self.base.categorias()
        if not categorias:
            print("Não há categorias disponíveis.")
            return

        while True:
            print("\n--- Categorias ---")
            for numero, categoria in enumerate(categorias, 1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")

            opcao = self.ler_opcao("Escolha uma categoria: ", len(categorias))
            if opcao == 0:
                return
            self.navegar_categoria(categorias[opcao - 1])

    def navegar_categoria(self, categoria):
        """Lista as orientações de uma categoria e exibe a escolhida."""
        orientacoes = self.base.por_categoria(categoria)

        while True:
            print(f"\n--- {categoria} ---")
            for numero, orientacao in enumerate(orientacoes, 1):
                print(f"{numero}. {orientacao.titulo}")
            print("0. Voltar")

            inicio = time.time()
            opcao = self.ler_opcao("Escolha uma orientação: ", len(orientacoes))
            if opcao == 0:
                return

            escolhida = orientacoes[opcao - 1]
            escolhida.exibir()
            ajudou = self.ler_sim_nao(
                "\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("categoria", escolhida.titulo, escolhida.id, True,
                           ajudou, 1, round(time.time() - inicio, 1))

    # ------------------------------------------------------------------
    # Indicadores
    # ------------------------------------------------------------------
    def indicadores(self):
        """Calcula os indicadores com o histórico. Devolve um dicionário."""
        total = len(self.historico)
        if total == 0:
            return None

        encontrados = [h for h in self.historico if h.get("encontrou")]
        ajudaram = [h for h in self.historico if h.get("ajudou")]

        # Tempo médio: só atendimentos em que a resposta foi encontrada
        tempos = [h.get("tempo_segundos", 0) for h in encontrados]
        tempo_medio = round(sum(tempos) / len(tempos), 1) if tempos else 0.0

        tentativas = [h.get("tentativas", 1) for h in self.historico]

        # Facilidade: uma nota por sessão (a nota fica repetida nos registros)
        notas_por_sessao = {}
        for h in self.historico:
            if h.get("nota_facilidade") is not None:
                notas_por_sessao[h.get("sessao")] = h["nota_facilidade"]
        notas = list(notas_por_sessao.values())

        # Dúvidas sem solução: perguntas sem resposta encontrada ou que não ajudaram
        sem_solucao = []
        for h in self.historico:
            if h.get("origem") == "pergunta" and not h.get("ajudou"):
                if h.get("pergunta") not in sem_solucao:
                    sem_solucao.append(h.get("pergunta"))

        return {
            "total": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudaram) / total, 1),
            "tempo_medio": tempo_medio,
            "tentativas_media": round(sum(tentativas) / total, 1),
            "facilidade_media": round(sum(notas) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def exibir_indicadores(self):
        """Mostra os indicadores na tela."""
        ind = self.indicadores()
        print("\n=== Indicadores ===")
        if ind is None:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos registrados: {ind['total']}")
        print(f"Resposta encontrada: {ind['encontrada_pct']}%")
        print(f"Taxa de acerto (ajudou): {ind['acerto_pct']}%")
        print(f"Tempo médio para encontrar: {ind['tempo_medio']} s")
        print(f"Tentativas por atendimento: {ind['tentativas_media']}")
        facilidade = ind["facilidade_media"]
        print("Facilidade de uso (1 a 5): "
              + (str(facilidade) if facilidade is not None else "sem notas"))
        print("Dúvidas sem solução:")
        if ind["sem_solucao"]:
            for duvida in ind["sem_solucao"]:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")

    # ------------------------------------------------------------------
    # Exportação CSV (atendimentos.csv)
    # ------------------------------------------------------------------
    def exportar_csv(self):
        """Exporta o histórico para CSV usando csv.DictWriter."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            # utf-8-sig: o Excel abre os acentos corretamente
            with open(self.caminho_csv, "w", newline="",
                      encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
            return True
        except OSError:
            print("Aviso: não consegui exportar o CSV.")
            return False

    # ------------------------------------------------------------------
    # Saída do programa
    # ------------------------------------------------------------------
    def encerrar(self):
        """Pede a nota de facilidade, salva tudo e mostra os indicadores."""
        desta_sessao = [h for h in self.historico if h.get("sessao") == self.sessao]
        if desta_sessao:
            nota = self.ler_opcao(
                "\nDe 1 a 5, quão fácil foi usar o assistente? ", 5, minimo=1)
            print("=" * 60)
            for atendimento in desta_sessao:
                atendimento["nota_facilidade"] = nota

        self.salvar_historico()
        if self.exportar_csv():
            print(f"Atendimentos exportados para {self.caminho_csv}")
        self.exibir_indicadores()
        print()
        print("=" * 60)
        print("Obrigado por usar o assistente!")