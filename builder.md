# Flow Builder — protocolo MCP

> Ler **antes** de criar/editar. Hub: [SKILL.md](SKILL.md).

## Antes de criar (gate)

**Proibido** `create_flow` / `add_flow_node` sem pedido claro e **OK do usuário**.

| Precisa estar claro | Se faltar → perguntar |
|---------------------|------------------------|
| Objetivo | O que o lead faz/recebe no fim? |
| Entrada | Gatilho, campanha, ou `connection_flow` de onde? |
| Coleta | Lead responde? (wait/menu) |
| Saída | Subfluxo, humano, encerramento? |
| Copy / mídias | Texto do usuário ou fluxo de referência na **conta**? |
| CRM | Move kanban? Quais colunas (`list_crms`)? |
| Reuso | Subfluxo existente? (`list_flows`) |
| Silêncio | Rmkt: voltar, avançar ou encerrar? |

Pedido vago (*“monta um funil”*) → **parar e perguntar**.

### Classificar

```
Esteira / vários fluxos / kanban novo / roteador?
  SIM → jornada (Template A) → estratégia → OK → construir
  NÃO → 1 fluxo claro?
         SIM → Template C (fluxograma) → OK → construir
         MÉDIO (ramos) → Template B + fluxograma → OK
```

**Edit pontual** (ex.: ligar 1 handle, ajustar 1 texto): validação breve + confirmar destino → pode construir sem Template A.

---

## Fases MCP (após OK)

```
0  Contexto     get_flow | list_flows se reuso | list_* se dept/crm/pixel/campos
1  Schema       get_node_type 1× por cada node_type novo da sessão
2  Construção   add_flow_node position {x:0,y:0}; ramos: position_near_node_id + auto_connect false
3  Wiring       add_flow_connection em CADA saída de branch
4  Verificar    get_flow → wiring_needed: false; nós ≈ plano
5  Layout       python …/layout_flow.py <FLOW_ID>
6  Entrega      resumo + pedir refresh/fit view
```

Prompts MCP (se existirem no servidor): `flow_mcp_context`, `flow_content_writing_guide`, `connection_management_guide`, `flow_branch_positioning_guide`. Se ausentes → seguir esta skill + `get_node_type`.

**Copy:** [whatsapp-copy.md](whatsapp-copy.md) antes de textos ao lead. Preferir texto do usuário; humanizar tom sem inventar fatos.

---

## Templates

### C — Fluxo simples (padrão)

```markdown
## Fluxo — [nome ou id]

**Pedido:** […]
**Tipo:** criar | editar (id …)
**Entrada / Saída:** […]

### Fluxograma
start → … → wait/menu → …
  ├─ responde → …
  └─ timeout → …

**Nós ~N | Ramos:** sim/não
Aguardando OK para implementar.
```

### B — Subfluxo com blocos

```markdown
## Plano — [nome] (id … | NOVO)

| # | node_type | Função | Saídas |
|---|-----------|--------|--------|
| 1 | message | actions: … | → 2 |
| 2 | wait_response | save → campo | response → 3; timeout → 4 |

Aguardando OK.
```

### A — Esteira (vários fluxos)

Só quando o usuário pede jornada/CRM modular. Tabela: etapa | kanban | subfluxo | rmkt voltar/avançar. Inventário MCP: `list_flows`, `list_crms`, `list_custom_fields`. Ver [kanban-journey.md](kanban-journey.md), [patterns-v2.md](patterns-v2.md).

---

## Wiring rápido

| Bloco | Ligue |
|-------|-------|
| Linear | omitir `connections[]` (auto) |
| `wait_response` | resposta + **timeout** |
| `interactive_menu` | cada opção + **menu_other** + **menu_timeout** |
| `ai` | cada `output_key` + **failure** |
| `condition` | **success** + **failure** |
| `integration` | success + failure |

JSON: [reference.md](reference.md).

---

## Erros MCP — recuperação

| Sintoma | Ação |
|---------|------|
| ID rejeitado (dept/crm/campo) | `list_*` da conta → corrigir → retry |
| action_type inválido | `get_node_type` → só actions listadas |
| Fluxo arquivado | pedir desarquivar na UI ou outro fluxo |
| `wiring_needed: true` | `get_flow` → preencher slots vazios |
| HTTP body quebrado na UI | corrigir **na UI**, um bloco; não massa via MCP |

---

## Segurança

**Nunca** `delete_flow` → `archive_flow`.
