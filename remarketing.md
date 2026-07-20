# Remarketing / repescagem

> Silêncio do lead. Decisão voltar/avançar: [sequencing.md](sequencing.md). Copy: [whatsapp-copy.md](whatsapp-copy.md).

## Regra de ouro

Remarketing por **não resposta** = **`wait_response` (ou menu) com timeout** — nunca `smart_interval` no lugar do wait.

`smart_interval` só **depois** do timeout (gate de horário, pausa entre ondas).

---

## Topologia

```
message → wait_response (timeout do plano)
  ├─ responde → tronco
  └─ timeout → [gate horário?] → message rmkt
                 → wait (mesmo assunto)
                      ├─ responde → tronco
                      └─ timeout → onda 2 … ou encerrar
```

| Modo | Wiring |
|------|--------|
| Voltar (dado inválido) | back-edge ao **mesmo** wait |
| Avançar (silêncio) | nova msg + **novo** wait (forward) |
| Encerrar | dept / connection_flow / fim |

---

## Gate de horário

Antes de msg proativa, só dentro do comercial:

- Preferir `smart_interval` **weekly** (Horários), **ou**
- `condition` hora + loop `smart_interval` curto (back-edge)

**Não inventar** horários — perguntar ao usuário.

---

## Ondas

- 2–3 ondas típicas; copy **do plano** (não inventar oferta)
- Cada onda = avanço de coluna no canvas
- Após max ondas → humano ou encerrar conforme plano

---

## Anti-padrões

- `smart_interval` 2h “esperando resposta”
- Rmkt na saída de **resposta** (lead já falou)
- Mesma copy em todas as ondas
- Esquecer timeout no wait/menu
