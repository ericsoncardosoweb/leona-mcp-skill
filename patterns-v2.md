# Fluxos modulares — reutilizar, não reinventar

> **Como** montar automações em subfluxos reutilizáveis em vez de monolitos.  
> Sequência de blocos dentro de cada peça: [sequencing.md](sequencing.md).  
> Kanban + campo `etapa`: [kanban-journey.md](kanban-journey.md).

**Regra de ouro:** antes de criar nós novos, **procure fluxo existente** (`list_flows` → `get_flow`). Conectar com `connection_flow` quase sempre vence duplicar blocos.

---

## Monolito vs modular

| Monolito (evitar) | Modular (preferir) |
|-------------------|-------------------|
| 1 fluxo com 40–80 nós | 6–10 subfluxos com 5–15 nós |
| Mesma lógica copiada em 3 entradas | 1 roteador + N `connection_flow` |
| Editar pagamento quebra boas-vindas | Fronteiras isoladas por responsabilidade |
| Remarketing clonado por produto | 1 subfluxo rmkt parametrizado via manipulator |
| Canvas impossível de ler | `layout_flow.py` por subfluxo |

Modularizar por **responsabilidade**, não por mensagem nem por “ficar bonito no canvas”.

---

## Workflow do agente (reuse-first)

```
1. list_flows — existe subfluxo com nome/função parecida?
2. get_flow no candidato — topologia serve? wiring_needed?
3. Se SIM → connection_flow (ou estender 1–2 nós na borda)
4. Se NÃO → create_flow novo subfluxo mínimo
5. manipulator (contrato de contexto) → connection_flow
6. layout_flow.py no fluxo tocado
```

**Não redistribuir:** evite copiar nós de um fluxo para outro “no MCP”. Isso cria divergência. **Estenda na borda** ou **chame subfluxo**.

---

## Catálogo de subfluxos (tipos reutilizáveis)

Desenhe a conta como **biblioteca**. Nomes vêm do plano; os **papéis** são genéricos:

| Papel | Responsabilidade única | Entra via | Sai via |
|-------|------------------------|-----------|---------|
| **Entrada** | Boas-vindas, contexto inicial | Gatilho / campanha | `connection_flow` → Roteador |
| **Roteador** | Classificar intenção/produto | Qualquer entrada | `connection_flow` por rota |
| **Apresentação / Filtros** | Copy + qualificação de 1 linha | Roteador | Pagamento ou rmkt |
| **Pagamento / Comprovante** | PIX + wait + validação | Funil de venda | Sync pós-pago |
| **Sync pós-ação** | Kanban + pixel + CRM | Pagamento validado | Produção |
| **Produção / Entrega** | Coleta → gera → entrega mídia | Sync ou gate | Pós-venda / NPS |
| **Remarketing** | Ondas por silêncio | Timeout de wait/menu | Tronco ou encerrar |
| **Erro IA / Integração** | Contexto + notify + handoff | failure de bloco | department / fim |
| **Atendimento** | Humano, fila, dept | IA / menu / rmkt final | — |
| **Pós-venda** | NPS, upsell, recorrência | Entrega positiva | Gestão resultados |

Um subfluxo = **um papel**. Se mistura dois papéis, divida.

---

## Contrato entre subfluxos (`manipulator` antes do `connection_flow`)

O pai **prepara o contato**; o filho **assume** sem repetir setup.

Campos típicos do contrato (definir no plano da conta):

| Campo | Quem seta | Para quê no filho |
|-------|-----------|-------------------|
| `fluxo_origem` | Pai, antes do `connection_flow` | Debug, rmkt, erro |
| `etapa` | Marco de jornada (numérico) | `condition` de roteamento |
| `etapa_contexto` | Texto curto legível | IA, logs, rmkt |
| `produto` / `produto_fonte` | Roteador ou menu | Subfluxo de produto |
| Variáveis de negócio | Wait / IA upstream | Produção, pagamento |

```
[Pai] … → manipulator (contrato) → connection_flow → [Filho] start → …
```

**Filho não re-seta** o que o pai já definiu — só atualiza no **próximo marco** da jornada ([kanban-journey.md](kanban-journey.md)).

---

## Padrões de reuso

### P1 — Um roteador, várias entradas

```
Boas Vindas v2 ──connection_flow──┐
Atendimento v2 ──connection_flow──┼→ [Roteador] → subfluxos por rota
Remarketing recuperação ──────────┘
```

Duplicar classificação IA em cada entrada = anti-padrão.

### P2 — Estender na borda, não clonar o miolo

Precisa de 1 passo extra antes da produção?

```
✅ Pagamento Sucesso (existente) → novo condition → connection_flow novo
❌ Copiar 22 nós de Pagamento Sucesso para fluxo paralelo
```

### P3 — Remarketing centralizado

Mesma mecânica (wait → timeout → gate → ondas) para vários produtos:

```
timeout → manipulator (etapa_contexto=rmkt checkout) → connection_flow → [Remarketing Checkout]
```

Copy das ondas fica **no subfluxo rmkt** — não em cada funil.

### P4 — Erro centralizado

```
ai | integration (failure) → manipulator (error.*) → connection_flow → [Erro IA]
```

Um fluxo Erro; todos os failures convergem.

### P5 — Subfluxo “sem gatilho próprio”

Processos internos: `can_be_activated: false` — só via `connection_flow`. Evita lead cair no meio da esteira.

### P6 — Pasta / naming convention

Ex.: prefixo `[v2]` para biblioteca modular; pasta “Processos” para sync/erro. Facilita `list_flows` humano e agente.

---

## Quando criar subfluxo novo vs reutilizar

| Situação | Ação |
|----------|------|
| Mesma sequência wait+validação em 2 funis | **Reutilizar** subfluxo |
| Variante só de copy (A/B) | `distributor` **dentro** do subfluxo — não novo fluxo |
| Produto novo com mesmo esqueleto | Novo subfluxo **só** se ramo de coleta/entrega difere |
| Ajuste de 1 mensagem no rmkt | Editar **1** subfluxo rmkt |
| Funil experimental | `create_flow` + `archive_flow` se descartar — nunca `delete_flow` |

---

## Tamanho alvo por subfluxo

| Métrica | Alvo |
|---------|------|
| Nós | 5–15 (até ~20 se sync horizontal) |
| `connection_flow` internos | 0–3 (preferir delegar) |
| Ramificações | Preferir delegar roteador externo |
| Plano + OK usuário | Se ≥15 nós **ou** ramificações densas |

Fluxo passou de ~20 nós **e** tem 2+ responsabilidades → **cortar** em subfluxos.

---

## Topologia da biblioteca (genérica)

```
                    ┌── [Apresentação A] ──► [Pagamento] ──┐
[Entrada] → [Roteador]── [Apresentação B] ──► [Pagamento] ──┼→ [Sync] → [Produção] → [Pós-venda]
                    └── [Atendimento] ──────────────────────┘
                              │
                    timeouts ─┴─► [Remarketing] ──► retorno ao tronco ou encerrar

[Erro IA] ◄── failures espalhados
```

---

## Integração com Kanban e `etapa`

Marcos de jornada = par **`manipulator` (`etapa`) + `kanban`** no mesmo trecho — ver [kanban-journey.md](kanban-journey.md).

Subfluxos **não** movem kanban aleatoriamente — só nos **marcos** definidos na jornada global.

---

## Checklist modular

```
□ list_flows antes de create_flow
□ Subfluxo tem 1 responsabilidade clara
□ manipulator (contrato) imediatamente antes de cada connection_flow
□ Roteador único servindo múltiplas entradas (se aplicável)
□ Remarketing / Erro centralizados — não clonados
□ Nenhuma cópia de blocos entre fluxos “para economizar”
□ Filho não re-seta campos que o pai já definiu
□ layout_flow.py em cada fluxo editado
□ wiring_needed: false em todos os tocados
```

---

## Anti-padrões

- Monolito “porque é mais rápido agora”
- Copiar fluxo inteiro para mudar 1 condição
- `connection_flow` entre cada par de mensagens
- Remarketing duplicado por produto (5× o mesmo wait+rmkt)
- Subfluxo filho refaz boas-vindas / roteador
- Kanban a cada mensagem (polui CRM) — ver kanban-journey
- Criar fluxo novo sem buscar biblioteca existente

---

## Relacionados

| Tema | Arquivo |
|------|---------|
| Ordem e interação de blocos | [sequencing.md](sequencing.md) |
| Kanban + manipulator / etapa | [kanban-journey.md](kanban-journey.md) |
| Remarketing | [remarketing.md](remarketing.md) |
| Builder MCP | [builder.md](builder.md) — **Template A** (mapa jornada) e **Template B** (subfluxo) |
