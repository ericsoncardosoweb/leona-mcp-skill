---
name: leona-flow
description: >-
  Expert WhatsApp flow builder for Leona MCP (any business). Validates request + flowchart OK before building;
  wait_response with save to resposta or persistent fields; reuse labels/fields (no duplicates);
  AI auth from account integration; output_conditions; payment+receipt; remarketing via wait timeout;
  layout_flow.py before done; never delete_flow (archive_flow). Use /leona-flow.
---

# Leona Flow

Skill de **plataforma [Leona Flow](https://leonaflow.com)** — criar e editar automações WhatsApp via MCP para **qualquer negócio** (delivery, e-commerce, cursos, consultoria, serviços, ofertas low-ticket, etc.).

**Não inventar fatos comerciais** (preço, prazo, chave PIX, URL, benefício). **Pode** reescrever tom/estrutura da copy ([whatsapp-copy.md](whatsapp-copy.md)).

---

## Router — leia só o necessário

| Pedido | Arquivo |
|--------|---------|
| Criar / editar fluxo | [builder.md](builder.md) |
| Qual bloco / wait vs intervalo / menu / IA / HTTP | [blocks.md](blocks.md) |
| Variáveis, campos, menu `save_user_data`, globals | [variables.md](variables.md) |
| Ordem COLETA→PERSIST→DECISÃO→AÇÃO | [sequencing.md](sequencing.md) |
| IA 3 camadas (`output_conditions`) | [ai-copilot-pattern.md](ai-copilot-pattern.md) |
| PIX / comprovante / recibo | [payment-comprovante.md](payment-comprovante.md) |
| Remarketing / silêncio | [remarketing.md](remarketing.md) |
| Canvas / espaçamento | [layout.md](layout.md) + `scripts/layout_flow.py` |
| Subfluxos reutilizáveis | [patterns-v2.md](patterns-v2.md) |
| Kanban + etapa | [kanban-journey.md](kanban-journey.md) |
| JSON / handles MCP | [reference.md](reference.md) |
| Copy WhatsApp | [whatsapp-copy.md](whatsapp-copy.md) |

---

## Hard rules (sempre)

1. **Antes de construir:** validar pedido → fluxograma/plano → **OK do usuário** ([builder.md](builder.md)).
2. Lead deve responder → **`wait_response`** (ou menu). **`smart_interval` = pausa do fluxo**, não escuta o lead.
3. **Nunca `delete_flow`.** Desativar: `archive_flow`.
4. IDs de conta (`department`, `crm`, `pixel`, **labels**, **campos**) → sempre `list_*`; **não duplicar** etiqueta/campo — [variables.md](variables.md).
5. Schema → `get_node_type` **1× por `node_type` novo** na sessão (antes do primeiro `add_flow_node` desse tipo).
6. **Não diga pronto** sem: `wiring_needed: false` + **`layout_flow.py` executado**.
7. 1 entrega ao lead (texto+mídia+delay) → **1 `message` com várias actions**, não vários nós.
8. Falha de IA/integração crítica → ligar **failure**; não deixar solto.
9. Wait: salvar em **`resposta`** (buffer) ou campo **persistente** semântico; IA auth = integração da conta ([variables.md](variables.md), [ai-copilot-pattern.md](ai-copilot-pattern.md)).

---

## Definition of Done

```
□ Pedido validado + OK do usuário (fluxograma)
□ get_flow → wiring_needed: false
□ Contagem de nós bate com o plano
□ layout_flow.py rodou (informar N colunas)
□ Usuário orientado: refresh / fit view no Leona
```

**Layout por zonas** (setup | tronco | IA/exceções | rmkt): obrigatório se o fluxo tiver **≥3 ramos** ou **wait+IA+timeout/rmkt**. Fluxo linear curto: só o script basta. Detalhe: [layout.md](layout.md).

---

## Anti-padrões (topo)

- `smart_interval` no lugar de `wait_response`
- Só bloco `pix` sem wait + validação de comprovante
- `add_flow_node` sem OK do usuário
- Inventar IDs, preços, chaves PIX ou campos/etiquetas duplicadas
- `delete_flow`
- Vários `message` seguidos sem wait no meio
- Corrigir `request_body` HTTP em massa via MCP ([reference.md](reference.md))
- Declarar pronto sem `layout_flow.py`
- Wait sem `save_user_data` / inventar `ai_integration_id` sem copiar da conta
