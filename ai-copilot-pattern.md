# Padrão Copilot — IA em papéis e 3 camadas

> Hub: [blocks.md](blocks.md) · [variables.md](variables.md).  
> 1 bloco IA = **1 papel**. Não misturar extração + validação + conversa no mesmo nó.

## Papéis (escolha um)

| Papel | Flags típicas | `user_message` | `maintain_context` | `response_variable` |
|-------|---------------|----------------|--------------------|---------------------|
| **Extrator / recibo** | `understand_receipt` + image/pdf | `{comprovante}` | `false` | `ai.response` |
| **Validador** | sem multimodal (texto estruturado) | campos `{comprovante.*}` + esperado do plano | `false` | `ai.response` |
| **Router / copilot** | image + audio conforme etapa | `{resposta}` ou `{last_user_message}` | `false` (curto) | `ai.response` |
| **Agente conversacional** | image + audio | bloco `[ESTADO]` + mensagem do lead | **`true`** | nome dedicado (`router`, …) |

Funil de pagamento: extrator → validador → (opcional) copilot de exceção. Ver [payment-comprovante.md](payment-comprovante.md).

---

## Credencial — descobrir na conta (não inventar)

Ordem:

1. **`list_flows`** → fluxo recente que já usa IA com sucesso  
2. **`get_flow`** → no `ai_call`, copiar:
   - preferido: `"api_key_source": "integration", "ai_integration_id": <id>`
   - se só houver global: `"api_key": "{g_chave_gpt}"` (ou o nome global da conta)
3. Reaplicar o **mesmo** padrão nos novos blocos IA da sessão  
4. **Nunca** colar `sk-...` no fluxo  

Não existe `list_ai_integrations` no MCP — a fonte da verdade é um fluxo vivo da **conta atual**.

`fail_reason_variable`: **`error.log`** em fluxos novos.

`auto_send_response`: **`false`** quando o funil controla as mensagens.

---

## Ordem de avaliação na plataforma

```
0. condition determinística (type da mídia, campo já salvo)
1. output_conditions[]     → micro-prompts PRIMEIRO (≤10, ≤200 chars)
2. system_prompt           → só se nada bater (fallback_output_key)
3. condition pós-IA        → contains em {response_variable} se usar #tokens
```

### Pré-filtro de mídia (camada 0)

```
wait salvou comprovante|resposta|foto
  → type image|document → tronco (validador / produção)
  → type text|audio|video|sticker → copilot OU msg “mande o arquivo”
```

---

## Camada 1 — `output_conditions`

Casos óbvios: dúvida, objeção, mídia ok, opção detectável, pedir humano, comprovante detectado.

```json
{
  "output_conditions": [
    { "prompt": "Lead tem dúvida de preço, prazo ou como funciona", "output_key": "duvida" },
    { "prompt": "Lead quer avançar / comprar / agendar", "output_key": "avancar" }
  ],
  "fallback_output_key": "padrao",
  "auto_send_response": false,
  "fail_reason_variable": "error.log"
}
```

Wire: cada `output_key` + **failure**.

Após a saída: **manipulator** com valor canônico (intenção / etapa) → `connection_flow` ou ação — ver [variables.md](variables.md).

---

## Camada 2 — prompt fallback

Só se camada 1 não bater. Resposta curta (`#duvida`) **ou** valor canônico.

Agente: inclua estado no `user_message`:

```
[ESTADO]
etapa={etapa}
produto={produto}

[MENSAGEM]
{resposta}
```

(ajuste campos aos da conta — não inventar)

---

## Camada 3 — conditions pós-IA

`contains` em `{ai.response}` (ou variável dedicada). Nunca `equal` em frase longa.

---

## Checklist

- [ ] Auth copiada de fluxo da conta (integração mais recente / global)
- [ ] 1 papel por bloco IA
- [ ] Pré-filtro `type` quando há upload
- [ ] `output_conditions` + `fallback_output_key` se for router
- [ ] Toda `output_key` + failure ligados
- [ ] `error.log` + `auto_send_response: false` em funil
- [ ] Entrada lê `{resposta}` ou campo persistente correto ([variables.md](variables.md))
