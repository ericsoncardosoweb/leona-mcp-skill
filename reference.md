# Referência MCP — wiring e receitas

> Confirme schema com `get_node_type` antes de escrever. Exemplos = mecânica, não negócio.

## Variáveis em templates

`{first_name}`, `{last_message}`, `{campo}`, `{ai.response}`, `{global…}` — ver [variables.md](variables.md).

## Condition — mídia (pré-IA)

```json
{
  "ruleType": "any",
  "conditions": [
    { "category": "custom_field", "fieldName": "comprovante",
      "fieldOperator": "type", "fieldValue": "image" },
    { "category": "custom_field", "fieldName": "comprovante",
      "fieldOperator": "type", "fieldValue": "document" }
  ]
}
```

Troque `fieldName` pelo campo do wait/menu.

## AI — output_conditions

```json
{
  "output_conditions": [
    { "prompt": "Lead tem dúvida de preço ou prazo", "output_key": "duvida" },
    { "prompt": "Lead quer avançar / comprar / agendar", "output_key": "avancar" }
  ],
  "fallback_output_key": "padrao",
  "auto_send_response": false,
  "fail_reason_variable": "error.log"
}
```

Auth preferida: `api_key_source: integration` + `ai_integration_id` da conta.

## Wiring — handles

| Origem | condition_config |
|--------|------------------|
| ai output | `{ "output_key": "duvida" }` |
| ai/condition failure | `{ "condition_result": "failure" }` |
| condition success | `{ "condition_result": "success" }` |
| wait timeout | handle timeout / `no_response` (ver `available_outgoing_slots`) |
| menu | `menu_option` / `menu_other` / `menu_timeout` |
| distributor | `a1`, `a2`, … |

Linear: omitir `connections[]`. Branch: uma `add_flow_connection` por handle.

## Gate de horário (condition)

```json
{
  "ruleType": "all",
  "conditions": [
    { "category": "system", "systemSubtype": "time", "systemOperator": "after", "time": "8", "timeMinute": "0" },
    { "category": "system", "systemSubtype": "time", "systemOperator": "before", "time": "23", "timeMinute": "0" }
  ]
}
```

**Validar** operadores no `get_node_type(condition)` — nomes podem variar. Preferir `smart_interval` weekly quando possível ([blocks.md](blocks.md)).

## HTTP — request_body

- Sempre **string** JSON  
- Na UI: aspas retas `"`; chaves entre aspas  
- Não corrigir em massa via MCP (risco `\u0022` / loose)  
- Ex.: `"whatsapp": "{phone_number}"`, números sem aspas  

Failure **não** deve engolir o funil sem rota.

## Manipulator

```json
{
  "action_type": "set_contact_custom_field",
  "config": {
    "field_name": "etapa",
    "operation": "set_value",
    "value_type": "text",
    "value": "checkout"
  }
}
```

1 action por nó.

## Message multi-action (esqueleto)

```json
{
  "node_type": "message",
  "actions": [
    { "action_type": "send_message", "order": 1,
      "config": { "message_text": "…", "typing_delay_seconds": 2 } },
    { "action_type": "delay_between_messages", "order": 2,
      "config": { "delay_seconds": 3 } },
    { "action_type": "send_message", "order": 3,
      "config": { "message_text": "…" } }
  ]
}
```
