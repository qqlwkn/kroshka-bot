import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN.")

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("🔥 Новинки", callback_data="new")],
        [InlineKeyboardButton("🛒 Мой заказ", callback_data="cart")],
        [InlineKeyboardButton("📍 Где мы находимся", callback_data="location")],
        [InlineKeyboardButton("📞 Связаться с нами", callback_data="contact")],
    ])

def catalog_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥐 Выпечка", callback_data="cat_bakery")],
        [InlineKeyboardButton("🍰 Десерты", callback_data="cat_desserts")],
        [InlineKeyboardButton("🍬 Сладости", callback_data="cat_sweets")],
        [InlineKeyboardButton("🍪 Печенье и вафли", callback_data="cat_cookies")],
        [InlineKeyboardButton("☕ Кофе и напитки", callback_data="cat_drinks")],
        [InlineKeyboardButton("🎁 Наборы", callback_data="cat_sets")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="home")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍰 <b>КРОШКА</b>\n\n"
        "Свежая выпечка, десерты и сладости.\n"
        "Заказывайте заранее — забирайте без ожидания.\n\n"
        "Выберите раздел:",
        parse_mode="HTML", reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    d=q.data
    if d=="home":
        await q.edit_message_text("🍰 <b>КРОШКА</b>\n\nВыберите раздел:",parse_mode="HTML",reply_markup=main_menu())
    elif d=="catalog":
        await q.edit_message_text("🛍 <b>КАТАЛОГ</b>\n\nВыберите категорию:",parse_mode="HTML",reply_markup=catalog_menu())
    elif d=="new":
        await q.edit_message_text("🔥 <b>НОВИНКИ</b>\n\nРаздел пока готовится 👀",parse_mode="HTML",reply_markup=back())
    elif d=="cart":
        await q.edit_message_text("🛒 <b>МОЙ ЗАКАЗ</b>\n\nКорзина пока пустая.",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍 Открыть каталог",callback_data="catalog")],[InlineKeyboardButton("⬅️ Назад",callback_data="home")]]))
    elif d=="location":
        await q.edit_message_text("📍 <b>МЫ НАХОДИМСЯ ЗДЕСЬ</b>\n\nАдрес магазина добавим после открытия.",parse_mode="HTML",reply_markup=back())
    elif d=="contact":
        await q.edit_message_text("📞 <b>СВЯЗАТЬСЯ С НАМИ</b>\n\nТелефон и Telegram добавим здесь.",parse_mode="HTML",reply_markup=back())
    elif d.startswith("cat_"):
        names={"cat_bakery":"🥐 Выпечка","cat_desserts":"🍰 Десерты","cat_sweets":"🍬 Сладости","cat_cookies":"🍪 Печенье и вафли","cat_drinks":"☕ Кофе и напитки","cat_sets":"🎁 Наборы"}
        await q.edit_message_text(f"<b>{names[d]}</b>\n\nТовары добавим следующим этапом.",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ К каталогу",callback_data="catalog")]]))

def back():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад",callback_data="home")]])

app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(button))
print("KroshkaSweetBot запущен. Ctrl+C — остановить.")
app.run_polling()
