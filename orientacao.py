class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação na tela, com fonte, data e aviso."""
        print("=" * 60)
        print(f">> {self.titulo}  [{self.categoria}]")
        print("\nR:",self.resposta)
        print("=" * 60)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print("=" * 60)
        print(f"Onde: {self.onde}")
        print("=" * 60)
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")


