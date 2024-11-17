import datetime
import os
from pathlib import Path


import bot
from bot import ai_helper
from bot.utils import email_to_send
from bot.utils.rag import query_rag
from bot.utils import rag
from bot.utils import document_chunker
from bot.utils import brainstorm
from bot.utils import text_to_speech_impl
from bot.utils import translate_english
from bot.utils import doc_summary
from bot.utils import document_loader
from dotenv import load_dotenv
from bot.Database import database as db
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.utils.vector_db import save_to_chroma

(
    SELECTING,
    SUMMARIZE_PAPER,
    BRAINSTORM,
    ASSISTANT,
    SYBILLA
) = range(5)

load_dotenv()
SALUTE_SCOPE = os.getenv("SPEECH_SCOPE")
SALUTE_AUTH_DATA = os.getenv("SPEECH-AUTH-DATA")

keyboard = [["summarize", "brainstorm"], ["assistant", "sybilla"]]


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
4. brainstorm: Давай поищем какие-нибудь научные работы!
5. sybilla: Давай обсуждаем какие-то научные работы
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
            text="Давай поищем какие-нибудь научные работы!",
        )
        return BRAINSTORM
    elif text == "assistant":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Спроси про что-то на научном"
        )
        return ASSISTANT
    elif text == "sybilla":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Отправь научную работу который хочешь суммизировать!"
        )
        return SYBILLA

    return SELECTING


async def summarize_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.document.file_id
    filename = update.message.document.file_name.strip()
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(filename)
    text_to_send = await bot.utils.doc_summary.text_from_file(
        filename, update, context
    )
    if text_to_send.split(":")[0]=="err":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Эх что-то пошло не так: "
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_to_send[1]
        )
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_to_send)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Подождите 30 секудн чтобы получить аудио суммари ",
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Вот ваши аудио-суммари: "
        )
        summary_file = open(f"{filename}.txt", "w+")
        summary_file.write(text_to_send)
        summary_file.close()
        await text_to_speech(f"{filename}.txt", update=update, context=context)


async def brainstorm_a_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("email:"):
        if db.checking_user_exits(update.effective_user.id):
            if db.checking_user_email_exits(user_id=update.effective_user.id) == "":
                email = update.message.text.split(":")[1]
                userid = update.effective_user.id
                db.User.update(email=email).where(db.User.userid == userid).execute()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="получил ваш email: " f"{email}",
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Есл хотите получить резултать в данном email",
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="отправьте текст в формате mail:{что вы хотите}",
                )
        else:
            email = update.message.text.split(":")[1]
            db.User.create(
                userid=update.effective_user.id,
                name=update.effective_user.first_name,
                username=update.effective_user.username,
                chromacollection="",
                email=email,
                usertoken="",
                gigachat_token="",
                lastGen=datetime.datetime.now(),
                last_gen_gigachat=datetime.datetime.now(),
            )
    elif update.message.text.startswith("mail:"):
        if db.checking_user_email_exits(user_id=update.effective_user.id) != "":
            email = db.User.get(userid=update.effective_user.id).email
            text_to_find = update.message.text.split(":")[1]
            text_to_find_enf = await translate_english.translate_text(text_to_find)
            doc_to_send = await brainstorm.generate_find_the_paper(
                user_query=text_to_find_enf
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="чекните ваш mail"
            )
            email_to_send.send_mail(email_to=email, texttosend=doc_to_send)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="добавь mail"
            )

    elif update.message.text.startswith("nml:"):
        text_to_find = update.message.text.split(":")[1]
        text_to_find_enf = await translate_english.translate_text(text_to_find)
        doc = await brainstorm.generate_find_the_paper(user_query=text_to_find_enf)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=doc)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="nml: , email: , mail:"
        )


async def discuss_a_paper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_root = Path(__file__).parent.parent
    try:
        pdf_dir = bot_root / "researchpdf"
        if not pdf_dir.exists():
            try:
                pdf_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print("Error: Bot doesn't have permission to create directory")
                return
            except Exception as e:
                print(f"Error creating directory: {str(e)}")
                return

        if update.message.text is None:
            file_id = update.message.document.file_id
            filename = update.message.document.file_name.strip()
            # Convert the PosixPath to string when combining with filename
            file_path = str(pdf_dir / filename)
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(file_path)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Документы загружены! отправь еще если хочешь!"
            )
        elif update.message.text.startswith("ask:"):
            documents = await document_loader.load_data(str(pdf_dir))  # Convert path to string
            chunk = await document_chunker.split_the_documents(documents)
            chroma_path = bot_root / "chromadb"
            if not chroma_path.exists():
                try:
                    chroma_path.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    print("Error: Bot doesn't have permission to create directory")
                    return
                except Exception as e:
                    print(f"Error creating directory: {str(e)}")
                    return

            await save_to_chroma(chunk, str(chroma_path))  # Convert path to string
            query_text = update.message.text.split(":", 1)[1].strip()  # Use maxsplit=1 and strip()
            response = await rag.query_rag(query_text, str(chroma_path))  # Convert path to string
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    except Exception as e:
        error_message = f"Error processing file: {str(e)}"
        print(error_message)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message
        )
        return None

    # TODO: File is downloaded, convert to vector store
    # TODO: Can split the user text and then do the thing if he asks by "ask:"




async def text_to_speech(Filename, update: Update, context: ContextTypes.DEFAULT_TYPE):
    Data = await text_to_speech_impl.text_to_speech_impl(
        filename=Filename,
        update=update,
        context=context,
        SALUTE_AUTH_DATA=SALUTE_AUTH_DATA,
        SALUTE_SCOPE=SALUTE_SCOPE,
    )
    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=Data)


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Найду и расскажу:"
    )
    text = update.message.text
    result = await ai_helper.ai_help(text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)


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
                filters.Regex("^(summarize|brainstorm|assistant|sybilla)$"),
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
        SYBILLA: [
            MessageHandler(
                (filters.Document or filters.TEXT) and ~(filters.COMMAND | filters.Regex("^End|end$")),
                discuss_a_paper,
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
