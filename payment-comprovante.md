# PIX + comprovante (padrão plataforma)

> Genérico para qualquer conta. **Não inventar** chave PIX, valor, recebedor ou prompts — usar plano do usuário ou `get_flow` em fluxo de pagamento **da própria conta** (`list_flows`).

## Anti-padrão fatal

Só bloco `pix` e parar. PIX na Leona = **esteira**.

## Esteira mínima (7 passos)

```
1. Instrução          message (chave, recebedor, valor — do plano)
2. Facilitar cópia    pix e/ou interactive_menu (botão copiar)
3. Aguardar           wait_response + save → campo comprovante
4. Pré-filtro         condition type image|document → ok; text|audio|video|sticker → copilot / re-pedir
5. Extração           ai #1 understand_receipt (+ image/pdf se preciso)
6. Validação          ai #2 confere valor/chave/recebedor esperados
7. Rotas              válido → sucesso | inválido → voltar wait | incorreto → humano
```

Timeout do wait → [remarketing.md](remarketing.md) (wait, não smart_interval).

Campo do wait: preferir **`comprovante`** (persistente). Credencial das IAs: copiar integração da conta — [ai-copilot-pattern.md](ai-copilot-pattern.md).

---

## Topologia

```
[setup manip/kanban se marco de checkout]

→ message (instruções PIX)
→ [pix | menu COPY] → wait_response (save comprovante)
     ├─ response → condition type image|document
     │                ├─ ok → IA #1 (recibo) → IA #2 (valida)
     │                │         ├─ válido → sucesso / sync / próximo fluxo
     │                │         ├─ inválido → msg → wait (voltar)
     │                │         └─ incorreto / suspeito → handoff
     │                └─ não mídia → copilot texto OU re-pedir
     └─ timeout → rmkt → novo wait
```

---

## IA #1 — extração

- `user_message`: `{comprovante}` (campo salvo)
- `understand_receipt: true` (+ image/pdf conforme conta)
- `auto_send_response: false`
- Saída dedicada → IA #2; failure → humano/log

## IA #2 — validação de negócio

- Entrada: dados do recibo + **valores esperados do plano** (não inventar)
- Resposta curta canônica (ex.: `valido` / `invalido` / `incorreto`) — alinhar com o usuário
- Rotas com `condition` **contains** em `{ai.response}`

Variáveis de recibo: [variables.md](variables.md).

---

## Wiring checklist

- [ ] wait: response + timeout
- [ ] type image e document cobertos
- [ ] IA failure ligados
- [ ] inválido = **voltar** ao wait; silêncio = **avançar** rmkt
- [ ] IDs dept/crm via `list_*`
- [ ] `layout_flow.py` no fim

---

## Descoberta na conta

```
list_flows → procurar nomes: pagamento, pix, comprovante, checkout
get_flow → copiar topologia e prompts da CONTA — não de IDs externos
```
