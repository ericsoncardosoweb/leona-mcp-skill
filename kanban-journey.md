# Kanban + manipulator — jornada

> Marcos de CRM. Modular: [patterns-v2.md](patterns-v2.md). Antes de `kanban`: **`list_crms`**.

## Dois sistemas, um marco

| | Para | Quem consome |
|---|------|----------------|
| **kanban** | Pipeline visível | Time humano |
| **manipulator** (campo etapa/status) | Estado máquina | condition, ai, subfluxos |

Nos **marcos** (não a cada msg):

```
evento → manipulator (campo de etapa) → kanban (coluna do mesmo marco) → próximo
```

MCP: 1 campo por nó manipulator — vários campos = vários nós empilhados.

---

## Desenhar colunas

1. Coluna = **estado de negócio**, não mensagem enviada  
2. Poucas colunas (6–8 no funil principal)  
3. `conversion_goal` só onde há conversão real (venda, pedido pago, agendamento confirmado…)  
4. Boards separados se venda ≠ operação ≠ pós-venda  

### Exemplos genéricos (adaptar ao negócio)

**Comércio / serviço**

```
Novo → Qualificação → Proposta → Checkout → Pago → Entrega → Pós-venda
```

**Agendamento (clínica, salão, consultoria)**

```
Novo → Interesse → Agendado → Confirmado → Realizado → Follow-up
```

**Info-produto / curso**

```
Lead → Nutrição → Oferta → Checkout → Aluno → Onboarding
```

Nomes e IDs: **sempre** da conta do usuário via `list_crms`.

---

## Campo máquina

Combine com o usuário um campo (ex.: `etapa`, `status_funil`). Valores estáveis (`1`…`N` ou tokens curtos).  
`list_custom_fields` antes de criar chave nova.

---

## Anti-padrões

- Kanban a cada mensagem  
- Coluna de outro CRM  
- Inventar `crm_column_id`  
- Manipulator depois da condition que lê o campo  
