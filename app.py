from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import json
import os
import logging

# Loglama sazlamalary
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7983997462:AAE7OlRTGdoAH9hv9CQ5h56a5gJHjweyjGA"

# Admin ID
ADMIN_USER_ID = 5330851495

# VPN kody
vpn_code = "ss://YWVzLTI1Ni1jZmI6OWMwNzUyZTM5ZWY2ZjIyYw@203.18.98.194:167"

# Faýl atlary
USERS_FILE = "ulanyjylar.json"
CHANNELS_FILE = "kanallar.json"

# Ulanyjylary ýüklemek/ýazmak
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

# Kanallary ýüklemek/ýazmak
def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        data = {
            "ADMIN_KANALLAR": ["@HTTP_CUST0M", "@Hiddify_tm"],
            "BEÝLEKI_KANALLAR": [
                "@PLAT1NUMS1",
                "@FULL_SERWERS",
                "@Turkmen_Shadowsocks",
                "@Dragonvp_n",
                "@utiha_servers",
                "@PLAT1NUM_CHAT",
                "https://t.me/addlist/PcDP7B2IRLNiZDhi"
            ]
        }
        save_channels(data)
        return data
    try:
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"ADMIN_KANALLAR": [], "BEÝLEKI_KANALLAR": []}

def save_channels(data):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Başlangyç maglumatlar
users = load_users()
channels = load_channels()

# /start buýrugy
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)
    save_users(users)

    keyboard = []

    # Hökman kanallar
    for channel in channels["ADMIN_KANALLAR"]:
        if channel.startswith("@"):
            keyboard.append([InlineKeyboardButton(f"🔗 {channel}", url=f"https://t.me/{channel[1:]}")])
        else:
            keyboard.append([InlineKeyboardButton(f"🔗 {channel}", url=channel)])

    # Beýleki kanallar
    for channel in channels["BEÝLEKI_KANALLAR"]:
        if channel.startswith("@"):
            keyboard.append([InlineKeyboardButton(f"🔗 {channel}", url=f"https://t.me/{channel[1:]}")])
        elif channel.startswith("http"):
            keyboard.append([InlineKeyboardButton("🔗 Kanallaryň sanawy", url=channel)])

    # Barlag düwmesi
    keyboard.append([InlineKeyboardButton("✅ Agzalygy barla ✅", callback_data="check_sub")])

    await update.effective_message.reply_text(
        "✨ Aşakdaky kanallara agza bolmasaňyz, kody alyp bilmersiňiz. Ilki kanallara goşulun:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Agzalyk barlagy
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    not_joined = []

    for channel in channels["ADMIN_KANALLAR"]:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except Exception as e:
            logger.error(f"Ýalňyşlyk (Kanal: {channel}): {e}")
            not_joined.append(channel)

    if not_joined:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Aşakdaky kanallara entek goşulmadyňyz:\n"
                f"{chr(10).join(not_joined)}\n\n"
                "Täzeden barlamak üçin /start ýazyp, '✅ Agzalygy barla ✅' düwmesine basyň."
            )
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 Agzalygyňyz tassyklanyldy!\n\n"
                f"**VPN kodyňyz:**\n\n"
                f"`{vpn_code}`\n\n"
                "✅ Kody göçürip VPN programmaňyza giriň."
            ),
            parse_mode="Markdown"
        )

# Admin paneli
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Bu buýrugy ulanyp bilmersiňiz!")
        return

    keyboard = [
        [InlineKeyboardButton("Kanallary görkez", callback_data="view_channels")],
        [InlineKeyboardButton("➕ Kanal goş", callback_data="add_channel")],
        [InlineKeyboardButton("➖ Kanal aýyr", callback_data="remove_channel")],
        [InlineKeyboardButton("VPN kodyny üýtget", callback_data="change_vpn_code")],
        [InlineKeyboardButton("Ulanyjylaryň sany", callback_data="user_count")],
    ]

    await update.message.reply_text(
        "👑 Admin paneli - Aşakdaky opsiýalary saýlaň:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Admin jogap beriji
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id != ADMIN_USER_ID:
        await query.edit_message_text("⛔ Bu amaly ýerine ýetirip bilmersiňiz!")
        return

    data = query.data

    if data == "view_channels":
        text = "📋 ADMIN KANALLAR:\n" + "\n".join(channels["ADMIN_KANALLAR"])
        text += "\n\n📋 BEÝLEKI KANALLAR:\n" + "\n".join(channels["BEÝLEKI_KANALLAR"])
        await query.edit_message_text(text)
    elif data == "add_channel":
        await query.edit_message_text(
            "➕ Goşuljak kanaly şu formatda ýazyň:\n\n`admin @kanal_ady` ýa-da `other @kanal_ady`",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_add_channel"] = True
    elif data == "remove_channel":
        await query.edit_message_text(
            "➖ Aýryljak kanaly şu formatda ýazyň:\n\n`admin @kanal_ady` ýa-da `other @kanal_ady`",
            parse_mode="Markdown"
        )
        context.user_data["awaiting_remove_channel"] = True
    elif data == "change_vpn_code":
        await query.edit_message_text("✏️ Täze VPN koduny giriziň:")
        context.user_data["awaiting_vpn_code"] = True
    elif data == "user_count":
        await query.edit_message_text(f"👥 Jemi ulanyjylar: {len(users)}")

# Admin habar beriji
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        return

    text = update.message.text

    if context.user_data.get("awaiting_add_channel"):
        try:
            type_, channel = text.split()
            if type_ == "admin":
                channels["ADMIN_KANALLAR"].append(channel)
            elif type_ == "other":
                channels["BEÝLEKI_KANALLAR"].append(channel)
            save_channels(channels)
            await update.message.reply_text(f"✅ Kanal goşuldy: {channel}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Nädogry format! Dogry format: `admin @kanal` ýa-da `other @kanal`\nÝalňyşlyk: {e}")
        context.user_data["awaiting_add_channel"] = False

    elif context.user_data.get("awaiting_remove_channel"):
        try:
            type_, channel = text.split()
            if type_ == "admin" and channel in channels["ADMIN_KANALLAR"]:
                channels["ADMIN_KANALLAR"].remove(channel)
                await update.message.reply_text(f"✅ Kanal aýryldy: {channel}")
            elif type_ == "other" and channel in channels["BEÝLEKI_KANALLAR"]:
                channels["BEÝLEKI_KANALLAR"].remove(channel)
                await update.message.reply_text(f"✅ Kanal aýryldy: {channel}")
            else:
                await update.message.reply_text("⚠️ Kanal tapylmady!")
            save_channels(channels)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Nädogry format! Dogry format: `admin @kanal` ýa-da `other @kanal`\nÝalňyşlyk: {e}")
        context.user_data["awaiting_remove_channel"] = False

    elif context.user_data.get("awaiting_vpn_code"):
        global vpn_code
        vpn_code = text
        await update.message.reply_text(f"✅ VPN kody üýtgedildi:\n\n`{vpn_code}`", parse_mode="Markdown")
        context.user_data["awaiting_vpn_code"] = False

# Boty işe girizmek
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(check_sub, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(view_channels|add_channel|remove_channel|change_vpn_code|user_count)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input))

    logger.info("🤖 Bot işe girizilýär...")
    app.run_polling()

if __name__ == "__main__":
    main()
