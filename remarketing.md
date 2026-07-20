# Remarketing no Leona

> Guia para construir repescagem / follow-up com qualidade. Hub: [SKILL.md](SKILL.md).  
> **Decisão voltar vs avançar vs encerrar:** [sequencing.md](sequencing.md) § Remarketing.

**Regra de ouro:** remarketing por **silêncio do lead** usa **`wait_response` com timeout** — nunca `smart_interval` no lugar do wait. O lead precisa poder responder **antes** do rmkt e ter essa resposta capturada.

Intervalo Inteligente entra **depois** do timeout (gate de horário, pausa entre ondas) — ver [blocks.md](blocks.md) § Intervalo Inteligente.

---

## Voltar, avançar ou encerrar (decisão obrigatória)

Antes de ligar qualquer timeout a uma mensagem, classifique o comportamento:

| Modo | Gatilho típico | O que fazer | Wiring |
|------|----------------|-------------|--------|
| **Voltar** | Resposta inválida; formato errado; re-pedir mesmo dado | Msg correção → **mesmo** wait/menu | **Back-edge** |
| **Avançar** | Silêncio após pergunta/oferta | Msg rmkt → **novo** wait (mesmo assunto) | **Coluna forward** |
| **Encerrar** | Max ondas; opt-out | `connection_flow` / `department` | Forward ou fim |

**Voltar ≠ Avançar:** voltar repete a **mesma etapa** (comprovante inválido → wait comprovante de novo). Avançar é **nova onda** de copy quando o lead **não respondeu** (silêncio).

**Lead respondeu cedo:** saída `client-response` → tronco principal — **nunca** encaminhar para rmkt.

Árvore completa: [sequencing.md](sequencing.md) § Remarketing.

---

## O que é remarketing neste guia

Sequência automática quando o lead **não responde** dentro do prazo (ou abandona um passo), com:

1. Mensagem(s) de repescagem (copy do plano — **não inventar**)
2. Nova chance de responder (`wait_response` ou `interactive_menu`)
3. Saída se responder (tronco principal) ou próxima onda / encerramento

Não confundir com **subfluxos** só de roteamento (`connection_flow` → fluxo “Remarketing X”) — isso é organização; a **mecânica** continua sendo wait + timeout.

---

## Topologia correta (padrão coluna)

```
message (pergunta / oferta)
  → wait_response (timeout: ex. 2h — do plano)
       ├─ client-response → tronco principal (lead voltou)
       └─ timeout → [gate horário?] → message rmkt 1
                         → wait_response (mesmo assunto / comprovante / menu)
                              ├─ responde → tronco
                              └─ timeout → message rmkt 2 → wait → …
```

Cada **mensagem rmkt** = avanço **forward** (nova coluna no canvas).  
Volta ao wait após comprovante inválido ou re-pergunta = **back-edge** (não conta coluna extra).

---

## Passo a passo — construir remarketing

### 1. Definir gatilho

| Gatilho | Saída de origem |
|---------|-----------------|
| Lead não respondeu pergunta | `wait_response` → **timeout** |
| Menu sem clique | `interactive_menu` → **menu_timeout** |
| Após N horas no checkout | `wait_response` no passo de pagamento → timeout |

**Não usar:** `smart_interval` de 2h “esperando ver se responde”.

### 2. Gate de horário (opcional, recomendado em ação proativa)

Só enviar rmkt dentro do comercial. Duas formas válidas:

#### Forma A — Intervalo Inteligente modo **Horários** (preferir quando possível)

```
wait_response timeout → smart_interval (schedule_type: weekly)
  → message rmkt → wait_response …
```

O fluxo **dorme** até entrar em uma faixa ativa. Se **já** estiver no horário, **segue na hora**.  
Configuração na UI: aba **Horários** — ver [blocks.md](blocks.md) § Modo Horários.

#### Forma B — Condicional + loop (legado, ainda comum)

```
wait_response timeout → condition (Hora depois + Hora antes)
       ├─ success → message rmkt
       └─ failure → smart_interval (ex. 20 min, schedule_type: time)
              → volta ao mesmo condition
```

`smart_interval` aqui é **pausa técnica** (não escuta lead). Confirmar horários com o usuário — [blocks.md](blocks.md) § Horário de atendimento.

### 3. Mensagens de remarketing

- Uma coluna por onda (msg 1, msg 2, msg 3…)
- Tom e textos vêm do **plano** — slot vazio se não fornecido
- **Escrita:** [whatsapp-copy.md](whatsapp-copy.md) § Remarketing — lembrete → valor → porta aberta; sem culpa
- `typing_delay_seconds`: 2–3 em textos longos

### 4. Fechar o loop

| Objetivo | Wiring |
|----------|--------|
| Dar outra chance | timeout rmkt → novo `wait_response` (ou menu) |
| Encerrar / CRM | timeout final → `connection_flow` → subfluxo recuperação |
| Handoff humano | menu rmkt → opção atendente → `connection_flow` / dept |

### 5. Layout

Seguir [layout.md](layout.md). Timeouts e loops = back-edges; rmkt messages = colunas forward.

---

## Onde usar cada bloco no rmkt

| Situação | Bloco |
|----------|-------|
| Esperar resposta do lead (com rmkt se não responder) | **`wait_response`** |
| Lead respondeu antes do timeout | Saída **client-response** → tronco |
| Só enviar rmkt fora de madrugada | **Horários** no Intervalo Inteligente **ou** condition + loop |
| Pausa fixa entre re-checagens de relógio | `smart_interval` **time** (15–30 min) |
| Pausa até data/hora exata | `smart_interval` **date** |
| Lead pode interromper com mensagem no meio da pausa | **Erro** — deveria ser `wait_response` upstream |

---

## Remarketing + comprovante / PIX

Timeout do wait de comprovante → rmkt pedindo envio → mesmo campo `comprovante` → validação.  
Esteira completa: [payment-comprovante.md](payment-comprovante.md).

---

## Subfluxos (`connection_flow`)

Padrão em contas maduras: funil principal dispara rmkt via `connection_flow` → fluxo “Remarketing …” reutilizável.

Antes do `connection_flow`: **manipulador** com contexto (`etapa`, `produto`, origem).

Subfluxo interno ainda obedece: **wait + timeout**, não intervalo longo no lugar do wait.

---

## Checklist remarketing

- [ ] Gatilho = **timeout** de `wait_response` ou `menu_timeout` (não intervalo longo antes da pergunta)
- [ ] Saída **client-response** ligada ao tronco (lead que responde cedo não recebe rmkt)
- [ ] Gate horário se ação proativa (Horários no intervalo **ou** condition + loop)
- [ ] Cada onda rmkt = `message` → `wait` (ou menu) com timeout definido
- [ ] Caminho de saída final (CRM, humano, encerrar)
- [ ] Layout: rmkt forward, loops back-edge — [layout.md](layout.md)
- [ ] Copy não inventada

---

## Anti-padrões

- `smart_interval` (2h) no lugar de `wait_response` timeout 2h
- Timeout do wait → message rmkt **direto** sem gate quando rmkt não deve rodar de madrugada
- Remarketing sem saída se o lead responder no wait anterior
- Várias mensagens rmkt seguidas **sem** novo wait/menu (lead não tem como responder no meio)
- `smart_interval` time curto (&lt; 15 min) em loop de condition — polling excessivo
- Coluna nova só por mensagem rmkt sem ponto de resposta depois

---

## Referência MCP (intervalo no gate)

Pausa entre re-checagens (forma B):

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

Gate por janela semanal (forma A) — exemplo ilustrativo; validar com `get_node_type` (`smart_interval`):

```json
{
  "action_type": "smart_interval",
  "config": {
    "schedule_type": "weekly",
    "weekly_schedule": {
      "monday": { "enabled": true, "start_time": "08:00", "end_time": "23:00" },
      "tuesday": { "enabled": true, "start_time": "08:00", "end_time": "23:00" },
      "wednesday": { "enabled": true, "start_time": "08:00", "end_time": "23:00" },
      "thursday": { "enabled": true, "start_time": "08:00", "end_time": "23:00" },
      "friday": { "enabled": true, "start_time": "08:00", "end_time": "23:00" },
      "saturday": { "enabled": false, "start_time": "08:00", "end_time": "18:00" },
      "sunday": { "enabled": false, "start_time": "08:00", "end_time": "18:00" }
    }
  }
}
```

Horários e dias: **sempre confirmar com quem pediu o fluxo** — não inventar.
