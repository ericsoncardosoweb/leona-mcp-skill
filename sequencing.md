# Sequenciamento inteligente de blocos

> **Como** montar fluxos poderosos: ordem, interação entre blocos, wiring consciente e remarketing.  
> Hub: [SKILL.md](SKILL.md). Config de cada bloco: [blocks.md](blocks.md).

**Foco deste arquivo:** plataforma Leona — **não** modelo de negócio. Tags, produtos e APIs específicas ficam no plano do usuário ou em skill companion `leona-farol`.

---

## Ciclo universal de um trecho de fluxo

Todo segmento bem desenhado segue quatro fases. Pular fase = bug silencioso.

```
COLETA → PERSISTÊNCIA → DECISÃO → AÇÃO
```

| Fase | Blocos | Regra |
|------|--------|-------|
| **Coleta** | `message`, `wait_response`, `interactive_menu` | 1 pergunta por wait; sequência de envio = **1 `message` com várias actions** |
| **Persistência** | `manipulator` (`set_contact_custom_field`, `save_user_data` no wait/menu) | **Obrigatório** antes de qualquer bloco que **leia** o valor |
| **Decisão** | `ai`, `condition` | 1 `ai` = 1 tarefa; preferir `output_conditions` da IA a cascata longa de `condition` |
| **Ação** | `message`, `integration`, `kanban`, `pixel`, `connection_flow`, `department` | Efeito colateral ou entrega; failure sempre ligado |

**Teste mental antes de adicionar nó:** “Este bloco coleta, persiste, decide ou age?” Se não souber, o fluxo ainda não está claro.

---

## Leis de interação (aplicar sempre)

### 1. Persistência antes de leitura

```
❌ condition (campo X) → manipulator (set X)
✅ wait/menu (save X) → manipulator (normaliza X, se preciso) → condition (X)
```

`condition` e corpo de `integration` que usam `{campo}` exigem que o campo já exista upstream.

### 2. Captura vs pausa

```
Lead pode (ou deve) falar no meio? → wait_response ou menu
Só pausa técnica / relógio / horário?     → smart_interval
```

Detalhe: [blocks.md](blocks.md) § wait vs intervalo.

### 3. Convergência antes de bloco caro

Ramos paralelos (`distributor`, várias saídas de IA) devem **remesclar** antes de:

- nova chamada `ai`
- `integration` HTTP
- `connection_flow` de processo longo

Remescla = um nó comum (`manipulator`, `condition` compartilhado, ou tronco único).

### 4. Failure nunca solto

| Bloco | Ligaturas obrigatórias |
|-------|-------------------------|
| `ai` | cada `output_key` + **failure** |
| `wait_response` | **client-response** + **timeout** |
| `interactive_menu` | cada `menu_option` + **menu_other** + **menu_timeout** |
| `condition` | **success** + **failure** |
| `integration` | **success** + **failure** (podem ir ao **mesmo** destino) |

### 5. Subfluxo na borda

`connection_flow` marca **fronteira de responsabilidade** — não entre cada par de mensagens.

Antes do bloco: `manipulator` com contexto mínimo (origem, etapa, variáveis que o filho precisa).

Arquitetura modular (quando usar subfluxo): [patterns-v2.md](patterns-v2.md).  
Kanban + campo `etapa`: [kanban-journey.md](kanban-journey.md).

---

## Matriz — o que pode vir depois de quê

| Depois de… | Pode ir para… | Evitar ir direto para… |
|------------|---------------|-------------------------|
| `message` (pergunta) | `wait_response`, `interactive_menu` | `smart_interval` longo, `condition` sem dado |
| `wait_response` (resposta) | `manipulator`, `ai`, `condition` | `message` longa sem processar resposta |
| `wait_response` (timeout) | gate horário, rmkt, `connection_flow` | tronco principal como se tivesse respondido |
| `interactive_menu` (opção) | tronco da opção, `connection_flow` | `condition` no campo antes do save do menu |
| `ai` (success) | `manipulator`, ação, roteamento | cascata de 5+ `condition` pós-IA |
| `ai` (output_key) | caminho específico da intenção | misturar output_key com `condition_result` |
| `condition` (success/failure) | ramo correspondente | ramo sem destino |
| `manipulator` | `condition`, `integration`, `message` | outro manip só para 1 campo (agrupar) |
| `integration` | próximo passo **mesmo** em success e failure* | parar fluxo só porque API falhou |
| `distributor` | variantes `message` → **merge** | lógica duplicada em cada ramo |

\*Exceto quando failure exige caminho diferente (retry, notify humano).

---

## Receitas de sequência (genéricas)

### R1 — Perguntar e rotear

```
message (contexto)
  → wait_response (save → campo_resposta, timeout configurado)
       ├─ client-response → ai (classifica) OU condition (campo já normalizado)
       └─ timeout → [ver remarketing § voltar vs avançar]
```

### R2 — Menu como funil

```
message (intro)
  → interactive_menu (save → escolha)
       ├─ menu_option A → tronco A (ideal: connection_flow se subfluxo grande)
       ├─ menu_option B → tronco B
       ├─ menu_other → ai copilot OU reexibir menu [blocks.md § menu_other]
       └─ menu_timeout → remarketing ou reenvio menu
```

### R3 — Texto livre → rota mínima

```
wait_response
  → ai (output_conditions: intenção_1 | intenção_2 | … | fallback)
       ├─ cada output_key → manipulator (valor exato) → 1 condition OU connection_flow
       └─ failure → erro padronizado
```

**Não** encadear 8 `condition` após IA para cada hashtag — isso é trabalho da IA.

### R4 — Bypass condicional (pular coleta)

Quando dado **já existe** (campo preenchido, tag, resposta anterior):

```
condition (campo/tag has_value?)
  ├─ success → pula wait → processamento / entrega
  └─ failure → wait_response (coleta) → …
```

Padrão visto em produção: gate antes de wait longo — economiza coluna e reduz fricção.

### R5 — Processamento assíncrono + entrega

```
coleta (wait/menu)
  → manipulator (normaliza input)
  → ai (prepara payload) — opcional
  → integration (gera recurso → variável)
       ├─ success → condition (recurso pronto?) → message (1 nó: texto + send_multi_media + delay + texto)
       └─ failure → notify / connection_flow erro
  → interactive_menu (feedback) — opcional
```

**Entrega ao lead = 1 bloco `message`** com actions empilhadas — ver [blocks.md](blocks.md) § message.

### R6 — Variantes A/B sem duplicar lógica

```
distributor
  ├─ message variante 1 ─┐
  ├─ message variante 2 ─┼→ MESMO nó downstream (condition / wait / ai)
  └─ message variante 3 ─┘
```

### R7 — Hub classificador (muitas rotas, um cérebro)

```
manipulator (contexto mínimo)
  → ai (output_conditions: rotas fixas + humano + menu_fallback)
       ├─ rota conhecida → manipulator → condition curta OU connection_flow direto
       ├─ humano → message → wait_response (response + timeout → mesmo destino)
       ├─ menu_fallback → interactive_menu
       └─ failure → subfluxo erro
```

Regra: **IA decide**; `condition` só confirma campo já persistido ou faz match literal (tag, contains).

---

## IA vs condition — onde colocar inteligência

| Pergunta | Resposta |
|----------|----------|
| Texto livre, intenção, N categorias | **`ai`** com `output_conditions` |
| Campo **já salvo** no manipulator/wait | **`condition`** (`contains`, `equal`, `type`) |
| Só tipo de arquivo (imagem/PDF) | **`condition`** `fieldOperator: type` |
| Dúvida fora do menu | **`ai`** no ramo `menu_other` |
| 10+ rotas | **1 `ai`** + no máximo 1 condition de confirmação — não 10 conditions |

Downstream de IA: operador **`contains`**, nunca `equal` em texto gerado.

---

## Remarketing — voltar, avançar ou encerrar

Remarketing não é “mandar mensagem depois de X tempo”. É **decidir o que fazer com o silêncio ou com resposta inválida**.

Gatilho correto: **timeout** de `wait_response` ou **menu_timeout** — nunca `smart_interval` no lugar do wait ([remarketing.md](remarketing.md)).

### Árvore de decisão (aplicar em todo timeout)

```
Timeout / menu_timeout / resposta inválida
  │
  ├─ Lead ainda está NA MESMA etapa? (faltou dado, formato errado, não clicou)
  │     ├─ SIM, mesma pergunta/comprovante/menu
  │     │     → VOLTA (back-edge) OU nova onda pedindo o MESMO (forward com novo wait)
  │     └─ NÃO, etapa concluída mas sem engajamento
  │           → AVANÇA onda rmkt (nova coluna) OU encerra
  │
  ├─ Ação proativa (msg rmkt) pode rodar agora?
  │     ├─ NÃO (fora horário) → gate → smart_interval → revalida
  │     └─ SIM → message rmkt → NOVO wait/menu (nova chance de captura)
  │
  └─ Limite de ondas atingido?
        ├─ SIM → connection_flow recuperação / department / tags encerramento
        └─ NÃO → próxima onda (forward)
```

### Três modos de remarketing

| Modo | Quando | Topologia | Layout |
|------|--------|-----------|--------|
| **Voltar** | Resposta inválida; re-pedir mesmo input; `menu_other` mapeável → reexibir menu | msg correção → **mesmo** `wait_response` ou menu anterior | **Back-edge** |
| **Avançar** | Silêncio; nova argumentação; nova onda | msg rmkt → **novo** wait (mesmo assunto) → timeout → msg rmkt 2… | **Coluna forward** |
| **Encerrar** | Max tentativas; opt-out; handoff | `connection_flow` / `department` / tag final | Forward ou fim |

### Voltar — regras

- Comprovante/foto **inválida** → explicar → **volta ao wait** do mesmo campo (não pular validação).
- Menu: lead digitou fora → `menu_other` → se IA mapeou opção → manipulator → **tronco da opção**; senão → msg breve → **reexibir menu** (back-edge).
- **Não voltar** para coleta já satisfeita (campo preenchido + validado) — use `condition` bypass (R4).

### Avançar — regras

- Cada onda = `message` rmkt + **`wait_response` ou menu depois** (lead precisa poder responder no meio).
- Silêncio no wait principal → timeout → [gate horário?] → rmkt 1 → wait → timeout → rmkt 2…
- Lead que responde **antes** do timeout → saída **client-response** → tronco principal (**nunca** recebe rmkt).

### Encerrar — regras

- Definir no plano: quantas ondas, destino final (humano, CRM, subfluxo).
- Timeout final **sem** novo wait = dead-end — evitar.

### Gate de horário (entre timeout e rmkt)

Preferir Intervalo modo **Horários**; alternativa condition + loop ([blocks.md](blocks.md)).  
`smart_interval` aqui é **pausa técnica** — não substitui wait upstream.

---

## Onde colocar cada tipo de bloco no funil

```
ENTRADA
  message curta / distributor (A/B)
  manipulator (contexto — leve)

QUALIFICAÇÃO
  wait + ai OU menu
  condition só em campos já persistidos

CONVERSÃO / PEDIDO
  message + wait (comprovante, dados)
  [payment-comprovante.md](payment-comprovante.md) se PIX

PÓS-AÇÃO (sync)
  sequência horizontal: persist → recursos conta (kanban/pixel/sale) → integration
  remescla de ramos paralelos antes do HTTP

PRODUÇÃO / ENTREGA
  gate bypass → wait coleta mídia → processamento → message multimídia → menu feedback

SAÍDA
  connection_flow pós-venda / humano / rmkt recuperação
```

Sync pós-ação e PIX têm receitas dedicadas — não repetir lógica de negócio aqui.

---

## Erros comuns de sequência

| Erro | Correção |
|------|----------|
| `condition` antes do `manipulator` que popula o campo | Inverter ordem |
| `smart_interval` “esperando resposta” | `wait_response` com timeout |
| RMKT sem wait depois da mensagem | Msg → wait/menu sempre |
| Timeout → rmkt direto às 3h sem gate | Gate horário se ação proativa |
| IA + 6 conditions para cada intenção | `output_conditions` na IA |
| `integration` failure desligado | Ligar failure (mesmo destino ou notify) |
| Vários `message` seguidos (intro + áudio + dica) | **1 `message`** com `actions[]` — [blocks.md](blocks.md) § message |
| Subfluxo a cada 2 mensagens | Agrupar actions; só `connection_flow` com responsabilidade clara |
| Ramos paralelos sem remescla | Um nó comum antes do próximo passo caro |
| Lead responde cedo e mesmo assim recebe rmkt | Timeout não ligado à rmkt; response ligada ao tronco |

---

## Checklist antes de declarar trecho pronto

```
□ Cada trecho obedece COLETA → PERSISTÊNCIA → DECISÃO → AÇÃO
□ Waits têm response + timeout ligados
□ Menus têm option + other + timeout
□ IA tem failure + cada output_key
□ Remarketing: decidi voltar / avançar / encerrar para cada timeout
□ Lead que responde cedo não passa pelo ramo rmkt
□ Integrations: failure ligado
□ get_flow → wiring_needed: false
□ layout_flow.py executado
```

---

## Estudar fluxos reais (estrutura, não copy)

Use `get_flow` para ver **sequência de blocos**, não para copiar tags/produtos:

| Foco | O que observar |
|------|----------------|
| Entrada + variantes | `distributor` → merge |
| Roteamento | 1 `ai` + saídas vs cascata `condition` |
| Coleta produção | gate → wait vs bypass |
| Entrega mídia | `message` multi-action → menu |
| Pós-ação | coluna horizontal + remescla |

IDs úteis (conta exemplo): `66000`, `66007`, `54817`, `56319` — estrutura apenas.

Domínio Farol: skill companion `leona-farol`.
