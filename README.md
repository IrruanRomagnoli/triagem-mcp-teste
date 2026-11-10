# Triagem de issues com agente de IA + MCP

Projeto da disciplina **Sistemas de Informação e Resultados Empresariais** (Ciência da Computação). Este repositório é privado e de teste.

**Processo automatizado:** triagem de issues do GitHub (ler a issue, escolher o label, comentar).
**Pergunta:** um agente de IA (Claude Code + servidor MCP do GitHub, com aprovação humana) responde mais rápido que a triagem feita à mão?

## O que foi feito

| Rodada | Issues | Quem abriu | Quem triou |
|---|---|---|---|
| AS-IS (baseline, triagem manual) | #7 a #14 | conta do dono do repositório (textos escritos pelo Claude) | **Mauricio**, à mão |
| TO-BE (agente + MCP) | #15 a #22 | **Mauricio** | agente de IA propôs; o dono do repositório aprovou; aplicado via MCP |

## Resultados (n = 8 por rodada)

| Indicador | AS-IS (manual) | TO-BE (agente + MCP) |
|---|---|---|
| Horas até a 1ª resposta, mediana | 18,32 h | 0,32 h (~19 min) |
| Horas até a 1ª resposta, média | 18,18 h | 0,36 h |
| Issues com resposta | 8 de 8 | 8 de 8 |
| Sem label em 24 h | 0 de 8 | 0 de 8 |
| Reclassificações | 0 | 0 |

**Como ler (limitações):**
- As ~18 h do AS-IS são o tempo até a pessoa sentar para triar (tudo de uma vez). No TO-BE a pessoa já estava presente. A diferença é de **disponibilidade**, não só de velocidade do agente.
- Amostra pequena (8 por rodada) e issues sintéticas.
- "Sem label em 24 h" e reclassificações deram 0 nas duas rodadas: não discriminaram.
- A qualidade do label escolhido não foi medida (não há gabarito).

## Definição dos indicadores

| Indicador | Definição |
|---|---|
| Primeira resposta | primeiro comentário ou evento `labeled` de um usuário diferente do autor e que não seja bot |
| horas_ate_primeira_resposta | `createdAt` até a primeira resposta; vazio se não houver |
| sem_label_em_24h | `pendente` se ainda não passaram 24 h e não há label; `true` se não houve label nas primeiras 24 h; `false` caso contrário |
| reclassificacoes | número de eventos `unlabeled` da issue |

## Para conferir ou refazer a medição no Windows

O script `baseline/medir.py` só **lê** o GitHub (nunca escreve). Use o **PowerShell**.

**1. Instalar (uma vez)**

```powershell
winget install GitHub.cli
winget install Python.Python.3.12
```

Feche e abra o PowerShell de novo. Confira: `gh --version` e `python --version`.

**2. Entrar no GitHub com a sua conta (a que foi convidada para o repositório)**

```powershell
gh auth login
```

Escolha GitHub.com, HTTPS e login pelo navegador.

**3. Baixar o repositório**

```powershell
gh repo clone IrruanRomagnoli/triagem-mcp-teste
cd triagem-mcp-teste
```

Sem o `gh`, também dá para usar o botão **Code → Download ZIP** nesta página e extrair.

**4. Medir** (substitua `FIM` por `AGORA` para medir até o momento atual)

Baseline (issues #7 a #14):

```powershell
python baseline\medir.py --repo IrruanRomagnoli/triagem-mcp-teste --inicio 2026-11-09T22:49:56Z --fim 2026-11-10T17:20:00Z --saida meu-baseline
```

TO-BE (issues #15 a #22):

```powershell
python baseline\medir.py --repo IrruanRomagnoli/triagem-mcp-teste --inicio 2026-11-10T17:21:00Z --fim AGORA --saida meu-to-be --titulo "Resumo TO-BE (agente de IA + MCP)"
```

Cada comando cria uma pasta com `triagem.csv` (uma linha por issue) e `resumo.md`. Para só ver o resumo sem gravar nada, acrescente `--verificar`.

**Horário:** o script usa UTC. Horário de Brasília + 3 h = UTC (14:21 em Brasília = 17:21Z).

**Se der erro `TLS handshake timeout`:** é instabilidade de rede; rode de novo.

## Regras do trabalho

- O agente **propõe**; ações irreversíveis exigem **aprovação humana**.
- Só contas e dados de teste. Nada de dados reais de terceiros (LGPD).
- Nenhum token ou chave está neste repositório. Não coloque nenhum.
