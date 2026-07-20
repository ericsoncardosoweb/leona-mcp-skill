# Kanban + manipulator — jornada do lead

> Desenhar **etapas de CRM** e sincronizar com **campos customizados** para o fluxo rotear de forma inteligente.  
> Modularização: [patterns-v2.md](patterns-v2.md). Sequência de blocos: [sequencing.md](sequencing.md).

**Antes de qualquer bloco `kanban`:** `list_crms` (MCP) — `crm_id` e `crm_column_id` devem ser da **conta atual**. Coluna de outro CRM é rejeitada.

---

## Dois sistemas, um marco

| Mecanismo | Para quê | Quem usa |
|-----------|----------|----------|
| **`kanban`** (`create_kanban_card`) | Pipeline **visível** para time — cards, colunas, metas | Humanos, relatórios, operação |
| **`manipulator`** (`set_contact_custom_field`) | Estado **máquina** no contato — roteamento automático | `condition`, IA, subfluxos |

**Boa prática:** nos **marcos** da jornada, atualize **os dois juntos** (ou manipulator imediatamente antes/depois do kanban na mesma coluna):

```
marco atingido (ex.: pagamento validado)
  → manipulator (etapa = N, etapa_contexto = texto curto)
  → kanban (coluna que representa o mesmo marco)
  → próximo passo (pixel, sync, connection_flow…)
```

Lead no CRM e lead no fluxo **falando a mesma língua**.

---

## Desenhar colunas Kanban (jornada)

### Princípios

1. **Uma coluna = um estado de negócio** — não uma mensagem enviada.
2. Colunas seguem a **ordem real** da jornada (esquerda → direita no board).
3. **Poucas colunas** valem mais que micro-etapas (6–8 no funil principal).
4. Coluna com **`conversion_goal: true`** = meta de conversão (ex.: venda fechada) — usar só onde faz sentido comercial.
5. Boards **separados** para papéis diferentes (venda vs produção vs pós-venda).

### Modelo genérico — board **Vendas / CRM**

```
Novo Lead → Qualificação → Proposta/Preview → Follow-up → Checkout → [Venda Concluída ✓]
```

| Coluna | Lead está… | Move kanban quando… |
|--------|------------|------------------------|
| Novo Lead | Entrou no canal | Primeiro contato / boas-vindas |
| Qualificação | Conversando, definindo interesse | Após primeira qualificação (menu/IA) |
| Proposta / Preview | Viu oferta, considerando | Após apresentação enviada |
| Follow-up | Sumiu ou pendente | Timeout rmkt **ou** reentrada |
| Checkout | Decidiu comprar, dados/PIX | Início pagamento |
| Venda Concluída | Pagou (meta) | Comprovante **validado** — não no PIX pedido |

### Modelo genérico — board **Produção / Operações**

```
Tentar Recuperar → Gerando → Entregue → Revisão → Concluído
```

| Coluna | Lead está… | Move kanban quando… |
|--------|------------|------------------------|
| Fila / Novo pedido | Pagou, aguarda produção | Sync pós-pago |
| Gerando | Processamento ativo | API/IA iniciou produção |
| Entregue | Mídia/pronto enviado | Message de entrega |
| Revisão / Concluído | Fechado operacionalmente | NPS ok ou handoff revisão |

### Modelo genérico — board **Gestão de resultados**

```
Pós-venda | Venda perdida | Recuperação | Recorrente | Para revisão
```

Use para **desfechos** — não para cada passo do funil.

---

## Múltiplos CRMs na mesma jornada

Contas maduras usam **2–3 boards**:

```
Board Vendas     — funil comercial até conversão
Board Produção   — fulfillment após pagamento
Board Resultados — pós-venda, perdido, recuperação
```

**Sequência típica pós-pagamento** (coluna horizontal no fluxo):

```
kanban (Produção — fila)
  → manipulator (etapa = produção)
  → kanban (Vendas — venda concluída + value {comprovante.valor})
  → pixel / approved_sale / …
  → connection_flow → subfluxo produção
```

Ordem exata vem do **plano** — o padrão é: **operacional + comercial alinhados no mesmo marco**, não kanban espalhado.

---

## Campo `etapa` — convenção com manipulator

Use campo customizado **`etapa`** (numérico ou texto curto) como **índice de máquina de estados**.

### Por que numérico ajuda

```
condition: etapa equal 3  → checkout
condition: etapa equal 4  → pago
condition: etapa equal 5  → produção
```

Estável em `condition`; não depende de copy longa.

### Campos complementares

| Campo | Tipo | Uso |
|-------|------|-----|
| `etapa` | number/text | Roteamento automático |
| `etapa_contexto` | text | Debug, IA, rmkt (“IA classificador”, “rmkt checkout”) |
| `fluxo_origem` | text | Qual subfluxo chamou |
| Campos de negócio | text | `produto`, `briefing`, etc. |

### Quando setar `etapa`

| Momento | Ação |
|---------|------|
| Entrada em subfluxo | `etapa` + `fluxo_origem` no start |
| Marco concluído (pagou, enviou foto, briefing ok) | Novo valor de `etapa` |
| Antes de `connection_flow` | Filho sabe em que marco o lead está |
| Erro IA/integração | `etapa_contexto` descreve falha |
| **Não** setar | A cada mensagem cosmetica |

### Agrupar no manipulator

**Um nó manipulator por marco** com várias actions relacionadas:

```json
{
  "action_type": "set_contact_custom_field",
  "config": {
    "field_name": "etapa",
    "operation": "set_value",
    "value_type": "text",
    "value": "4"
  }
}
```

Evite 4 nós manipulator seguidos só para campos do **mesmo marco** — agrupe ([blocks.md](blocks.md) § manipulator).

`list_custom_fields` antes de criar campos novos.

---

## Quando mover Kanban (e quando não)

### Mover ✅

- Lead **mudou de fase de negócio** (qualificou, entrou checkout, pagou, produção iniciou, entregue)
- Valor do deal relevante (`value: "{comprovante.valor}"` na coluna de venda)
- Handoff para operação (card na fila produção)

### Não mover ❌

- Cada `message` enviada
- Cada timeout de rmkt (use coluna Follow-up **uma vez**, não a cada onda)
- Antes do wait terminar (lead ainda não completou a etapa)
- Duplicar move para mesma coluna sem mudança de estado

---

## Roteamento por `etapa` + Kanban

### Fluxo decide por campo; humano vê board

```
condition (etapa equal 4)  → connection_flow Produção
condition (etapa equal 2)  → connection_flow Apresentação
failure → rmkt ou atendimento
```

Kanban **reflete** o resultado; `condition` **dirige** automação.

### Remarketing alinhado à jornada

Timeout no checkout com lead ainda `etapa=3`:

```
manipulator (etapa_contexto=rmkt checkout)  — etapa permanece 3
→ connection_flow Remarketing Checkout
→ kanban (Follow-up) — se ainda não estiver lá
```

**Voltar conteúdo** vs **avançar onda**: [sequencing.md](sequencing.md) § Remarketing.  
Etapa **não avança** se o lead não concluiu o marco.

---

## Configuração MCP — kanban

```json
{
  "node_type": "kanban",
  "actions": [{
    "action_type": "create_kanban_card",
    "config": {
      "crm_id": 1255,
      "crm_column_id": 2666,
      "value": "{comprovante.valor}"
    }
  }]
}
```

| Campo | Nota |
|-------|------|
| `crm_id` | De `list_crms` |
| `crm_column_id` | Coluna **desse** CRM |
| `value` | Opcional; template com variáveis |
| `remove_kanban_card` | Limpar card ao encerrar / perder venda |

Prompt MCP: `kanban_resources_guide`.

---

## Configuração MCP — manipulator no marco

Par típico no sync pós-pago:

```
manipulator: etapa=4
  → kanban: CRM / Venda Concluída, value={comprovante.valor}
  → pixel / approved_sale / integration
```

Início de subfluxo produção:

```
manipulator: etapa=5, etapa_contexto=producao
  → kanban: Controle de Produção / fila
  → coleta ou integration
```

---

## Desenhar jornada nova (passo a passo)

```
1. list_crms + list_custom_fields + list_flows (MCP)
2. Mapear jornada **com o usuário** (Template A ou perguntas)
3. Preencher Template A em builder.md com o usuário
4. Fluxograma estratégia → OK
5. Por subfluxo: Template B → construir → layout_flow.py
```

Template completo: **[builder.md](builder.md) § Template A — Mapa de jornada**.

---

## Checklist kanban + manipulator

```
□ list_crms antes de todo bloco kanban
□ Coluna corresponde a marco de negócio (não a mensagem)
□ manipulator (etapa) no mesmo marco que kanban
□ etapa numérica documentada no plano da conta
□ conversion_goal só na coluna de meta real
□ value preenchido onde deal amount importa
□ Rmkt não avança etapa se marco não concluído
□ Subfluxos não duplicam moves de kanban do pai
□ Agrupar campos no manipulator por marco
```

---

## Anti-padrões

- Kanban sem `list_crms` (ID inválido)
- Coluna micro (“Enviou msg 2”) — polui pipeline
- Só kanban sem `etapa` — fluxo não roteia de forma confiável
- Só `etapa` sem kanban — time perde visibilidade
- `condition` lendo `etapa` antes do manipulator setar
- Mover para Venda Concluída **antes** de validar pagamento
- Três boards atualizados na mesma mensagem sem necessidade

---

## Relacionados

| Tema | Arquivo |
|------|---------|
| Biblioteca de subfluxos | [patterns-v2.md](patterns-v2.md) |
| PIX / comprovante (marco checkout) | [payment-comprovante.md](payment-comprovante.md) |
| Bloco manipulator / kanban | [blocks.md](blocks.md) |
| Remarketing por etapa | [remarketing.md](remarketing.md) + [sequencing.md](sequencing.md) |
