# Execute a análise no seu próprio ambiente

Este pacote contém um notebook para Google Colab, um comando para executar o mesmo notebook e uma skill opcional para orientar uma IA. Os dados são públicos; não precisa de conta do autor, acesso ao Drive dele, token ou chave de API. No Colab, cada pessoa usa sua própria conta Google. Pelo comando, nenhuma conta Google é necessária.

Para a apresentação do projeto e o início rápido, leia o [README](README.md). A fonte é o [catálogo de Boletins de Urna de 2026 do TSE](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna); o [roteiro de download manual](README.md#1-de-onde-vêm-os-dados-e-onde-baixar-as-bases) explica como obter ZIPs e hashes. O programa faz esse download automaticamente. Consulte também as [definições e limitações](METODOLOGIA.md).

## Escolha como usar

| Forma | Para quem | Arquivo principal |
|---|---|---|
| Colab | Quer acompanhar células e gráficos no navegador | `assets/Analise_TSE_2026.ipynb` |
| Comando | Quer repetir a análise no computador ou servidor | `scripts/tse.py` |
| Skill | Quer que uma IA conduza a mesma execução e leitura | `SKILL.md`, junto com o restante da pasta |

A skill usa o programa e o notebook incluídos. O pacote funciona sem IA, assinatura de IA ou conector Google Drive.

## Opção A — mesmo fluxo no Google Colab

1. Baixe e extraia o ZIP deste pacote. Guarde a pasta inteira; o ZIP do GitHub pode nomeá-la `tse-reproducivel-main`.
2. [Abra diretamente o notebook no Colab](https://colab.research.google.com/github/antunesclarissa/tse-reproducivel/blob/main/assets/Analise_TSE_2026.ipynb) usando sua própria conta Google. Como alternativa, use o upload descrito a seguir.
3. Use **Arquivo → Fazer upload de notebook** e selecione `assets/Analise_TSE_2026.ipynb`. Os nomes dos menus podem variar com o idioma.
4. Na primeira seção, confira os parâmetros. O padrão `ESCOPO = "PILOTO"` processa apenas o Acre para testar a instalação. Para todas as UFs e o exterior, escolha `ESCOPO = "COMPLETO"` e mantenha `INCLUIR_EXTERIOR = True`.
5. Mantenha `HORARIO_CORTE = "17:16:00"` para o corte inclusivo padrão. O dia é `2026-10-25`, e o corte é interpretado em Brasília sob a hipótese `RELOGIO_ARQUIVO`. A versão não foi adaptada para outras eleições.
6. Escolha um ambiente Python com CPU e use **Ambiente de execução → Executar tudo**. Não monte o Google Drive. Os downloads são feitos diretamente do catálogo e do repositório públicos do TSE.
7. Acompanhe as confirmações de hash e cobertura. Se uma partição faltar ou um hash divergir, o programa interrompe a execução. Não trate um resultado parcial como nacional.
8. Leia os resultados na ordem do notebook. A seção de limites temporais conserva as seções que encerraram depois do corte e mantém valores não identificáveis como indeterminados.
9. A última célula oferece o download do ZIP de resultados. Salve-o antes de encerrar a sessão. O ZIP inclui tabelas CSV, gráficos PNG, parâmetros, fontes e manifesto com hashes. O notebook executado pode ser baixado pelo menu Arquivo.

O Colab compartilha texto, código, saídas e comentários quando um notebook é compartilhado. A máquina de execução não acompanha esse compartilhamento. Estas instruções seguem a [documentação do Google](https://research.google.com/colaboratory/faq.html).

## Opção B — executar por comando

Use Python 3.11 ou superior compatível com as bibliotecas. Execute os comandos dentro da pasta extraída `tse-reproducivel`. O piloto é a forma de conferir sua instalação antes do processamento nacional. A duração, o espaço em disco e a memória dependem do escopo e da máquina; GPU não é necessária.

### macOS ou Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/tse.py executar --escopo piloto --corte 17:16:00 --saida resultados_piloto
```

### Windows — PowerShell

Não é necessário ativar o ambiente:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\tse.py executar --escopo piloto --corte 17:16:00 --saida resultados_piloto
```

### Nacional e outros cortes

No ambiente Python escolhido:

```bash
python scripts/tse.py executar --escopo nacional --corte 17:16:00 --saida resultados_nacional
python scripts/tse.py executar --escopo nacional --corte 17:00:00 --saida resultados_1700
```

No Windows, substitua `python` pelo executável do ambiente, como nos comandos anteriores. As duas execuções consultam o catálogo novamente; compare os manifestos antes de atribuir diferenças somente ao horário de corte.

Outras opções:

```bash
python scripts/tse.py --help
python scripts/tse.py executar --help
python scripts/tse.py executar --escopo piloto --ufs AC,AL --saida resultados_piloto
python scripts/tse.py preparar --escopo nacional --corte 17:16:00 --saida configurado
python scripts/tse.py auditar assets/Analise_TSE_2026.ipynb
```

`preparar` gera um notebook configurado sem baixar os dados. Ele pressupõe dependências já instaladas; se for levá-lo ao Colab, altere `INSTALAR_DEPENDENCIAS` para `True`. Para uso direto no Colab, prefira o arquivo em `assets`.

`--sem-exterior` exclui ZZ do modo nacional, que deixa de ter o escopo Brasil + exterior. `--relogio desconhecido` preserva a falta de informação de fuso; os limites temporais passam a ser triviais. Não mude o fuso para aproximar números alegados.

O comando usa [NBClient, do projeto Jupyter](https://nbclient.readthedocs.io/en/latest/client.html), para executar as células e salvar suas saídas. `requirements-validado.txt` registra as versões diretas testadas; não fixa todas as dependências transitivas. Para tentar reproduzir esse conjunto de versões, instale-o em vez de `requirements.txt`.

## Onde ficam os resultados

Na pasta informada em `--saida`:

```text
arquivos/                        ZIPs públicos baixados e hashes, reutilizáveis
notebooks/                       notebooks configurados ou executados
execucoes/<data-e-escopo>/
  tabelas/                       CSVs, inclusive limites_votos_ate_171600.csv
  graficos/                      gráficos PNG
  dicionarios/                   documentação dos arquivos de origem
  intermediarios/                dados consolidados em Parquet
  manifesto_downloads.json        URLs, versões e SHA-512 verificados
  parametros_execucao.json        parâmetros, versões e momento da execução
  resumo_calculado.json           totais do recorte efetivamente processado
  cobertura_corte_171600.json     seções com horário conhecido e desconhecido
  resultados_tse_2026_*.zip       tabelas, gráficos, fontes e documentação
```

Os nomes temporais refletem o corte escolhido. Os ZIPs de resultados não incluem os dados brutos nem os intermediários volumosos. Conserve a pasta `arquivos` se precisar dos mesmos bytes no futuro. Uma nova execução continua conferindo os hashes oficiais.

Para reutilizar um ZIP obtido manualmente, coloque-o na pasta `arquivos/` dentro da pasta informada em `--saida`, mantendo o nome original do TSE. No Colab, o cache padrão é `/content/tse_reproducivel/arquivos/`. A presença do arquivo não dispensa a consulta e a conferência do hash; se o arquivo não corresponder ao recurso selecionado, o programa baixa a versão anunciada. CSVs soltos enviados ao Drive não são entradas deste programa.

## Como conferir a reprodução

- Compare `parametros_execucao.json`: eleição, escopo, exterior, fuso e corte devem coincidir.
- Compare as URLs, versões e hashes de `manifesto_downloads.json`. O catálogo atual pode ser revisado; os mesmos parâmetros não garantem os mesmos dados em datas diferentes.
- Confira se todas as partições esperadas foram processadas e se as checagens contábeis passaram.
- A reconciliação com uma totalização oficial independente continua pendente se `REFERENCIA_OFICIAL` estiver vazia. Hash correto e contas internas reconciliadas não substituem essa comparação.
- Um teste piloto confere a execução do programa, mas não prova que a execução nacional naquele ambiente foi concluída.

## Como ler os cálculos sem confundir as medidas

1. Os gráficos por horário de encerramento somam todos os votos das seções de cada grupo. Não contam apenas os votos depositados depois daquele horário.
2. O cálculo até 17h16 usa comparação inclusiva, `encerramento <= corte`. Nas seções fechadas até esse instante, todos os votos compõem um mínimo para cada candidato. Nas outras seções não é possível repartir os votos por candidato e horário com o BU.
3. O limite superior conservador é o total final do candidato. Ele é um limite matemático, não uma estimativa. `INDETERMINADO` não equivale a zero. As seções do exterior sem conversão de fuso permanecem nessa incerteza.
4. 17h16 é um corte escolhido para a análise. O [texto do TSE](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno) menciona 17h10 como estimativa dos procedimentos de encerramento, sem instituir um prazo universal para invalidar votos.
5. O contador biométrico não revela o candidato escolhido. Correlação, unanimidade e desvio de Benford exigem interpretação contextual e não demonstram fraude por si sós.

As faixas 17h/17h16/19h dos gráficos comparativos são fixas. Alterar `--corte` muda a tabela de limites temporais, e não essas faixas históricas.

## Opção C — usar como skill no Codex

A skill é opcional. Para descoberta local, copie a pasta inteira `tse-reproducivel` para `.agents/skills/` dentro do projeto onde você trabalha. O resultado deve ser:

```text
seu-projeto/.agents/skills/tse-reproducivel/SKILL.md
seu-projeto/.agents/skills/tse-reproducivel/scripts/tse.py
seu-projeto/.agents/skills/tse-reproducivel/assets/Analise_TSE_2026.ipynb
```

Preserve os demais arquivos da pasta. Depois, peça no Codex:

```text
Use $tse-reproducivel para rodar o piloto no meu ambiente e conferir os arquivos gerados.
```

Depois do piloto:

```text
Use $tse-reproducivel para executar o escopo nacional, com exterior e corte inclusivo às 17:16:00 de Brasília. Mostre a cobertura, as checagens e os limites da interpretação.
```

A descoberta e a invocação seguem a [documentação oficial de skills](https://learn.chatgpt.com/docs/build-skills). Não é necessário instalar a skill para executar o comando. Este pacote não inclui um plugin de marketplace.

## Como disponibilizar a outras pessoas

**Distribuição direta:** envie o ZIP deste pacote, ou disponibilize-o para download. Quem receber poderá extrair e seguir as opções A, B ou C.

**Repositório público:** compartilhe o endereço deste [repositório](https://github.com/antunesclarissa/tse-reproducivel) ou o link do notebook no Colab. Para manter uma versão própria, faça um fork ou crie um repositório com os arquivos do pacote. O Colab também pode abrir notebooks hospedados no GitHub.

**Compartilhamento pelo Colab:** carregue a cópia limpa em uma conta escolhida para publicação e configure leitura. Compartilhar um arquivo por uma conta pode associá-lo ao perfil e ao proprietário dessa conta; remover dados do arquivo não torna a conta anônima. Por isso, para distribuir o código sem vínculo com o Drive original, prefira o ZIP ou um repositório dedicado.

Publique a cópia em `assets`, que está sem saídas. Não publique o notebook original da conta nem a pasta de resultados inteira sem revisão. Antes de publicar, execute o scanner descrito em [PRIVACIDADE.md](PRIVACIDADE.md). Defina a licença de redistribuição que pretende conceder; este pacote não presume uma escolha de licença pelo autor.

## Se der erro

Se faltar uma biblioteca, confirme que instalou as dependências com o mesmo Python que executa o comando. Se o catálogo, hash ou arquivo do TSE estiver indisponível, guarde o erro e tente mais tarde; não desative a verificação. Se o ambiente do Colab for encerrado, os arquivos temporários podem ser perdidos: uma nova execução será necessária. O notebook parcial salvo por comando serve para diagnóstico e não representa conclusão da análise.
