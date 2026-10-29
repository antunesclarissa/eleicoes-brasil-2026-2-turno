# Privacidade da distribuição e das suas execuções

O pacote público contém código, instruções e um notebook sem saídas de execução. Ele usa fontes públicas do TSE, caminhos relativos ou o armazenamento temporário genérico do Colab. Não requer acesso ao Drive do autor, senhas, tokens ou chave de IA. No Colab, cada pessoa usa sua própria conta para executar e salvar suas cópias.

A busca textual da versão publicada, realizada em 29/10/2026, não encontrou e-mails, vínculos individuais com arquivos do Google Drive, caminhos de pastas pessoais ou formatos de credenciais reconhecidos pelo scanner. Isso é uma verificação limitada aos arquivos examinados, não uma garantia de detecção universal.

## Como repetir a busca no seu ambiente

Dentro da pasta do pacote:

```bash
python scripts/tse.py auditar assets/Analise_TSE_2026.ipynb
python scripts/tse.py auditar .
```

O scanner procura e-mails, links individuais de arquivos Google, seletores de conta, pastas pessoais, alguns formatos de tokens e URLs com credenciais. Ele imprime o arquivo e a categoria do achado, sem imprimir o dado encontrado. Retorno 0 significa que esses padrões não foram encontrados; retorno 1 pede revisão; retorno 2 indica erro.

O scanner examina arquivos textuais de formatos selecionados com até 20 MB. Ele ignora ambientes virtuais e repositórios internos, não lê pixels e não abre ZIPs. Extraia o pacote antes de examinar. Achados podem ser falsos positivos. Ausência de achados não garante ausência de todo dado pessoal.

## O que revisar antes de publicar uma nova execução

Confira o código e os parâmetros que você alterou, as saídas, mensagens de erro, metadados e arquivos adicionais. Um erro pode revelar um caminho do seu computador. Uma referência independente que você inserir pode apontar para arquivo privado. Documentos, imagens e comentários adicionados precisam de revisão própria.

Prefira distribuir novamente a cópia limpa de `assets`. Se quiser publicar resultados executados, revise-os separadamente. Não inclua `.venv`, `.env`, credenciais, pastas do Drive ou capturas de tela da sua conta.

Limpar o arquivo não anonimiza a conta que o hospeda. Ao compartilhar pelo Drive, Colab ou repositório, considere também nome do perfil, autoria dos commits, permissões e informações públicas desse serviço. O pacote não modifica esses dados de conta.
