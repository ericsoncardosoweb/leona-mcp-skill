<p align="center">
  <a href="https://leonaflow.com">
    <img src="https://img.shields.io/badge/Leona%20Flow-WhatsApp%20Automation-111827?style=for-the-badge" alt="Leona Flow" />
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/Cursor-Agent%20Skill-0ea5e9?style=for-the-badge" alt="Cursor Skill" />
  &nbsp;
  <img src="https://img.shields.io/badge/MCP-Native-22c55e?style=for-the-badge" alt="MCP" />
</p>

<h1 align="center">Leona Flow — Cursor Skill</h1>

<p align="center">
  <strong>A inteligência operacional para construir automações WhatsApp de elite na plataforma <a href="https://leonaflow.com">Leona Flow</a>.</strong><br />
  Do pedido em linguagem natural ao fluxo vivo no canvas — com padrões de produção, não improvisos.
</p>

<p align="center">
  <a href="https://leonaflow.com"><strong>Conhecer o Leona Flow →</strong></a>
  ·
  <a href="https://leonaflow.com">Criar conta grátis</a>
  ·
  <a href="#instalação">Instalar a skill</a>
</p>

---

## Por que isso existe

O [Leona Flow](https://leonaflow.com) já entrega a máquina: WhatsApp estável, copiloto IA multimídia, conexões híbridas (API própria + Meta Oficial), CRM, PIX, MCP nativo.

Falta o **cérebro de construção** — o playbook que impede o agente de:

- trocar `wait_response` por intervalo e **perder a mensagem do lead**
- soltar um botão PIX e achar que “pagamento está pronto”
- empilhar 40 nós sem layout e entregar um canvas ilegível
- inventar preço, chave PIX ou coluna de CRM que não existe na conta

Esta skill transforma o Cursor + MCP Leona em um **arquiteto de fluxos**: valida o pedido, desenha o plano, monta a lógica, liga todas as saídas e organiza o canvas — para **qualquer negócio**.

| Sem a skill | Com `/leona-flow` |
|-------------|-------------------|
| Fluxo “bonito” que quebra em produção | Topologia testada (coleta → persistência → decisão → ação) |
| Copy robótica de SAC | Mensagens humanas, no ritmo do WhatsApp |
| Canvas empilhado | Layout em colunas com espaçamento por altura do bloco |
| IDs inventados | Sempre `list_*` da **sua** conta |
| Um bloco PIX e fim | Esteira completa: instrução → wait → recibo → validação → rmkt |

---

## O poder do Leona Flow

Plataforma feita para quem escala conversa como canal de venda e operação:

- **Liberdade híbrida** — números próprios e/ou API Oficial Meta, na mesma conta  
- **Copiloto IA multimídia** — texto, imagem, áudio, vídeo e música no fluxo  
- **MCP nativo** — seus agentes (Cursor, Claude, GPT…) editan fluxos de verdade  
- **Operação completa** — CRM/Kanban, departamentos, pixel, PIX, automações 24/7  
- **Infra AWS** — pensada para pico de lançamento, não para demo  

> Seu instinto. Sua máquina.  
> **[leonaflow.com](https://leonaflow.com)**

Esta skill é o **manual vivo** para o agente usar essa máquina sem repetir os erros clássicos de automação WhatsApp.

---

## O que a skill faz (de ponta a ponta)

### 1. Descoberta antes de construir
Valida objetivo, entrada, coleta, saída, copy e CRM. Mostra fluxograma. **Só implementa com o seu OK.**

### 2. Escolha inteligente de blocos
Sabe quando usar `wait_response`, `smart_interval`, menu 2.0, condition, manipulator, IA com `output_conditions`, HTTP, PIX, kanban, `connection_flow`.

### 3. Memória do fluxo
Domina variáveis de sistema, campos customizados, globals, `save_user_data` do menu/wait, `{ai.response}` e dados de recibo (`understand_receipt`).

### 4. Dinheiro e silêncio
Esteira de **PIX + comprovante** (não só o botão) e **remarketing** por timeout — o lead sempre pode responder antes da onda.

### 5. Canvas profissional
`layout_flow.py` organiza colunas e empilha irmãos pela **altura real do bloco** — sem sobreposição. Fluxos ramificados ganham zonas (setup · tronco · IA · rmkt).

### 6. Segurança operacional
**Nunca** `delete_flow`. Desativa com `archive_flow`. IDs estrangeiros são rejeitados — a skill força inventário da conta.

---

## Para quem é

Qualquer operação que vende ou atende no WhatsApp:

Pizzaria · restaurante · e-commerce · consultoria · cursos · info-produtos · clínicas · salões · imobiliárias · ofertas low-ticket · X1 · remarketing · pós-venda · suporte

Um playbook de **plataforma**. Zero lock-in de nicho.

---

## Instalação

### 1. Skill no Cursor

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

### 2. Conta + MCP Leona

1. Crie ou acesse sua conta em **[leonaflow.com](https://leonaflow.com)**  
2. Configure o servidor MCP Leona no `.cursor/mcp.json`  
3. Opcional: `LEONA_MCP_URL` e `LEONA_MCP_TOKEN` no ambiente  

### 3. Regra Cursor (recomendado)

```powershell
Copy-Item "$env:USERPROFILE\.cursor\skills\leona-flow\rules\leona-flow-builder.mdc" "$env:USERPROFILE\.cursor\rules\"
```

```bash
cp ~/.cursor/skills/leona-flow/rules/leona-flow-builder.mdc ~/.cursor/rules/
```

### 4. Python 3

Necessário para o script de layout (`scripts/layout_flow.py`).

---

## Como usar no chat

```
/leona-flow
```

Ou: *“Siga a skill leona-flow e monte este funil.”*

O agente deve: validar → fluxograma → **seu OK** → MCP → wiring completo → `layout_flow.py` → pedir refresh no canvas Leona.

### Mapa rápido

| Você pede | A skill lê |
|-----------|------------|
| Criar / editar fluxo | [builder.md](builder.md) |
| Qual bloco usar | [blocks.md](blocks.md) |
| Variáveis e campos | [variables.md](variables.md) |
| Ordem inteligente | [sequencing.md](sequencing.md) |
| IA / texto livre | [ai-copilot-pattern.md](ai-copilot-pattern.md) |
| PIX / comprovante | [payment-comprovante.md](payment-comprovante.md) |
| Remarketing | [remarketing.md](remarketing.md) |
| Canvas bagunçado | [layout.md](layout.md) |
| Subfluxos / esteira | [patterns-v2.md](patterns-v2.md) |
| Kanban + etapa | [kanban-journey.md](kanban-journey.md) |
| Copy WhatsApp | [whatsapp-copy.md](whatsapp-copy.md) |
| JSON / handles | [reference.md](reference.md) |

Índice do agente: **[SKILL.md](SKILL.md)**

---

## Definition of Done

Um fluxo só está “pronto” quando:

1. Pedido validado + plano/fluxograma aprovado  
2. `get_flow` → `wiring_needed: false`  
3. Contagem de nós alinhada ao plano  
4. **`layout_flow.py` executado**  
5. Você deu refresh / fit view no Leona  

```powershell
python "$env:USERPROFILE\.cursor\skills\leona-flow\scripts\layout_flow.py" <FLOW_ID>
```

---

## Regras de ouro (não negociáveis)

| Regra | Por quê |
|-------|---------|
| Lead responde → `wait_response` | `smart_interval` **não escuta** o lead |
| Não inventar fatos comerciais | Preço, PIX, URL e benefício vêm do seu plano |
| IDs só da conta atual | `list_departments`, `list_crms`, `list_custom_fields`… |
| Nunca `delete_flow` | Use `archive_flow` |
| 1 entrega = 1 `message` multi-action | Evita canvas inchado e colunas fantasma |

---

## Estrutura do repositório

```
leona-mcp-skill/
├── SKILL.md                 # Router + hard rules
├── builder.md               # Protocolo MCP
├── blocks.md                # Escolha de blocos
├── variables.md             # Campos, globals, saves
├── sequencing.md            # Interação entre blocos
├── ai-copilot-pattern.md    # IA em 3 camadas
├── payment-comprovante.md   # PIX + recibo
├── remarketing.md           # Silêncio / ondas
├── layout.md                # Canvas + zonas
├── patterns-v2.md           # Modularização
├── kanban-journey.md        # CRM por marcos
├── reference.md             # Receitas JSON
├── whatsapp-copy.md         # Tom conversacional
├── scripts/layout_flow.py   # Layout automático
└── rules/                   # Regra Cursor opcional
```

---

## Comece a escalar

Automação WhatsApp não é “mais um chatbot”. É a diferença entre lead frio e conversão 24/7.

**Plataforma:** [leonaflow.com](https://leonaflow.com)  
**Skill:** este repositório + `/leona-flow` no Cursor  

<p align="center">
  <a href="https://leonaflow.com"><strong>Criar conta no Leona Flow →</strong></a>
</p>

---

## Contribuição

Melhorias de padrão de plataforma (blocos, wiring, layout, copy) são bem-vindas via Pull Request.  
Mantenha a skill **conta-agnóstica** — sem IDs de um cliente específico.

---

<p align="center">
  Mantida para a comunidade <a href="https://leonaflow.com">Leona Flow</a>.<br />
  <sub>Cursor Agent Skill · MCP · WhatsApp Automation</sub>
</p>
