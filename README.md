# Leona Flow — Skill Cursor (`/leona-flow`)

Boas práticas para **criar e editar fluxos WhatsApp** na plataforma [Leona](https://leonasolutions.com.br) usando o **MCP Leona** no Cursor.

Genérica para qualquer conta Leona. Para **Farol Família** (APIs, produtos, esteira v2), use também a skill companion `leona-farol` (instalação separada).

---

## O que esta skill cobre

- Escolha correta de blocos (`wait_response` vs `smart_interval`, IA vs condição, menu 2.0)
- **Sequenciamento inteligente** — ordem COLETA→PERSIST→DECISÃO→AÇÃO, remarketing voltar/avançar
- **Fluxos modulares** — biblioteca de subfluxos reutilizáveis (`connection_flow`)
- **Kanban + manipulator** — marcos de jornada com campo `etapa`
- Wiring completo (todas as saídas ligadas)
- Layout do canvas em colunas (`layout_flow.py`)
- Remarketing e gate de horário comercial
- Esteira PIX + validação de comprovante (padrão Leona)
- Padrões v2 — esteira modular, roteador, sync pós-pago, produção mídia
- Segurança: nunca excluir fluxo via agente (`archive_flow` para desativar)
- **Copy WhatsApp** — tom conversacional, formatação nativa, estruturas de conversão ([whatsapp-copy.md](whatsapp-copy.md))

**Regra de ouro:** não inventar **fatos comerciais** (preço, prazo, URL). A skill define *como* montar e *como escrever*; conteúdo factual vem do plano aprovado.

---

## Instalação

### 1. Skill no Cursor (recomendado)

Clone este repositório direto na pasta de skills do Cursor:

**macOS / Linux**

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git ~/.cursor/skills/leona-flow
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git "$env:USERPROFILE\.cursor\skills\leona-flow"
```

Atualizar depois:

```bash
cd ~/.cursor/skills/leona-flow && git pull
```

### 2. MCP Leona

Configure o servidor MCP Leona no `.cursor/mcp.json` da sua conta. Variáveis opcionais:

- `LEONA_MCP_URL`
- `LEONA_MCP_TOKEN`

### 3. Regra do Cursor (opcional)

Copie a regra deste repo para o Cursor:

```powershell
Copy-Item "$env:USERPROFILE\.cursor\skills\leona-flow\rules\leona-flow-builder.mdc" "$env:USERPROFILE\.cursor\rules\"
```

macOS / Linux:

```bash
cp ~/.cursor/skills/leona-flow/rules/leona-flow-builder.mdc ~/.cursor/rules/
```

Lembra o agente de rodar layout, usar `wait_response` e seguir os padrões da skill.

### 4. Script de layout

Requisito: **Python 3** no PATH. O script usa credenciais do `mcp.json` ou das variáveis de ambiente acima.

---

## Como usar no chat

Anexe a skill na conversa:

```
/leona-flow
```

Ou peça explicitamente: *“Siga a skill leona-flow para montar este fluxo.”*

### Gatilhos úteis

| Você pede | O agente deve ler |
|-----------|-------------------|
| Criar/editar fluxo | [builder.md](builder.md) — **validar → fluxograma → OK** → construir |
| Fluxo simples pontual | [builder.md](builder.md) Template C |
| Esteira modular / jornada | Mapear jornada → estratégia → Template A |
| Canvas bagunçado | [layout.md](layout.md) → script + [layout-lanes.md](layout-lanes.md) |
| Remarketing / repescagem | [remarketing.md](remarketing.md) |
| PIX, comprovante, pagamento | [payment-comprovante.md](payment-comprovante.md) |
| Qual bloco usar | [blocks.md](blocks.md) |
| Sequência e interação entre blocos | **[sequencing.md](sequencing.md)** |
| Fluxos modulares / reutilizar | **[patterns-v2.md](patterns-v2.md)** |
| Kanban + manipulator / jornada | **[kanban-journey.md](kanban-journey.md)** |
| Copy / mensagens robóticas | **[whatsapp-copy.md](whatsapp-copy.md)** |
| JSON / wiring MCP | [reference.md](reference.md) |

---

## Mapa dos arquivos

| Arquivo | Conteúdo |
|---------|----------|
| [SKILL.md](SKILL.md) | Índice principal e Definition of Done |
| [whatsapp-copy.md](whatsapp-copy.md) | **Copy WhatsApp** — tom, formatação, emojis, frameworks de conversão por objetivo |
| [builder.md](builder.md) | Fases de construção, ordem MCP, **Template A/B** (jornada + subfluxo) |
| [layout.md](layout.md) | Colunas, `layout_flow.py`, checklist |
| [layout-lanes.md](layout-lanes.md) | **Padrão de faixas** — setup, tronco, IA hub, produção, RMKT |
| [ai-copilot-pattern.md](ai-copilot-pattern.md) | **Bloco IA 3 camadas** — output_conditions + fallback + pós-IA |
| [blocks.md](blocks.md) | Blocos — wait vs intervalo, IA, menu, HTTP, **Intervalo Inteligente (3 modos)** |
| [sequencing.md](sequencing.md) | **Ordem inteligente** — leis de interação, receitas, remarketing voltar/avançar |
| [patterns-v2.md](patterns-v2.md) | **Modular** — biblioteca, reuse-first, contratos entre subfluxos |
| [kanban-journey.md](kanban-journey.md) | **Kanban + etapa** — desenho de colunas, marcos, manipulator |
| [remarketing.md](remarketing.md) | Repescagem — wait + timeout, gate horário, ondas |
| [payment-comprovante.md](payment-comprovante.md) | PIX + comprovante — esteira completa (não só bloco pix) |
| [reference.md](reference.md) | Receitas JSON e handles MCP |
| [scripts/layout_flow.py](scripts/layout_flow.py) | Organiza o canvas após wiring completo |
| [rules/leona-flow-builder.mdc](rules/leona-flow-builder.mdc) | Regra Cursor (opcional) |

---

## Definition of Done

O agente **não deve dizer “pronto”** sem:

1. Pedido validado + plano/fluxograma **aprovado** pelo usuário
2. `get_flow` → `wiring_needed: false`
3. **`layout_flow.py` executado** (esboço)
4. **Faixas aplicadas** ([layout-lanes.md](layout-lanes.md)) — fluxos com IA hub + produção + RMKT

Canvas empilhado **durante** a criação é normal. Script + faixas resolvem no final.

```powershell
python "$env:USERPROFILE\.cursor\skills\leona-flow\scripts\layout_flow.py" <FLOW_ID>
python ...\layout_flow.py <FLOW_ID> --col-w 400 --gap 100
```

---

## Erros comuns (evitar)

| Erro | Correto |
|------|---------|
| Só bloco `pix` sem wait + validação | Esteira em [payment-comprovante.md](payment-comprovante.md) |
| `smart_interval` para “esperar o lead” | **`wait_response`** |
| Terminar sem rodar layout | `layout_flow.py` + faixas ([layout-lanes.md](layout-lanes.md)) em fluxo complexo |
| Vários blocos `message` para mesma sequência | **1 bloco** com actions (texto, mídia, delay) |
| `delete_flow` | **`archive_flow`** (exclusão só manual na UI) |
| Inventar textos, chaves PIX, valores | Usar copy do plano ou fluxos de referência |

---

## Intervalo Inteligente — 3 modos (UI Leona)

| Aba | Uso |
|-----|-----|
| **Intervalo** | Pausa fixa (minutos, horas, dias) |
| **Data** | Continuar em data/hora específica |
| **Horários** | Esperar janela comercial da semana (ideal antes de remarketing) |

Detalhes: [blocks.md](blocks.md) § `smart_interval`.

---

## Licença e contribuição

Skill mantida para uso da comunidade Leona. Sugestões e melhorias: abra um PR neste repositório.

**Farol Família:** domínio de negócio em skill companion `leona-farol` (instalação separada) — use as duas juntas quando for conta Farol.
