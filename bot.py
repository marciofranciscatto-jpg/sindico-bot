import os
import anthropic
from telegram import Update, constants
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    filters, ContextTypes
)

TOKEN    = os.environ["TELEGRAM_TOKEN"]
API_KEY  = os.environ["ANTHROPIC_API_KEY"]
ALLOWED  = os.environ.get("ALLOWED_CHAT_ID", "")   # deixe vazio para aceitar todos

client = anthropic.Anthropic(api_key=API_KEY)

SYSTEM = """Você é o assistente pessoal do síndico do Condomínio Edifício Tomaz Pompeu,
localizado na Rua Tomaz Pompeu, 171, Bairro Meireles, Fortaleza-CE.
O condomínio possui 18 andares, 4 apartamentos por andar, totalizando 72 unidades,
com taxa condominial atual de R$ 1.100,00 e arrecadação mensal de R$ 79.200,00.

Você auxilia em todos os assuntos de gestão condominial: administrativos, reformas,
inadimplência, comunicação, relacionamento com condôminos, recursos humanos e segurança.
Utilize como referência a legislação brasileira (Código Civil – Lei 10.406/2002,
Lei 4.591/64, Lei 8.245/91, NRs do Ministério do Trabalho) e as melhores práticas.

Seja preciso, assertivo, educado e cordial. Nunca invente informações ou sugira algo
que confronte a legislação. Quando solicitado, elabore documentos como notificações,
circulares, atas e comunicados já formatados para uso imediato."""

# Histórico por chat (memória de curto prazo)
historico: dict[str, list] = {}


def permitido(chat_id: str) -> bool:
    return not ALLOWED or chat_id == ALLOWED


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    if not permitido(cid):
        return
    historico[cid] = []
    await update.message.reply_text(
        "👋 *Olá, Síndico!*\n\n"
        "Sou seu assistente de gestão condominial. Pode me enviar qualquer dúvida, "
        "solicitação ou pedido de documento.\n\n"
        "🏢 *Rua Tomaz Pompeu, 171 – Meireles, Fortaleza/CE*\n"
        "📐 72 unidades · 18 andares\n"
        "💰 R$ 1.100,00 / mês por unidade\n\n"
        "Comandos disponíveis:\n"
        "/start — reiniciar\n"
        "/limpar — apagar histórico\n"
        "/ajuda — ver exemplos de uso",
        parse_mode=constants.ParseMode.MARKDOWN,
    )


async def cmd_limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    historico[cid] = []
    await update.message.reply_text("🗑️ Histórico apagado. Nova conversa iniciada.")


async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    if not permitido(cid):
        return
    await update.message.reply_text(
        "💡 *Exemplos de uso:*\n\n"
        "• _Redija uma notificação de vazamento para o apto 802_\n"
        "• _Como cobrar um condômino inadimplente?_\n"
        "• _Quais as obrigações do síndico segundo o Código Civil?_\n"
        "• _Crie uma circular sobre obras no elevador_\n"
        "• _Como convocar uma assembleia extraordinária?_\n"
        "• _Modelo de ata de assembleia_\n"
        "• _Quais manutenções obrigatórias devo fazer?_",
        parse_mode=constants.ParseMode.MARKDOWN,
    )


async def handle_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    if not permitido(cid):
        return

    texto = update.message.text
    if cid not in historico:
        historico[cid] = []

    historico[cid].append({"role": "user", "content": texto})

    # Mantém no máximo 20 turnos (40 mensagens)
    if len(historico[cid]) > 40:
        historico[cid] = historico[cid][-40:]

    await update.message.chat.send_action("typing")

    try:
        resposta = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM,
            messages=historico[cid],
        )
        reply = resposta.content[0].text
        historico[cid].append({"role": "assistant", "content": reply})

        # Telegram tem limite de 4096 chars por mensagem
        for i in range(0, len(reply), 4096):
            await update.message.reply_text(reply[i : i + 4096])

    except Exception as err:
        await update.message.reply_text(f"❌ Erro ao processar: {err}")


async def handle_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    if not permitido(cid):
        return
    legenda = update.message.caption or "Analise esta imagem no contexto condominial."
    await update.message.reply_text(
        "📷 Recebi a imagem. No momento processo apenas texto. "
        "Descreva o que vê e posso ajudar com orientações."
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("limpar", cmd_limpar))
    app.add_handler(CommandHandler("ajuda",  cmd_ajuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_texto))
    app.add_handler(MessageHandler(filters.PHOTO, handle_foto))
    print("Bot rodando…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
