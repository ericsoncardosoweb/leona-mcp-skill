---
name: leona-flow
description: >-
  Boas práticas de automação WhatsApp no Leona (MCP). OBRIGATÓRIO: validar pedido + fluxograma/plano aprovado antes de construir;
  copy WhatsApp humanizada → whatsapp-copy.md; layout_flow.py + faixas (layout-lanes.md) antes de pronto;
  wait_response para lead; delete_flow. PIX → payment-comprovante.md. Remarketing → remarketing.md.
  Farol → leona-farol. Use /leona-flow.
---

# Leona Flow

Skill de **plataforma Leona** — blocos, wiring, layout e padrões de automação.

| `leona-flow` | `leona-farol` |
|--------------|---------------|
| Plataforma, builder, layout, blocos | Negócio Farol, APIs, esteira v2 |

> **Farol Família:** skill companion `leona-farol` (instalação separada)

> **Regra de ouro:** NÃO inventar **fatos** (preços, prazos, URLs, benefícios não aprovados). **Pode** (e deve) escrever/reescrever copy seguindo [whatsapp-copy.md](whatsapp-copy.md).

---

## Por onde começar

| Arquivo | Quando ler |
|---------|------------|
| **[whatsapp-copy.md](whatsapp-copy.md)** | **Antes de escrever** mensagens, menus, waits, RMKT — tom, formatação WA, conversão |
| **[builder.md](builder.md)** | Criar/editar fluxo — fases, Definition of Done, ordem MCP |
| **[layout.md](layout.md)** | Canvas — `layout_flow.py` + checklist |
| **[layout-lanes.md](layout-lanes.md)** | **Padrão de faixas** — setup, tronco, IA hub, produção, RMKT (fluxos complexos) |
| **[ai-copilot-pattern.md](ai-copilot-pattern.md)** | **Bloco IA 3 camadas** — `output_conditions`, fallback `#tokens`, cond pós-IA |
| **[blocks.md](blocks.md)** | Qual bloco usar — wait vs intervalo, IA, menu, HTTP |
| **[sequencing.md](sequencing.md)** | **Ordem inteligente** — interação entre blocos, remarketing voltar/avançar |
| **[remarketing.md](remarketing.md)** | Repescagem — wait + timeout, gate horário, ondas |
| **[payment-comprovante.md](payment-comprovante.md)** | PIX, pagamento, comprovante, recibo |
| **[patterns-v2.md](patterns-v2.md)** | **Fluxos modulares** — reutilizar subfluxos, biblioteca, contratos |
| **[kanban-journey.md](kanban-journey.md)** | **Kanban + manipulator** — etapas da jornada, campo `etapa`, marcos |
| **[reference.md](reference.md)** | JSON, wiring MCP, receitas |

Instalação e mapa completo: **[README.md](README.md)** (compartilhar com a comunidade).

---

## Definition of Done (resumo)

Não encerre a sessão sem:

1. **Pedido validado** + fluxograma/plano **aprovado** pelo usuário ([builder.md](builder.md) § Antes de criar)
2. `wiring_needed: false`
3. **`layout_flow.py` executado** (esboço)
4. **Faixas aplicadas** ([layout-lanes.md](layout-lanes.md)) — obrigatório se IA copilot + produção + RMKT

Fluxo simples (&lt; 25 nós, linear): só `layout_flow.py` pode bastar.  
Fluxo complexo (ex.: Preview `66309`): **faixas** após o script.  
Esteira modular: mapear jornada → estratégia → plano (Template A).

Canvas empilhado **durante** a criação é normal. Problema é terminar **sem** layout legível por zona.

---

## CRÍTICO — Nunca excluir fluxos

**Jamais** `delete_flow`. Para desativar: **`archive_flow`**. Exclusão permanente → usuário faz na UI Leona (segurança).

---

## Gatilhos rápidos

| Pedido | Ação |
|--------|------|
| PIX / comprovante | [payment-comprovante.md](payment-comprovante.md) + `get_flow` em `49331`, `55593`, `56091` |
| Lead deve responder | **`wait_response`** — ver [blocks.md](blocks.md) |
| Remarketing / repescagem | [remarketing.md](remarketing.md) |
| Intervalo Inteligente (Horários na UI) | [blocks.md](blocks.md) § smart_interval |
| Canvas bagunçado | [layout.md](layout.md) + script + [layout-lanes.md](layout-lanes.md) |
| Bloco IA / menu_other / texto livre | **[ai-copilot-pattern.md](ai-copilot-pattern.md)** |
| Criar/editar fluxo | [builder.md](builder.md) § **Antes de criar** → depois MCP |
| Fluxo simples pontual | Template C (fluxograma + OK) |
| Esteira / jornada CRM | Mapear jornada → estratégia → Template A |
| Sequência / interação de blocos | **[sequencing.md](sequencing.md)** |
| Fluxos modulares / reutilizar subfluxos | **[patterns-v2.md](patterns-v2.md)** |
| Kanban + manipulator / jornada | **[kanban-journey.md](kanban-journey.md)** |
| Plano etapa ↔ kanban ↔ subfluxo | [builder.md](builder.md) § Template A |
| Copy robótica / formatação WA | **[whatsapp-copy.md](whatsapp-copy.md)** — ler antes de `message` / menu / wait |

**PIX ≠ só bloco `pix`:** instrução → wait comprovante → validação (duas IAs) → remarketing no timeout.

---

## Checklist final

### Segurança
- [ ] Sem `delete_flow`; desativar com `archive_flow`

### Builder + layout
- [ ] [builder.md](builder.md) — pedido validado; fluxograma/plano **aprovado** antes de construir
- [ ] Esteira: jornada mapeada **com usuário** → estratégia → plano de fluxos
- [ ] [patterns-v2.md](patterns-v2.md) — subfluxo reutilizado, não monolito clonado
- [ ] [kanban-journey.md](kanban-journey.md) — marco = manipulator `etapa` + kanban
- [ ] [layout.md](layout.md) — **`layout_flow.py` rodou**
- [ ] [layout-lanes.md](layout-lanes.md) — faixas (setup vertical, tronco, IA hub, produção, RMKT) se fluxo complexo

### Remarketing (se aplicável)
- [ ] [remarketing.md](remarketing.md) — timeout no wait, não intervalo longo

### PIX (se aplicável)
- [ ] [payment-comprovante.md](payment-comprovante.md)

### Copy WhatsApp
- [ ] [whatsapp-copy.md](whatsapp-copy.md) — tom humano, `\n` entre ideias, emojis moderados, 1 CTA por bloco
- [ ] Estrutura alinhada ao objetivo do nó (AIDA, PAS, lembrete RMKT, etc.)
- [ ] Lido em voz alta — não soa bot/SAC

### Blocos
- [ ] [blocks.md](blocks.md) — wait vs intervalo; menu_other; failure ligado
- [ ] [sequencing.md](sequencing.md) — COLETA→PERSIST→DECISÃO→AÇÃO; rmkt voltar/avançar
- [ ] [ai-copilot-pattern.md](ai-copilot-pattern.md) — se fluxo tem IA + texto livre
- [ ] Integração HTTP: corpo com **aspas retas** `"` na UI; **sem** correção em massa de `request_body` via MCP ([reference.md](reference.md) § Integração HTTP)

---

## Anti-padrões (topo)

- Declarar pronto **sem** `layout_flow.py` **e** sem faixas em fluxo complexo
- Confiar **só** no script em fluxo com IA hub + produção + RMKT ([layout-lanes.md](layout-lanes.md))
- **`add_flow_node` sem validar pedido** ou sem OK do usuário (fluxograma/plano)
- Assumir jornada kanban/copy quando usuário não definiu
- `smart_interval` para esperar resposta do lead
- Só bloco `pix` sem wait + validação
- `delete_flow`
- Inventar preço, prazo, URL ou benefício não aprovado
- Copy robótica ("Informamos", "Prezado", wall of text, emoji spam) — ver [whatsapp-copy.md](whatsapp-copy.md)
- Monolito ou clonar fluxo inteiro em vez de `connection_flow`
- Kanban a cada mensagem sem marco de jornada
- **Vários blocos `message` seguidos** para intro + mídia + texto — **1 bloco, várias actions**
- **`update_flow_node` em massa no `request_body`** de integrações HTTP — grava `\u0022` ou loose; corrigir **só na UI**, um bloco por vez ([reference.md](reference.md) § Integração HTTP)

Lista completa: [blocks.md](blocks.md) e [reference.md](reference.md).
