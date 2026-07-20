# Leona Flow — Skill Cursor (`/leona-flow`)

Boas práticas para **criar e editar fluxos WhatsApp** na [Leona](https://leonasolutions.com.br) via **MCP**, para **qualquer negócio**: delivery, e-commerce, cursos, consultoria, serviços, ofertas no WhatsApp, etc.

Skill de **plataforma** (blocos, wiring, layout, variáveis) — não de um nicho específico.

---

## O que cobre

- Escolha de blocos (`wait_response` vs `smart_interval`, IA, menu, condition)
- Variáveis, campos customizados, globals, saves de menu/wait
- Sequência COLETA → PERSIST → DECISÃO → AÇÃO
- PIX + validação de comprovante (esteira completa)
- Remarketing por timeout
- Layout em colunas com espaçamento por altura do bloco (`layout_flow.py`)
- Fluxos modulares e kanban por marcos
- Copy WhatsApp humanizada (sem inventar fatos comerciais)
- Segurança: nunca `delete_flow` → `archive_flow`

---

## Instalação

**macOS / Linux**

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git ~/.cursor/skills/leona-flow
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git "$env:USERPROFILE\.cursor\skills\leona-flow"
```

Atualizar: `cd ~/.cursor/skills/leona-flow && git pull`

### MCP Leona

Configure o servidor no `.cursor/mcp.json`. Opcionais: `LEONA_MCP_URL`, `LEONA_MCP_TOKEN`.

### Regra Cursor (opcional)

```powershell
Copy-Item "$env:USERPROFILE\.cursor\skills\leona-flow\rules\leona-flow-builder.mdc" "$env:USERPROFILE\.cursor\rules\"
```

### Script de layout

Python 3 no PATH. Credenciais via `mcp.json` ou env.

---

## Uso

No chat: `/leona-flow` ou “siga a skill leona-flow”.

| Pedido | Arquivo |
|--------|---------|
| Criar/editar | [builder.md](builder.md) |
| Blocos | [blocks.md](blocks.md) |
| Variáveis / campos | [variables.md](variables.md) |
| Layout | [layout.md](layout.md) |
| PIX / comprovante | [payment-comprovante.md](payment-comprovante.md) |
| Remarketing | [remarketing.md](remarketing.md) |
| IA copilot | [ai-copilot-pattern.md](ai-copilot-pattern.md) |
| Copy | [whatsapp-copy.md](whatsapp-copy.md) |

Índice do agente: [SKILL.md](SKILL.md).

---

## Licença

Uso da comunidade Leona. Contribuições via PR.
