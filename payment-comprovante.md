# Padrão PIX + validação de comprovante (Leona)

> **Referência viva na conta** — consultar via MCP `get_flow` antes de inventar topologia:
>
> | Fluxo | ID | O que copiar |
> |-------|-----|--------------|
> | Pagamento e validação de comprovante | `49331` | Esteira completa + remarketing + validação IA (**arquivado** — ver fluxos ativos abaixo) |
> | Pagamento e validação - Personalizados | `55593` | RMKT com gate horário + menu pós-timeout + copilot |
> | Receber Pix | `56091` | Apresentação PIX (msg + menu copiar) + wait |
> | Aguardar Comprovante | `64594` | Subfluxo só validação (sem cobrança PIX) |
> | Pagamento Sucesso | `49373` | Destino após comprovante válido |

**Gatilho:** usuário pede PIX, pagamento, comprovante, reconhecer recibo, validar transferência.

**Anti-padrão fatal:** colocar **só** bloco `pix` e parar. PIX na Leona = **esteira inteira** (instrução → espera → tipo → IA → roteamento → remarketing).

> Não inventar textos, chaves PIX, valores ou prompts de validação — copiar do plano do usuário ou dos fluxos de referência acima.

---

## O que “ativar PIX/comprovante” significa

Mínimo obrigatório (7 etapas lógicas):

```
1. Instrução de pagamento     (msg: chave, recebedor, valor — do plano)
2. Facilitar cópia da chave   (menu COPY ou bloco pix — opcional mas padrão Leona)
3. Aguarda comprovante        (wait_response + save_user_data → campo comprovante)
4. Pré-filtro de mídia        (condition type image → document)
5. Extração do recibo         (IA #1: understand_receipt + understand_image)
6. Validação de negócio       (IA #2: chave, recebedor, valor esperado)
7. Roteamento                 (válido → sucesso | inválido → loop | incorreto → humano)
```

Opcional mas presente nos fluxos de referência: **remarketing** na saída **timeout** do wait (nunca `smart_interval` no lugar do wait).

---

## Topologia padrão (49331 / 56091)

```
[setup: manip etapa + kanban Checkout]

→ message (instruções PIX: chave, recebedor, peça comprovante)
→ interactive_menu (botão COPY chave PIX)
     ├─ menu_option → (opcional msg curta) → wait_response
     └─ menu_other ──────────────────────────→ wait_response
          save_user_data: comprovante
          ├─ client-response → validação
          └─ timeout → remarketing (ver abaixo)

VALIDAÇÃO
→ condition: comprovante type = image
     ├─ success ──┐
     └─ failure → condition: comprovante type = document
                      ├─ success ──┤
                      └─ failure → IA copilot (texto fora de contexto) OU msg pedindo imagem

→ IA #1 — extração (#notpaid)
     user_message: {comprovante}
     understand_receipt: true
     understand_image: true
     understand_pdf: true (se conta aceita PDF)
     auto_send_response: false
     system_prompt: "responda apenas #notpaid"  ← do fluxo de referência; ajustar só se plano exigir
     Saídas:
       output_key comprovante → IA #2
       output_key fallback    → msg fallback + notificar humano (integração)

→ IA #2 — validador
     user_message: Valor / Chave PIX / Recebedor / **Data: {comprovante.data}**
     understand_receipt: false
     understand_image: false
     system_prompt: ver seção **Prompt canônico IA #2** abaixo
       • estilo simples: `correto` / `incorreto` / `invalido`
       • estilo planos (49331): `1 foto`…`10 fotos` / `incorreto` / `invalido`
     Saídas via condition (contains, nunca equal):
       ai.response contains invalido  → msg profissional + notify crítico + handoff suporte (ver abaixo)
       ai.response contains incorreto → integração "Pagou errado, valor diferente" + fluxo pós-pagamento
       failure (demais)               → connection_flow → Pagamento Sucesso (49373) ou próximo passo do funil

→ connection_flow failure IA → Erro bloco I.A (49372) com manip de contexto
```

### Bloco `pix` vs mensagem + menu

| Abordagem | Quando | Referência |
|-----------|--------|------------|
| **message + menu COPY** | Padrão Farol/Leona — chave visível + botão copiar | `56091`, `49331` |
| **pix (`send_pix_button`)** | Valor dinâmico `{valor_ticket}` + botão nativo | Funis com manip de valor antes |

**Nunca** um sem o outro sem wait: botão PIX ou menu COPY **sempre** seguidos (direta ou via menu_other) de **`wait_response`** pedindo comprovante.

---

## `wait_response` — comprovante

Configuração típica (validar schema com `get_node_type`):

- `wait_for_response` — timeout longo (ex.: 31 days) ou conforme plano
- `save_user_data` → campo **`comprovante`**
- Wiring **obrigatório:**
  - `client-response` → cadeia de validação
  - `timeout` → remarketing (ou gate horário → remarketing)

**Campo:** usar sempre o mesmo nome (`comprovante`) nas conditions e IAs downstream.

---

## Pré-filtro por tipo (antes da IA)

Cascata curta — **não** pular para IA se lead mandou texto sem imagem:

```
wait → condition image (fieldName: comprovante, fieldOperator: type, fieldValue: image)
         failure → condition document (fieldValue: document)
                       failure → msg "envie print/imagem do comprovante" → back-edge wait
                       success ──┐
         success ────────────────┴→ IA #1
```

Personalizados (`55593`) também trata `type = text` com IA copilot antes de re-pedir comprovante.

---

## Duas IAs — por quê

| | IA #1 | IA #2 |
|---|-------|-------|
| **Função** | OCR / extrair dados do recibo (`#notpaid`, campos `comprovante.*`) | Comparar com recebedor/chave/valor do negócio |
| **Flags** | `understand_receipt: true`, `understand_image: true` | `understand_receipt: false` (usa variáveis extraídas) |
| **Saídas** | `output_key: comprovante` / `fallback` | `condition_result: success` → conditions downstream |
| **Erro** | `fail_reason_variable: ai.fail.reason` | idem → subfluxo erro IA |

**Não fundir** extração + validação em um bloco só — o padrão Leona separa para loops e notificações distintas.

---

## Remarketing (timeout do wait)

Padrão coluna forward — **timeout do `wait_response`**, não intervalo:

```
wait_response (comprovante)
  └─ timeout → [gate horário?] → message rmkt 1
                    → wait_response (mesmo campo comprovante)
                         └─ timeout → message rmkt 2 → wait → …
```

Referência `49331`: até 3 mensagens de remarketing empilhadas antes de voltar ao pedido principal.

Referência `55593`: gate `condition` horário + loop `smart_interval` **só no gate**; depois menu com opções (enviar comprovante / atendente / encerrar).

Cada rmkt = **nova coluna** no layout. Loop inválido → **back-edge** ao `wait_response` inicial.

Detalhes de horário comercial: [SKILL.md](SKILL.md) § Horário de atendimento.

---

## Subfluxo reutilizável

Quando o funil principal já enviou PIX e só precisa validar:

```
connection_flow → Aguardar Comprovante (64594)
```

Esse subfluxo começa em wait (sem msg PIX) e replica validação IA + roteamento.

---

## Checklist — pedido “ativar PIX / comprovante”

Antes de declarar pronto, confirmar **todos**:

- [ ] Message com instruções (chave, recebedor, pedido de comprovante) — **não só bloco pix**
- [ ] Menu COPY ou `pix` + **`wait_response`** com `save_user_data` → `comprovante`
- [ ] Saídas wait: **client-response** + **timeout** (timeout → rmkt se plano tiver)
- [ ] Conditions `type` image / document antes da IA
- [ ] IA #1 com `understand_receipt` + saídas `comprovante` / `fallback`
- [ ] IA #2 validador com variáveis `{comprovante.valor}` etc.
- [ ] Conditions `contains` em `ai.response`: `invalido` → loop wait; `incorreto` → humano
- [ ] `connection_flow` sucesso → fluxo pós-pagamento do plano
- [ ] Failure IA → manip contexto → Erro bloco I.A
- [ ] Integração notificar grupo em fallback/incorreto (se plano tiver)
- [ ] `layout_flow.py` executado (ver [SKILL.md](SKILL.md))

---

## Anti-padrões

- Só bloco `pix` sem `wait_response`
- `smart_interval` em vez de wait para “esperar comprovante”
- Uma IA fazendo OCR + validação + roteamento sem saídas discretas
- `equal` em resposta de IA (usar **`contains`**)
- Timeout do wait sem remarketing quando funil de referência usa rmkt
- Pular pré-filtro image/document e mandar texto direto ao validador
- Inventar chave PIX, valor ou copy de validação

---

## Prompt canônico IA #2 (validador)

Script de manutenção: `.cursor/skills/leona-farol/scripts/_patch_comprovante_validator.js`

**user_message** (todos os fluxos):

```
Valor: {comprovante.valor}
Chave PIX: {comprovante.chave_pix}
Recebedor: {comprovante.nome_recebedor}
Data: {comprovante.data}
```

**Normalização PIX** — aplicar antes de comparar:

1. Remover todos os não-dígitos de `chave_pix`
2. Se 13 dígitos começando com `55`, remover o `55`
3. Válido se 11 dígitos finais = `11974012055` (ex.: `+55 (11) 97401-2055` → válido)

**Recebedor** — match flexível (contains): Raiana, Gabriela, Feliciano, Macedo, G C F, Rajana

**Data** — mesmo dia calendário que hoje (`America/Sao_Paulo`); ontem ou mais antigo → `invalido`

**Respostas:**

| Estilo | Fluxos | Tokens |
|--------|--------|--------|
| Simples | 55593, 63212, 67955 | `correto` / `#correto`, `incorreto`, `invalido` |
| Planos | 49331, 56091, 64594, 55551 | `1 foto`…`10 fotos`, `incorreto`, `invalido` |

Condições downstream continuam com `ai.response contains invalido` / `incorreto`; sucesso = demais respostas.

---

## Path `invalido` — mensagem + notify crítico + handoff

Script de manutenção: `.cursor/skills/leona-farol/scripts/_patch_comprovante_invalid_ux.js`

**Não confundir** com path `incorreto` (valor divergente) — esse mantém notify *"Pagou errado, valor diferente"*.

### Mensagem ao cliente (exata)

```
Olha, {first_name}! Conferi seu comprovante e teve algum problema com as informações.

Se puder validar e enviar tudo certinho, agradeço muito.

Enquanto isso, vou transferir aqui pra equipe de suporte continuar seu atendimento, tá? Dou uma olhada aqui e já volto.
```

### Notify crítico (`notify-group`)

- URL: `https://www.farolfamilia.com.br/api/whatsapp/notify-group`
- Headers: `Authorization: Bearer {g_farol_secret}`, `x-internal-secret: {g_farol_secret}`
- Body JSON: `text` (alerta abaixo) + `groupSlug: comercial`

```
🚨 *ALERTA CRÍTICO — Falha na validação de pagamento*

Erro ao validar comprovante PIX — revisão manual urgente

Cliente: {first_name}
WhatsApp: {phone_number}
Valor: {comprovante.valor}
Chave PIX: {comprovante.chave_pix}
Data: {comprovante.data}
Pacote: {pacote_ensaio}
Resposta validador: {ai.response}
```

### Topologia

```
condition invalido → message (copy acima) → integration (notify crítico) → connection_flow
```

Handoff: **[v2] Suporte Comercial (69261)** ou **Distribuidor (51200)** se o fluxo já usava.

| Fluxo | Msg | Notify inválido (dedicado) | Handoff |
|-------|-----|---------------------------|---------|
| 55593 Personalizados | 1900277 | 2461571 | Distribuidor 51200 |
| 63212 Temáticos | 2188296 | 2461572 | Distribuidor 51200 |
| 67955 Upsell | 2378759 | 2461573 | Distribuidor 51200 |
| 64594 Aguardar | 2241847 | 2461574 | Suporte 69261 |
| 56091 Receber Pix | 1921258 | 2461576 | Suporte 69261 |
| 49331 Comprovante | 1664312 | — | arquivado — desarquivar no Leona |

Notify `incorreto` permanece separado (ex.: 2350960, 2350986, 2378790 em Personalizados/Temáticos/Upsell).
