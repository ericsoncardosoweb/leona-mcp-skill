# Layout do canvas

> Obrigatório ao fechar edição. Hub: [SKILL.md](SKILL.md).

## Dois níveis

| Nível | Quando | Como |
|-------|--------|------|
| **1. Script** | Sempre | `layout_flow.py` — colunas por profundidade; Y pelo **altura do bloco** |
| **2. Zonas** | ≥3 ramos **ou** wait+IA+rmkt/timeout | Ajuste manual / `reposition_flow_nodes` por faixa |

Durante a construção, empilhar em `{x:0,y:0}` é normal. Problema é **terminar** sem layout.

---

## Procedimento

```
1. wiring_needed: false
2. python …/scripts/layout_flow.py <FLOW_ID>
   [--col-w 400 --gap 100 se muitos ramos]
3. Se zonas necessárias → aplicar faixas (abaixo)
4. Pedir refresh / fit view no Leona
```

```powershell
python "$env:USERPROFILE\.cursor\skills\leona-flow\scripts\layout_flow.py" <FLOW_ID>
python …\layout_flow.py <FLOW_ID> --dry-run
```

O script só move **x/y** — não mexe em conexões.

---

## Como o script espaça

- **Coluna (X)** = profundidade no grafo *forward* (back-edges de timeout/loop **não** avançam coluna).
- **Y** = empilha irmãos na coluna; altura ≈ tipo do nó + nº de actions (evita sobreposição).
- Timeout / volta = tende a ir **mais abaixo** na ordenação.

Nova coluna natural após: `wait_response`, `interactive_menu`, branch de IA/condition.

---

## Modelo mental — zonas (fluxos ramificados)

```
Y menor (cima)     tronco feliz / produção
Y médio            hub IA / exceções / menu_other
Y maior (baixo)    remarketing / timeouts / loops de horário

X esquerda         setup: manipulators + tags + kanban (empilhados)
X → direita        progresso do funil
```

Checklist zonas:

- [ ] Setup vertical à esquerda (não espalhado no tronco)
- [ ] Tronco legível esquerda→direita
- [ ] Loops de horário / failure IA **fora** do tronco (abaixo ou cluster)
- [ ] Ondas de rmkt em pista inferior, forward por onda
- [ ] Nada sobreposto após script + ajuste

---

## Durante criação (MCP)

- Linear: `position {x:0,y:0}`
- Ramo: `position_near_node_id` = pai, `auto_connect_to_flow_tail: false`
- **Não** layout manual bloco a bloco no meio da construção
- Após wiring: script → zonas se preciso

---

## Anti-padrões

- Pronto sem `layout_flow.py`
- Layout antes do wiring completo
- Confiar só no script quando há hub IA + rmkt + tronco (aplique zonas)
- Vários `message` sem wait = colunas fantasma — fundir actions
