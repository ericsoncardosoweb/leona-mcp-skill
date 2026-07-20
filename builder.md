# Flow Builder — playbook MCP Leona

> Ler **antes** de criar ou editar qualquer fluxo. Hub: [SKILL.md](SKILL.md).

## Definition of Done (não diga “pronto” sem isso)

```
□ Pedido validado + OK do usuário (fluxograma / plano — ver § Antes de criar)
□ Plano aprovado (esteira modular ou ≥15 nós / ramificações)
□ get_flow → wiring_needed: false
□ Contagem de nós/ligações bate com o plano
□ layout_flow.py executado com sucesso (informar N colunas)
□ Usuário orientado: refresh / fit view no canvas Leona
```

**Canvas empilhado durante a criação é normal** — só vira problema se a sessão terminar **sem** rodar o layout (ver [layout.md](layout.md)).

---

## Antes de criar — **não pule** (gate de descoberta)

**Proibido** chamar `create_flow` ou `add_flow_node` enquanto o pedido não estiver claro e **aprovado** pelo usuário.

### Pipeline completo (esteira / vários fluxos / jornada CRM)

```
1. VALIDAR pedido     → pedido vago? perguntar; bem definido? seguir
2. MAPEAR jornada     → com o usuário (Template A ou perguntas guiadas)
3. ESTRATÉGIA         → fluxograma da esteira (subfluxos + connection_flow)
4. PLANO DE CRIAÇÃO   → quais fluxos criar / reutilizar / editar (Template A + B)
5. OK do usuário      → só então FASE 0 MCP e construção
```

### Atalho — fluxo simples e pontual

Quando **todas** forem verdade:

- **Um** fluxo só (ou editar trecho de fluxo existente)
- Objetivo claro: entrada, passos, saída — sem montar esteira nova
- Sem desenhar jornada kanban / biblioteca modular do zero
- Estimativa &lt;15 nós e ramificações leves (ou só ajuste pontual)

Então:

```
1. VALIDAR pedido (breve — confirmar entendimento)
2. FLUXOGRAMA do fluxo único (Template C)
3. OK do usuário → construir
```

**Não** exigir Template A completo — mas **sempre** mostrar fluxograma antes de construir.

---

### Passo 1 — Validar se a solicitação está bem definida

Antes de mapear ou desenhar, o agente **avalia** o pedido. Se faltar informação crítica, **perguntar** — **não assumir**.

| Precisa estar claro | Se faltar → perguntar |
|---------------------|------------------------|
| Objetivo do fluxo | O que o lead deve fazer/receber ao final? |
| Entrada | Gatilho, campanha, ou `connection_flow` de qual fluxo? |
| Coleta vs automático | Lead responde em algum passo? (wait/menu) |
| Saída | Próximo subfluxo, humano, encerramento? |
| Copy e mídias | Textos fornecidos ou fluxo de referência? (**não inventar fatos**) — se reescrever, seguir [whatsapp-copy.md](whatsapp-copy.md) |
| Kanban / etapa | Move card em algum marco? Quais colunas? |
| Reuso | Pode usar subfluxo existente? (`list_flows`) |
| Remarketing | Silêncio → voltar, avançar ou encerrar? |

**Pedido vago** (ex.: *“monta um funil de vendas”*, *“melhora o fluxo”*) → **parar**, fazer perguntas, **não** começar MCP de construção.

**Pedido pontual** (ex.: *“no fluxo 56319, ligue menu_timeout ao pós-venda”*) → validação breve + fluxograma local → OK.

---

### Passo 2 — Classificar: completo vs simples

```
Esteira modular / vários fluxos / kanban / roteador / produtos?
  ├─ SIM → Pipeline completo (mapear → estratégia → plano)
  └─ NÃO → Fluxo simples? (1 fluxo, pedido claro, <15 nós)
            ├─ SIM → Template C (fluxograma) → OK → construir
            └─ NÃO (médio: 1 fluxo ramificado) → Template B + fluxograma → OK
```

---

### Passo 3 — Mapear jornada (pipeline completo)

Conduzir **com o usuário** — não preencher sozinho.

1. **Template A** (tabela etapa ↔ kanban ↔ subfluxo) — preferido para esteiras
2. **Perguntas guiadas** se o usuário não tiver mapa pronto

Agente complementa com MCP: `list_flows`, `list_crms`, `list_custom_fields` (Passo 0 em § Plano).

Referência: [kanban-journey.md](kanban-journey.md), [patterns-v2.md](patterns-v2.md).

---

### Passo 4 — Estratégia (fluxograma da esteira)

Entregável em markdown **antes** do plano de blocos:

```markdown
## Estratégia — fluxograma

[Entrada] → [Roteador] → …
     ↓ timeout              ↓ produto A / B
[Remarketing]          [Subfluxo X]

Legenda: (reutilizar id …) | (criar novo) | (editar …)
```

Usuário vê **quantos fluxos**, **como se conectam**, **o que reutiliza** — ainda sem listar cada `node_type`.

---

### Passo 5 — Plano de criação

Após fluxograma aprovado:

- **Template A** — mapa de jornada (pipeline completo)
- **Template B** — por subfluxo a criar ou editar
- Lista: `create_flow` × N | reutilizar id … | editar fluxo …

Encerrar com: **“Aguardando sua OK para implementar.”**

---

## Fases MCP (ordem fixa — **só após OK do usuário**)

**Antes de cada bloco com copy visível ao lead:** ler [whatsapp-copy.md](whatsapp-copy.md) + prompt MCP `flow_content_writing_guide`.

```
FASE 0 — Contexto
  flow_mcp_context → get_flow → get_node_type por cada node_type novo
  list_flows — existe subfluxo reutilizável? → patterns-v2.md
  Ler sequencing.md se coleta/roteamento/rmkt; kanban-journey.md se marcos CRM

FASE 1 — Plano de blocos (se Template B ainda não detalhou wiring)
  Confirmar handles — já aprovado na fase de descoberta

FASE 2 — Construção (só lógica)
  add_flow_node com position {x:0,y:0} ou position_near_node_id
  NÃO fazer layout manual bloco a bloco

FASE 3 — Wiring
  add_flow_connection para CADA saída de branch (menu, wait, IA, condition)
  get_flow → wiring_needed: false

FASE 4 — Layout (OBRIGATÓRIO)
  python .../scripts/layout_flow.py <FLOW_ID>
  [--col-w 400 --gap 100 se 30+ nós ou muitos ramos]

FASE 5 — Entrega
  Resumo lógico + confirmação de layout + pedir refresh no Leona
```

---

## Sessão MCP (detalhe)

| # | Ação | Por quê |
|---|------|---------|
| 1 | `flow_mcp_context` | Regras atuais do servidor |
| 2 | `get_flow` | Estado + `wiring_needed` |
| 3 | `get_node_type` / `node_<type>` **por bloco** | Schema real |
| 4 | `connection_management_guide` | Wiring de branches |
| 5 | `flow_branch_positioning_guide` | Posição ao criar ramo |
| 6 | `list_*` antes de dept/kanban/pixel/CRM… | IDs estrangeiros rejeitados |
| 7 | Implementar até plano completo | — |
| 8 | `get_flow` → `wiring_needed: false` | Zero nós soltos |
| 9 | [layout.md](layout.md) | Canvas legível |

---

## Plano antes de construir

**Sempre:** validar pedido + fluxograma + **OK do usuário** antes de `add_flow_node` — ver **§ Antes de criar** acima.

**Template A + estratégia:** esteira modular, vários fluxos, kanban/jornada, roteador.

**Template C:** fluxo simples pontual (1 fluxo, pedido claro, &lt;15 nós).

**Template B:** detalhe de blocos por subfluxo (após Template A ou fluxo médio ramificado).

Referências: [patterns-v2.md](patterns-v2.md), [kanban-journey.md](kanban-journey.md), [sequencing.md](sequencing.md).
---

### Passo 0 — Inventário (agente preenche via MCP antes de pedir OK)

```
□ list_flows — subfluxos existentes que podem ser reutilizados
□ list_crms — boards e colunas (crm_id, crm_column_id)
□ list_custom_fields — campo etapa e demais campos da jornada
```

Anote IDs reais da conta no plano — **não inventar** colunas ou fluxos.

---

### Template A — Mapa de jornada (etapa ↔ kanban ↔ subfluxo)

Preencher **com o usuário** (ou confirmar defaults). Uma linha = **um marco** — não cada mensagem.

```markdown
## Plano de jornada — [nome da conta / projeto]

**Objetivo:** [ex.: funil venda + produção modular]
**Boards CRM:** [list_crms → nomes]
**Campo máquina:** `etapa` (tipo: number | text)

### Marcos da jornada

| etapa | Nome do marco | Board CRM | Coluna Kanban | manipulator (campos) | Subfluxo (connection_flow) | Gatilho do marco |
|-------|---------------|-----------|---------------|----------------------|----------------------------|------------------|
| 1 | Boas-vindas | CRM | Novo Lead | etapa=1, fluxo_origem=… | [Entrada v2] (id / novo) | Primeiro contato |
| 2 | Qualificação | CRM | Qualificação | etapa=2, produto=… | [Roteador] (reutilizar id …) | Após menu/IA |
| 3 | Checkout | CRM | Checkout | etapa=3 | [Pagamento] (id …) | Lead aceita comprar |
| 4 | Pago | CRM | Venda Concluída ✓ | etapa=4, value={comprovante.valor} | [Sync pós-pago] (id …) | Comprovante validado |
| 5 | Produção | Controle Produção | Fila / Gerando | etapa=5 | [Produção X] (id …) | Sync concluído |
| 6 | Entregue | Controle Produção | Entregue | etapa=6 | [Pós-venda] (id …) | Mídia entregue |

### Biblioteca de subfluxos

| Papel | Nome do fluxo | ID | Reutilizar? | Entradas (quem chama) |
|-------|---------------|-----|-------------|------------------------|
| Roteador | … | … | sim / criar | Entrada, Atendimento |
| Remarketing checkout | … | … | sim / criar | timeout wait pagamento |
| Erro IA | … | … | sim | failure de qualquer ai |
| … | … | … | … | … |

### Remarketing por marco

| Marco (etapa) | Gatilho | Modo | Comportamento |
|---------------|---------|------|---------------|
| 3 Checkout | wait timeout 2h | Avançar | rmkt onda 1 → novo wait → onda 2 |
| 3 Checkout | comprovante inválido | **Voltar** | msg → mesmo wait comprovante |
| 5 Produção | wait fotos timeout | Avançar | rmkt → smart_interval gate → dept |

### Contrato entre subfluxos (campos mínimos)

| Campo | Setado por | Consumido por |
|-------|------------|---------------|
| fluxo_origem | pai antes de connection_flow | Erro, rmkt |
| etapa | manipulator no marco | condition, filho |
| produto | Roteador / menu | subfluxos de produto |
| … | … | … |

### Diagrama da esteira

```
[Entrada] → [Roteador] → [Apresentação] → [Pagamento] → [Sync] → [Produção] → [Pós-venda]
                ↓ timeouts                    ↓ invalido
           [Atendimento]                  [Remarketing]
```

**Nós totais estimados:** ~N (soma subfluxos) | **Novos fluxos:** N | **Reutilizados:** N

Aguardando sua OK para implementar.
```

**Regras ao preencher:**

- Se linha tem subfluxo existente → marcar **Reutilizar** + ID; não clonar.
- Coluna kanban e `etapa` devem representar o **mesmo marco** ([kanban-journey.md](kanban-journey.md)).
- Remarketing: classificar **Voltar / Avançar / Encerrar** antes de ligar timeouts ([sequencing.md](sequencing.md)).
- Células vazias = perguntar ao usuário — **não inventar** nomes de coluna, etapa ou copy.

---

### Template B — Plano de um subfluxo (blocos + wiring)

Use **por subfluxo** após Template A aprovado (ou sozinho se fluxo isolado &lt;15 nós sem ramos).

```markdown
## Plano — [nome do subfluxo] (id … ou NOVO)

**Papel:** [Entrada | Roteador | Pagamento | …]
**Nós:** N | **Ramos:** sim/não
**Entrada:** connection_flow de […] | gatilho próprio
**Saída:** connection_flow para […]

### Sequência (COLETA → PERSIST → DECISÃO → AÇÃO)

| # | node_type | Função | Saídas a ligar |
|---|-----------|--------|----------------|
| 1 | manipulator | etapa=N, … | always → 2 |
| 2 | message | **actions[]:** texto + mídia + delay + texto (1 nó) | always → 3 |
| 3 | wait_response | save → campo | client-response → 4; timeout → 5 |
| 4 | ai | output: a, b, failure | … |
| … | … | … | … |

### Marcos kanban neste subfluxo

| Nó # | kanban coluna | value |
|------|---------------|-------|
| 1 | … | — |

[diagrama ASCII esquerda → direita]

Aguardando sua OK para implementar.
```

---

### Template C — Fluxo simples (fluxograma + OK)

Para pedido **pontual e bem definido** — substitui Template A. Obrigatório **fluxograma**; tabela de jornada **não**.

```markdown
## Fluxo simples — [nome ou id do fluxo]

**Pedido validado:** [1 frase — o que o usuário pediu]
**Tipo:** criar novo | editar existente (id …)
**Entrada:** [gatilho / start / connection_flow de …]
**Saída:** [fim | connection_flow → …]

### Fluxograma

```
start → manipulator? → message [actions: …] → wait_response
                          ├─ resposta → …
                          └─ timeout → …
```

**Nós estimados:** N | **Ramos:** sim/não
**Reutiliza subfluxo?** não | connection_flow → id …

### Dúvidas em aberto (se houver)

- [ ] …

Aguardando sua OK para implementar.
```

Se após o fluxograma o fluxo crescer (≥15 nós ou esteira), **voltar** ao pipeline completo (Template A + estratégia).

---

### Template mínimo (legado — preferir Template C)

```markdown
## Plano — [nome do fluxo]

**Nós:** N | **Ramos:** sim/não

1. [tipo] — o que faz — saídas: ...
2. ...

[diagrama ASCII esquerda → direita]

Aguardando sua OK para implementar.
```

---

## Wiring — lembretes

- Cadeia **linear**: omitir `connections[]` no `add_flow_node` (auto-connect).
- **Branch**: uma `add_flow_connection` por handle; `auto_connect_to_flow_tail: false` no nó filho.
- `wait_response`: ligar **resposta** + **timeout**.
- `interactive_menu`: cada `menu_option` + **`menu_other`** + **`menu_timeout`**.
- `ai`: cada `output_key` + **failure**.
- `condition`: **success** + **failure**.

JSON e handles: [reference.md](reference.md).

---

## Gatilhos → arquivo certo

| Pedido do usuário | Ler |
|-------------------|-----|
| PIX, comprovante, pagamento | [payment-comprovante.md](payment-comprovante.md) + `get_flow` nos fluxos `49331`, `55593`, `56091` |
| Remarketing / repescagem | [remarketing.md](remarketing.md) |
| Intervalo Inteligente | [blocks.md](blocks.md) § smart_interval |
| canvas bagunçado, colunas | [layout.md](layout.md) |
| Farol Família, APIs, produtos | `leona-farol` |
| Sequência de blocos, interação, rmkt voltar/avançar | **[sequencing.md](sequencing.md)** |
| Fluxos modulares / reutilizar | **[patterns-v2.md](patterns-v2.md)** |
| Kanban + manipulator / jornada | **[kanban-journey.md](kanban-journey.md)** |

---

## Segurança

- **Nunca** `delete_flow` — usar `archive_flow` para desativar.
- Exclusão permanente → usuário faz manual na UI Leona.
