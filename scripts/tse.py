#!/usr/bin/env python3
"""Executa a mesma análise do notebook e verifica referências pessoais em arquivos."""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
from pathlib import Path
import re
import sys

PACOTE = Path(__file__).resolve().parents[1]
NOTEBOOK = PACOTE / "assets" / "Analise_TSE_2026.ipynb"
UFS = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO ZZ".split())


def horario(valor):
    try:
        return dt.time.fromisoformat(valor).strftime("%H:%M:%S") if re.fullmatch(r"\d{2}:\d{2}(:\d{2})?", valor) else erro_horario()
    except ValueError:
        raise argparse.ArgumentTypeError("Use HH:MM ou HH:MM:SS, entre 00:00:00 e 23:59:59.") from None


def erro_horario():
    raise ValueError("horário inválido")


def substituir_parametros(fonte, valores):
    """Altera atribuições conhecidas por posição sintática, sem executar o texto."""
    linhas = fonte.splitlines(keepends=True)
    mudancas = []
    for no in ast.parse(fonte).body:
        if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
            nome = no.targets[0].id
            if nome in valores:
                mudancas.append((no.lineno - 1, no.end_lineno, f"{nome} = {valores[nome]}\n"))
    presentes = {no.targets[0].id for no in ast.parse(fonte).body
                 if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name)}
    if set(valores) - presentes:
        raise ValueError("O notebook não contém todos os parâmetros esperados pelo programa.")
    for inicio, fim, substituto in reversed(mudancas):
        linhas[inicio:fim] = [substituto]
    return "".join(linhas)


def preparar(args):
    import nbformat

    nb = nbformat.read(NOTEBOOK, as_version=4)
    uf_piloto = list(dict.fromkeys(args.ufs.split(",")))
    if not uf_piloto or not set(uf_piloto) <= UFS:
        raise ValueError("UF inválida. Separe as siglas maiúsculas por vírgula, por exemplo AC,AL.")
    if args.escopo == "nacional" and args.ufs != "AC":
        raise ValueError("--ufs só se aplica ao escopo piloto; o nacional inclui todas as UFs.")
    if args.sem_exterior and args.escopo == "piloto" and "ZZ" in uf_piloto:
        raise ValueError("ZZ em --ufs é incompatível com --sem-exterior.")
    valores = {
        "ESCOPO": repr("COMPLETO" if args.escopo == "nacional" else "PILOTO"),
        "UF_PILOTO": repr(uf_piloto),
        "INCLUIR_EXTERIOR": repr(not args.sem_exterior),
        "HORARIO_CORTE": repr(args.corte),
        "RELOGIO_ARQUIVO": repr(args.relogio.upper()),
        # A pasta de execução é passada ao kernel; o código compartilhável fica relativo.
        "RAIZ": 'Path(".")',
        "INSTALAR_DEPENDENCIAS": "False",
    }
    celulas = [c for c in nb.cells if c.cell_type == "code" and "parametros" in c.metadata.get("tags", [])]
    if len(celulas) != 1:
        raise ValueError("Notebook sem uma única célula de parâmetros identificada.")
    celulas[0].source = substituir_parametros(celulas[0].source, valores)
    for c in nb.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None
    nbformat.validate(nb)
    return nb


def executar(args):
    try:
        import nbformat
        from nbclient import NotebookClient
        from jupyter_client import AsyncKernelManager
    except ImportError:
        print("Instale as dependências: python -m pip install -r requirements.txt", file=sys.stderr)
        return 2
    nb = preparar(args)
    pasta = Path(args.saida).expanduser().resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    carimbo = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destino = pasta / "notebooks" / f"{carimbo}_{args.escopo}.ipynb"
    destino.parent.mkdir(exist_ok=True)
    nbformat.write(nb, destino)
    if args.comando == "preparar":
        print("Notebook configurado, sem execução:", destino)
        return 0

    print(f"Escopo: {args.escopo}; corte inclusivo: {args.corte} Brasília.", flush=True)
    print("A consulta e os downloads usam fontes públicas do TSE. Nenhuma conta é necessária.", flush=True)
    indice_total = sum(c.cell_type == "code" for c in nb.cells)
    andamento = [0]

    def progresso(cell, cell_index, **kwargs):
        andamento[0] += 1
        titulo = cell.source.splitlines()[0][:90]
        print(f"[{andamento[0]}/{indice_total}] {titulo}", flush=True)

    # Usa o Python da instalação atual, mesmo sem um kernel registrado globalmente.
    km = AsyncKernelManager(kernel_name="python3")
    km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    cliente = NotebookClient(nb, km=km, timeout=args.timeout, startup_timeout=120,
                             allow_errors=False, store_widget_state=False,
                             resources={"metadata": {"path": str(pasta)}},
                             on_cell_execute=progresso)
    try:
        cliente.execute(cleanup_kc=True)
    except Exception as erro:
        print(f"Execução interrompida: {type(erro).__name__}: {erro}", file=sys.stderr)
        print("O notebook parcial foi preservado para diagnóstico; ele não é um resultado completo.", file=sys.stderr)
        return 1
    finally:
        nbformat.write(nb, destino)
    print("Concluído. Notebook com tabelas e gráficos:", destino)
    print("Os CSVs, gráficos, parâmetros e o ZIP estão em:", pasta / "execucoes")
    return 0


PADROES = {
    "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "link_para_arquivo_google": re.compile(r"https?://(?:colab\.research\.google\.com/drive/|drive\.google\.com/(?:file/d/|drive/folders/)|docs\.google\.com/(?:document|spreadsheets|presentation)/d/)[\w-]+"),
    "seletor_de_conta": re.compile(r"authuser=\d+"),
    "pasta_pessoal": re.compile(r"/(?:Users|home)/[^/\s\"'\\]+|[A-Z]:\\(?:Users|Documents and Settings)\\[^\\\s\"']+"),
    "token_ou_chave": re.compile(r"ya29\.[\w.-]{12,}|AIza[\w-]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "url_com_credencial": re.compile(r"https?://[^\s/\"']+:[^\s/\"']+@|[?&](?:access_token|refresh_token|sig|token)=[A-Za-z0-9%._~-]{10,}", re.I),
}


def auditar(args):
    alvo = Path(args.alvo).expanduser()
    if not alvo.exists():
        raise ValueError("O arquivo ou pasta solicitado não existe.")
    arquivos = [alvo] if alvo.is_file() else sorted(alvo.rglob("*"))
    achados, inspecionados, ignorados = [], 0, 0
    for arquivo in arquivos:
        if not arquivo.is_file():
            continue
        if any(p in {".git", ".venv", "venv", "__pycache__", "node_modules"} for p in arquivo.relative_to(alvo.parent if alvo.is_file() else alvo).parts):
            continue
        if arquivo.suffix.lower() not in {".ipynb", ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".csv", ".html"} or arquivo.stat().st_size > 20_000_000:
            ignorados += 1
            continue
        try:
            bruto = arquivo.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            ignorados += 1
            continue
        inspecionados += 1
        textos = [bruto]
        if arquivo.suffix == ".ipynb":
            n = json.loads(bruto)
            # Também inspeciona strings decodificadas (inclusive caminhos Windows).
            def strings(obj):
                if isinstance(obj, str):
                    yield obj
                elif isinstance(obj, list):
                    for v in obj:
                        yield from strings(v)
                elif isinstance(obj, dict):
                    for v in obj.values():
                        yield from strings(v)
            textos.extend(strings(n))
        local = str(arquivo.relative_to(alvo.parent if alvo.is_file() else alvo))
        for categoria, padrao in PADROES.items():
            if any(padrao.search(t) for t in textos):
                # O relatório identifica o tipo de achado, sem republicar seu conteúdo.
                achados.append({"arquivo": local, "categoria": categoria})
    relatorio = {"arquivos_textuais_inspecionados": inspecionados,
                 "arquivos_ignorados_formato_tamanho_ou_leitura": ignorados,
                 "achados_para_revisao": achados,
                 "limite": "Busca por padrões; não identifica todo dado pessoal nem examina imagens ou arquivos compactados."}
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return 1 if achados else 0


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", action="version", version="tse-reproducivel 1.0.0")
    sub = p.add_subparsers(dest="comando", required=True)
    for nome, ajuda in [("executar", "Baixar dados públicos e executar a análise completa."),
                        ("preparar", "Gerar notebook configurado, sem baixar dados nem executar.")]:
        s = sub.add_parser(nome, help=ajuda)
        s.add_argument("--escopo", choices=["piloto", "nacional"], default="piloto")
        s.add_argument("--ufs", default="AC", help="Siglas do piloto separadas por vírgula. Padrão: AC.")
        s.add_argument("--corte", type=horario, default="17:16:00", help="Corte inclusivo no dia 25/10/2026, Brasília.")
        s.add_argument("--relogio", choices=["local", "brasilia", "desconhecido"], default="local")
        s.add_argument("--sem-exterior", action="store_true")
        s.add_argument("--saida", default="resultados")
        s.add_argument("--timeout", type=int, default=7200, help="Máximo de segundos por célula; -1 desativa.")
    a = sub.add_parser("auditar", help="Procurar referências pessoais em arquivos textuais.")
    a.add_argument("alvo", help="Arquivo ou pasta a examinar. ZIPs devem ser extraídos antes.")
    return p


def main():
    args = parser().parse_args()
    try:
        return auditar(args) if args.comando == "auditar" else executar(args)
    except (ValueError, OSError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
