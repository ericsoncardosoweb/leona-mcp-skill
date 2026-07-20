# Referência — blocos e wiring Leona

> Confirme schema com `get_node_type`/`node_<type>` antes de escrever.
> Exemplos são **mecânica de bloco**, não conteúdo de negócio.

## Wait vs Intervalo — regra fundamental

### O que cada bloco faz (plataforma Leona)

| Bloco | `node_type` | Escuta o lead? | Continua quando |
|-------|-------------|----------------|-----------------|
| Aguarda Resposta | `wait_response` | **Sim** — qualquer mensagem na janela | Lead responde **ou** timeout |
| Intervalo Inteligente | `smart_interval` | **Não** | Intervalo termina |
| Pausa curta em sequência | `delay_between_messages` | Não | Após segundos no bloco `message` |

### Mensagens do lead durante a pausa

```
wait_response (timeout 2h):
  Lead manda "oi" após 10 min → fluxo SEGUE (saída resposta) ✅

smart_interval (2h):
  Lead manda "oi" após 10 min → fluxo IGNORA para este passo;
  só continua após 2h completos ❌ (para capturar essa msg precisava wait)
```

### Mapa de decisão

| Objetivo | Bloco correto | Bloco errado |
|----------|---------------|--------------|
| Esperar nome, foto, comprovante | `wait_response` | `smart_interval` |
| Lead pode responder antes do timeout | `wait_response` | `smart_interval` |
| Remarketing se **não** responde em X | `wait_response` (timeout X) | `smart_interval` (X) |
| Re-checar horário comercial em 20 min | `smart_interval` → `condition` | `wait_response` |
| Pausa entre duas mensagens (≤1 min) | `delay_between_messages` | `smart_interval` |
| Menu com opções | `interactive_menu` | — |

### Remarketing — topologia

```
CORRETO:
  msg → wait_response (timeout: 2h)
        ├─ responde → tronco (lead tomou iniciativa)
        └─ timeout → [opcional: gate horário] → msg rmkt

ERRADO:
  msg → smart_interval (2h) → msg rmkt
        (lead que manda no meio não é capturado)
```

### Gate de horário — por que `smart_interval` é ok no loop

No loop `condition` (fora do horário) → `smart_interval` 20min → `condition`:

- Objetivo é **esperar o relógio**, não o lead
- Mensagens do lead nesse intervalo **não** devem disparar o remarketing fora da lógica do wait anterior
- O remarketing em si já foi disparado pelo **timeout** do `wait_response` upstream

Se o lead ainda pode **interromper** o rmkt com uma resposta, isso deve estar no `wait_response` **antes** do gate — não no `smart_interval` do loop.

### Anti-padrões

- `smart_interval` após pergunta esperando resposta
- Substituir `wait_response` por intervalo “porque é o mesmo tempo”
- Remarketing só com intervalo, sem saída de resposta no wait
- `smart_interval` para “dar tempo do lead pensar” quando ele já pode mandar msg

---

Útil em `menu_other` ou após `wait_response`:

```json
{
  "ruleType": "any",
  "conditions": [
    { "category": "custom_field", "fieldName": "tag",
      "fieldOperator": "type", "fieldValue": "image" },
    { "category": "custom_field", "fieldName": "tag",
      "fieldOperator": "type", "fieldValue": "document" }
  ]
}
```

Troque `fieldName` pelo campo que o wait/menu salvou.

## Menu 2.0 — `save_user_data`

Salvar opção escolhida no campo do plano (ex.: `categoria`, `plano`, `estilo`):

- Opção válida (`menu_option`) → usar campo salvo direto no roteamento
- Não duplicar manipulador copiando tag→campo se o menu já salvou

Saídas a wirear sempre: cada `menu_option`, `menu_other`, `menu_timeout`.

## Bloco `ai` — condicionais inteligentes (camada 1)

Ver padrão completo: [ai-copilot-pattern.md](ai-copilot-pattern.md).

```json
{
  "output_conditions": [
    { "prompt": "Lead enviou imagem ou áudio fora do momento esperado", "output_key": "midia_cedo" },
    { "prompt": "Lead tem dúvida sobre preço, prazo ou como funciona", "output_key": "duvida" },
    { "prompt": "Lead expressa objeção ou quer adiar", "output_key": "objecao" },
    { "prompt": "Lead quer avançar: sim, ok, vamos, bora", "output_key": "avancar" }
  ],
  "fallback_output_key": "padrao",
  "understand_image": true,
  "understand_audio": true,
  "auto_send_response": false,
  "fail_reason_variable": "error.log"
}
```

Prioridade: condicionais avaliadas **antes** do system prompt principal. Fallback pode instruir `#duvida`, `#suporte` → roteamento na **camada 3** (condicionais `contains` em `ai.response` após o bloco IA). Referência: fluxo `49331`.

## Bloco `ai` — autenticação

Integração cadastrada (preferir):

```json
{
  "api_key_source": "integration",
  "ai_integration_id": <id da conta>
}
```

Remover `api_key` do config. Validar ID com `get_flow` em fluxo que já usa IA corretamente.

Fallback sem integração:

```json
{
  "api_key_source": "manual",
  "api_key": "{variavel_global}"
}
```

## Wiring MCP — saídas

| Origem | Conexão |
|--------|---------|
| `ai` saída por intenção | `{ "condition_type": "always", "condition_config": { "output_key": "duvida" } }` |
| `ai` failure | `{ "condition_result": "failure" }` |
| `condition` success | `{ "condition_result": "success" }` |
| `condition` failure | `{ "condition_result": "failure" }` |
| `wait_response` timeout | handle timeout / `no_response` (costuma ser back-edge) |
| `interactive_menu` | `menu_option` por opção; `menu_other`; `menu_timeout` |
| `distributor` | `a1`, `a2`, … uma conexão por saída |

Cadeia linear sem ramificação: pode omitir `connections[]` no MCP (sequencial automático).
Branches: **uma** `add_flow_connection` por handle.

## Reconhecimento de comprovante

> **Padrão de qualidade Leona (esteira completa):** [payment-comprovante.md](payment-comprovante.md) — fluxos MCP `49331`, `55593`, `56091`, `64594`.

### Opção A — Condição por tipo (pré-IA)

1. `wait_response` → campo `comprovante`
2. Cascata: `condition` type **image** → failure → type **document**
3. `success` (image ou doc) → IA #1; `failure` → msg + back-edge ao wait

### Opção B — Duas IAs (padrão conta)

1. **IA #1** — `understand_receipt: true`, `user_message: {comprovante}`, prompt `#notpaid` → saída `output_key: comprovante`
2. **IA #2** — validador com `{comprovante.valor}`, `{comprovante.chave_pix}`, `{comprovante.nome_recebedor}`
3. Conditions `contains` em `ai.response`: `invalido` / `incorreto` / sucesso → `connection_flow`

Ver wiring completo e remarketing em [payment-comprovante.md](payment-comprovante.md).

## Horário de atendimento (gate + loop)

Garante que remarketing, follow-up ou outra ação **só execute dentro da janela comercial**.

### Fluxo lógico

```
[trigger: wait timeout | menu_timeout | smart_interval rmkt…]
  → condition (evaluate_condition)
       ruleType: all
       ├─ Hora depois {inicio}    ex. 08:00  ("Hora depois 8h")
       └─ Hora antes {fim}        ex. 23:00  ("Hora antes 23h")
       ├─ success → message / ação
       └─ failure → smart_interval ({intervalo}) → reentra condition
```

### Parâmetros (sempre confirmar com o usuário)

| Parâmetro | UI Leona | Notas |
|-----------|----------|-------|
| Início | Hora depois | Inclusivo — após esse horário |
| Fim | Hora antes | Exclusivo na prática — antes desse horário |
| Intervalo de re-tentativa | `smart_interval` | 15–30 min típico; **não escuta lead** — só re-checa horário |
| Timeout do wait anterior | `wait_response` | Ex.: 2h sem resposta → inicia gate; lead pode responder antes |

Antes de criar via MCP: `get_node_type` (`condition`) para operadores de hora exatos na API.

### Exemplo conceitual MCP (`evaluate_condition`)

Estrutura ilustrativa — **validar** com `get_node_type` antes de escrever:

```json
{
  "action_type": "evaluate_condition",
  "config": {
    "ruleType": "all",
    "conditions": [
      { "category": "time", "fieldOperator": "after_hour", "fieldValue": "8" },
      { "category": "time", "fieldOperator": "before_hour", "fieldValue": "23" }
    ]
  }
}
```

Nomes de `category` / `fieldOperator` podem diferir na API — copiar de fluxo existente na conta ou do schema MCP.

### `smart_interval` no loop

```json
{
  "action_type": "smart_interval",
  "config": {
    "delay_minutes": 20
  }
}
```

Confirmar campo exato (`delay_minutes` vs `minutes`) com `get_node_type` (`smart_interval`).

### Wiring MCP

| De | Para | Condição |
|----|------|----------|
| wait timeout | condition horário | handle timeout / `no_response` |
| condition | message | `condition_result: success` |
| condition | smart_interval | `condition_result: failure` |
| smart_interval | condition horário | saída principal (loop) |

### Layout

- Tratar aresta `smart_interval → condition` como **back-edge**
- Não contar o loop como colunas forward extras
- Mensagem de remarketing na coluna **após** `success` do gate

### Anti-padrões

- Timeout do wait → message direto (ignora horário comercial)
- Loop sem `smart_interval` (condition sozinho não “espera” até abrir)
- **`smart_interval` no lugar de `wait_response` para remarketing ou coleta**
- Horário inventado sem confirmação do usuário
- `ruleType: any` com uma regra só (use `all` para janela início+fim)
- Intervalo de re-tentativa muito curto (&lt; 10 min) — custo e spam de execução

---

## Remarketing (coluna)

```
[mensagem(s) rmkt] → [menu | wait] ── responde ──►
        ├─ success → entrega/obrigado
        └─ failure/timeout → próximo rmkt (forward) ou volta (back-edge)
```

## Delays — três mecanismos distintos

| Situação | Bloco | Escuta lead? |
|----------|-------|--------------|
| ≤ 1 min entre mensagens no mesmo bloco | `delay_between_messages` (`message`) | Não |
| Esperar resposta do lead (com timeout) | `wait_response` | **Sim** |
| Pausa > 1 min sem capturar mensagens | `smart_interval` | **Não** |

### Intervalo Inteligente — `schedule_type`

| UI | MCP | Campos |
|----|-----|--------|
| Intervalo | `time` | `interval_value` + `interval_unit` (`minutes` \| `hours` \| `days`) |
| Data | `date` | `scheduled_date` (datetime futuro) |
| Horários | `weekly` | `weekly_schedule`: `monday`…`sunday` → `enabled`, `start_time`, `end_time` (HH:MM) |

Modo **Horários**: fluxo espera entrar em faixa ativa; se já estiver dentro, continua na hora. UI: importar **Usar horários de funcionamento** da conexão. Detalhes: [blocks.md](blocks.md) § smart_interval. Remarketing: [remarketing.md](remarketing.md).

Não converter delay curto em `smart_interval`. Não converter espera de lead em `smart_interval`.

## Integração HTTP

- Mapear campos da resposta **no próprio bloco** (`response_fields` + `response_mapping`)
- **Sempre** conectar success **e** failure ao próximo passo
- Erro: `{response.erro}` ou campo equivalente do schema

### `request_body` — STRING obrigatória (crítico)

O editor Leona trata `request_body` como **texto** (`.trim()`). Gravar como **objeto** via MCP **quebra o editor** — tela preta ao abrir o bloco.

| Onde | Formato |
|------|---------|
| Tipo no MCP | **string** (`json.dumps({...})`) — nunca objeto |
| UI Leona | JSON estrito com aspas duplas |
| Runtime Farol | Aceita loose **e** JSON estrito (`parseLooseLeonaBody`) |

### Corpo — JSON estrito na UI

O Leona **valida** o campo *Corpo da requisição* como JSON. Formato loose (estilo JavaScript) **não passa** na UI.

| Tipo | Formato correto | Errado |
|------|-----------------|--------|
| Chave | `"whatsapp"` | `whatsapp` |
| String / variável | `"{phone_number}"` | `{phone_number}` |
| Número | `1440` | `"1440"` (ok, mas preferir número) |
| Header | `"Content-Type": "application/json"` | sem aspas nas chaves |

**Exemplo válido** (`POST` com variáveis Leona):

```json
{
  "whatsapp": "{phone_number}",
  "client_name": "{full_name}",
  "lookback_minutes": 1440,
  "limit": 60,
  "max_media": 8
}
```

**Headers** (aba *Header da requisição* — mesmo padrão):

```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {g_farol_secret}",
  "x-internal-secret": "{g_farol_secret}"
}
```

Via MCP: `request_body` = **string** (`json.dumps(...)` em Python). O backend Leona **não preserva** aspas literais no editor — costuma gravar formato loose (`whatsapp:`) ou escape `\u0022`, ambos **inválidos na UI**.

**Nunca** passar `request_body` como objeto JSON no MCP — quebra o editor.

### Aspas retas — o que a UI exige (crítico)

O validador do Leona exige o caractere `"` (aspas duplas retas, U+0022) **literal** no textarea — não aceita:

| Gravado no campo | Válido na UI? |
|------------------|---------------|
| `"whatsapp": "{phone_number}"` | ✅ sim |
| `whatsapp: {phone_number}` (loose) | ❌ não |
| `\u0022whatsapp\u0022: \u0022{phone_number}\u0022` | ❌ não — escape Unicode **não** conta como aspas |

**Única forma garantida de corrigir corpo inválido:** abrir o bloco na **UI Leona** → aba *Corpo da requisição* → Ctrl+A → colar JSON com aspas retas → Salvar.

### Proibição para agentes (MCP)

- **Nunca** aplicar correção de `request_body` **em massa** via `update_flow_node` (destrói aspas ou grava `\u0022`).
- **Nunca** usar `encode` com `\u0022` pensando que o editor aceita — o textarea mostra o escape literal.
- Ao revisar integrações: **um bloco por vez**, validar na UI com o usuário, ou só gerar JSON paste-ready sem chamar MCP no corpo.

**Anti-padrão:**

```json
{
  whatsapp: {phone_number},
  client_name: {full_name}
}
```

**Anti-padrão MCP (invalida a UI):**

```json
{
  \u0022whatsapp\u0022: \u0022{phone_number}\u0022
}
```

### Mapear resposta — não confundir os nomes

No bloco `integration`, aba **Mapear resposta**:

| MCP / UI | Significado |
|----------|-------------|
| `response_fields[].name` | Rótulo da extração (coluna **Nome do campo**) |
| `response_fields[].path` | JSON path na resposta HTTP (coluna **Caminho**) |
| `response_mapping` | `{ "nome_extração": "campo_customizado_contato" }` |

**Regra:** o bloco seguinte usa `{campo_customizado_contato}` — valor de `response_mapping`, **não** inventar outro nome.

Exemplo correto (RAG Farol `body.answer`):

```json
{
  "response_fields": [{ "name": "resposta", "path": "body.answer" }],
  "response_mapping": { "resposta": "resposta" }
}
```

Mensagem seguinte: `{resposta}`.

**Anti-padrão:** `name: "rag_answer"` no mapeamento + `{resposta}` na mensagem — nomes diferentes confundem no canvas e quebram se `response_mapping` estiver errado ou ausente.

**Farol Família:** padrão RAG completo → `leona-farol` § Integração Farol.

## Erro de bloco — manipulador de contexto

Campos típicos antes de `connection_flow` ao subfluxo de erro:

| Campo | Exemplo |
|-------|---------|
| `fluxo_origem` | Nome do fluxo atual |
| `etapa_contexto` | Descrição curta da etapa |
| `error.block_type` | `ai` ou `integration` |
| `error.log` | Via `fail_reason_variable` no bloco IA |

## Nomenclatura MCP (`node_type`)

| UI / conceito | `node_type` |
|---------------|-------------|
| Mensagem | `message` |
| Menu botões | `interactive_menu` |
| Aguardar | `wait_response` |
| Condição | `condition` |
| IA | `ai` |
| Manipulador | `manipulator` |
| HTTP | `integration` |
| Subfluxo | `connection_flow` |
| Distribuidor | `distributor` |
| Tags | `tags` |
| Intervalo | `smart_interval` |

Variáveis comuns: `{phone_number}`, `{full_name}`, `{first_name}`, `{tag}`.

## Esteira v2 (roteador, sync, produção)

Diagramas de **sequência de blocos** e remarketing: **[sequencing.md](sequencing.md)**.  
Modularização (subfluxos): [patterns-v2.md](patterns-v2.md).

Estudar estrutura via `get_flow` — observar ordem de blocos, não copiar tags/produtos de conta exemplo.

## Anti-padrões

- **`smart_interval` em vez de `wait_response` para esperar lead**
- Remarketing via intervalo longo sem wait com timeout
- Coluna nova por mensagem sem wait
- Loop/timeout como forward no layout
- Duplicar nó de remescla
- Perder `option_id` ao editar menu
- `equal` em resposta de IA
- Cascata de conditions pós-IA
- Layout antes de wiring completo
- Auto-layout MCP só em fluxos 30+ nós
- **Vários blocos `message` encadeados** para mesma sequência de envio — usar **1 nó** com múltiplas actions ([blocks.md](blocks.md) § message)
- Pixel no semáforo **e** no sync — evento duplicado (ver [patterns-v2.md](patterns-v2.md) § semáforo)
- Vários `approved_sale` sem remescla em um nó `tags` comum
- HTTP sync só no success — failure deve seguir pipeline ou convergir no mesmo nó
- Hub roteador sem ligar failure da IA e `menu_timeout` do menu
