# Padrão Copilot — bloco de IA em 3 camadas

> **Documento canônico** para classificação, roteamento e condução conversacional.  
> Referência visual: fluxo **`49331`** (Pagamento e validação de comprovante).  
> Referência Farol a corrigir: **`66309`** [v2] Gerar Preview de Imagem.  
> Hub: [blocks.md](blocks.md) · [SKILL.md](SKILL.md) · Farol: `leona-farol` (pattern-copilot-menu-other)

---

## Ordem de avaliação na plataforma (obrigatório)

```
1. output_conditions[]     → micro-prompts, avaliados PRIMEIRO
2. system_prompt principal → só se nenhuma condicional interna bater (fallback_output_key)
3. condition pós-IA        → cascade contains em ai.response (ramo fallback / keywords)
```

Condicionais **determinísticas** antes do bloco IA (tipo de mídia, campo salvo) ficam **ainda antes** da camada 1.

---

## As 3 camadas

### Camada 0 — Pré-filtro determinístico (opcional, recomendado)

**Bloco:** `condition` (não IA)

| Quando | Exemplo |
|--------|---------|
| Campo já salvo com tipo conhecido | `fotodocliente` type = image |
| Link de rede social | `fotodocliente` contains instagram.com |
| Valor exato no manipulador | `ensaio_estilo` equal "Na Praia" |

**Regra:** IA só recebe o que o filtro **não** resolveu.

```
wait → condition (imagem?) → SIM → produção
                    failure → condition (link social?) → SIM → msg + wait
                                      failure → IA copilot
```

---

### Camada 1 — Condicionais internas (`output_conditions`)

**Onde:** dentro do bloco `ai`, até 10 entradas (≤200 chars cada).

**Para quê:** triagem **rápida** por micro-prompt — sem depender do prompt principal.

| Tipo de micro-prompt | Exemplos de `output_key` |
|---------------------|--------------------------|
| Afirmação / negação | `confirmacao`, `negacao` |
| Dúvida explícita | `duvida` |
| Objeção | `objecao` |
| Mídia no contexto certo | `foto_ok`, `midia_cedo` |
| Padrão detectável na lista | `tema_detectado`, `opcao_menu` |
| Link / documento no texto | `link_detectado`, `documento` |

**Saída da camada 1 → tratamento dedicado** (não precisa ser msg final):

| Destino | Quando |
|---------|--------|
| **Outro bloco IA** | Normalizar valor (ex.: tema exato), extrair dados, segunda análise |
| **Manipulador** | Só se `ai.response` já é valor exato (título, código) |
| **Integração RAG** | `duvida` com pergunta clara |
| **Msg fixa + wait/menu** | Redirecionamento simples |
| **Validador `equal` + tronco** | Campo de negócio após manip |
| **`connection_flow`** | Handoff subfluxo |

**Config mínima:**

```json
{
  "output_conditions": [
    { "prompt": "Lead enviou imagem ou documento com foto", "output_key": "foto_ok" },
    { "prompt": "Lead mencionou nome de tema/cenário da lista do contexto", "output_key": "tema_detectado" },
    { "prompt": "Lead perguntou preço, prazo ou como funciona", "output_key": "duvida" }
  ],
  "fallback_output_key": "padrao",
  "auto_send_response": false,
  "understand_image": true,
  "understand_audio": true
}
```

**Wiring MCP (saída direta por output_key):**

```json
{ "condition_type": "always", "condition_config": { "output_key": "tema_detectado" } }
```

---

### Camada 2 — Prompt principal (`fallback_output_key`)

**Quando roda:** nenhuma `output_condition` bateu.

**Para quê:** análise mais profunda, condução conversacional, casos ambíguos.

**Pode instruir o modelo a responder com token único** em `ai.response`:

| Token | Uso típico |
|-------|------------|
| `#duvida` | Pergunta comercial / processo |
| `#suporte` / `#humano` | Handoff equipe |
| `#avancar` | Lead quer seguir |
| `#pagamento` | Ação de integração (49331) |
| `#mudanca` | Mudar escolha anterior |

**Regras do prompt principal:**

- Tokens são para **roteamento** — a msg ao lead pode ser separada na camada 3
- Pode combinar: texto curto + token (ex.: "Claro! #duvida") **somente** se a cascata pós-IA souber separar
- Preferir **só token** quando a msg ao lead vem de bloco dedicado (RAG, msg fixa)
- **PROIBIDO** listar opções de menu inteiras no texto se `contains` for usar títulos como rota (caso Luzinete)

---

### Camada 3 — Condicionais pós-IA (`condition` + `contains`)

**Quando:** saída do `fallback_output_key` (e ramos que usam keywords em `ai.response`).

**Onde:** blocos `condition` **depois** do bloco IA — cascata visual (referência 49331).

```
IA (fallback → ai.response pode ter #duvida, #suporte, #avancar…)
  → Cond: ai.response contains #duvida
       ├─ SIM → RAG / msg {ai.response} / volta wait
       └─ NÃO → Cond: ai.response contains #suporte
                    ├─ SIM → msg handoff → connection_flow
                    └─ NÃO → Cond: ai.response contains #avancar
                                 ├─ SIM → próximo marco
                                 └─ NÃO → msg fixa convite → wait/menu
```

**Operador:** `contains` em `ai.response` — **nunca** `equal` para tokens (texto pode ter conversa + token).

**Por que existe se já temos `output_conditions`?**

| Camada | Papel |
|--------|-------|
| 1 `output_conditions` | Triagem **rápida**, casos **óbvios**, saídas com tratamento **específico** |
| 2 prompt principal | Casos **ambíguos**, condução, tokens de roteamento |
| 3 `contains` | Desdobrar fallback em **mensagens e ações distintas** por token |

**Não é legado descartável** — é complementar. O erro foi usar **só** camada 1 **ou** **só** camada 3 mal aplicada.

---

## Padrão composto — escolha de tema (Farol)

Quando o lead cita tema em texto livre, **não** resolver tudo no mesmo bloco.

```
output_condition tema_detectado
  → IA #2 — NORMALIZAÇÃO DE TEMA (uma tarefa só)
       system_prompt: lista EXATA de títulos; ai.response = SOMENTE um título
  → manip ensaio_estilo = {ai.response}
  → condition equal (validador nos títulos exatos)
       ├─ SIM → tronco / preview
       └─ NÃO → menu ou msg convite
```

**Lista de temas** deve estar no prompt da IA #2 (ou variável de contexto), não espalhada em frases conversacionais do fallback.

---

## Padrão composto — Preview foto (66309) — implementado

```
wait foto 2315676
  → condition type image/document → produção
  → condition links sociais → msg → wait principal
  → IA #1 — COPILOT FOTO 2315677 (triagem)
       output_conditions:
         foto_ok         → volta condition imagem
         tema_detectado  → msg tranquiliza (usa {ensaio_estilo} já salvo) → wait principal
         duvida          → RAG → msg {resposta} → wait principal
         suporte         → handoff → distribuidor 51200
         padrao          → (prompt principal + tokens)
  → cascade pós-IA (só ramo padrao — 2414926/2414927):
       #suporte/#humano → handoff
       #duvida          → RAG (se não saiu na camada 1)
       default          → msg {ai.response} → wait principal (UM wait)
```

**Regra tema na etapa foto:** reconhecer temas da lista no prompt (para classificar `tema_detectado`), mas **não** alterar `ensaio_estilo` — é só demonstração rápida.

**Anti-padrões Preview:**

- `padrao` → segundo wait duplicando `2315676`
- `opcao_estilo` + manip nesta etapa → grava frase errada em `ensaio_estilo`
- Sem cascata pós-IA no fallback → `ai.response` ignorado ou vazado ao lead

---

## `ai.response` — o que pode ser em cada camada

| Camada / saída | Conteúdo de `ai.response` | Quem envia ao lead |
|----------------|---------------------------|-------------------|
| `output_key` → manip | Valor **exato** (título, código) | Msg dedicada depois do manip |
| `output_key` → RAG | Acolhimento curto (opcional) | `{resposta}` da integração |
| `output_key` → IA #2 | Entrada implícita via variável | — |
| fallback + `#token` | Token ou texto+token | Msg pós-condicional ou RAG |
| fallback conversa | Texto natural | `send_message` com `{ai.response}` |

**Nunca** `auto_send_response: true` em copilot com roteamento — o grafo decide o que enviar.

**Mensagens fixas pós-IA** (não `{ai.response}`): seguir [whatsapp-copy.md](whatsapp-copy.md) — curtas, 1 ideia, tom de conversa. Prompts da IA podem pedir tom humano; blocos `message` downstream devem **materializar** esse tom.

---

## Wiring MCP — resumo

| Origem | condition_config |
|--------|------------------|
| Saída `output_key` da IA | `{ "output_key": "duvida" }` |
| Failure IA | `{ "condition_result": "failure" }` → Erro 49372 |
| Cond pós-IA success | `{ "condition_result": "success" }` |
| Cond pós-IA failure | `{ "condition_result": "failure" }` → próxima cond |

---

## Checklist de implementação

### Bloco IA
- [ ] `output_conditions` com prioridade correta (casos óbvios primeiro)
- [ ] `fallback_output_key` definido (`padrao` ou nome do fluxo)
- [ ] `auto_send_response: false`
- [ ] Multimodal ligado conforme etapa
- [ ] Uma **tarefa** por bloco — normalização em IA separada se preciso

### Pós-IA
- [ ] Cascata `contains` no ramo fallback (se usa `#tokens`)
- [ ] Cada token → tratamento **distinto** (msg, RAG, integração, handoff)
- [ ] **Um** wait principal por etapa de coleta
- [ ] Volta ao mesmo wait após dúvida / padrao / confirmação

### Campos de negócio
- [ ] Manip só com valor exato
- [ ] Validador `equal` em listas fechadas (estilo, pacote)
- [ ] Nunca `contains` em `ai.response` para validar título de menu

### Testes
- [ ] Clique menu (bypass IA)
- [ ] Texto livre válido (tema, foto)
- [ ] Off-menu / ambíguo (fallback + cascata)
- [ ] Dúvida → RAG → volta wait
- [ ] Foto + texto no mesmo buffer

---

## Referências MCP

| Fluxo | ID | O que estudar |
|-------|-----|---------------|
| Pagamento comprovante | `49331` | IA `#mudanca`/`#pagamento` + cascata pós-IA |
| Filtros estilo v2 | `66270` | `output_conditions` + validador equal |
| Preview foto v2 | `66309` | Copilot foto 3 camadas — tema sem manip, cascade, um wait |

---

## Para o agente

1. Ler este doc + `get_flow` antes de mutar bloco IA
2. Não remover cascata pós-IA só porque existe `output_conditions`
3. Não usar `output_conditions` para tudo — tema complexo → IA #2
4. Documentar tokens (`#…`) usados no prompt principal na tabela do fluxo
5. Após mudança: testar os 5 cenários do checklist
