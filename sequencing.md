# Sequenciamento — interação entre blocos

> Ordem inteligente. Escolha de bloco: [blocks.md](blocks.md). Rmkt: [remarketing.md](remarketing.md).

## Lei central

```
COLETA → PERSISTÊNCIA → DECISÃO → AÇÃO
```

| Fase | Blocos | Regra |
|------|--------|-------|
| Coleta | wait, menu | 1 pergunta; **sempre save** (`resposta` ou campo persistente) |
| Persistência | save no wait/menu, manipulator | **Antes** de quem lê o valor |
| Decisão | ai, condition | 1 ai = 1 tarefa; preferir `output_conditions` a cascata longa |
| Ação | message, integration, kanban, connection_flow, department | Depois de decidir |

```
❌ condition(X) → manipulator(set X)
✅ wait/menu (save X) → manip? → condition | ai → ação
```

---

## Pares que funcionam

| Depois de… | Segue bem com… | Evitar |
|------------|----------------|--------|
| wait (resposta) | manip, ai, condition | msg longa sem processar |
| menu_option | tronco da opção (campo já salvo) | manip eco desnecessário |
| menu_other | condition tipo mídia **ou** ai | ignorar other |
| ai (output_key) | manip (valor canônico) → ação/rota | 6 conditions iguais |
| ai failure | subfluxo erro / dept | silêncio |
| condition success/failure | ações distintas | deixar failure solto |
| timeout wait | rmkt (avançar) ou gate horário | `smart_interval` no lugar do wait |

---

## Receitas curtas

**Qualificação**

```
message → menu|wait → save campo → ai|condition → connection_flow|msg
```

**Texto livre / copilot**

```
wait|menu_other → [condition tipo?] → ai (output_conditions)
  → cada key → manip → rota
  → failure → erro
```

**Pagamento** — [payment-comprovante.md](payment-comprovante.md)

**Modular** — manip contexto → `connection_flow` ([patterns-v2.md](patterns-v2.md))

---

## Remarketing: voltar vs avançar

| Modo | Quando | Wiring |
|------|--------|--------|
| **Voltar** | Dado inválido; re-pedir o mesmo | msg → **mesmo** wait (back-edge) |
| **Avançar** | Silêncio; nova onda de copy | msg rmkt → **novo** wait (forward) |
| **Encerrar** | Max ondas / opt-out | dept / fim / outro fluxo |

Lead respondeu cedo → saída de resposta → **tronco**, nunca rmkt.

---

## Anti-padrões

- Decidir sem persistir
- Dois waits seguidos sem processar o primeiro
- IA monólito (triagem+venda+validação)
- Rmkt só com `smart_interval`
- Kanban a cada mensagem (só em **marcos**)
