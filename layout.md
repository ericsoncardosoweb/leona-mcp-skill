# Layout do canvas Leona

> **Obrigatório ao fechar qualquer sessão de edição.** Hub: [SKILL.md](SKILL.md).

## Dois níveis de layout

| Nível | Quando | Ferramenta |
|-------|--------|------------|
| **1. Esboço** | Sempre | `layout_flow.py` — colunas por profundidade |
| **2. Faixas** | Fluxos 25+ nós, IA copilot, produção, RMKT | **[layout-lanes.md](layout-lanes.md)** — zonas funcionais |

**Regra:** em fluxos complexos, o script **sozinho não basta**. Após o script, aplicar o **padrão de faixas** (manual ou `reposition_flow_nodes` por zona).

Referência canônica: fluxo **`66309`** [v2] Gerar Preview de Imagem.

---

## Regra de ouro

**Nunca declare o fluxo pronto sem:**
1. `wiring_needed: false`
2. `layout_flow.py` executado (ou reposicionamento equivalente)
3. **Faixas aplicadas** quando o fluxo tem IA hub + produção + remarketing ([layout-lanes.md](layout-lanes.md))

Durante a Fase 2 (construção), blocos empilhados ou sobrepostos são **esperados**. O MCP usa `{x:0,y:0}` e auto-posiciona (+274px horizontal, +80px por ramo).

---

## Procedimento (sempre nesta ordem)

```
① wiring_needed: false (zero nós soltos, todo handle ligado)
② layout_flow.py                    → esboço em colunas
③ Padrão de faixas (layout-lanes.md) → setup vertical, tronco em cima, IA hub, produção, RMKT
④ Ajustes pontuais                  → erro IA y+400~500; sync horizontal mesmo Y
⑤ get_flow + refresh / fit view no Leona
```

**Nunca:**
- confiar **só** no script em fluxos com IA + produção + RMKT;
- reposicionar bloco a bloco **durante** criação sem plano de zona;
- aplicar layout **antes** do wiring completo;
- dizer “pronto” se as faixas não estiverem legíveis.

```powershell
python "$env:USERPROFILE\.cursor\skills\leona-flow\scripts\layout_flow.py" <FLOW_ID>
python ...\layout_flow.py <FLOW_ID> --col-w 400 --gap 100
python ...\layout_flow.py <FLOW_ID> --dry-run
```

O script só altera **x/y** — nunca conexões ou ações.

---

## Modelo mental — faixas (preferir em fluxos complexos)

Ver diagrama completo em **[layout-lanes.md](layout-lanes.md)**.

- **Coluna esquerda (setup):** manip + tags + kanban **empilhados verticalmente**
- **Pista superior:** tronco feliz (wait → validação → ação)
- **Hub IA (centro, abaixo do tronco):** copilot — loops, RAG, exceções
- **Corredor superior paralelo:** produção / sync / polling
- **Pista inferior/direita:** remarketing / timeout

Leitura: **esquerda → direita = progresso**; **cima = feliz/produção**; **meio = IA**; **baixo = RMKT**.

---

## Modelo mental — colunas (script, fluxos simples)

Para fluxos lineares ou &lt; 25 nós, o script basta:

- **Coluna (X) = avanço no funil.** Nova coluna após `wait_response`, `interactive_menu` ou bloco que aguarda input.
- **Mesma coluna** = envios seguidos **sem resposta do lead** → preferir **1 bloco `message`** com várias actions.
- **Back-edge** = timeout/volta — **não** incrementa coluna no script; na faixa manual, vai para **pista RMKT**.
- **Ramos paralelos** = saídas empilhadas na vertical (Y) na mesma coluna.

---

## Constantes

| Parâmetro | Script (`layout_flow.py`) | Faixas (manual) |
|-----------|---------------------------|-----------------|
| `col_w` | 330 px (400 em fluxos grandes) | clusters ~300–350 px |
| `gap` | 70 px (100 espaçado) | separação entre **pistas** Y |
| Setup | — | coluna X ≈ 400–450, stack vertical |

---

## Posicionamento durante criação (MCP)

- Cadeia linear: `position {x:0,y:0}`.
- Ramo: `position_near_node_id` = id do pai, `auto_connect_to_flow_tail: false`, Y +80px por slot.
- Após wiring: reposicionar **por zona** em lotes ([layout-lanes.md](layout-lanes.md) § Para o agente).

---

## Exceções pós-script / pós-faixas

| Caso | Ajuste |
|------|--------|
| Erro IA | mesma X do bloco IA, **y + 400~500** (abaixo do hub, não no corredor sync) |
| Sync CRM / integrações em sequência | **mesmo Y**, colunas consecutivas (corredor produção) |
| Hub IA | **abaixo** do wait/cond do tronco — nunca mesma linha Y |
| Loop `foto_ok` / volta ao menu | seta visual **sobe** para pista superior |
| Loop horário `condition` ↔ `smart_interval` | back-edge na pista RMKT ou produção, não nova coluna forward |

---

## Anti-padrões visuais

- Script aplicado e declarado pronto **sem faixas** (fluxo complexo)
- IA na mesma linha Y do wait principal
- Mensagem redundante entre IA `padrao` e wait
- Dois waits com o mesmo papel (ex.: dois “envie foto”)
- Produção misturada com hub IA ou RMKT
- Setup em cadeia horizontal longa
- Coluna nova por mensagem (sem wait entre elas)
- Erro IA no meio do pipeline de sync
- Nó de remescla duplicado após saídas paralelas

Lista de faixas completa: [layout-lanes.md](layout-lanes.md) § Anti-padrões.
