---
name: tse-reproducivel
description: Reproduzir a análise dos Boletins de Urna presidenciais do segundo turno de 2026 no Colab ou por comando, conferir integridade e explicar seus limites temporais. Usar com este pacote de notebook e scripts.
---

# Reprodução dos BUs do TSE

Use os arquivos incluídos neste diretório. Leia [LEIA-ME.md](LEIA-ME.md) para instalação, comandos e procedimento no Colab; consulte [METODOLOGIA.md](METODOLOGIA.md) para definições, origem dos dados e limites, e [PRIVACIDADE.md](PRIVACIDADE.md) antes de distribuir cópias. O [README](README.md) apresenta o projeto para quem não conhece seu contexto e contém o catálogo oficial e o roteiro de download das bases.

- Execute `python scripts/tse.py executar --escopo piloto --corte 17:16:00 --saida resultados` a partir desta pasta. O escopo nacional usa `--escopo nacional` e inclui exterior por padrão. Escolha o escopo solicitado pelo usuário; o piloto é apropriado para testar a instalação.
- Use ambiente Python próprio, dependências de `requirements.txt` e somente downloads públicos do TSE. A análise não exige login, token, conexão com Drive ou API de IA. No Colab, o usuário entra com a própria conta e carrega `assets/Analise_TSE_2026.ipynb`.
- O script executa o notebook de ponta a ponta. Não reescreva cálculos para forçar coincidência com os números alegados. Uma falha de integridade, cobertura exigida ou contabilidade interrompe a execução; examine o erro antes de repetir.
- Registre escopo, corte inclusivo, hipótese de fuso, versões, URLs e hashes. Compare o manifesto entre execuções: o catálogo pode mudar. Um piloto nunca representa o resultado nacional.
- Horário de encerramento agrupa totais finais das seções; não informa a hora de cada voto por candidato. O cálculo temporal conserva todas as seções e produz limites. Preserve `INDETERMINADO` quando a contagem exata não for identificável. O corte 17h16 é uma escolha analítica.
- O contador biométrico é de eleitores com biometria que não foram habilitados por ela; não atribua esse contador a candidatos. Correlações, unanimidade e Benford não estabelecem fraude ou causa por si sós. Mantenha explícita a reconciliação externa pendente quando não houver referência independente.
- Para compartilhar, use a cópia sem saídas e rode `python scripts/tse.py auditar caminho_da_copia`. Não publique arquivos da conta, notebooks de diagnóstico ou resultados com caminhos pessoais sem revisar. O scanner é uma busca limitada por padrões.

Entregue os arquivos gerados e descreva o que efetivamente foi executado, a cobertura e as limitações. Instalar esta skill não autoriza publicar, compartilhar links da conta ou alterar permissões.
