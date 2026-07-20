# Variáveis, campos e etiquetas — memória reutilizável

> Sintaxe: `{nome}` em textos, prompts, HTTP e manipulator.  
> **Reuse-first:** `list_custom_fields` + `list_labels` **antes** de criar qualquer chave ou etiqueta.

## Três camadas

| Camada | Sintaxe típica | Quem grava |
|--------|----------------|------------|
| Sistema / contato | `{first_name}`, `{phone_number}`, `{last_message}`, `{customer.photo}`… | Plataforma |
| Campo customizado | `{resposta}`, `{cpf}`, `{comprovante}`… | wait / menu / manip / HTTP |
| Global da conta | `{g_chave_gpt}` ou `{global…}` (confirmar na conta) | Config da conta |
| Runtime do bloco | `{ai.response}`, `{error.log}`, `{comprovante.chave_pix}`… | IA / failure / recibo |

---

## Lei de ouro — nomes úteis e reaproveitáveis

Campos e etiquetas são **infraestrutura da conta**, não lixo de um fluxo.

| Faça | Evite |
|------|--------|
| `list_custom_fields` → reutilizar chave existente | Criar `resposta2`, `resposta_nova`, `campo1` |
| `list_labels` → reutilizar etiqueta existente | Duplicar “Cliente” / “cliente” / “CLIENTE VIP” |
| Nomes curtos, minúsculos, sem acento: `cpf`, `pedido`, `etapa` | Nomes longos/únicos de campanha: `resposta_quiz_pascoa_2026_v3` |
| Um conceito = uma chave | Sinônimos paralelos (`doc` + `documento` + `cpf_doc`) |
| Perguntar ao usuário se o nome do campo/etiqueta é novo | Inventar em silêncio |

**Antes de criar campo ou label:** se já existe algo equivalente na conta → **use o existente**.

---

## Temporário vs persistente

### Campo temporário de conversa → `resposta` (padrão)

Para pergunta pontual cujo valor será lido **já no próximo bloco** (IA, condition, mensagem) e pode ser sobrescrito depois:

```
wait_response + save_user_data → field_name: resposta
```

Depois:

- IA: `user_message: "{resposta}"` ou com contexto
- Mensagem: `Vi que você disse: {resposta}`
- Condition: `custom_field` `resposta` contains / type / has_value

**Não** criar `resposta_nome`, `resposta_foto`, `resposta_menu` para cada pergunta — reutilize **`resposta`** como buffer da conversa, a menos que o valor precise sobreviver a várias etapas.

### Informação persistente do contato → campo específico

Se o dado é identidade, documento, preferência ou ativo que outros fluxos vão consultar:

| Tipo de dado | Exemplos de chave | Notas |
|--------------|-------------------|--------|
| Documento | `cpf`, `cnpj`, `rg` | Um por tipo |
| Contato | `email`, `endereco` | Preferir nativos da plataforma se existirem |
| Mídia / arquivo durável | `comprovante`, `foto_cliente`, `documento` | Nome = o que é |
| Escolha de produto/serviço | `produto`, `plano`, `tamanho` | Menu `save_user_data` direto |
| Estado de jornada | `etapa`, `status_funil` | Tokens curtos (`1`, `checkout`, `pago`) |
| Contexto entre subfluxos | `fluxo_origem`, `etapa_contexto` | Preencher antes de `connection_flow` |

```
❌ wait (qual seu CPF?) → save em resposta → … e nunca promove
✅ wait → save em cpf   (persistente)
✅ wait → save em resposta → IA classifica → manip promove para produto/etapa
```

**Regra:** se outro fluxo ou o humano no CRM precisar desse dado amanhã → **campo específico**. Se só serve para a próxima decisão nesta conversa → **`resposta`**.

### Menu

`save_user_data` no campo semântico (`produto`, `horario`, `tamanho`) — não em `resposta`, salvo menu genérico de uma pergunta só.

| Saída | Uso |
|-------|-----|
| `menu_option` | Campo já preenchido → roteie; não ecoar no manip |
| `menu_other` | Texto no mesmo campo ou em `resposta` → IA |
| `menu_timeout` | Silêncio → rmkt / reexibir |

`option_id` estável ao renomear rótulo do botão.

---

## Etiquetas (`tags`)

1. `list_labels` sempre.  
2. Reutilizar nome **exato** já cadastrado.  
3. Etiqueta = **estado/segmento** reutilizável (`pago`, `lead_quente`, `aguardando_doc`) — não copy de campanha.  
4. Não criar variante por fluxo (`pago_upsell`, `pago_luto`) se o significado é o mesmo.  
5. Condition de tag: `list_labels` → `tagId`/`tagName` reais.

---

## Onde os dados nascem

```
wait + save_user_data     → resposta | campo persistente
menu + save_user_data     → campo da opção
manipulator               → 1 campo por nó
ai response_variable      → ai.response | nome dedicado (ex. router)
ai fail_reason_variable   → error.log (padrão)
HTTP response_mapping     → campos mapeados
understand_receipt        → comprovante.* (chave_pix, nome_recebedor, valor, data…)
```

**Lei de ordem:** nunca `condition` / IA lendo campo **antes** de gravar.

```
❌ condition(X) → manipulator(set X)
✅ wait/menu (save X) → [manip?] → condition | ai → ação
```

---

## Manipulator

- MCP: **1 action por nó**.
- Vários campos → vários nós (empilhar no setup).
- Preferir chaves já listadas.
- Valor: literal ou `{resposta}`, `{ai.response}`, `{campo}`.
- Ops: `set_value`, `add`, `subtract`, `multiply`, `divide`.

Contrato típico antes de `connection_flow`: `fluxo_origem`, `etapa` / `etapa_contexto` (+ intenção se router).

---

## Condition

`ruleType`: `all` | `any`. Saídas: **success** + **failure**.

| category | Uso |
|----------|-----|
| `custom_field` | Campos salvos (`resposta`, `cpf`, `comprovante`…) |
| `field` | Nome, número, e-mail nativos |
| `global_variable` | Globals |
| `system` (tag / time / weekday / date) | Etiquetas, horário comercial |
| `attendance` / `attendant` | Status / atendente (`list_account_members`) |

Operadores: `equal`, `contains`, `type` (image/document/text/audio/video…), `has_value`, `before`/`after`.

Pós-IA: **`contains`**, quase nunca `equal` em texto livre.

Pré-filtro de mídia (pagamento / upload):

```
type image|document → validador / produção
type text|audio|video|sticker → copilot ou “mande o arquivo”
```

---

## Bloco IA — variáveis e auth

| Config | Padrão | Notas |
|--------|--------|-------|
| `user_message` | `{resposta}` / `{comprovante}` / estado + msg | Ver papéis em [ai-copilot-pattern.md](ai-copilot-pattern.md) |
| `response_variable` | `ai.response` ou nome do papel (`router`) | Consistente no fluxo |
| `fail_reason_variable` | **`error.log`** | Evitar legado `ai.erro` / `ai.fail.reason` em fluxos novos |
| `auto_send_response` | **`false`** em funil | Agente controla a msg |
| `maintain_context` | `true` só em agente conversacional | Triagem/validador: `false` |

### Credencial (obrigatório descobrir na conta)

MCP **não** lista integrações de IA. Procedimento:

```
1. list_flows → achar fluxo recente com bloco ai que funciona
2. get_flow → copiar api_key_source + ai_integration_id (o mais recente / mais usado)
3. Preferir: { "api_key_source": "integration", "ai_integration_id": <id> }
4. Sem integração na conta → api_key: "{g_chave_gpt}" (ou nome global da conta)
5. Nunca sk-... fixo no JSON do fluxo
```

Detalhe completo: [ai-copilot-pattern.md](ai-copilot-pattern.md).

---

## Recibo

Com `understand_receipt`, use campos derivados do comprovante (ex. `{comprovante.chave_pix}`, `{comprovante.nome_recebedor}`, `{comprovante.valor}`) — **validar nomes** num fluxo de pagamento da conta.

Esteira: [payment-comprovante.md](payment-comprovante.md).

---

## Mensagens e HTTP

- Copy: `Oi, {first_name}!` — natural; dados: `{cpf}`, `{produto}`.
- HTTP body = **string** JSON; `"whatsapp": "{phone_number}"`.
- Mídia: HTTPS ou `{campo}`.

---

## Anti-padrões

- Criar campo/etiqueta sem `list_*`
- Duplicar etiqueta por variação de maiúscula/campanha
- Save de wait sem campo (dado some)
- Tudo em `resposta` quando o dado é identidade persistente
- Campo específico novo para cada pergunta descartável
- Condition antes do save
- Manip ecoando o que o menu já salvou
- Vários `set_contact_custom_field` no mesmo nó
- Inventar `ai_integration_id` sem copiar de fluxo da conta
