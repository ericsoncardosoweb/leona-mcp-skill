# Variáveis e campos — memória do fluxo

> Sintaxe MCP: `{nome}` em textos, prompts, HTTP e valores de manipulator.  
> Sempre `list_custom_fields` antes de inventar chave de campo.

## Três camadas de dados

| Camada | Onde vive | Sintaxe típica | Quem grava |
|--------|-----------|----------------|------------|
| **Sistema / contato** | Contato Leona | `{first_name}`, `{phone_number}`, `{last_message}`, `{customer.photo}`… | Plataforma |
| **Campo customizado** | Contato (EAV) | `{nome_do_campo}` ou conforme conta | wait / menu / manipulator / integration |
| **Global da conta** | Conta | `{global.chave}` ou `{g_chave}` (confirmar na conta) | Config da conta / UI |
| **Runtime do bloco** | Execução | `{ai.response}`, `{error.log}`, vars de recibo | `ai`, failures |

Confirmar nomes exatos com `list_custom_fields` e fluxos existentes da **conta do usuário**.

---

## Onde os dados nascem

```
wait_response + save_user_data     → campo (texto, mídia, áudio…)
interactive_menu + save_user_data  → campo = option escolhida (ou texto em menu_other)
manipulator set_contact_custom_field → campo (1 campo por nó MCP)
ai response_variable               → ex. ai.response
ai fail_reason_variable            → preferir error.log
integration response_mapping       → campos mapeados
understand_receipt                 → campos de recibo (valor, chave, recebedor, data…)
```

**Lei:** nunca `condition` / IA lendo campo **antes** do bloco que o grava.

```
❌ condition(X) → manipulator(set X)
✅ wait/menu (save X) → [manip normaliza] → condition(X) | ai
```

---

## Menu 2.0 e campos

No `interactive_menu`, configure **`save_user_data`** para o campo do plano (`produto`, `tamanho`, `horario`…).

| Saída | Uso do campo |
|-------|----------------|
| `menu_option` | Valor já no campo → roteie direto; **não** copiar de novo no manipulator |
| `menu_other` | Texto livre no mesmo campo (ou `tag`) → IA/condition |
| `menu_timeout` | Silêncio → rmkt / reexibir menu |

`option_id` estável: ao mudar **rótulo** do botão, **não** mudar `option_id` (quebra wiring).

---

## Manipulator

- MCP: **1 action por nó** (`set_contact_custom_field` **ou** `set_created_at`).
- Vários campos → vários nós em sequência (empilhar no layout / setup).
- Ops: `set_value`, `add`, `subtract`, `multiply`, `divide`.
- Valor pode ser literal ou `{ai.response}`, `{campo}`, etc.
- `list_custom_fields` — preferir chaves existentes.

---

## Condition — categorias

`ruleType`: `all` (E) | `any` (OU). Saídas: **success** | **failure**.

| category | Uso |
|----------|-----|
| `custom_field` | Campo salvo no contato |
| `field` | Nome, número, e-mail nativos |
| `global_variable` | Globals da conta |
| `system` + tag / time / weekday / date | Tags, horário, dia |
| `attendance` / `attendant` | Status do chat / atendente (`list_account_members`) |

Operadores úteis: `equal`, `contains`, `type` (image/document/text), `has_value`, `before`/`after` (hora).

**Pós-IA:** use `contains` em `{ai.response}`, quase nunca `equal` (texto varia).

Tags: `list_labels` — não inventar nome de etiqueta.

---

## Bloco IA — variáveis

| Config | Padrão | Notas |
|--------|--------|-------|
| `user_message` | `{last_message}` ou `{campo}` | Mídia: passe o campo da mídia |
| `response_variable` | `ai.response` | Consumido em msg/condition/manip |
| `fail_reason_variable` | Preferir `error.log` | Handoff / log |
| `output_conditions` | — | Rotas antes do prompt principal |
| `auto_send_response` | Em funil costuma ser **false** | Agente controla a msg |

Multimodal: `understand_image` / `audio` / `pdf` / **`understand_receipt`** (comprovante).

Auth: integração da conta (`api_key_source: integration`) > global; **nunca** `sk-...` fixo no fluxo.

Padrão 3 camadas: [ai-copilot-pattern.md](ai-copilot-pattern.md).

---

## Recibo (understand_receipt)

Com flag ligada, a plataforma extrai dados do comprovante para variáveis de recibo (ex.: valor, chave PIX, recebedor, data — **nomes exatos: validar no fluxo/schema da conta**).

Use na **IA validadora** e em conditions — não inventar nomes de campo.

Esteira completa: [payment-comprovante.md](payment-comprovante.md).

---

## Em mensagens e HTTP

- Copy: `Oi, {first_name}!` — natural.
- HTTP `request_body`: **string** JSON com aspas retas; variáveis entre aspas: `"whatsapp": "{phone_number}"`.
- Mídia: URL HTTPS pública ou `{campo_com_url}`.

---

## Anti-padrões

- Inventar `field_name` sem `list_custom_fields`
- Condition antes do save
- Duplicar manipulator só para ecoar o que o menu já salvou
- Vários `set_contact_custom_field` no **mesmo** nó manipulator
- Comparar `ai.response` com `equal` em frases longas
