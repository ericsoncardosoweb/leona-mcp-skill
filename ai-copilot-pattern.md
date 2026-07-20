# Padrão Copilot — IA em 3 camadas

> Classificação e roteamento com texto livre. Hub: [blocks.md](blocks.md) · [variables.md](variables.md).

## Ordem na plataforma

```
0. condition determinística (tipo mídia, campo já salvo) — opcional
1. output_conditions[]     → micro-prompts PRIMEIRO (≤10, ≤200 chars)
2. system_prompt           → só se nenhuma condition interna bater (fallback_output_key)
3. condition pós-IA        → contains em {ai.response} se o fallback usa #tokens
```

---

## Camada 1 — `output_conditions`

Casos óbvios com saída dedicada: afirmação, dúvida, objeção, mídia cedo, opção de menu detectável.

Cada item: `{ "prompt": "…", "output_key": "duvida" }` + `fallback_output_key` obrigatório.

Wire MCP: `condition_config.output_key` = chave. + **failure**.

---

## Camada 2 — prompt fallback

Só roda se camada 1 não bater. Pode pedir resposta curta com tokens (`#duvida`, `#humano`) **ou** um valor canônico (título de opção).

`auto_send_response: false` em funis — você controla a mensagem.

---

## Camada 3 — conditions pós-IA

Se o fallback devolve `#tokens` ou texto curto:

```
ai → condition contains "#duvida" → …
   → condition contains "#humano" → …
   → failure → fallback genérico
```

Use `contains`, não `equal`.

---

## Multimodal e recibo

| Flag | Quando |
|------|--------|
| `understand_image` / `audio` / `pdf` | Etapa pode receber esse tipo |
| `understand_receipt` | Validação de comprovante |

Recibo: [payment-comprovante.md](payment-comprovante.md).

---

## Auth

1. Integração da conta (`api_key_source: integration` + id)  
2. Variável global  
3. Nunca chave fixa `sk-...` no fluxo  

`fail_reason_variable`: preferir `error.log`.

---

## Checklist

- [ ] Pré-filtro determinístico quando possível
- [ ] `output_conditions` + `fallback_output_key`
- [ ] Toda `output_key` + failure ligados
- [ ] 1 IA = 1 tarefa (validador separado de triagem)
- [ ] Pós-IA com `contains` se usar tokens
