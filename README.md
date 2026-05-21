# Bot Telegram — Assistente do Síndico

## Como configurar

### 1. Criar o bot no Telegram
1. Abra o Telegram e busque por **@BotFather**
2. Digite `/newbot` e siga as instruções
3. Anote o **token** gerado (ex: `123456:ABC-DEF...`)

### 2. Obter seu Chat ID
1. Inicie uma conversa com **@userinfobot** no Telegram
2. Ele mostrará seu **Chat ID** numérico
3. Anote — será usado para restringir o bot só a você

### 3. Obter a API Key do Claude
1. Acesse https://console.anthropic.com
2. Vá em **API Keys** → **Create Key**
3. Anote a chave gerada

### 4. Deploy no Railway (gratuito)

1. Acesse https://railway.app e crie conta
2. Clique em **New Project → Deploy from GitHub**
   - Faça upload desta pasta como repositório GitHub, ou
   - Use **New Project → Empty Project → Add Service → GitHub Repo**
3. Nas **Variables** do serviço, adicione:
   ```
   TELEGRAM_TOKEN=seu_token_aqui
   ANTHROPIC_API_KEY=sua_chave_aqui
   ALLOWED_CHAT_ID=seu_chat_id_aqui
   ```
4. Railway detecta o `Procfile` e sobe automaticamente

### 5. Usando o bot
- `/start` — inicia e mostra dados do condomínio
- `/limpar` — apaga o histórico da conversa
- `/ajuda` — mostra exemplos de uso
- Qualquer texto — conversa com o assistente

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `TELEGRAM_TOKEN` | ✅ | Token do BotFather |
| `ANTHROPIC_API_KEY` | ✅ | Chave da API Claude |
| `ALLOWED_CHAT_ID` | ⬜ | Restringe ao seu chat (recomendado) |
