# Blocos Leona — escolha e uso

> Hub: [SKILL.md](SKILL.md) · Sequência: [sequencing.md](sequencing.md) · Variáveis: [variables.md](variables.md) · JSON: [reference.md](reference.md)  
> **Sempre** `get_node_type` na 1ª vez do tipo na sessão.

## Decisão rápida

| Situação | Bloco |
|----------|-------|
| Esperar / capturar resposta do lead | **`wait_response`** |
| Menu de opções | **`interactive_menu`** (não menu legado) |
| Pausa sem ouvir o lead | **`smart_interval`** |
| Pausa ≤1 min entre msgs do mesmo envio | `delay_between_messages` dentro de `message` |
| Classificar texto livre / N intenções | **`ai`** + `output_conditions` |
| Campo **já salvo** | **`condition`** |
| Persistência de campo | **`manipulator`** (1 campo/nó) |
| Chamar outro fluxo | **`connection_flow`** |
| HTTP | **`integration`** |
| PIX botão | `pix` **dentro** da esteira de pagamento |

---

## CRÍTICO — `wait_response` vs `smart_interval`

| | `wait_response` | `smart_interval` |
|---|-----------------|------------------|
| Escuta o lead? | **Sim** | **Não** |
| Continua quando | Resposta **ou** timeout | Só o tempo acaba |
| Remarketing por silêncio | timeout do wait | **Errado** como substituto |

```
Lead pode mandar algo que importa?
  SIM → wait_response | interactive_menu
  NÃO → só pausa? → smart_interval (time | date | weekly)
```

**Modos `smart_interval`:** `time` (duração), `date` (data/hora), `weekly` (janela comercial — preferir para gate de horário). Confirmar schema com `get_node_type`.

Gate comercial típico:

```
wait timeout → [smart_interval weekly OU condition hora]
  ├─ dentro → msg rmkt
  └─ fora → smart_interval curto → reavalia (back-edge)
```

Detalhe rmkt: [remarketing.md](remarketing.md).

---

## `message` — um bloco, várias actions

Mesma entrega (texto + mídia + delay + texto) = **1 nó**. Vários `message` só se houver wait/menu/condition/IA entre eles.

Actions: `send_message`, `send_multi_media`, `delay_between_messages`, `send_file`, `send_contact`, `send_sticker`.

- `typing_delay_seconds` = “digitando…” daquela msg  
- `delay_between_messages` = pausa **entre** actions  
- Mídia: HTTPS público  
- Copy: [whatsapp-copy.md](whatsapp-copy.md)

---

## `wait_response`

Actions típicas: `send_message` → `wait_for_response` → `save_user_data`.

- Salvar no campo do plano
- Wire **resposta** + **timeout**
- Timeout que re-pede = back-edge; onda nova de rmkt = forward

---

## `interactive_menu`

- `save_user_data` → campo ([variables.md](variables.md))
- Wire: cada `menu_option` + **`menu_other`** + **`menu_timeout`**
- List 4–10 / buttons 2–3; `option_id` estável

**`menu_other`:** mídia inesperada → msg + reexibir menu; texto → IA copilot ([ai-copilot-pattern.md](ai-copilot-pattern.md)) → mapear opção ou FAQ → menu.

---

## `condition`

`evaluate_condition` + `ruleType` all/any. Categorias: custom_field, field, global_variable, system (tag/time), attendance, attendant — [variables.md](variables.md).

Sempre **success** + **failure**. Não ler campo antes de gravar.

---

## `manipulator`

1 action/nó. Sequência de nós para vários campos. Ops matemáticas ok. Ver [variables.md](variables.md).

---

## `ai`

- 1 bloco = 1 tarefa (triagem **ou** validação **ou** resposta — não tudo)
- `output_conditions` (≤10, ≤200 chars) antes do prompt; `fallback_output_key` obrigatório se houver conditions
- Multimodal / **`understand_receipt`** quando faz sentido
- `auto_send_response: false` em funis controlados
- Auth: integração da conta; failure → `error.log`
- Padrão completo: [ai-copilot-pattern.md](ai-copilot-pattern.md)

---

## `integration` (HTTP)

- `request_body` = **string** JSON
- Corpo válido na UI: aspas retas `"`; via MCP o editor pode corromper — **corrigir na UI**, um bloco
- Mapear `response_fields`; ligar success **e** failure
- Detalhe: [reference.md](reference.md)

---

## `pix` e pagamento

Botão PIX **≠** esteira completa. Sempre: instrução → (pix|menu copy) → wait comprovante → tipo mídia → IA recibo → validação → rotas.  
[payment-comprovante.md](payment-comprovante.md).

---

## Outros

| Bloco | Nota |
|-------|------|
| `connection_flow` | Encerra execução atual; contexto via manip **antes** |
| `distributor` | Saídas `a1`…; uma conexão cada |
| `tags` | `list_labels` |
| `kanban` | `list_crms` — [kanban-journey.md](kanban-journey.md) |
| `department` | `list_departments` |
| `pixel` / `approved_sale` | `list_pixel_configs` / `list_products` |
| `notification` | Alerta para número interno, não o lead |
| `carousel` / `template` | Meta/UAZAPI — URLs HTTPS; schema via `get_node_type` |

---

## Erro genérico

Failure de `ai` / integração crítica:

```
manipulator (contexto + error.log) → connection_flow → subfluxo erro
  OU department / notification conforme plano do usuário
```

Não presumir API de negócio de outra conta.
