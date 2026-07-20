<p align="center">
  <a href="https://leonaflow.com">
    <strong>LEONA FLOW</strong>
  </a>
</p>

<h1 align="center">Skill de Automação WhatsApp</h1>

<p align="center">
  <strong>Descreva o que você quer. A IA monta o fluxo no Leona.</strong><br />
  Mais simples. Mais rápido. Com a qualidade de quem já opera no WhatsApp de verdade.
</p>

<p align="center">
  <a href="https://leonaflow.com"><strong>Criar conta grátis →</strong></a>
  &nbsp;·&nbsp;
  <a href="https://leonaflow.com">Conhecer o Leona Flow</a>
  &nbsp;·&nbsp;
  <a href="#como-instalar">Como instalar</a>
</p>

---

## O que é isso?

Uma **skill** (pacote de inteligência) para o seu assistente de IA — Cursor, Claude, VS Code e outras ferramentas compatíveis.

Com ela conectada ao **[Leona Flow](https://leonaflow.com)**, você fala em português o que precisa (“funil de vendas”, “pedido com PIX”, “atendimento 24h”) e a IA **cria e organiza o fluxo** direto na sua conta.

Você não precisa virar especialista em blocos.  
Você precisa de **resultado no WhatsApp**.

---

## Por que Leona Flow?

O [Leona Flow](https://leonaflow.com) é a plataforma de automação WhatsApp pensada para quem quer crescer sem travar:

- Resposta rápida, 24 horas por dia  
- IA multimídia no próprio fluxo  
- Conexões flexíveis (do jeito que a sua operação precisa)  
- CRM, times e escala na mesma conta  
- Infraestrutura estável para o dia a dia e para o pico  

**Esta skill** é o atalho: sua ideia → automação pronta no canvas, com boas práticas embutidas.

> Seu instinto. Sua máquina.  
> **[leonaflow.com](https://leonaflow.com)**

---

## O que você ganha

| Antes | Com a skill + Leona |
|-------|---------------------|
| Horas montando fluxo na mão | Minutos descrevendo o que quer |
| Automação que “quebra” no meio | Fluxos pensados para conversa real |
| Depender de alguém técnico o tempo todo | Você + IA + Leona, no seu ritmo |
| Canvas bagunçado | Organização automática do layout |

Serve para **qualquer negócio**: delivery, loja, curso, consultoria, clínica, imobiliária, ofertas no WhatsApp e muito mais.

---

## Como funciona (em 3 passos)

1. **Conta no Leona Flow** — [criar grátis](https://leonaflow.com)  
2. **Instalar a skill** no seu app de IA (abaixo)  
3. **Pedir no chat** — ex.: *“Use a skill leona-flow e monte um atendimento com menu e pagamento”*

A IA usa o MCP do Leona para criar o fluxo na **sua** conta. Depois é só abrir o Leona, dar um refresh no canvas e testar.

---

## Como instalar

### Pré-requisitos

1. Conta em **[leonaflow.com](https://leonaflow.com)**  
2. MCP Leona configurado no seu app de IA (token da conta — veja as configurações / integrações no Leona)  
3. Git e, se for usar o organizador automático de canvas, **Python 3** instalado  

> Dica: no Leona, procure a área de **MCP / integrações** da sua conta para gerar o acesso. Em caso de dúvida, o suporte Leona te orienta.

---

### Cursor (recomendado)

**1.** Abra o PowerShell (Windows) ou o Terminal (Mac/Linux).

**Windows**

```powershell
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git "$env:USERPROFILE\.cursor\skills\leona-flow"
```

**Mac / Linux**

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git ~/.cursor/skills/leona-flow
```

**2.** No Cursor, confirme que o MCP Leona está ativo nas configurações.

**3.** No chat do Agent, digite:

```
/leona-flow
```

Ou escreva: *“Siga a skill leona-flow”* e descreva o fluxo que você quer.

**Atualizar a skill depois:**

```bash
cd ~/.cursor/skills/leona-flow && git pull
```

(Windows: `cd $env:USERPROFILE\.cursor\skills\leona-flow` e depois `git pull`)

---

### Claude (Claude Code / skills)

Coloque a skill na pasta de skills do Claude:

**Mac / Linux**

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git ~/.claude/skills/leona-flow
```

**Windows**

```powershell
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git "$env:USERPROFILE\.claude\skills\leona-flow"
```

Garanta o MCP Leona nas configurações do Claude e peça: *“Use a skill leona-flow para montar meu fluxo.”*

---

### VS Code (agentes / skills compatíveis)

Se o seu fluxo de agente no VS Code usa a pasta padrão de skills do usuário:

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git ~/.agents/skills/leona-flow
```

Ou, só neste projeto:

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git .agents/skills/leona-flow
```

Ative o MCP Leona na extensão/agente que você usa e chame a skill pelo nome **leona-flow**.

---

### OpenCode, Antigravity, Codex e outros

A maioria das ferramentas modernas de agente lê skills nestas pastas (escolha a que o seu app documenta):

| Pasta | Uso comum |
|-------|-----------|
| `~/.cursor/skills/leona-flow` | Cursor |
| `~/.claude/skills/leona-flow` | Claude |
| `~/.codex/skills/leona-flow` | Codex |
| `~/.agents/skills/leona-flow` | Agentes genéricos / VS Code |

Comando genérico (Mac/Linux):

```bash
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git ~/.agents/skills/leona-flow
```

Windows (PowerShell), trocando a pasta conforme o app:

```powershell
git clone https://github.com/ericsoncardosoweb/leona-mcp-skill.git "$env:USERPROFILE\.agents\skills\leona-flow"
```

Depois:

1. Conecte o **MCP Leona** no app  
2. Peça no chat para usar a skill **leona-flow**  
3. Abra o [Leona Flow](https://leonaflow.com) e confira o canvas  

Se o seu app tiver “importar skill do GitHub”, use este repositório:

`https://github.com/ericsoncardosoweb/leona-mcp-skill`

---

## Como pedir (exemplos)

Fale como você falaria com um especialista:

- *“Quero um boas-vindas com menu de 3 opções e transferência para humano.”*  
- *“Monte um checkout com PIX e confirmação de pagamento.”*  
- *“Crie um follow-up se a pessoa não responder em algumas horas.”*  
- *“Organize o layout do fluxo X no canvas.”*  

Quanto mais claro o objetivo, melhor o resultado. A skill cuida da montagem técnica no Leona.

---

## Precisa de ajuda?

- Plataforma e conta: **[leonaflow.com](https://leonaflow.com)**  
- Planos e suporte: pelo site e canais oficiais Leona  
- Melhorias nesta skill: abra um Pull Request neste repositório  

---

<p align="center">
  <strong>Pare de perder lead por falta de automação.</strong><br />
  <a href="https://leonaflow.com">Comece grátis no Leona Flow →</a>
</p>

<p align="center">
  <sub>Skill oficial da comunidade · WhatsApp Automation · <a href="https://leonaflow.com">leonaflow.com</a></sub>
</p>
