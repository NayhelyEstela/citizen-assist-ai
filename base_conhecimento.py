import json
from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Conjunto de todas as orientações carregadas do arquivo JSON."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []   # lista de objetos Orientacao
        self.erro = ""          # mensagem se o carregamento falhar

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.

        Devolve True se carregou pelo menos uma orientação. Arquivo ausente
        ou corrompido não trava o programa: guarda a mensagem em self.erro.
        """
        self.orientacoes = []
        self.erro = ""
        try:
            with open(self.caminho, encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"Arquivo não encontrado: {self.caminho}"
            return False
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            self.erro = f"Arquivo ilegível ou corrompido: {self.caminho}"
            return False

        if not isinstance(registros, list):
            self.erro = "O JSON deve ser uma lista de orientações."
            return False

        ignorados = 0
        for registro in registros:
            try:
                self.orientacoes.append(Orientacao(**registro))
            except TypeError:   # campo faltando, sobrando ou registro inválido
                ignorados += 1

        if ignorados:
            self.erro = f"{ignorados} registro(s) inválido(s) foram ignorados."
        if not self.orientacoes:
            self.erro = self.erro or "A base está vazia."
            return False
        return True

    def categorias(self):
        """Lista as categorias sem repetir, na ordem em que aparecem."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Dá pontos a uma orientação para a pergunta.

        +3 por palavra-chave que aparece na pergunta.
        +1 por palavra da pergunta (4 letras ou mais) que aparece no título.
        """
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_norm:
                pontos += 3

        for palavra in set(pergunta_norm.split()):   # set: não conta repetida
            if len(palavra) >= 4 and f" {palavra} " in titulo_norm:
                pontos += 1

        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor.

        Só entram orientações com pelo menos 1 ponto.
        """
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados