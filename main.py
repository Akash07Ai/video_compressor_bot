from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import subprocess, os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("360p", callback_data="360"),
         InlineKeyboardButton("480p", callback_data="480"),
         InlineKeyboardButton("720p", callback_data="720")]
    ]
    await update.message.reply_text(
        "👋 Send me a video, then choose resolution 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    await file.download_to_drive("input.mp4")
    context.user_data["video_ready"] = True
    await update.message.reply_text("✅ Video received! Now select resolution (360p/480p/720p).")

async def compress_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("video_ready"):
        await query.edit_message_text("Please send a video first.")
        return

    res = query.data
    out = f"output_{res}p.mp4"

    subprocess.run([
        "ffmpeg", "-i", "input.mp4", "-vf", f"scale=-1:{res}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", out
    ])

    await query.message.reply_video(video=open(out, "rb"), caption=f"🎬 Compressed to {res}p ✅")

    os.remove("input.mp4")
    os.remove(out)
    context.user_data.clear()

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(CallbackQueryHandler(compress_video))
app.run_polling()

