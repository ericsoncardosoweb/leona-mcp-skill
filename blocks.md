# Blocos Leona — escolha e uso

> Hub: [SKILL.md](SKILL.md). **Ordem e interação entre blocos:** [sequencing.md](sequencing.md). JSON e handles: [reference.md](reference.md).

## Hierarquia do fluxo (boas práticas)

Padrão recomendado:

```
Coleta (wait / menu) → Processamento (ia / condition / manipulator) → Ação (msg / integração) → Roteamento (condition / connection_flow)
```

- **Coleta:** 1 pergunta por mensagem; máx. ~3 envios sem wait entre eles
- **Processamento:** 1 bloco `ai` = 1 tarefa
- **Ação:** não pular manipulador quando precisa persistir campo antes de condição
- **Roteamento:** `connection_flow` para subfluxos reutilizáveis

UX conversacional: sempre caminho de saída (timeout → follow-up ou humano); `typing_delay_seconds` 2–3 em textos longos.

---

## Escolha de bloco: IA vs condição

| Situação | Bloco |
|----------|-------|
| **Esperar resposta / iniciativa do lead** | **`wait_response`** (nunca `smart_interval`) |
| Pausa longa **sem** capturar mensagens | `smart_interval` |
| Classificar texto livre / intenção / N categorias | **1 `ai`** → manipulador com valor exato |
| Campo **já salvo** no manipulador | `condition` com `contains` |
| Resposta de IA em condição downstream | **`contains`**, nunca `equal` |
| Dúvida, objeção, mídia fora de contexto no funil | **`output_conditions`** (camada 1) + cascata pós-IA se fallback usa `#tokens` |
| 3–4 rotas fixas com destinos distintos | Cascata **curta** de `condition` |
| 10+ categorias | **1 `ai`** triagem + **IA #2** normalização se preciso |
| Só tipo de arquivo (imagem/PDF) | `condition` com `fieldOperator: type` **antes** da IA |
| Fallback ambíguo com `#duvida`, `#suporte`… | Prompt principal (camada 2) → **`contains`** em `ai.response` (camada 3) |

**Padrão completo:** [ai-copilot-pattern.md](ai-copilot-pattern.md) — 3 camadas (pré-filtro → `output_conditions` → prompt fallback → condicionais pós-IA).

**Anti-padrão:** um bloco IA faz triagem + normalização + conversa + roteamento; segundo wait duplicado; gravar campo de negócio com frase conversacional.

---

## CRÍTICO — `wait_response` vs `smart_interval`

**Erro comum que quebra fluxos em produção:** usar **Intervalo Inteligente** quando o objetivo é **esperar o lead**. São blocos opostos.

### Comportamento na plataforma

| | **`wait_response`** (Aguarda Resposta) | **`smart_interval`** (Intervalo Inteligente) |
|---|----------------------------------------|-----------------------------------------------|
| **Função** | Esperar **input do lead** | **Pausar** o fluxo por um tempo |
| **Lead manda mensagem durante** | **Captura** — fluxo segue pela saída de resposta | **Ignora** — mensagem não entra neste bloco |
| **Fluxo continua quando** | Lead responde **ou** timeout | **Só** quando o intervalo termina |
| **Iniciativa do lead** | ✅ Resposta antecipada funciona | ❌ Resposta antecipada não acelera o fluxo |
| **UI Leona** | “Aguardar pela resposta do cliente” | “Espera de X minutos” |

> **Intervalo Inteligente = delay no fluxo, não escuta o lead.**  
> Se o lead pode tomar iniciativa e mandar algo, o bloco **tem que ser** `wait_response`.

### Árvore de decisão (sempre aplicar)

```
Precisa capturar resposta / iniciativa do lead?
  ├─ SIM → wait_response (ou interactive_menu)
  │         └─ timeout configurado se “sem resposta em X”
  └─ NÃO → é só pausa no fluxo?
            ├─ ≤ 1 min entre msgs no mesmo bloco → delay_between_messages (message)
            ├─ > 1 min, lead NÃO deve interromper → smart_interval
            └─ agendamento / data específica → smart_interval (confirmar schema)
```

### Quando usar cada um

**`wait_response`**

- Pergunta aberta (“como posso ajudar?”, “qual seu nome?”)
- Pedido de foto, comprovante, documento
- Remarketing **com** chance de resposta antes do timeout (“ficou alguma dúvida?”)
- Qualquer etapa onde resposta **antecipada** deve ser processada
- Após menu/wait: lead pode voltar e falar — use wait, não intervalo

**`smart_interval`**

- Re-tentar **condição de horário** (loop com `condition` — lead não precisa falar)
- Aguardar abertura comercial **sem** ouvir mensagens nesse intervalo
- Pausa longa **antes** de ação automática (sem expectativa de resposta no meio)
- Remarketing **somente** se o plano diz “disparar após X min **sem** considerar mensagens no intervalo” (raro — confirmar)

**Nunca `smart_interval` para:**

- “Esperar 2h e ver se o lead responde” → use `wait_response` timeout 2h
- “Dar tempo pro lead mandar foto” → `wait_response`
- Substituir `wait_response` “porque é mais simples”

### Remarketing correto vs errado

**✅ Correto** (lead pode responder antes do rmkt):

```
message (pergunta) → wait_response (timeout: 2h)
  ├─ lead responde → processa resposta (tronco principal)
  └─ timeout (2h sem resposta) → [gate horário?] → message rmkt
```

**❌ Errado** (mensagens do lead no intervalo são perdidas para este passo):

```
message (pergunta) → smart_interval (2h) → message rmkt
```

**Gate de horário** (smart_interval aqui é **correto** — não é espera de lead):

```
wait_response timeout → condition horário
  ├─ success → message rmkt
  └─ failure → smart_interval 20min → volta condition   ← pausa técnica, não escuta lead
```

### Wiring

| Bloco | Saídas a ligar |
|-------|----------------|
| `wait_response` | **Resposta** (principal) + **timeout** / `no_response` |
| `smart_interval` | **Uma** saída — só após o tempo |

### Layout

- `wait_response` = **nova coluna** (ponto de resposta do lead)
- `smart_interval` em loop de horário = **back-edge** com `condition`
- `smart_interval` entre coleta e processamento de resposta = **erro de design** (coluna fantasma sem captura)

Detalhes e cenários: [reference.md](reference.md) § Wait vs Intervalo.

---

## Blocos — uso correto

### `message` — **um bloco, várias actions** (CRÍTICO)

> **Copy:** tom, formatação WhatsApp e estruturas de conversão → [whatsapp-copy.md](whatsapp-copy.md). Ler **antes** de definir `message_text`.

Na UI Leona, o bloco **Mensagem** é um **container**: texto, áudio, vídeo, imagem, arquivo, contato, sticker e pausas rodam **em sequência dentro do mesmo nó**, na ordem das actions (`order` 1, 2, 3…).

```
┌─ Mensagem (1 nó) ─────────────────────────────┐
│  📝 Texto introdutório                        │
│  🔗 Áudio (URL): {musica}                     │
│  ⏱ Delay: 0–10s                              │
│  📝 Texto pós-entrega                         │
└───────────────────────────────────────────────┘
         │
         ▼
    [menu | wait | próximo bloco lógico]
```

**Anti-padrão comum do agente:** criar `message → message → message` encadeados para uma **mesma entrega** ao lead. Isso infla o canvas, gera colunas fantasma e dificulta layout.

#### Regra de ouro

| Situação | O que fazer |
|----------|-------------|
| Vários textos/mídias **sem** resposta do lead no meio | **1 bloco `message`** com várias `actions[]` |
| Lead **precisa responder** entre envios | `wait_response` ou `interactive_menu` **entre** blocos |
| Ramo diferente no meio (condition, IA) | Blocos **separados** — lógica exige |
| Pausa **> ~1 min** entre envios | `smart_interval` ou `wait_response` — não só delay interno |
| Entrega típica (intro + mídia + dica) | **Sempre 1 bloco** |

#### Tipos de action no mesmo nó

| `action_type` | Uso | Config principal |
|---------------|-----|------------------|
| `send_message` | Texto e/ou mídia inline | `message_text`, `typing_delay_seconds`, opcional `media_url` + `media_type` |
| `send_multi_media` | Áudio/vídeo/imagem dedicado | `media_source: url`, `media_url`, `media_type`, `audio_forward` |
| `delay_between_messages` | Pausa **entre** items do bloco | `delay_seconds`; range: `delay_min_seconds` / `delay_max_seconds` |
| `send_file` | PDF/documento | `file_name`, `file_url` |
| `send_contact` / `send_sticker` | Contato / figurinha | ver `get_node_type(message)` |

**Dois tipos de “delay” — não confundir:**

| | `typing_delay_seconds` (dentro de `send_message`) | `delay_between_messages` |
|---|-----------------------------------------------------|--------------------------|
| Efeito | “Digitando…” antes **daquela** msg | Pausa **entre** actions do bloco |
| Onde | config do `send_message` | action separada |

#### Exemplo MCP — entrega mídia (padrão do print)

```json
{
  "node_type": "message",
  "actions": [
    {
      "action_type": "send_message",
      "order": 1,
      "config": {
        "message_text": "Agora o momento chegou 🎵🎶\n\nOuçam juntos…",
        "typing_delay_seconds": 3
      }
    },
    {
      "action_type": "send_multi_media",
      "order": 2,
      "config": {
        "media_source": "url",
        "media_type": "audio",
        "media_url": "{musica}",
        "audio_forward": true,
        "typing_delay_seconds": 6
      }
    },
    {
      "action_type": "delay_between_messages",
      "order": 3,
      "config": {
        "delay_seconds": 0,
        "delay_min_seconds": 0,
        "delay_max_seconds": 10
      }
    },
    {
      "action_type": "send_message",
      "order": 4,
      "config": {
        "message_text": "Ah, uma dica importante: ouça na velocidade normal…",
        "typing_delay_seconds": 3
      }
    }
  ]
}
```

Via MCP: passar **todas** as actions no mesmo `add_flow_node` ou `update_flow_node` — **não** um nó por linha de copy.

#### Árvore de decisão

```
Vai enviar N conteúdos seguidos ao lead?
  ├─ Lead NÃO responde no meio
  │     ├─ Sem branch no meio → 1 message com N actions
  │     └─ > ~10 actions → dividir em 2 blocos message (raro)
  └─ Lead DEVE responder no meio
        → message (actions) → wait_response | menu → message (actions) …
```

#### Ordem recomendada dentro do bloco

```
texto → mídia → documento → delay_between_messages → texto de fechamento
```

- Delay ≤1 min entre items: `delay_between_messages` **dentro** do bloco
- Mídia: URL HTTPS pública; variáveis `{musica}`, `{customer.photo}`, etc.
- Antes de criar: `get_node_type` (`message`) + prompt `node_message`

#### Quando **dois** blocos `message` fazem sentido

- Entre eles: `wait_response`, menu, condition, IA, kanban, integration
- Copy de **etapas diferentes** da jornada (apresentação vs entrega vs rmkt onda 2)
- Subfluxos distintos se conectam no meio

#### Layout

Vários `message` seguidos **sem wait** = colunas extras desnecessárias no canvas. **1 bloco multi-action = 1 coluna** ([layout.md](layout.md)).

MCP anti-pattern oficial: *"Do not split a single user-facing message into many message nodes unless flow logic requires it."*

### `wait_response` (Aguarda Resposta)

**Use quando o lead pode (ou deve) responder — inclusive antes do timeout.**

- Salvar resposta em campo customizado (`save_user_data` ou equivalente do schema)
- **Timeout obrigatório** em waits críticos (ex.: “sem resposta em 2h” → saída timeout)
- Resposta antecipada → saída principal **imediatamente** (não espera o timeout)
- Timeout que repete etapa = **back-edge** no layout
- Wiring: **sempre** duas saídas — resposta principal + timeout/`no_response`

**Não confundir:** timeout de 2h no `wait_response` ≠ `smart_interval` de 2h. O wait **escuta** o lead durante as 2h; o intervalo **não**.

### `smart_interval` (Intervalo Inteligente)

**Pausa no fluxo sem capturar mensagens do lead.** Uma saída: continua **só** quando a condição de tempo for satisfeita.

**Teste mental:** “Se o lead manda ‘oi’ no meio, preciso processar?” → **sim** = use `wait_response`, **não** este bloco.

**Não substituir:** `wait_response`, `delay_between_messages` (≤1 min no bloco message).

Antes de criar via MCP: `get_node_type` (`smart_interval`).

---

#### Três modos na UI (= `schedule_type` no MCP)

| Aba na UI | `schedule_type` | Quando usar |
|-----------|-----------------|-------------|
| **Intervalo** | `time` | Pausa fixa: X minutos, horas ou dias |
| **Data** | `date` | Continuar em data/hora específica (futuro) |
| **Horários** | `weekly` | Esperar entrar em faixa ativa da semana (comercial) |

---

#### Modo **Intervalo** (`time`)

Pausa duração fixa — ex.: re-checar condição em 20 min, pausa entre etapas automáticas.

```json
{
  "action_type": "smart_interval",
  "config": {
    "schedule_type": "time",
    "interval_value": 20,
    "interval_unit": "minutes"
  }
}
```

`interval_unit`: `minutes` | `hours` | `days`

**Uso típico em remarketing:** loop legado `condition` (fora do horário) → intervalo 20 min → volta ao `condition`. Ver [remarketing.md](remarketing.md).

---

#### Modo **Data** (`date`)

Fluxo **retoma na data/hora** configurada (deve ser futuro).

```json
{
  "action_type": "smart_interval",
  "config": {
    "schedule_type": "date",
    "scheduled_date": "2026-07-15T09:00:00"
  }
}
```

Confirmar formato exato com `get_node_type` / editor Leona.

---

#### Modo **Horários** (`weekly`) — aba da imagem

> *“O fluxo aguarda até entrar em um dos horários ativos. Se já estiver dentro da faixa, continua na hora.”*

Use para **gate de horário comercial** antes de remarketing, follow-up ou handoff — **sem** loop condition + intervalo curto.

**Na UI (Editar Intervalo Inteligente):**

1. Selecionar aba **Horários**
2. **Conexão** (opcional): escolher WhatsApp/conexão → **Usar horários de funcionamento** importa faixas cadastradas na conexão
3. **Dias da semana:** ativar toggle por dia (Seg–Dom) — **obrigatório ao menos 1 dia ativo**
4. Por dia ativo: definir faixa `início`–`fim` (ex.: 08:00–23:00)
5. **Mesclar faixas:** duas faixas no mesmo dia (ex.: 09:00–12:00 e 18:00–21:00) viram uma contínua 09:00–21:00
6. **Salvar**

**Via MCP** (exemplo — ajustar dias/horas conforme plano):

```json
{
  "action_type": "smart_interval",
  "config": {
    "schedule_type": "weekly",
    "weekly_schedule": {
      "monday":    { "enabled": true,  "start_time": "08:00", "end_time": "23:00" },
      "tuesday":   { "enabled": true,  "start_time": "08:00", "end_time": "23:00" },
      "wednesday": { "enabled": true,  "start_time": "08:00", "end_time": "23:00" },
      "thursday":  { "enabled": true,  "start_time": "08:00", "end_time": "23:00" },
      "friday":    { "enabled": true,  "start_time": "08:00", "end_time": "23:00" },
      "saturday":  { "enabled": false, "start_time": "08:00", "end_time": "18:00" },
      "sunday":    { "enabled": false, "start_time": "08:00", "end_time": "18:00" }
    }
  }
}
```

Chaves dos dias: `monday` … `sunday` (confirmar schema MCP).

**Topologia recomendada (remarketing):**

```
wait_response timeout → smart_interval (weekly / Horários) → message rmkt → …
```

**Não inventar** horários — perguntar ao usuário ou importar da conexão na UI.

Importação **Usar horários de funcionamento** pode ser **só na UI**; via MCP montar `weekly_schedule` manualmente ou copiar de fluxo existente com `get_flow`.

---

#### Onde **não** usar Intervalo Inteligente

| Errado | Certo |
|--------|-------|
| “Esperar 2h se o lead responde” | `wait_response` timeout 2h |
| “Esperar comprovante/foto” | `wait_response` |
| Remarketing com intervalo longo **sem** wait upstream | `wait_response` + timeout → rmkt |

Detalhes remarketing: [remarketing.md](remarketing.md).

---

#### Wiring e layout

- **Uma** saída (`always`) → próximo nó
- Loop com `condition` = **back-edge** ([layout.md](layout.md))
- Modo Horários antes de msg rmkt = coluna **forward** após o intervalo


### `condition` — horário de atendimento

Operadores de **hora** na UI Leona (confirmar schema com `get_node_type`):

- **Hora depois** — horário atual ≥ início (ex.: 8h → após 08:00)
- **Hora antes** — horário atual &lt; fim (ex.: 23h → antes de 23:00)
- Combinar com `ruleType: all` (E) para janela `início ≤ agora &lt; fim`

`success` = dentro do horário → executar ação. `failure` = fora → `smart_interval` → reentra no mesmo `condition`.

### `interactive_menu` (Menu 2.0)

- **`save_user_data`** no bloco — salvar opção no campo definido pelo plano
- Saídas obrigatórias: `menu_option`, **`menu_other`**, **`menu_timeout`**
- `menu_option` → destino direto se campo já salvo (evitar manip redundante)
- List (4–10 opções) vs button (2–3); `option_id` semântico (`opt_*`)
- Ao renomear título do botão: **manter `option_id`** (quebra conexões se mudar)

### `menu_other` (padrão genérico)

Lead digitou fora dos botões:

```
menu_other
  → condition OU: resposta type = image OU document
       ├─ SIM → msg "use as opções do menu" → reexibe menu
       └─ NÃO → bloco ai (copilot)
              ├─ output mapeou opção → manip normaliza → tronco
              ├─ output duvida → FAQ (integração/msg do plano) → menu
              ├─ fallback → msg breve → menu
              └─ failure → erro IA (subfluxo)
```

Condicional de mídia — ver [reference.md](reference.md).

### `condition`

- `evaluate_condition` com `ruleType`: `any` (OU) ou `all` (E)
- Operadores comuns: `contains`, `equal`, `type` (image/document/text…)
- Sempre ligar **success** e **failure**
- Não usar campo em condição antes do manipulador que o popula

### `manipulator`

- Persistir campos antes de condições que os leem
- Mapear `{ai.response}`, `{tag}`, variáveis de integração
- **Um manip por marco** — agrupar `etapa`, `etapa_contexto`, campos relacionados (evitar 5 manips seguidos)
- Par com `kanban` nos marcos da jornada — **[kanban-journey.md](kanban-journey.md)**
- `list_custom_fields` antes de campos novos

### `ai`

**Padrão Copilot em 3 camadas:** [ai-copilot-pattern.md](ai-copilot-pattern.md) — leitura obrigatória antes de montar bloco IA com texto livre.

**Condicionais inteligentes** (`output_conditions`): até 10 prompts (≤200 chars), avaliados **antes** do system prompt. Cada uma = saída `output_key`. Se nenhuma bater → `fallback_output_key` → prompt principal (pode usar `#tokens` em `ai.response`) → cascata `condition` com `contains` pós-IA.

**Multimodal** — ligar quando o lead pode mandar mídia:

| Flag | Quando |
|------|--------|
| `understand_image` | Etapa recebe ou pode receber imagem |
| `understand_audio` | Etapa recebe áudio |
| `understand_pdf` | Aceita documento |
| `understand_receipt` | Pagamento / comprovante |

**Autenticação** (prioridade):

1. Integração cadastrada (`api_key_source: integration` + `ai_integration_id`)
2. Variável global — só se conta sem integração
3. **Nunca** chave `sk-...` fixa no fluxo

**Wiring de saídas:**

```json
{ "condition_type": "always", "condition_config": { "output_key": "duvida" } }
```

Failure:

```json
{ "condition_result": "failure" }
```

**Erro:** `fail_reason_variable: "error.log"` (preferir sobre `ai.erro`).

Config e exemplos completos: [reference.md](reference.md).

### `integration` (HTTP)

- **`request_body` é sempre STRING** — o editor Leona chama `.trim()` no campo; se gravar como **objeto**, o bloco abre **tela preta** (`TypeError: e.trim is not a function`)
- **Corpo em JSON válido na UI** — mensagem: *"JSON inválido. Use chaves e valores entre aspas duplas."*
  - Chaves entre aspas: `"whatsapp"`, não `whatsapp`
  - Strings/variáveis entre aspas: `"whatsapp": "{phone_number}"`
  - Números sem aspas: `"lookback_minutes": 1440`
  - Headers: objeto com chaves/valores entre aspas
- **Via MCP:** enviar `request_body` como **string** (`json.dumps(...)` em Python). O servidor **não** grava aspas retas no editor — pode vir loose ou `\u0022` → **inválido na UI**. Não corrigir corpos em massa via MCP.
- **Via UI Leona:** colar JSON estrito com **aspas retas** `"` na aba *Corpo da requisição* — **única forma garantida**
- **Nunca** `\u0022` no corpo — o editor mostra o escape literal e rejeita o JSON
- Mapear body da resposta com `response_fields` + `response_mapping`
- Falha **não bloqueia** o funil — ligar **success e failure** ao próximo nó
- Detalhes: [reference.md](reference.md) § Integração HTTP

### `connection_flow`

- Subfluxos reutilizáveis (roteador, erro, remarketing)
- Passar contexto via manipulador **antes** do `connection_flow`

### `distributor`

- Saídas `a1`, `a2`, … — empilhar na vertical; remesclar à frente
- Uma conexão explícita por handle

### Recursos de conta (`department`, `kanban`, `pixel`, `approved_sale`…)

- Sempre `list_*` MCP antes de criar — IDs da conta atual
- Kanban: `list_crms` — coluna deve pertencer ao CRM — **[kanban-journey.md](kanban-journey.md)**

---

## PIX e validação de comprovante

> **Pedido de PIX, pagamento, comprovante ou reconhecimento de recibo** → ler **[payment-comprovante.md](payment-comprovante.md)** e consultar fluxos de referência via MCP (`49331`, `55593`, `56091`, `64594`).

**Regra:** ativar PIX **≠** só bloco `pix`. Esteira mínima:

```
instrução (chave/recebedor) → [menu COPY | pix] → wait_response (comprovante)
  → type image/document → IA extração → IA validador → roteamento
  timeout do wait → remarketing (wait_response, não smart_interval)
```

Copiar topologia dos fluxos *Pagamento e validação* da conta — não improvisar wiring de validação.

---

## Remarketing e comprovante

Padrão de coluna (genérico):

```
[rmkt msgs] → [menu | wait comprovante] ── responde ──►
     ├─ válido (success) → entrega / obrigado
     └─ inválido / timeout → próximo rmkt (forward) ou volta (back-edge)
```

Detalhes completos (duas IAs, loops, subfluxo): **[payment-comprovante.md](payment-comprovante.md)**. JSON mecânico: [reference.md](reference.md).

---

## Horário de atendimento (gate antes da ação)

Quando remarketing, follow-up, handoff humano ou qualquer **ação proativa** deve ocorrer **só dentro do horário comercial**, não ligue o timeout do wait direto à mensagem. Use um **gate** de condição de hora + **loop de espera**.

### Antes de implementar — perguntar ou confirmar

| Dado | Exemplo no print | Padrão se não informado |
|------|------------------|-------------------------|
| Início | 08:00 (`Hora depois 8h`) | **Perguntar** |
| Fim | 23:00 (`Hora antes 23h`) | **Perguntar** |
| Timeout do wait (rmkt) | Após 2 horas sem resposta | Do plano do fluxo |
| Re-tentativa fora do horário | `smart_interval` 20 min | 15–30 min (confirmar) |
| Fuso | — | Confirmar se conta Leona usa horário local da empresa |

**Não inventar** horário — sem esses dados, parar e pedir ao usuário.

### Topologia (do print)

```
wait_response (timeout: ex. 2h sem resposta)
  → condition [E] Hora depois {início} + Hora antes {fim}
       ├─ success (dentro do horário) → message / ação desejada → continua fluxo
       └─ failure (fora do horário)
              → smart_interval (ex. 20 min)
              → volta ao mesmo condition  ← loop até entrar na janela
```

**Leitura:** fora do horário o fluxo **não envia** a mensagem; ele **dorme** e revalida. Só no `success` da condição a remarketing dispara.

### Wiring

| Saída | Destino |
|-------|---------|
| `wait_response` timeout / `no_response` | Entrada do `condition` de horário |
| `condition` **success** | Mensagem ou bloco de ação |
| `condition` **failure** | `smart_interval` |
| `smart_interval` saída | **Mesmo** `condition` (back-edge) |

### Layout do canvas

- Loop `condition` ↔ `smart_interval` = **back-edge** (não cria coluna forward nova)
- Coluna forward da remarketing começa na **mensagem** após `success` do gate
- Empilhar `smart_interval` abaixo ou ao lado do `condition` na mesma zona X

### Onde aplicar (não só remarketing)

Mesmo gate serve para: follow-up após wait, transferência para humano, disparo de integração sensível ao horário, reexibição de menu após timeout — sempre que a **ação** não deve rodar de madrugada/fora do comercial.

Receita MCP e anti-padrões: [reference.md](reference.md) § Horário de atendimento.

---

## Erro de bloco (padrão genérico)

Toda saída **failure** de `ai` ou integração crítica:

```
Manipulador (contexto: fluxo, etapa, tipo bloco, error.log) → connection_flow → subfluxo de erro
```

Campos úteis no manip: `fluxo_origem`, `etapa_contexto`, `error.block_type` (`ai` | `integration`).

Notificar humano/grupo conforme o **plano do projeto** (não presumir API específica).
