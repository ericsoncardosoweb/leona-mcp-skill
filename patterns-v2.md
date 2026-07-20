# Fluxos modulares

> Reutilizar subfluxos. Sequência interna: [sequencing.md](sequencing.md).

## Regra

Antes de criar nós novos: `list_flows` → `get_flow` no candidato → se serve, **`connection_flow`**. Evite clonar blocos entre fluxos.

**Quando NÃO modularizar:** fluxo pontual &lt; ~15 nós, um só propósito — Template C basta.

---

## Workflow

```
1. list_flows
2. get_flow no candidato
3. Serve? → connection_flow (+ manip contexto antes)
4. Não? → create_flow mínimo
5. layout_flow.py no fluxo tocado
```

## Papéis úteis (biblioteca)

| Papel | Responsabilidade |
|-------|------------------|
| Entrada | Boas-vindas / contexto |
| Roteador | Intenção / produto / fila |
| Oferta / qualificação | Copy + coleta |
| Pagamento | PIX + comprovante |
| Entrega / operação | Pós-pago |
| Remarketing | Ondas por silêncio |
| Erro IA | failure → contexto + handoff |
| Atendimento | department / humano |

Um subfluxo = **um papel**.

## Contrato

Antes de `connection_flow`, manipulator grava o mínimo que o filho precisa (`origem`, `etapa`, campos de produto…). Filho não assume globals inventados.

## Anti-padrões

- Monolito 60+ nós com responsabilidades misturadas
- Copiar nós “no MCP” entre fluxos
- Modularizar funil de 8 nós sem necessidade
