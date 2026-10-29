# Definições, cálculos e limites

## Perguntas respondidas

O programa soma os votos dos BUs presidenciais do segundo turno de 2026 e descreve diferenças entre grupos de seções. Investiga como esses grupos se distribuem por encerramento, contador biométrico e votação. Para um instante escolhido, calcula os limites que podem ser sustentados pelos totais finais e pelo encerramento de cada seção.

É uma análise descritiva e reproduzível. Não identifica votos individuais, presença de fiscais, motivos do encerramento, fraude ou efeito causal de uma característica da seção.

## Fontes e unidade de contagem

A fonte é o [catálogo oficial de BUs de 2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna). Os ZIPs são separados por UF e turno. O código filtra ano 2026, turno 2, cargo Presidente e urna do tipo apurada. A documentação de campos é o dicionário distribuído pelo TSE nos arquivos baixados; ele é preservado na pasta `dicionarios` de cada execução.

Uma linha de origem representa uma seção e uma opção votável, como candidato, branco ou nulo. Contadores da seção se repetem em várias linhas. Por isso, o programa consolida uma linha por seção antes de somar esses contadores. Ele não expande seções agregadas e interrompe a análise se encontrar registros conflitantes pela chave de seção/opção votável.

| Campo ou medida | Uso na análise |
|---|---|
| `QT_VOTOS` | Contagem da opção votável na seção. |
| Votos válidos | Soma dos votos nominais dos candidatos. |
| `QT_COMPARECIMENTO` | Quantidade de eleitores que compareceram; comparada aos votos totais. |
| `DT_ENCERRAMENTO` | Data e hora de encerramento da seção; não é o horário de cada voto. |
| `QT_ELEI_BIOM_SEM_HABILITACAO` | Eleitores com biometria que não foram habilitados por ela, conforme o dicionário. |
| Taxa biométrica usada | Contador anterior dividido pelo comparecimento. Não mede, por seu complemento, o sucesso da biometria entre cadastrados. |

O programa identifica os nomes e números dos candidatos a partir dos dados. A escolha do voto não é inferida a partir do contador biométrico.

## Integridade e cobertura

O ZIP é comparado ao SHA-512 publicado pelo TSE antes da leitura. Esse teste verifica correspondência com o arquivo anunciado, sem provar a exatidão substantiva dos dados. Uma execução nacional exige as partições esperadas; uma falha não é escondida como resultado nacional.

Há checagens de votos totais contra comparecimento, aptos contra comparecimento mais abstenção e contador biométrico dentro de limites possíveis. A referência `REFERENCIA_OFICIAL`, vazia por padrão, permite comparar totais com uma fonte independente informada pelo usuário. Contabilidade interna e hash correto não substituem essa comparação externa.

## Horário e fuso

O corte é um instante completo, por exemplo **25/10/2026 às 17:16:00 em Brasília**, inclusive. A data é preservada; um encerramento no dia seguinte não é comparado apenas pela hora do relógio.

O dicionário descreve data/hora sem esclarecer o fuso da coluna. A hipótese padrão é `LOCAL`. A conversão segue os fusos e as exceções municipais documentados para 2026, com ajustes no Amazonas e em Fernando de Noronha. A análise preserva tanto o relógio bruto quanto o horário convertido e exporta um resumo das aberturas para conferência.

As referências de horários são o [TSE](https://www.tse.jus.br/comunicacao/noticias/2026/Setembro/faltam-26-dias-votacao-comeca-e-termina-no-mesmo-horario-em-todo-o-pais) e o [TRE-AM](https://www.tre-am.jus.br/comunicacao/noticias/2026/Setembro/eleitorado-do-amazonas-deve-ficar-atento-aos-horarios-de-votacao-nas-eleicoes-2026). Exterior não tem conversão confiável no programa: suas seções entram nos totais, recebem análise separada em relógio local e permanecem indeterminadas no corte de Brasília.

O padrão 17h16 é uma escolha analítica. O [esclarecimento do TSE sobre encerramento](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno) menciona 17h10 como estimativa de procedimentos, sem estabelecer um prazo universal para invalidar votos.

## Dois cálculos que não devem ser confundidos

**Grupos por encerramento:** a tabela soma todos os votos das seções que encerraram em determinada faixa. Uma seção que terminou às 17h20 pode ter a maioria dos votos depositados antes das 17h. Seu total final não deve ser chamado de votos depositados depois das 17h.

**Limites até um instante:** para cada candidato, o mínimo soma os votos de seções encerradas até o corte, inclusive. Nelas, todos os votos necessariamente antecedem o encerramento, sob a hipótese de fuso configurada. Seções posteriores ou com horário desconhecido continuam no universo, mas seus votos não podem ser repartidos por horário usando apenas os BUs.

O limite superior conservador é o total final do candidato em todas as seções carregadas. O resultado exato só é preenchido quando os limites coincidem; caso contrário, permanece `INDETERMINADO`. Não há distribuição proporcional, interpolação ou substituição de desconhecido por zero. Se a hipótese de relógio for `DESCONHECIDO`, os limites são triviais.

## Como ler os outros resultados

- **Gráficos de sensibilidade:** cada ponto usa o grupo de seções encerradas após um corte diferente. A composição do grupo muda. Não é uma curva de apuração dos mesmos votos ao longo do tempo.
- **Correlações biométricas:** Pearson, Spearman e uma comparação com variáveis centradas no município descrevem associação entre seções. O ajuste municipal reduz diferenças de composição, mas não demonstra causalidade.
- **Histogramas:** contam seções por faixa de participação do candidato. Seções têm tamanhos diferentes; a distribuição de seções não equivale à participação nacional ponderada pelos votos.
- **Unanimidade e supermaioria:** os critérios são simétricos e usam votos válidos. Os cortes por tamanho mostram a sensibilidade a seções pequenas. Não há exigência de distribuição gaussiana dos percentuais eleitorais.
- **Benford:** compara o primeiro dígito das contagens positivas com uma referência matemática. Não se presume que votos por seção, limitados pelo tamanho das seções, devam seguir essa distribuição. P-valor baixo não é uma probabilidade de fraude.
- **Alegado × calculado:** `ALEGACOES` contém valores fixos de comparação, visíveis nos parâmetros. Eles são exemplos de referências externas não verificadas, e não dados oficiais usados para ajustar o resultado. A tabela informa apenas coincidências ou diferenças numéricas. As demais tabelas continuam derivadas dos BUs, independentemente desses valores. Troque as referências apenas com sua própria fonte documentada; não as apresente como metas nem como fatos confirmados.

## Repetir uma execução

Guarde os parâmetros, versões, manifesto e ZIPs originais. Para comparar resultados de dois ambientes, confira se os arquivos têm as mesmas URLs e hashes e se escopo, exterior, fuso e corte coincidem. Se o catálogo mudar, a nova execução pode refletir outra versão dos dados.
