# Layout por faixas (lanes) — padrão visual Leona

> **Obrigatório** em fluxos com IA copilot, produção assíncrona e remarketing (25+ nós).  
> Referência canônica: fluxo **`66309`** [v2] Gerar Preview de Imagem (reorganização manual aprovada, jul/2026).  
> Hub: [layout.md](layout.md) · [SKILL.md](SKILL.md)

---

## Por que este padrão existe

O script `layout_flow.py` organiza por **profundidade do grafo** (colunas fixas, irmãos empilhados). Isso é útil como **primeiro passo**, mas produz canvas ilegível em fluxos reais:

- Tronco feliz, IA, produção e remarketing **na mesma coluna**
- Back-edges (loops) **competem** visualmente com avanço
- Setup espalhado horizontalmente
- Mensagens intermediárias **redundantes** entre IA e wait

O padrão de **faixas** organiza por **significado**, não por camada algorítmica.

---

## Modelo mental

```
                    PRODUÇÃO (pista superior — Y baixo/negativo)
                    ═══════════════════════════════════════════►
SETUP          TRONCO FELIZ (wait → validação → sync)
(coluna    ═══════════════════════════════════════════►
vertical)
                    IA HUB (pista central — abaixo do tronco)
                         ╲  loops / RAG / estilo / padrão
                          ╲
                    RMKT (pista inferior/direita — timeout)
                    ═══════════════════════════════════════════►
```

| Eixo | Significado |
|------|-------------|
| **X (esquerda → direita)** | Progresso geral no funil — mas por **zonas**, não grade rígida |
| **Y (cima → baixo)** | **Pista funcional** — feliz em cima, exceções/IA no meio, RMKT embaixo |
| **Coluna vertical esquerda** | Setup pré-conversa (manip, tags, kanban) |

**Leitura humana:** quem abre o fluxo identifica em 5s: entrada | conversa | IA | produção | repescagem.

---

## As 5 zonas

### Zona 1 — Coluna de entrada (setup)

**O quê:** tudo antes da primeira interação com o lead.

**Como posicionar:**
- **Mesma faixa X** (~400–450px da origem)
- **Empilhar verticalmente** (manip → tags → kanban) — **não** cadeia horizontal
- Manipulador de contexto **acima** das etiquetas (Y mais negativo)
- Mensagem de intro **um pouco à direita** (primeiro deslocamento horizontal real)

**Blocos típicos:** `manipulator` → `tags` → `kanban` → `message` (intro)

```
     [Manip]     Y ≈ −400
     [Tags ]
     [Tags ]     mesma coluna X
     [Kanban]
        ↘
      [Msg intro]   X + ~300
```

---

### Zona 2 — Pista superior (tronco feliz)

**O quê:** caminho sem desvio quando o lead coopera (envia o que foi pedido).

**Como posicionar:**
- **Y baixo ou negativo** (empurrar para cima no canvas)
- Avanço horizontal moderado (~300–350px entre clusters, não 400 fixo)
- Sequência típica: `wait_response` → `condition` (validação) → `message` / `integration` (produção)

**Regra:** este tronco **não passa pelo bloco de IA** no desenho — a IA fica **abaixo**, como desvio.

Exemplo Preview (`66309`):
```
wait foto → cond (é imagem?) → msg produção → integrações → intervalos → connection_flow
```

---

### Zona 3 — Hub da IA (copilot)

**O quê:** lead respondeu fora do script (texto livre, dúvida, mídia fora de hora).

**Como posicionar:**
- **Não** é a “próxima coluna” após o wait
- **Deslocado para baixo** do tronco (Y ≈ +700 a +900 em relação ao wait)
- **Mesmo cluster X** do ponto onde o desvio acontece (após condicional de falha)
- Saídas **irradiam** para destinos distintos — cada ramo com espaço Y próprio

**Saídas visuais (padrão):**

| `output_key` | Destino visual |
|--------------|----------------|
| `foto_ok` / avanço | **Loop de volta** ao condicional do tronco (seta sobe) |
| `duvida` | RAG (`integration`) → msg → **volta ao wait** |
| `opcao_*` | manip campo → msg confirmação → **volta ao wait** |
| `padrao` | **Direto ao wait** (sem mensagem intermediária) |
| `failure` | erro **muito abaixo** do bloco IA (Y +400~500), mesma coluna X |

**Anti-padrão:** mensagem fixa entre IA e wait só para repetir o que o wait já diz (`2315678` no Preview — **removido**).

**Anti-padrão:** dois waits com o mesmo papel (`2315676` + `2397915` ambos pedindo foto) — consolidar quando possível.

---

### Zona 4 — Corredor de produção (paralelo superior)

**O quê:** sync Farol, polling, geração de mídia, handoff.

**Como posicionar:**
- **Pista paralela** ao tronco feliz — **acima** (Y negativo)
- Integrações em sequência: **mesmo Y**, X consecutivo (corredor horizontal)
- `smart_interval` + `condition` (status) no mesmo corredor
- `connection_flow` (handoff) no **fim** do corredor

**Regra:** produção **não cruza** visualmente o hub da IA nem o remarketing.

---

### Zona 5 — Remarketing (inferior/direita)

**O quê:** timeout do wait, menu de repescagem, IA de RMKT, encerrar/continuar.

**Como posicionar:**
- **Faixa inferior** (Y positivo alto) e **direita** (X > 4500 em fluxos grandes)
- Agrupar: `wait timeout` → `menu` / `smart_interval` → `ai` RMKT → msgs → `connection_flow`
- **Separado** do tronco e da produção

**Regra:** back-edges de timeout **não** contam como coluna forward — desenhar na pista de baixo.

---

## Procedimento completo (atualizado)

```
① wiring_needed: false
② layout_flow.py          → esboço mecânico (colunas)
③ Aplicar faixas (este doc) → reposicionar por zona (manual ou reposition_flow_nodes)
④ Ajustes pontuais        → erro IA y+450; sync mesmo Y
⑤ get_flow + fit view no Leona
```

`layout_flow.py` **não substitui** o passo ③ em fluxos com IA + produção + RMKT.

---

## Constantes sugeridas (faixas)

| Zona | X aproximado | Y aproximado |
|------|--------------|--------------|
| Setup | 400–450 | −400 → +250 (vertical) |
| Tronco feliz | 700 → 2200 | −200 → +100 |
| Hub IA | 2100–2700 | +700 → +1100 |
| Erro IA | mesma X do IA | +1200 → +1500 |
| Produção | 2200 → 4400 | −600 → −200 |
| RMKT | 4700 → 6000 | +400 → +1500 |

Valores são **âncoras**, não grade rígida. O critério é **separação visual entre pistas**, não pixel perfeito.

---

## Checklist de faixas (Definition of Done visual)

- [ ] Setup em **coluna vertical** à esquerda (não horizontal)
- [ ] Tronco feliz na **pista superior**
- [ ] Bloco IA **abaixo** do tronco, como hub lateral (não próxima coluna forward)
- [ ] Loops (foto_ok, volta ao menu/wait) com setas que **sobem** ou **voltam** — visualmente separados
- [ ] Produção em **corredor paralelo superior**
- [ ] Remarketing em **zona inferior/direita**
- [ ] Erro IA **longe abaixo** do bloco IA (não entre integrações)
- [ ] Zero mensagens **redundantes** entre IA e wait
- [ ] Zero nós órfãos (`wiring_needed: false`)
- [ ] `fit view` — fluxo legível sem zoom excessivo

---

## Comparativo: script vs faixas

| Dimensão | `layout_flow.py` | Padrão de faixas |
|----------|------------------|------------------|
| Critério X | Profundidade topológica | Zona funcional |
| Critério Y | Irmãos empilhados | Pista (feliz / IA / RMKT) |
| Setup | Horizontal | **Vertical** |
| IA | Coluna seguinte | **Hub lateral** |
| Back-edge | Ignorado no X, empilhado no Y | **Pista própria** |
| Espaçamento | 330–400px fixo | **Clusters orgânicos** ~300–350 |
| Mensagens | Pode criar colunas extras | **Sem redundância** |

---

## Anti-padrões visuais (faixas)

- IA na mesma linha Y do wait principal
- Produção misturada com ramos de IA ou RMKT na mesma coluna
- Mensagem entre IA `padrao` e wait (duplica instrução)
- Dois waits pedindo a mesma coisa (foto, menu, etc.)
- Erro IA entre integrações de sync
- Coluna nova só por mensagem (sem wait/decisão entre elas)
- Confiar só no script e declarar “pronto” sem passo ③

---

## Referência — Preview 66309 (mapa aprovado)

| Zona | Nós (ids) | Papel |
|------|-----------|-------|
| Setup | `2314779` `2314825` `2414022` `2314784` | manip, tags, kanban |
| Intro | `2314828` | msg estilo anotado |
| Tronco | `2315676` `2314797` `2316498` | wait foto, validação |
| IA hub | `2315677` | copilot envio foto |
| IA ramos | `2413723` `2413725` `2315681` `2315679` | estilo, RAG |
| Produção | `2314789` `2314800` `2314781` … `2315674` | sync + polling |
| RMKT | `2315685` `2315713` `2315755` `2414127` | timeout + repescagem |
| Erro | `2315680` `2316279` | failure → fluxo erro |

> **Pendente (feedback usuário):** lógica do bloco IA — documentar em `blocks.md` / `leona-farol` após definição final.

---

## Para o agente

Ao reorganizar canvas:

1. Ler `get_flow` e classificar cada nó numa das **5 zonas**
2. `reposition_flow_nodes` em **lotes por zona** (não nó a nó aleatório)
3. Não alterar conexões durante layout
4. Remover nós **redundantes** só se o usuário confirmar ou forem órfãos
5. Em fluxos Farol com `menu_other` / copilot: cruzar com `leona-farol` (pattern-copilot-menu-other) para **lógica**; este doc cobre **visual**
