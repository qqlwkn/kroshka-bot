import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

PRODUCTS = {
    "bakery": [("🥐 Круассан",120),("🍩 Пончик",90),("🥨 Слойка",110)],
    "desserts": [("🍰 Чизкейк порционный",220),("🧁 Маффин шоколадный",140),("🍮 Десерт в стаканчике",180)],
    "sweets": [("🍫 Шоколад",150),("🍬 Конфеты",250),("🍭 Мармелад",180)],
    "cookies": [("🍪 Печенье",160),("🧇 Вафли",140),("🍪 Печенье с шоколадом",190)],
    "drinks": [("☕ Кофе",150),("🥤 Лимонад",120),("🧃 Сок",130)],
    "sets": [("🎁 Набор «Крошка»",590),("🎁 Сладкий набор",790)]
}
NAMES = {"bakery":"🥐 Выпечка","desserts":"🍰 Десерты","sweets":"🍬 Сладости","cookies":"🍪 Печенье и вафли","drinks":"☕ Кофе и напитки","sets":"🎁 Наборы"}
carts = {}

def menu():
    return ReplyKeyboardMarkup([["🛍 Каталог","🔥 Новинки"],["🛒 Мой заказ","📍 Мы находимся здесь"],["📞 Связаться с нами"]], resize_keyboard=True)

def catalog():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥐 Выпечка",callback_data="cat:bakery"),InlineKeyboardButton("🍰 Десерты",callback_data="cat:desserts")],
        [InlineKeyboardButton("🍬 Сладости",callback_data="cat:sweets"),InlineKeyboardButton("🍪 Печенье и вафли",callback_data="cat:cookies")],
        [InlineKeyboardButton("☕ Кофе и напитки",callback_data="cat:drinks"),InlineKeyboardButton("🎁 Наборы",callback_data="cat:sets")]
    ])

def price(name):
    for items in PRODUCTS.values():
        for n,p in items:
            if n == name: return p
    return 0

def cart_text(uid):
    c=carts.get(uid,{})
    if not c: return "🛒 <b>Ваш заказ пуст</b>\n\nДобавьте товары из каталога."
    total=0; out=["🛒 <b>Ваш заказ</b>\n"]
    for n,q in c.items():
        s=price(n)*q; total+=s; out.append(f"{n} × {q} — {s} ₽")
    out.append(f"\n<b>Итого: {total} ₽</b>")
    return "\n".join(out)

def cart_buttons(uid):
    rows=[]
    for n,q in carts.get(uid,{}).items():
        rows.append([InlineKeyboardButton("➖",callback_data="dec:"+n),InlineKeyboardButton(f"{n} × {q}",callback_data="noop"),InlineKeyboardButton("➕",callback_data="inc:"+n)])
    if carts.get(uid):
        rows += [[InlineKeyboardButton("✅ Оформить предзаказ",callback_data="checkout")],[InlineKeyboardButton("🗑 Очистить",callback_data="clear")]]
    rows.append([InlineKeyboardButton("🛍 Каталог",callback_data="catalog")])
    return InlineKeyboardMarkup(rows)

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 <b>Добро пожаловать в «Крошку»!</b>\n\nСладости, выпечка и десерты. Выбирайте товары и оформляйте предзаказ.",parse_mode="HTML",reply_markup=menu())

async def catalog_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍 <b>Каталог «Крошки»</b>\n\nВыберите категорию:",parse_mode="HTML",reply_markup=catalog())

async def cart_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    await update.message.reply_text(cart_text(uid),parse_mode="HTML",reply_markup=cart_buttons(uid))

async def callbacks(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.from_user.id; data=q.data
    if data=="catalog":
        await q.edit_message_text("🛍 <b>Каталог «Крошки»</b>\n\nВыберите категорию:",parse_mode="HTML",reply_markup=catalog()); return
    if data.startswith("cat:"):
        key=data[4:]
        kb=[[InlineKeyboardButton(f"{n} — {p} ₽",callback_data="add:"+n)] for n,p in PRODUCTS[key]]
        kb.append([InlineKeyboardButton("⬅️ Категории",callback_data="catalog")])
        await q.edit_message_text(f"<b>{NAMES[key]}</b>\n\nВыберите товар:",parse_mode="HTML",reply_markup=InlineKeyboardMarkup(kb)); return
    if data.startswith("add:"):
        n=data[4:]; carts.setdefault(uid,{})[n]=carts.get(uid,{}).get(n,0)+1
        await q.answer("Добавлено в заказ ✅"); return
    if data.startswith("inc:"):
        n=data[4:]; carts.setdefault(uid,{})[n]=carts.get(uid,{}).get(n,0)+1
    elif data.startswith("dec:"):
        n=data[4:]
        if n in carts.get(uid,{}):
            carts[uid][n]-=1
            if carts[uid][n]<=0: del carts[uid][n]
    elif data=="clear": carts[uid]={}
    elif data=="checkout":
        if not carts.get(uid): await q.answer("Корзина пустая",show_alert=True); return
        context.user_data["order_details"]=True
        await q.message.reply_text("📦 <b>Предзаказ</b>\n\nНапишите: имя + телефон + желаемое время забора.\n\nНапример: Антон, +7 900 000-00-00, завтра 18:00",parse_mode="HTML"); return
    else: return
    await q.edit_message_text(cart_text(uid),parse_mode="HTML",reply_markup=cart_buttons(uid))

async def text(update:Update,context:ContextTypes.DEFAULT_TYPE):
    t=update.message.text; uid=update.effective_user.id
    if context.user_data.get("order_details"):
        order=cart_text(uid); details=t
        if ADMIN_CHAT_ID:
            try: await context.bot.send_message(int(ADMIN_CHAT_ID),f"🔔 <b>Новый предзаказ «Крошка»</b>\n\n{order}\n\n👤 {details}",parse_mode="HTML")
            except Exception: logging.exception("admin notification failed")
        carts[uid]={}; context.user_data["order_details"]=False
        await update.message.reply_text("✅ <b>Заявка принята!</b>\n\nМы свяжемся с вами для подтверждения.",parse_mode="HTML",reply_markup=menu()); return
    if t=="🛍 Каталог": await catalog_cmd(update,context)
    elif t=="🛒 Мой заказ": await cart_cmd(update,context)
    elif t=="🔥 Новинки": await update.message.reply_text("🔥 <b>Новинки</b>\n\nСюда добавим новые позиции.",parse_mode="HTML",reply_markup=menu())
    elif t=="📍 Мы находимся здесь": await update.message.reply_text("📍 <b>«Крошка»</b>\n\nАдрес и график работы добавим перед запуском.",parse_mode="HTML",reply_markup=menu())
    elif t=="📞 Связаться с нами": await update.message.reply_text("📞 <b>Связаться с нами</b>\n\nТелефон и Telegram добавим перед запуском.",parse_mode="HTML",reply_markup=menu())
    else: await update.message.reply_text("Выберите раздел в меню 👇",reply_markup=menu())

def main():
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN is not set")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("catalog",catalog_cmd)); app.add_handler(CommandHandler("cart",cart_cmd))
    app.add_handler(CallbackQueryHandler(callbacks)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text))
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__": main()
