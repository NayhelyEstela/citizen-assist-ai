# Citizen Assist AI

Assistente de terminal, escrito em Python, que orienta **jovens no primeiro emprego** sobre documentos, trabalho e dinheiro. Ele responde só com o que está na base de conhecimento (`data/base_conhecimento.json`), mostra a **fonte** e a **data de verificação** de cada resposta e **não coleta dados pessoais**.

> **Aviso:** este assistente **não é um canal oficial**. Ele reúne orientações de fontes oficiais, mas as regras podem mudar. Confirme sempre no site indicado.

Projeto da Global Solution 2026.2 (FIAP): Pensamento Computacional e Automação com Python 3.

## Integrantes

| Nome                            | RM       |
|---------------------------------|----------|
| [Kauanne Paula de Oliveira]     | [574191] |
| [Nayhely Estela Calle Castill0] | [571416] |

## Público e problema escolhidos

**Público:** jovens que estão procurando ou acabaram de conseguir o primeiro emprego.

**Problema:** quem está começando costuma não saber por onde começar: quais documentos tirar, como acessar a Carteira de Trabalho Digital, o que é o FGTS, como o salário chega à conta, o que fazer se for demitido ou se quiser fazer bicos como MEI. As informações existem nos sites do governo, mas estão espalhadas e com linguagem difícil.

**Solução:** um assistente que responde perguntas em texto livre ou por navegação em categorias, em linguagem simples, sempre dizendo **quais documentos levar, onde ir e de onde veio a informação**.

A base tem **15 orientações** em **3 categorias**: *Documentos e identidade*, *Trabalho e vagas* e *Dinheiro e formalização*.

## ODS relacionados

- **ODS 8: Trabalho decente e crescimento econômico** (meta 8.6, reduzir a proporção de jovens sem emprego, educação ou formação): o assistente ajuda o jovem a se preparar para ser contratado e a conhecer seus direitos.
- **ODS 4: Educação de qualidade** (meta 4.4, aumentar o número de jovens com competências para o emprego): orienta sobre Jovem Aprendiz e cursos gratuitos (QualificaPro).
- **ODS 10: Redução das desigualdades** (meta 10.2, inclusão social e econômica): facilita o acesso a informações e serviços públicos gratuitos.

## Como executar

Requisitos: **Python 3.8 ou superior**. O projeto usa apenas a biblioteca padrão (`json`, `csv`, `re`, `time`, `os`, `datetime`), sem instalar nada.

```bash
git clone https://github.com/NayhelyEstela/citizen-assist-ai.git
cd citizen-assist-ai
python main.py        
```

Menu principal:

| Opção | O que faz |
|---|---|
| 1 | Fazer uma pergunta em texto livre |
| 2 | Navegar por categorias |
| 3 | Ver indicadores |
| 0 | Sair (pede a nota de facilidade de 1 a 5, salva o histórico, exporta o CSV e mostra os indicadores) |

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                  # menu principal
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento (+ normalizar)
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # as orientações
    ├── historico.json           # atendimentos (gerado pelo programa)
    └── atendimentos.csv         # exportação dos atendimentos (gerado pelo programa)
```

### Classes e composição

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Responsabilidade | Atributos | Métodos |
|---|---|---|---|
| `Orientacao` | Guardar os dados de uma orientação e exibi-la | `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte`, `verificado_em` | `exibir()` |
| `BaseConhecimento` | Ler o JSON, listar categorias e buscar | `caminho`, `orientacoes`, `erro` | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | Conversar com o cidadão, guardar o histórico e calcular indicadores | `nome`, `base`, `historico`, `sessao`, `caminho_historico`, `caminho_csv` | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `encerrar()` e métodos auxiliares |

Cada registro do JSON vira um objeto com `Orientacao(**registro)`, já que as chaves do JSON têm os mesmos nomes dos parâmetros do `__init__`.

## Regra de pontuação usada

A "inteligência" do assistente é baseada em regras: a pergunta é comparada com cada orientação, que recebe pontos, e a de maior pontuação é mostrada.

**1. Normalização.** Pergunta, palavras-chave e título são comparados em minúsculas, sem acentos e sem pontuação. O texto normalizado recebe um espaço no começo e no fim, para que a busca por `sus` não encontre `sus` dentro de outra palavra.

**2. Pontos.**

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) que aparece no título | +1 |

**3. Confiança** (da melhor orientação):

| Pontos | Resultado |
|---|---|
| 6 ou mais | Confiança **ALTA** |
| 3 a 5 | Confiança **MÉDIA** |
| menos de 3 | "Não encontrei": sugere outras palavras ou as categorias |

**4. Resultado.** `buscar()` devolve uma lista de **tuplas `(pontos, orientacao)`**, da maior para a menor pontuação. O assistente mostra a melhor orientação e até **duas alternativas** (só as que têm 3 pontos ou mais, para não sugerir algo irrelevante).

**Pesos e limites:** usamos exatamente os pesos e limites do enunciado (+3, +1, 6 e 3), sem ajustes. Eles ficam nas constantes `LIMITE_ALTA` e `LIMITE_MEDIA` no começo do `assistente.py`.

**Exemplo calculado.** Pergunta: *"Como acessar a carteira de trabalho digital?"* → orientação 4, **11 pontos (ALTA)**:

- +3 pela palavra-chave `carteira de trabalho`
- +3 pela palavra-chave `carteira de trabalho digital`
- +5 pelas palavras `como`, `acessar`, `carteira`, `trabalho` e `digital`, que estão no título

Outra pergunta: *"Como tirar meu título de eleitor?"* → orientação 2, **6 pontos (ALTA)**.

## Regras de atendimento

- **Navegação por categorias:** categorias e orientações numeradas, com "0. Voltar" em todas as telas.
- **Entradas inválidas:** opção fora da faixa, letras, texto vazio e resposta s/n inválida nunca encerram o programa; o assistente avisa e pede de novo.
- **Transparência:** toda resposta mostra a fonte, a data de verificação e o aviso de que o assistente não é canal oficial.
- **Arquivos:** JSON da base ausente ou corrompido não trava o programa. Se `historico.json` estiver corrompido, o arquivo antigo é renomeado para `.corrompido` e um novo histórico é iniciado.
- **Interrupção:** `Ctrl+C` ou fim da entrada salvam o histórico e o CSV e encerram sem erro.

### Dados pessoais

O assistente nunca pede nome, CPF, telefone ou e-mail. Uma mensagem é **recusada e não é registrada** quando:

1. tem **8 ou mais dígitos** (soma de todos os dígitos da mensagem) ou o caractere **`@`** (regra do enunciado); ou
2. combina com um dos padrões a mais que a equipe adicionou (expressões regulares sobre o texto normalizado):
   - documento ou contato seguido de número, mesmo parcial: *"meu cpf termina em 8900"*, *"cep 01310"*;
   - e-mail por extenso: *"joao arroba gmail ponto com"*;
   - apresentação com nome: *"meu nome é ..."*, *"me chamo ..."*;
   - endereço: *"meu endereço"*, *"moro na rua ..."*;
   - números falados: 5 ou mais palavras de dígito seguidas.

A palavra "cpf" sozinha **não** bloqueia, porque *"como consultar meu cpf"* é uma pergunta legítima. Pela mesma razão o padrão é *"meu nome é"* e não *"meu nome"*.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` assim que termina. Campos: `data`, `sessao`, `origem` (`pergunta` ou `categoria`), `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas`, `tempo_segundos`, `confianca` e `nota_facilidade`. Ao sair, os atendimentos são exportados para `data/atendimentos.csv` com `csv.DictWriter`.

**O que conta como um atendimento:** cada pergunta digitada (ou cada orientação aberta pela navegação) gera um registro. As `tentativas` contam quantas perguntas a pessoa fez até uma resposta ajudar. O tempo é medido com `time.time()` e inclui o tempo de digitação e leitura da pessoa.

| Indicador | Como é calculado |
|---|---|
| Resposta encontrada (%) | atendimentos com `encontrou = True` ÷ total |
| Taxa de acerto (%) | atendimentos com `ajudou = True` ÷ total |
| Tempo médio para encontrar | média de `tempo_segundos` só dos atendimentos em que a resposta foi encontrada |
| Tentativas por atendimento | média da coluna `tentativas` |
| Facilidade de uso (1 a 5) | média das notas, **uma nota por sessão** (para quem fez muitos atendimentos não pesar mais) |
| Dúvidas sem solução | perguntas digitadas que não acharam resposta ou em que a pessoa disse que não ajudou, sem repetição |

## Integrações com outras disciplinas

Nenhuma. Obtou-se pela realização independente desta diciplina.

## Fontes consultadas

Cada orientação traz sua fonte no campo `fonte` e a data em que a equipe conferiu no campo `verificado_em` (2026-11-11 para as orientações 1 a 12 e 2026-11-13 para as orientações 13 a 15).

| Id | Orientação | Fonte |
|---|---|--|
| 1 | CPF: situação e comprovante | https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf |
| 2 | Primeiro título de eleitor | https://www.tre-sp.jus.br/servicos-eleitorais/carta-de-servicos/primeiro-titulo-de-eleitor |
| 3 | Criar a conta gov.br | https://www.gov.br/pt-br/servicos/criar-sua-conta-gov.br |
| 4 | Carteira de Trabalho Digital | https://www.gov.br/pt-br/temas/carteira-de-trabalho-digital |
| 5 | Jovem Aprendiz | https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/julho/aprendizagem-profissional-regras-direitos-e-funcionamento-do-contrato-de-aprendizagem |
| 6 | Saldo do FGTS | https://www.fgts.gov.br |
| 7 | Contrato de experiência | https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm |
| 8 | Cursos gratuitos (QualificaPro) | https://ufrb.edu.br/cfp/atividades-para-a-comunidade/4209-qualificapro-plataforma-de-cursos-gratuitos-que-conecta-trabalhadores-ao-mercado-de-trabalho |
| 9 | Seguro-desemprego | https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego |
| 10 | Conta-salário | https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20BCB&numero=284 |
| 11 | Portabilidade do salário | https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20BCB&numero=284 |
| 12 | Abrir MEI | https://www.gov.br/empresas-e-negocios/pt-br/empreendedor |
| 13 | Sacar o FGTS depois de ser demitido | https://www.fgts.gov.br/Paginas/subpaginas/saque-dispensa.aspx |
| 14 | Primeiro emprego: o que preciso | https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital |
| 15 | O que é o FGTS e quando dá para sacar | https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/fgts/fundo-de-garantia-do-tempo-de-servico-fgts |

## Teste com usuários

OBS: O atendimento.csv e historico.json correspondem a rodada 2, arquivos correspondentes a rodada 1 foram descartadas para obtenção dos indicadores da rodada 2.

### Usuários

Os mesmos 5 usuários, todos de fora da equipe, participaram das duas rodadas: a segunda aconteceu depois da melhoria. Os usuários são identificados só por letras, sem nomes.

| Usuário | Situação |
|---|---|
| **A** | 16 anos, ensino médio, nunca trabalhou |
| **B** | 18 anos, acabou de ser contratado (1º emprego CLT) |
| **C** | 21 anos, faz bicos e quer se formalizar |
| **D** | 19 anos, demitido com 2 meses de emprego |
| **E** | 17 anos, quer o 1º emprego e não sabe por onde começar |

**Total: 5 usuários, 41 atendimentos registrados** (26 na rodada 1, 15 na rodada 2).

### Rodada 1: antes da melhoria (26 atendimentos)

| Usuário | Atendimentos | Resposta encontrada | Ajudou | Nota de facilidade (1 a 5) |
|---|---|---|---|---|
| A | 5 | 2 | 2 | 3 |
| B | 4 | 3 | 3 | 5 |
| C | 7 | 4 | 2 | 4 |
| D | 5 | 4 | 1 | 3 |
| E | 5 | 2 | 1 | 2 |

| Indicador (saída do programa) | Resultado |
|---|---|
| Resposta encontrada | **57,7 %** (15 de 26) |
| Taxa de acerto (ajudou) | **34,6 %** (9 de 26) |
| Tempo médio para encontrar* | 53,2 s |
| Tentativas por atendimento | 1,5 |
| Facilidade de uso (média das 5 notas) | **3,4** |

\* Média do tempo, em segundos, só dos atendimentos em que a resposta foi encontrada. Inclui o tempo de digitação e leitura da pessoa.

O que os números mostram:

- **Achar não é resolver.** Em 6 atendimentos o assistente respondeu com confiança MÉDIA, mas a resposta não resolvia a dúvida. Das 11 respostas MÉDIA, 5 ajudaram; a única ALTA ajudou.
- **Sem resposta, 11 atendimentos.** Alguns eram só questão de palavras: C tentou "qualifica pro" e "curso de graça", não achou nada e só chegou à orientação pelo menu de categorias. D perguntou "Perdi o emprego, como peço o seguro?" e não achou nada; só achou depois de reescrever com "seguro desemprego". A perguntou "Posso trabalhar com 15 anos?" e não achou nada.
- **As notas acompanham a dificuldade de achar resposta:** E, que esbarrou em dúvidas sem resposta, deu 2; B, com quase tudo resolvido, deu 5.

### Dúvidas sem solução

Dúvidas que seguem sem resposta útil ao final das duas rodadas. São **lacunas de conteúdo**: a orientação ainda não existe, então nenhuma palavra-chave resolve. A coluna "Registros" conta as vezes em que a dúvida (ou uma reformulação dela) apareceu nas duas rodadas.

| # | Dúvida | Usuário | Registros | Por que segue sem solução | Após as novas orientações |
|---|---|---|---|---|---|
| 1 | **Primeiro emprego: por onde começar? Quais documentos preciso?** | E | 3 | Não há orientação sobre o tema. | Coberta pela orientação 14 (ver Melhoria 2) |
| 2 | **Como sacar o FGTS depois de ser demitido?** | D | 3 | A orientação do FGTS só explica a consulta de saldo. | Coberta pela orientação 13 (ver Melhoria 2) |
| 3 | **Menor de idade precisa de autorização dos pais para trabalhar?** | A | 3 | Não coberto. | Segue sem resposta |
| 4 | Quanto se paga de DAS por mês no MEI? | C | 2 | A orientação cita o DAS, mas não o valor. | Segue sem resposta |
| 5 | O que levar ao RH depois de contratado? | B | 2 | Não coberto. | Segue sem resposta |
| 6 | Preciso de certificado de reservista? | E | 2 | Só aparece como documento do título de eleitor. | Segue sem resposta |
| 7 | O título de eleitor é obrigatório para trabalhar? | E | 1 | A orientação explica como tirar, não se é exigido. | Segue sem resposta |
| 8 | Quanto tempo demora para cair o seguro-desemprego? | D | 1 | A orientação explica o pedido, não o prazo. | Segue sem resposta |
| 9 | Posso ter MEI e carteira assinada ao mesmo tempo? | C | 1 | Não coberto. | Segue sem resposta |
| 10 | Como emitir nota fiscal de MEI? | C | 1 | Não coberto. | Segue sem resposta |

Os itens 1 a 6 foram repetidos pelo mesmo usuário nas duas rodadas. São os melhores candidatos a novas orientações, que precisam de fonte oficial verificada (campos `fonte` e `verificado_em`). Os itens **1 e 2** ganharam orientação na Melhoria 2 (abaixo); os itens 3 a 10 continuam sem cobertura. A última coluna indica só que a busca agora encontra a orientação: **a dúvida só deve ser dada como resolvida depois de um novo teste com os usuários**.

### Melhoria 1: novas palavras-chave

Nas perguntas já cobertas pela base, o problema era só de vocabulário: a pessoa escrevia de um jeito e a palavra-chave estava cadastrada de outro. Foram adicionadas 7 palavras-chave em `data/base_conhecimento.json`, cada uma ligada a um caso observado:

| Orientação | Palavras-chave novas | Caso que motivou |
|---|---|---|
| Jovem Aprendiz | `com 15 anos`, `com 16 anos` | A: *"Posso trabalhar com 15 anos?"* não achou nada |
| QualificaPro | `qualifica pro`, `curso de graca` | C: *"Como entrar no qualifica pro?"* e *"Onde faço curso de graça?"* não acharam nada |
| Seguro-desemprego | `mandado embora`, `perdi o emprego` | D: *"Perdi o emprego, como peço o seguro?"* não achou nada |
| Portabilidade do salário | `salario em outro banco` | B: *"Posso receber meu salário em outro banco?"* só chegou à resposta com 3 pontos, no limite da confiança MÉDIA |

### Melhoria 2: novas orientações

Foram adicionadas 3 orientações em `data/base_conhecimento.json` (categoria *Trabalho e vagas*), todas com `fonte` oficial e `verificado_em` = 2026-11-13. **Uma delas não nasce de falha observada**, e isso fica registrado aqui:

| Id | Orientação | Origem | Dúvida da tabela |
|---|---|---|---|
| 13 | Sacar o FGTS depois de ser demitido sem justa causa | **Falha observada** (D perguntou nas duas rodadas e a orientação de saldo não ajudou) | Item 2 |
| 14 | Primeiro emprego: o que preciso para ser contratado | **Falha observada** (E perguntou nas duas rodadas e não havia orientação) | Item 1 |
| 15 | O que é o FGTS e quando dá para sacar | **Adição por avaliação de conteúdo**: ninguém perguntou isso nos testes. Entra porque a orientação 13 pressupõe que a pessoa já sabe o que é o FGTS e em que casos ele sai | nenhum |

Como a orientação 15 não veio de um caso observado, não há evidência de que seja necessária. Por isso ela ganhou uma pergunta própria na rodada 2 (veja "Atualização da rodada 2") para testar se de fato é encontrada e se ajuda.

Junto com elas, as 7 palavras-chave da Melhoria 1 foram aplicadas no arquivo da base.

#### Conflito de palavras-chave do FGTS e ajuste

A busca dá **+3 por palavra-chave** presente na pergunta e **+1 por palavra do título**. Antes das novas orientações, a orientação 6 (saldo) tinha as palavras-chave soltas `fgts` e `fundo de garantia`, que aparecem em qualquer pergunta sobre o tema. Com 13, 15 e 6 juntas, isso causaria:

- Toda pergunta com "FGTS" pontuaria na orientação 6 e empataria com as outras (o desempate é a ordem no arquivo, e a 6 vem primeiro). Ex.: "O que é o FGTS?" faria 4 pontos na 6 e 4 na 15; "Como sacar o saldo do FGTS?" empataria entre 6 e 13.
- Palavras-chave genéricas propostas para a 14 (`ser contratado`, `por onde comecar`, `quais documentos preciso`) capturariam perguntas de outros temas, como a de B ("Acabei de ser contratado, o que eu preciso levar no RH?", item 5), que **deve continuar sem resposta**, e "por onde começar um MEI".

Ajustes feitos, para que cada orientação responda só às dúvidas que lhe correspondem:

| Orientação | Retirado | Acrescentado (exemplos) |
|---|---|---|
| 6, saldo do FGTS | `fgts`, `fundo de garantia`, `meu fgts` (soltos) | `saldo fgts`, `ver fgts`, `ver meu fgts`, `vejo meu fgts`, `quanto tenho de fgts`, `consultar saldo`, `saldo do fundo de garantia`, `extrato fgts`, `aplicativo fgts` |
| 13, sacar o FGTS | (nenhum) | `sacar meu fgts`, `sacar o saldo do fgts`, `sacar o saldo`, `sacar saldo`, `saco o fgts`, `saco meu fgts`, `pego o fgts`, `retirar o fgts`, `pegar o fgts`, `tirar o fgts` |
| 14, primeiro emprego | `ser contratado`, `por onde comecar`, `por onde comeco`, `quais documentos preciso` (genéricas) | `primeiro trabalho`, `documentos para o primeiro emprego` |
| 15, o que é o FGTS | (nenhum) | `quando posso sacar o fgts`, `quando da para sacar o fgts`, `em que casos posso sacar o fgts`, `como funciona o fundo de garantia`, `o que e fundo de garantia`, `para que serve o fundo de garantia` |

Nenhuma palavra-chave se repete entre orientações.

| Pergunta | Base original (12 orientações) | Base atual (15 orientações) |
|---|---|---|
| Como sacar o FGTS depois de ser demitido? | 6 (saldo), 4 pts | **13**, 7 pts (ALTA) |
| Quero meu primeiro emprego, por onde começo? | não encontrou | **14**, 8 pts (ALTA) |
| Para que serve o FGTS? / O que é o FGTS? | 6 (saldo), 4 pts | **15**, 5 e 4 pts |
| Quando posso sacar o FGTS? | 6 (saldo), 4 pts | **15**, 6 pts (ALTA); 13 como alternativa |
| Como sacar o saldo do FGTS? | 6 | **13**, 8 pts; 6 como alternativa |
| Como saco meu FGTS? | 6 | **13**, 4 pts |
| Como consultar o saldo do FGTS? | 6 | 6 (continua) |
| Acabei de ser contratado, o que eu preciso levar no RH? | não encontrou | não encontrou (lacuna mantida) |
| Jovem aprendiz tem FGTS? | 5 | 5 (continua) |

Nas 21 perguntas das rodadas 1 e 2, a orientação devolvida só mudou onde era esperado: as que não achavam nada e agora acham pelas palavras-chave novas, e as duas dúvidas FGTS/primeiro emprego (itens 1 e 2).

**Efeitos colaterais conhecidos do ajuste:**

- Perguntas que dizem **só "FGTS"** ("FGTS", "quero meu fgts") agora dão "não encontrei", porque a palavra solta foi retirada da orientação 6. Antes caíam na orientação de saldo, o que muitas vezes era a resposta errada.
- "Posso sacar o FGTS para comprar casa?" vai para a 13 (saque na demissão), e a 15, que tem a resposta sobre casa própria, aparece só como alternativa.

### Rodada 2: depois da melhoria (15 atendimentos)

Os mesmos 5 usuários voltaram: 10 atendimentos repetem dúvidas da rodada 1 que não tinham resposta e 5 são reformulações novas.

| Usuário | Atendimentos | Resposta encontrada | Ajudou | Nota de facilidade (1 a 5) |
|---|---|---|---|---|
| A | 3 | 2 | 2 | 4 |
| B | 3 | 2 | 2 | 5 |
| C | 3 | 2 | 2 | 4 |
| D | 3 | 3 | 2 | 3 |
| E | 3 | 1 | 1 | 3 |

| Indicador (saída do programa) | Rodada 1 | Rodada 2 |
|---|---|---|
| Resposta encontrada | 57,7 % | 66,7 % (10 de 15) |
| Taxa de acerto (ajudou) | 34,6 % | 60,0 % (9 de 15) |
| Tempo médio para encontrar* | 53,2 s | 45,3 s |
| Tentativas por atendimento | 1,5 | 1,1 |
| Facilidade de uso | 3,4 | 3,8 |

**Efeito da melhoria, dúvida por dúvida.** Como a rodada 2 tem muitas perguntas difíceis de propósito, o mais confiável é olhar as 10 dúvidas repetidas:

| Dúvida repetida da rodada 1 | Usuário | Rodada 2 |
|---|---|---|
| Posso trabalhar com 15 anos? | A | **Resolvida** (Jovem Aprendiz) |
| Como entrar no qualifica pro? | C | **Resolvida** (QualificaPro) |
| Onde faço curso de graça? | C | **Resolvida** (QualificaPro) |
| Perdi o emprego, como peço o seguro? | D | **Resolvida** (seguro-desemprego) |
| Meu pai precisa assinar alguma autorização? | A | Segue sem resposta (item 3) |
| Acabei de ser contratado, o que eu preciso levar no RH? | B | Segue sem resposta (item 5) |
| Quanto pago de DAS por mês? | C | Segue sem resposta (item 4) |
| Como sacar o FGTS depois de ser demitido? | D | Achou a orientação, mas não ajudou (item 2) |
| Quero meu primeiro emprego, por onde começo? | E | Segue sem resposta (item 1) |
| Preciso de certificado de reservista? | E | Segue sem resposta (item 6) |

**4 de 10 foram resolvidas** com palavras-chave. As outras 6 são lacunas de conteúdo, como esperado. Nas 5 reformulações novas (*"Com 16 anos eu posso trabalhar?"*, *"Quero receber meu salário em outro banco"*, *"Minha empresa quer abrir conta salário pra mim"*, *"Fui mandado embora semana passada, e agora?"* e *"Onde faço curso de graça pra melhorar meu currículo?"*), as 5 ajudaram.

**Atualização da rodada 2: novas orientações (13, 14 e 15).** Os números e a tabela acima são da execução original, feita **antes** das novas orientações, e **não foram recalculados**. A tabela abaixo mostra só o que a busca devolve hoje para as perguntas afetadas:

| Pergunta | Usuário | Origem | Busca com as novas orientações |
|---|---|---|---|
| Como sacar o FGTS depois de ser demitido? | D | repetida (item 2) | Orientação 13, 7 pts, ALTA. Antes: orientação 6, que não ajudou |
| Quero meu primeiro emprego, por onde começo? | E | repetida (item 1) | Orientação 14, 8 pts, ALTA. Antes: sem resposta |
| **Para que serve o FGTS?** | B (sugerido: acabou de ser contratado) | **nova, para testar a orientação 15** | Orientação 15, 5 pts, MÉDIA |

A terceira linha é a pergunta incluída na rodada 2 para a orientação 15, que não nasce de falha observada.

**Observação: abastecer todas as dúvidas é complexo.** Cada orientação nova mexe nas anteriores: em um tema com várias orientações vizinhas (FGTS tem 3), uma palavra-chave genérica numa delas já captura as perguntas das outras, e foi preciso conferir pergunta por pergunta para separar. Há ainda uma troca sem saída fácil: palavra solta acha mais perguntas, mas erra mais; palavra específica erra menos, mas deixa passar quem escreve de outro jeito (ver "FGTS" sozinho acima). O custo de manutenção cresce a cada orientação, e a lista de dúvidas possíveis de jovens no primeiro emprego não tem fim. Por isso: (1) cada orientação precisa de fonte oficial verificada; (2) toda palavra-chave nova deve ser conferida contra uma lista fixa de perguntas; (3) as lacunas continuam sendo medidas pelo uso real, e não só pelo que se imagina que as pessoas perguntam.

## Limitações

- **A busca é por regras, não entende o sentido da frase.** Ela só compara palavras. Quem escreve de um jeito diferente das palavras-chave não acha a resposta, e palavras comuns como "como" valem 1 ponto no título mesmo sem relação com o assunto (uma melhoria possível é ignorar essas palavras na pontuação).
- **Palavra solta × palavra específica.** Palavra-chave solta acha mais perguntas, mas erra mais; palavra específica erra menos, mas deixa passar quem escreve de outro jeito. Exemplo: perguntas só com "FGTS" hoje dão "não encontrei".
- **Base pequena.** São 15 orientações. Seguem sem resposta, por exemplo, autorização dos pais para menor de idade, valor do DAS do MEI e certificado de reservista (ver "Dúvidas sem solução").
- **A resposta pode ficar desatualizada.** As regras do governo mudam. Por isso cada resposta mostra a data de verificação e o aviso de que o assistente não é canal oficial.
- **Detecção de dados pessoais é uma heurística.** Ela pega 8 ou mais dígitos, `@` e alguns padrões, mas não detecta todos os casos. Um nome sem apresentação ("João Silva quer abrir MEI") passa.
- **O tempo medido inclui a digitação e a leitura da pessoa**, não só o tempo de busca.
- **Resposta de "Com 16 anos eu posso trabalhar?"** é a do Jovem Aprendiz, que não cobre outras formas de trabalho.
- **Teste com poucos usuários.** Foram 5 pessoas, e as mesmas voltaram na segunda rodada, já com o conhecimento da primeira, o que pode ter influenciado o resultado.

## Vídeo técnico

[Pendente]