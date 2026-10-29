# Análise reproduzível dos Boletins de Urna — TSE 2026

Programa em Python e notebook para baixar dados públicos do Tribunal Superior Eleitoral (TSE), verificar a integridade dos arquivos e produzir tabelas e gráficos sobre votação por seção eleitoral.

Esta versão analisa **Presidente, segundo turno de 2026**, com data de referência **25/10/2026**. Há um piloto no Acre e um modo nacional com as 27 UFs e o exterior. O projeto é independente e não é um produto oficial do TSE.

**Comece pelo Colab:** [abrir o notebook no Google Colab](https://colab.research.google.com/github/antunesclarissa/eleicoes-brasil-2026-2-turno/blob/main/assets/Analise_TSE_2026.ipynb).

## O que este projeto faz

- Baixa os Boletins de Urna (BUs) do catálogo oficial, por UF, e confere o hash SHA-512 publicado pelo TSE.
- Consolida os registros em uma linha por seção, sem multiplicar os contadores que se repetem nas linhas dos candidatos.
- Calcula totais por candidato, grupos de horário de encerramento, indicadores biométricos, correlações, unanimidade e um diagnóstico exploratório de Benford.
- Para um horário escolhido, calcula **limites de votos por candidato até aquele instante**, mantendo no universo as seções que encerraram depois dele.
- Exporta CSVs, gráficos, parâmetros, URLs e hashes, além de um ZIP dos resultados.

**Limite essencial:** o BU contém totais finais, sem a hora de cada voto por candidato. Portanto, somar os votos de seções que fecharam depois das 17h não informa quantos votos foram depositados depois das 17h. Resultados temporais não identificáveis permanecem `INDETERMINADO`. Correlações, unanimidade e Benford não demonstram fraude por si sós. Veja [como os cálculos funcionam](METODOLOGIA.md).

## 1. De onde vêm os dados e onde baixar as bases

**Catálogo oficial usado pelo programa:** [Resultados — 2026 — Boletim de Urna, Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna).

Na seção **Dados e recursos** dessa página:

1. Escolha a UF desejada, ou **ZZ** para exterior.
2. Localize **Boletim de Urna — Segundo turno**. O catálogo também contém primeiro turno; não misture os dois.
3. Abra o recurso e clique em **Ir para recurso** para baixar o ZIP de dados.
4. Baixe também o recurso **Hash SHA2 — Segundo turno** da mesma UF e versão. O programa usa seu conteúdo SHA-512 para conferir o ZIP.
5. Extraia o ZIP para consultar o CSV e o dicionário de dados que o acompanha. O código lê o CSV diretamente do ZIP e preserva o dicionário nos resultados.

Exemplo concreto do Acre, versão utilizada na validação do programa:

| Arquivo | Download oficial |
|---|---|
| Base do Acre, segundo turno | [bweb_2t_AC_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AC_261020260742.zip) |
| Hash correspondente | [bweb_2t_AC_261020260742.zip.sha512](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AC_261020260742.zip.sha512) |

Para outras UFs e versões, use o catálogo. Há também uma [lista de links por UF](fontes/recursos_segundo_turno.csv), registrada em 29/10/2026 a partir do catálogo consultado no teste. Essa lista é uma referência de download; o programa consulta o catálogo novamente a cada execução.

**Interface pública consultada pelo código:** [API do catálogo do TSE](https://dadosabertos.tse.jus.br/api/3/action/package_show?id=resultados-2026-boletim-de-urna).

**Preciso baixar os arquivos manualmente?** Não. As opções Colab e comando fazem os downloads automaticamente. O roteiro acima permite inspecionar as fontes por conta própria. Não é preciso enviar as bases ao seu Drive nem ter acesso à conta de quem criou este repositório. O programa verifica arquivos já presentes na pasta de cache antes de reutilizá-los; os detalhes estão no [guia completo](LEIA-ME.md).

## 2. Rodar no Colab, sem instalar Python no computador

1. [Abra o notebook deste repositório no Colab](https://colab.research.google.com/github/antunesclarissa/eleicoes-brasil-2026-2-turno/blob/main/assets/Analise_TSE_2026.ipynb) e entre na sua própria conta Google.
2. Se quiser guardar as suas alterações, salve uma cópia na sua conta pelo menu Arquivo. Isso salva o notebook; não é necessário montar o Drive no ambiente de execução.
3. Confira a primeira seção, **Parâmetros**. O padrão é `ESCOPO = "PILOTO"`, com `UF_PILOTO = ["AC"]`, para testar com uma base menor.
4. Para todas as UFs e exterior, altere para `ESCOPO = "COMPLETO"` e mantenha `INCLUIR_EXTERIOR = True`.
5. Use um ambiente Python com **CPU** e selecione **Ambiente de execução → Executar tudo**. As células instalam as bibliotecas ausentes, consultam o TSE e calculam os resultados.
6. Acompanhe as verificações. Uma falha de hash, contabilidade ou cobertura exigida interrompe a execução.
7. Leia as tabelas e gráficos e baixe o ZIP oferecido pela última célula. Guarde-o antes de encerrar a sessão: o armazenamento temporário do Colab pode ser apagado.

Também é possível usar **Code → Download ZIP** neste repositório e carregar `assets/Analise_TSE_2026.ipynb` pelo menu de upload do Colab. Cada pessoa executa os cálculos no próprio ambiente.

## 3. Rodar por comando no computador ou servidor

Requisitos: Git, para clonar o repositório, e **Python 3.11 ou superior compatível com as bibliotecas**. Sem Git, baixe **Code → Download ZIP**, extraia e abra um terminal na pasta extraída. Não precisa de conta Google ou chave de IA. GPU não é necessária.

### macOS ou Linux

```bash
git clone https://github.com/antunesclarissa/eleicoes-brasil-2026-2-turno.git
cd eleicoes-brasil-2026-2-turno
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/tse.py executar --escopo piloto --corte 17:16:00 --saida resultados_piloto
```

Depois de conferir o piloto, rode o nacional:

```bash
python scripts/tse.py executar --escopo nacional --corte 17:16:00 --saida resultados_nacional
```

### Windows — PowerShell

```powershell
git clone https://github.com/antunesclarissa/eleicoes-brasil-2026-2-turno.git
cd eleicoes-brasil-2026-2-turno
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\tse.py executar --escopo piloto --corte 17:16:00 --saida resultados_piloto
```

Para o nacional:

```powershell
.\.venv\Scripts\python.exe scripts\tse.py executar --escopo nacional --corte 17:16:00 --saida resultados_nacional
```

### Parâmetros principais

| Parâmetro | Padrão | Significado |
|---|---|---|
| `--escopo` | `piloto` | `piloto` processa as UFs selecionadas; `nacional` processa todas e o exterior. |
| `--ufs` | `AC` | UFs do piloto, por exemplo `AC,AL`. Não restringe o modo nacional. |
| `--corte` | `17:16:00` | Horário inclusivo em Brasília, em 25/10/2026, para a tabela de limites temporais. |
| `--relogio` | `local` | Hipótese sobre o relógio dos arquivos: `local`, `brasilia` ou `desconhecido`. |
| `--sem-exterior` | desativado | Exclui ZZ do modo nacional; muda o universo da análise. |
| `--saida` | `resultados` | Pasta que receberá arquivos baixados, notebooks e resultados. |

Para conferir as opções, use `python scripts/tse.py executar --help`. Para outro corte, por exemplo 17h em ponto, use `--corte 17:00:00`. Isso muda a tabela de limites; as faixas históricas 17h/17h16/19h dos gráficos comparativos permanecem fixas e identificadas nos rótulos.

O programa executa o notebook incluído, de ponta a ponta. O modo nacional exige mais download, memória e tempo que o piloto; a duração depende da máquina, da conexão e da disponibilidade da fonte. Esta versão não foi adaptada para outros cargos, anos ou turnos.

## 4. Encontrar e conferir os resultados

Dentro da pasta escolhida em `--saida`:

| Local | Conteúdo |
|---|---|
| `arquivos/` | ZIPs oficiais e hashes; cache reutilizável. |
| `notebooks/` | Notebook executado, com tabelas e gráficos. |
| `execucoes/<data-e-escopo>/tabelas/` | CSVs, incluindo totais por candidato e limites do corte escolhido. |
| `execucoes/<data-e-escopo>/graficos/` | Gráficos PNG. |
| `execucoes/<data-e-escopo>/manifesto_downloads.json` | URLs, versões e hashes conferidos. |
| `execucoes/<data-e-escopo>/parametros_execucao.json` | Parâmetros, versões das bibliotecas e momento da execução. |
| `execucoes/<data-e-escopo>/resultados_tse_2026_*.zip` | Tabelas, gráficos e documentação para guardar. |

Para comparar duas execuções, confira **escopo, fuso, corte, URLs e hashes**. A fonte pode ser atualizada; os mesmos parâmetros não garantem os mesmos arquivos em datas diferentes. A reconciliação com uma totalização oficial independente continua pendente enquanto `REFERENCIA_OFICIAL` estiver vazia.

**Validação registrada:** instalação em ambiente novo no macOS, piloto do Acre com 2.270 seções, 432.228 votos válidos, quinze células de código sem erro e dez gráficos. Esses números descrevem o piloto, não uma totalização nacional. Detalhes e limites em [VALIDACAO.json](VALIDACAO.json).

## 5. Usar como skill, opcionalmente

A skill orienta uma IA a usar este pacote; ela não é necessária para executar o programa. Para uso local no Codex, copie **a pasta inteira do repositório**, preservando os arquivos, para `.agents/skills/tse-reproducivel/` dentro do seu projeto. Leia [as instruções de instalação](LEIA-ME.md#opção-c--usar-como-skill-no-codex).

Depois, peça:

```text
Use $tse-reproducivel para executar o piloto no meu ambiente, conferir a cobertura e explicar os arquivos gerados.
```

## 6. Privacidade e documentação

O notebook publicado está sem saídas e sem vínculos com arquivos pessoais do Google Drive. Os dados vêm de fontes públicas do TSE. Antes de publicar suas próprias alterações ou resultados, execute:

```bash
python scripts/tse.py auditar .
```

A busca é limitada a padrões textuais; não garante detectar todo dado pessoal. Consulte [PRIVACIDADE.md](PRIVACIDADE.md).

- [Guia completo de execução](LEIA-ME.md)
- [Definições, cálculos e limites](METODOLOGIA.md)
- [Notebook para baixar ou inspecionar](assets/Analise_TSE_2026.ipynb)
- [Código do comando](scripts/tse.py)
- [Instruções da skill](SKILL.md)
- [Versões diretas testadas](requirements-validado.txt)

Este repositório não inclui os grandes ZIPs de dados nem concede uma licença de software que não tenha sido escolhida pelo titular. As condições dos dados de origem são as indicadas no catálogo do TSE.
