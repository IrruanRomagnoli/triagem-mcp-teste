#!/usr/bin/env python3
"""Mede a triagem manual (AS-IS) de issues. Somente leituras (gh issue list / gh api GET)."""
import argparse, csv, json, statistics, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(f"erro em gh {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def gh_pages(path):
    # `gh api` usa GET por padrao; --paginate concatena arrays JSON, entao decodifico em sequencia.
    out, dec, i = [], json.JSONDecoder(), 0
    txt = gh("api", "--paginate", "-X", "GET", path)
    while i < len(txt):
        if txt[i].isspace():
            i += 1
            continue
        obj, i = dec.raw_decode(txt, i)
        out += obj
    return out


def is_bot(u):
    return not u or u.get("type") == "Bot" or u.get("login", "").endswith("[bot]")


def metricas(created, autor, comentarios, eventos, agora):
    """created: datetime; comentarios/eventos: listas da API do GitHub."""
    resp = [ts(c["created_at"]) for c in comentarios
            if not is_bot(c["user"]) and c["user"]["login"] != autor]
    resp += [ts(e["created_at"]) for e in eventos if e["event"] == "labeled"
             and not is_bot(e.get("actor")) and e["actor"]["login"] != autor]
    horas = round((min(resp) - created).total_seconds() / 3600, 2) if resp else ""
    labeled = [ts(e["created_at"]) for e in eventos if e["event"] == "labeled"]
    if any(t <= created + timedelta(hours=24) for t in labeled):
        sem24 = False
    elif not labeled and agora < created + timedelta(hours=24):
        sem24 = "pendente"
    else:
        sem24 = True
    return horas, sem24, sum(e["event"] == "unlabeled" for e in eventos)


def resumo(linhas, repo, ini, fim, agora, nota, titulo):
    n = len(linhas)
    h = [l["horas_ate_primeira_resposta"] for l in linhas if l["horas_ate_primeira_resposta"] != ""]
    s24 = [l["sem_label_em_24h"] for l in linhas if l["sem_label_em_24h"] != "pendente"]
    pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "n/d"
    rec = [l["reclassificacoes"] for l in linhas]
    return f"""# {titulo}

- Repositório: {repo}
- Janela (UTC): {ini:%Y-%m-%dT%H:%M:%SZ} a {fim:%Y-%m-%dT%H:%M:%SZ}
- Executado em (UTC): {agora:%Y-%m-%dT%H:%M:%SZ}

## Métricas
- n (issues na janela): {n}
- Com primeira resposta: {len(h)} ({pct(len(h), n)}); sem resposta: {n - len(h)} ({pct(n - len(h), n)})
- Horas até a primeira resposta: média {f'{statistics.mean(h):.2f}' if h else 'n/d'} · mediana {f'{statistics.median(h):.2f}' if h else 'n/d'} (n={len(h)})
- Sem label em 24h: {s24.count(True)} de {len(s24)} avaliáveis ({pct(s24.count(True), len(s24))}); pendentes: {n - len(s24)}
- Reclassificações (eventos unlabeled): total {sum(rec)} · média {f'{statistics.mean(rec):.2f}' if rec else 'n/d'} · mediana {f'{statistics.median(rec):.2f}' if rec else 'n/d'}

## Limitações
- Primeira resposta ignora o autor da issue e bots; se a mesma pessoa abre e triagem, nada conta como resposta.
- Label aplicado na criação conta como labeled (evento no mesmo instante).
- Amostra pequena: média e mediana não são generalizáveis.
- Horas medidas em tempo corrido (inclui noites e fins de semana).
{nota}"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--inicio", required=True)
    p.add_argument("--fim", required=True, help="ISO UTC ou AGORA")
    p.add_argument("--saida", default=str(Path(__file__).parent))
    p.add_argument("--verificar", action="store_true", help="imprime o resumo, nao grava arquivos")
    p.add_argument("--nota", default="", help="limitacao extra para o resumo")
    p.add_argument("--titulo", default="Resumo AS-IS (triagem manual)", help="titulo do resumo.md")
    a = p.parse_args()
    agora = datetime.now(timezone.utc)
    ini = ts(a.inicio)
    fim = agora if a.fim == "AGORA" else ts(a.fim)

    issues = json.loads(gh("issue", "list", "--repo", a.repo, "--state", "all", "--limit", "1000",
                           "--json", "number,createdAt,author,labels,state"))
    issues = [i for i in issues if ini <= ts(i["createdAt"]) <= fim]
    linhas = []
    for i in sorted(issues, key=lambda i: i["number"]):
        n, autor = i["number"], i["author"]["login"]
        com = gh_pages(f"repos/{a.repo}/issues/{n}/comments?per_page=100")
        ev = gh_pages(f"repos/{a.repo}/issues/{n}/events?per_page=100")
        h, s24, rec = metricas(ts(i["createdAt"]), autor, com, ev, agora)
        linhas.append({"numero": n, "criada_em": i["createdAt"], "autor": autor, "estado": i["state"],
                       "labels": ";".join(l["name"] for l in i["labels"]),
                       "horas_ate_primeira_resposta": h,
                       "sem_label_em_24h": str(s24).lower() if isinstance(s24, bool) else s24,
                       "reclassificacoes": rec})
    # CSV guarda texto; volto a bool para o resumo
    for l in linhas:
        l["sem_label_em_24h"] = {"true": True, "false": False}.get(l["sem_label_em_24h"], l["sem_label_em_24h"])
    md = resumo(linhas, a.repo, ini, fim, agora, a.nota, a.titulo)
    if a.verificar:
        print(md)
        return
    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)
    campos = ["numero", "criada_em", "autor", "estado", "labels", "horas_ate_primeira_resposta",
              "sem_label_em_24h", "reclassificacoes"]
    with open(out / "triagem.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, campos)
        w.writeheader()
        w.writerows(linhas)
    (out / "resumo.md").write_text(md, encoding="utf-8")
    print(f"gravado em {out}/triagem.csv e resumo.md (n={len(linhas)})")


if __name__ == "__main__":
    main()
