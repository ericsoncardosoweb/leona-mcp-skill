# Copy WhatsApp — escrita para fluxos Leona

> **Quando ler:** antes de escrever ou revisar `message_text`, corpo de menu, legendas de wait, ondas de remarketing ou textos de handoff.  
> **Regra de ouro:** não inventar preço, prazo, benefício ou URL — **estruturar e humanizar** o que o plano/usuário forneceu.  
> MCP: ler também o prompt `flow_content_writing_guide` antes de `add_flow_node` / `update_flow_node` com copy.

---

## Princípio central

WhatsApp é **conversa no celular**, não e-mail nem landing page colada no chat.

| Robótico (evitar) | Humano (buscar) |
|-------------------|-----------------|
| "Informamos que seu pedido foi registrado." | "Pronto — recebi seu pedido ✅" |
| "Por gentileza, aguarde." | "Já estou vendo isso…" |
| "Selecione uma das opções abaixo:" | "Qual faz mais sentido pra você?" |
| "Prezado cliente" | Nome ou "Oi!" — nunca formalismo de SAC |
| Parágrafo único com 6 linhas | 2–4 blocos curtos com respiro |
| Emoji em toda linha 🎉✨🔥💯 | 0–2 emojis com função clara |

**Teste obrigatório:** ler em voz alta. Se soar como notificação de banco ou bot genérico, reescrever.

---

## Leitura dinâmica (formatação WhatsApp)

Use o que o WhatsApp **renderiza de verdade**:

| Recurso | Sintaxe | Uso |
|---------|---------|-----|
| **Negrito** | `*texto*` | Título da mensagem, benefício-chave, CTA, valor |
| _Itálico_ | `_texto_` | Ênfase suave, citação, tom acolhedor |
| ~Tachado~ | `~texto~` | Preço antigo **só se o plano trouxer** |
| Quebra de linha | `\n` | Entre ideias — **nunca** `\n` literal visível |
| Lista numerada | `1.` `2.` | Só passos objetivos (PIX, envio de foto) — máx. 3 itens |

### Ritmo visual (mobile)

```
[gancho — 1 linha]

[contexto ou benefício — 1–2 linhas]

[ação ou pergunta — 1 linha]
```

- **Máx. ~4 linhas visíveis** antes de um `wait_response` ou menu — o resto na próxima action ou próximo bloco.
- **Linha em branco** (`\n\n`) entre blocos de ideia — nunca wall of text.
- **Uma ideia por parágrafo** — o olho escaneia negrito e primeira linha.
- **Variáveis naturais:** `Oi, {first_name}!` — não `Cliente: {full_name}` no meio de frase conversacional (ok em notificação interna).

### `typing_delay_seconds`

| Tamanho do texto | Delay sugerido |
|------------------|----------------|
| ≤ 2 linhas | 1–2 s |
| 3–5 linhas | 2–3 s |
| Entrega emocional (áudio, preview) | 3–5 s no primeiro `send_message` |

Copy longa + delay curto = sensação de spam; copy curta + delay longo = sensação de travamento.

---

## Emojis — moderação com propósito

| Contexto | Regra |
|----------|-------|
| Boas-vindas / entrega | 1 emoji no gancho **ou** no fechamento |
| Pagamento / comprovante | Neutro — ✅ ou 📎 só se ajudar |
| Erro / handoff | 🤝 ou nenhum — empatia no texto |
| Remarketing | 1 emoji na onda 2+ — não repetir o mesmo em todas |
| Menu / botões | Emoji no **botão** só se couber (1 caractere) |

**Proibido:** emoji-decoração em cada linha; sequências 🎉🔥💯; emoji que contradiz o tom (🎉 em "pagamento recusado").

---

## Tom e voz

- **Segunda pessoa:** você / te / seu
- **Frases curtas:** 8–15 palavras na média
- **Voz ativa:** "Me manda a foto" > "A foto deve ser enviada"
- **Objetivo sem frieza:** clareza primeiro; calor humano na transição
- **Perguntas reais** em waits — não "Digite 1 para sim"
- **Confirmações leves:** "Show", "Perfeito", "Entendi" — variar, não repetir em todo fluxo

---

## Estruturas por objetivo do bloco

Escolha **uma** estrutura conforme o job do nó. Não misturar apresentação completa + cobrança + menu na mesma mensagem.

### 1. Abertura / boas-vindas

**Framework:** Gancho → Ponte → Convite

```
Oi, {first_name}! 👋

*[Benefício ou curiosidade em 1 linha]*

[Convite: pergunta única OU "escolhe abaixo"]
```

- Gancho = emoção, nome ou situação — não "Bem-vindo ao nosso sistema"
- Uma pergunta ou menu — nunca os dois competindo

### 2. Apresentação de oferta / produto

**Framework:** AIDA comprimido (WhatsApp)

| A | I | D | A |
|---|---|---|---|
| Atenção (1 linha) | Interesse (o que é / para quem) | Desejo (benefício concreto do plano) | Ação (próximo passo único) |

```
*[Nome do produto/serviço — do plano]*

[1–2 linhas: transformação ou resultado — só fatos aprovados]

[CTA: "Quer ver como funciona?" / menu / wait]
```

- Prova social **só se fornecida** ("+2.000 famílias" no plano)
- Não empilhar 5 benefícios — priorizar o **#1 do contexto**

### 3. Coleta (`wait_response`)

**Framework:** Contexto mínimo → Pedido único

```
[Por que precisa — 1 linha, opcional]

*[Pergunta clara]*

(ex.: formato aceito, se relevante)
```

- **Uma pergunta por wait** — segunda pergunta = segundo bloco
- Evitar "Responda com…" robótico → "Me conta…" / "Manda…" / "Qual…"
- Placeholder mental: lead responde em 3 segundos de leitura

### 4. Menu (`interactive_menu`)

**Corpo do menu** (texto acima dos botões):

```
[1 linha de contexto]

*[Pergunta ou instrução curta]*
```

**Títulos dos botões:**

- 2–4 palavras, **verbo + objeto**: "Ver planos", "Falar com time", "Já paguei"
- Evitar "Opção 1", "Clique aqui", "Saiba mais" genérico
- **Não repetir** no corpo todas as opções que já aparecem nos botões

### 5. Pagamento / PIX

Ver [payment-comprovante.md](payment-comprovante.md). Copy:

```
*[Valor ou pacote — do plano]*

Chave PIX:
`{chave}` ou linha isolada

Recebedor: {nome}

[1 linha: o que fazer depois — "Me manda o comprovante aqui"]
```

- Valor e chave **visíveis** — negrito ou linha isolada
- Passos numerados só se ≥ 2 ações distintas
- Sem urgência falsa ("última vaga" sem dado no plano)

### 6. Entrega (preview, áudio, arquivo)

**Framework:** Momento → Entrega → Micro-dica

```
[Gancho emocional curto — 1 linha]

[mídia / preview na action seguinte]

[Dica prática — 1 linha, tom de amigo]
```

- Vários textos + mídia = **1 bloco `message`**, várias actions ([blocks.md](blocks.md))
- Pós-entrega: **uma** pergunta de feedback ou menu — não texto + menu + wait redundantes

### 7. Remarketing

Ver [remarketing.md](remarketing.md). Tom por onda:

| Onda | Intenção | Estrutura |
|------|----------|-----------|
| 1 | Lembrete gentil | "Oi — ficou pendente [X]. Ainda quer [benefício]?" |
| 2 | Valor + facilidade | Reforço do benefício **aprovado** + remover fricção ("é só responder aqui") |
| 3 | Fechamento humano | Honestidade ("último lembrete") — **sem culpa** |

- Cada onda = tom **ligeiramente** diferente — não copiar/colar a mesma frase
- Escassez/prazo **somente** se estiver no plano do usuário

### 8. Erro / handoff / suporte

**Framework:** Empatia → Clareza → Próximo passo

```
[Pede desculpas leve — 1 linha]

[O que aconteceu em linguagem simples — sem "erro 500"]

[Já estou te encaminhando / alguém te chama em X — se plano disser]
```

### 9. Notificação interna (grupo WhatsApp)

Tom **operacional**, não conversacional com lead:

```
🔔 *[Título do evento]*

[Contexto em 2–3 linhas]

Cliente: {full_name}
WhatsApp: {phone_number}
```

- Quebras `\n` reais — ver [reference.md](reference.md) § Integração HTTP
- Sem emoji decorativo; 🔔 ou ⚠️ no título basta

---

## Frameworks de conversão (escolher pelo contexto)

| Contexto do fluxo | Framework | Foco |
|-------------------|-----------|------|
| Lead frio / anúncio | **AIDA** comprimido | Curiosidade → benefício → 1 CTA |
| Dor conhecida (restauração, suporte) | **PAS** micro | Problema 1 linha → agitação leve → solução = produto |
| Wait / qualificação | **Hook–Bridge–Ask** | Gancho → por que importa → pergunta |
| Checkout / PIX | **Clareza + fricção zero** | Valor, chave, ação — nada mais |
| Pós-entrega / NPS | **Reciprocidade** | Agradecer entrega → pedido pequeno ("curtiu?") |
| Remarketing silêncio | **Lembrete → Valor → Porta aberta** | 3 ondas, tom crescente em humanidade, não pressão |

**Regra:** um bloco = **um** framework. Não fazer AIDA inteiro num menu de 3 botões.

---

## Checklist antes de gravar no MCP

```
□ Objetivo deste nó é único (informar OR pedir OR vender OR entregar)?
□ Lido em voz alta — soa humano?
□ ≤ 4 linhas antes de wait/menu (mobile)?
□ *Negrito* só em 1–3 âncoras — não bold em tudo?
□ 0–2 emojis com função?
□ Uma CTA / uma pergunta?
□ Botões do menu ≠ parágrafo repetido no corpo?
□ Variáveis encaixadas na frase (não lista de campos)?
□ \n entre blocos — não \\n literal?
□ Preços/prazos/benefícios só do plano aprovado?
```

---

## Anti-padrões (copy)

| Anti-padrão | Por quê |
|-------------|---------|
| "Prezado(a)", "Informamos", "Gentileza" | Tom SAC anos 2000 |
| Listar 4+ benefícios seguidos | Não escaneia no celular |
| "Digite SIM" / "Responda 1" | Quebra ilusão de conversa |
| Menu + parágrafo listando as mesmas opções | Redundante |
| CAIXA ALTA em frases inteiras | Agressivo no WhatsApp |
| Link nu sem contexto | Baixa confiança — 1 linha antes |
| "Estamos processando sua solicitação" | Genérico — dizer **o quê** acontece |
| Copiar tom de e-mail marketing | Parágrafos longos, "caro cliente" |
| Emoji strip / spam emoji | Amador ou bot |
| Inventar urgência, desconto, prazo | Viola regra de ouro |
| Vários blocos `message` só para quebrar copy | Usar actions no mesmo nó |

---

## Exemplos genéricos (estrutura — adaptar ao plano)

### Antes → depois (boas-vindas)

**Robótico:**
```
Bem-vindo! Somos a empresa X. Oferecemos diversos produtos. Selecione uma opção abaixo para continuar o atendimento.
```

**Humanizado:**
```
Oi! 👋

Aqui você monta seu pedido em poucos passos — bem tranquilo.

*Por onde quer começar?*
```
*(botões no menu — não listar opções no texto)*

### Antes → depois (wait)

**Robótico:**
```
Por favor, envie uma foto de rosto frontal para prosseguirmos com a análise do seu cadastro.
```

**Humanizado:**
```
Pra eu gerar seu preview, preciso de *uma foto sua de rosto* — bem iluminada, de frente.

Pode mandar aqui 📎
```

### Antes → depois (remarketing onda 1)

**Robótico:**
```
Notamos que você não concluiu sua compra. Retorne ao fluxo para finalizar.
```

**Humanizado:**
```
Oi — vi que ficou pendente por aqui.

Ainda quer seguir? É só me responder 🙂
```

---

## Integração com outras docs

| Tópico | Arquivo |
|--------|---------|
| Onde colocar copy no fluxo | [sequencing.md](sequencing.md) |
| Menu + IA + texto livre | [ai-copilot-pattern.md](ai-copilot-pattern.md) |
| RMKT ondas | [remarketing.md](remarketing.md) |
| PIX / comprovante | [payment-comprovante.md](payment-comprovante.md) |
| Multi-action no mesmo nó | [blocks.md](blocks.md) § message |
| Variáveis / campos | [variables.md](variables.md) |

---

## Fluxo de trabalho do agente

1. **Plano aprovado** com fatos (preço, nome produto, tom de marca se houver)
2. Ler **este arquivo** + objetivo do nó no fluxograma
3. Escrever draft → **checklist** → mostrar ao usuário se copy nova ou sensível
4. Gravar no MCP com `message_text` final — texto **exato**, sem placeholder
5. Revisar no celular (preview mental: 390px de largura)

**Copy existente robótica:** propor rewrite seguindo este guia — **não** alterar fatos comerciais sem OK.
