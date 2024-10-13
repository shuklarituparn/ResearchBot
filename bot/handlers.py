import datetime
import os

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
(
    SELECTING,
    SUMMARIZE_PAPER,
    BRAINSTORM,
    ASSISTANT,
) = range(4)

load_dotenv()
SALUTE_SCOPE = os.getenv("SPEECH_SCOPE")
SALUTE_AUTH_DATA = os.getenv("SPEECH-AUTH-DATA")

keyboard = [["summarize", "brainstorm"], ["assistant"]]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
Добро пожаловать в бот для помочь по научной работе!! 
Пиши /help чтобы узнать больше!  
    """
    markUP = ReplyKeyboardMarkup(keyboard)
    print(update.effective_user.first_name)
    await update.message.reply_text(text=text, reply_markup=markUP)
    return SELECTING


async def help_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""
    Используйте следующие команды чтобы работать с ботом

1. /start   чтобы снова запустить бот
2. /help    Чтобы получить помочь
3. summarize: Отправь научную работу который хочешь суммизировать! Также получи аудио суммари
4. brainstorm: Давайте поищем какие-нибудь научные работы!
""",
    )


async def task_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "summarize":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отправь научную работу который хочешь суммизировать!",
        )
        return SUMMARIZE_PAPER
    elif text == "brainstorm":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Давайте поищем какие-нибудь научные работы!",
        )
        return BRAINSTORM
    elif text == "assistant":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Спроси про что-то на научном"
        )
        return ASSISTANT

    return SELECTING


async def summarize_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.document.file_id
    filename = update.message.document.file_name.strip()
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(filename)



async def brainstorm_a_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def text_to_speech(Filename, update: Update, context: ContextTypes.DEFAULT_TYPE):
   pass


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пока пока!")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Был рад вам помочь!"
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING: [
            MessageHandler(
                filters.Regex("^(summarize|brainstorm|assistant)$"),
                task_selector,
            ),
        ],
        SUMMARIZE_PAPER: [
            MessageHandler(
                filters.Document and ~(filters.COMMAND | filters.Regex("^End|end$")),
                summarize_paper,
            ),
        ],
        BRAINSTORM: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^End|end$")),
                brainstorm_a_paper,
            ),
        ],
        ASSISTANT: [
            MessageHandler(
                filters.TEXT and ~(filters.COMMAND | filters.Regex("^End|end$")),
                ask_ai,
            ),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^End|end$"), end)],
    name="my_conv",
    persistent=True,
)

help_handler = CommandHandler("help", help_user)
