import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time

# Tumhara API Token
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo' 
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# 👑 ONLY ONE BOSS
BOSS_ADMIN = 'Ben_ADFA'

# Filters
bad_words = ['gali1', 'gali2', 'badword', 'spam', 'scam', 'fuck', 'shit', 'bitch', 'asshole'] 

# --- PREMIUM UI STRINGS ---
DIVIDER = "━━━━━━━━━━━━━━━━━━━"

RULES_TEXT = f"""📌 *Code on the Go - Official Rules*
{DIVIDER}
1️⃣ *Be respectful:* No harassment or personal attacks.
2️⃣ *Stay on topic:* Keep conversation focused on COTG.
3️⃣ *English only:* So everyone can understand.
4️⃣ *No spam/ads:* Unauthorized promos will be removed.
5️⃣ *Appropriate content:* No hateful or adult content.
6️⃣ *Protect privacy:* Don't share personal info.
7️⃣ *Admin moderation:* Severe violations result in removal.
{DIVIDER}
*Thank you for keeping our community clean!* 😇"""

IDE_INFO = f"""🚀 *About Code on the Go (COTG)*
{DIVIDER}
COTG is your ultimate standalone mobile IDE. Build real Android apps completely on your phone, even offline! 📱💻

✨ *Key Features:*
• Real-time Android app compilation.
• Modern Kotlin & Java support.
• No PC or internet required.

🌐 *Website:* [appdevforall.org/codeonthego](https://www.appdevforall.org/codeonthego/)
🎥 *YouTube:* [App Dev for All](https://youtube.com/@appdevforall)
{DIVIDER}"""

# --- PREMIUM VIP BUTTON LAYOUT ---
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/CodeOnTheGoOfficial"))
    markup.add(InlineKeyboardButton("🎥 Subscribe on YouTube", url="https://youtube.com/@appdevforall"))
    
    btn_rules = InlineKeyboardButton("📜 Group Rules", callback_data="show_rules")
    btn_ide = InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info")
    markup.row(btn_rules, btn_ide)
    
    btn_admin = InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN}")
    btn_close = InlineKeyboardButton("❌ Close", callback_data="close_menu")
    markup.row(btn_admin, btn_close)
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main"))
    markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

# --- COMMANDS ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (f"Hello *{message.from_user.first_name}*! 👋\n"
            f"{DIVIDER}\n"
            f"I am **CG**, the highly advanced AI Assistant for Code on the Go.\n\n"
            f"How can I assist you today? Select an option below:")
    bot.reply_to(message, text, reply_markup=get_main_menu())

# --- SECRET ADMIN COMMAND: /status ---
@bot.message_handler(commands=['status'])
def bot_status(message):
    username = message.from_user.username
    if username == BOSS_ADMIN:
        bot.reply_to(message, f"🟢 **CG System Status: ONLINE & ACTIVE**\n{DIVIDER}\nBoss @{username}, all filters are running perfectly at 100% capacity! 🚀")

# --- VIP FEATURE: /report COMMAND ---
@bot.message_handler(commands=['report'])
def report_message(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, f"🚨 **REPORTED!**\nAdmin @{BOSS_ADMIN}, please review this message when you are online.")
        bot.delete_message(message.chat.id, message.message_id) 
    else:
        warning = bot.reply_to(message, "⚠️ To report someone, you must **reply** to their message and type `/report`.")
        time.sleep(5)
        bot.delete_message(message.chat.id, warning.message_id)
        bot.delete_message(message.chat.id, message.message_id)

# --- INTERACTIVE BUTTON CLICKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=RULES_TEXT, reply_markup=get_back_button(), parse_mode='Markdown')
    elif call.data == "show_ide_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=IDE_INFO, reply_markup=get_back_button(), parse_mode='Markdown', disable_web_page_preview=True)
    elif call.data == "back_to_main":
        text = (f"Hello again! 👋\n{DIVIDER}\n"
                f"I am **CG**, the highly advanced AI Assistant for Code on the Go.\n\n"
                f"How can I assist you today?")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=text, reply_markup=get_main_menu(), parse_mode='Markdown')
    elif call.data == "close_menu":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

# --- VIP WELCOME MESSAGE ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            continue
            
        name = new_member.username if new_member.username else new_member.first_name
        welcome_text = (f"Welcome to the community, @{name}! 🎉\n"
                        f"{DIVIDER}\n"
                        f"We are excited to have you here in *Code on the Go Discussions*.\n\n"
                        f"💡 *Did you know?* COTG lets you build Android apps directly from your phone! I am **CG**, your AI assistant here.\n\n"
                        f"Please click the buttons below to read our official rules and learn more.")
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# --- EXTREME AI MODERATION & CHAT ---
@bot.message_handler(func=lambda message: True)
def smart_moderation_and_chat(message):
    if message.text is None:
        return
        
    text = message.text.lower()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    
    # Check if the sender is Ben
    is_boss = (message.from_user.username == BOSS_ADMIN) if message.from_user.username else False

    # 1. Check for Bad Words
    if any(word in text for word in bad_words):
        if not is_boss:
            try:
                bot.delete_message(chat_id, message.message_id)
                warning_msg = bot.send_message(chat_id, f"⚠️ @{username}, please keep the language clean! Refer to our community rules. 😇")
                time.sleep(10)
                bot.delete_message(chat_id, warning_msg.message_id)
            except Exception: pass
        return 

    # 2. SMART PROMO BLOCKER (Blocks rival groups/channels)
    promo_links = ['t.me/', 'telegram.me/', 'discord.gg/', 'chat.whatsapp.com/']
    if any(promo in text for promo in promo_links):
        if not is_boss:
            if 'codeonthegoofficial' not in text and 'ben_adfa' not in text:
                try:
                    bot.delete_message(chat_id, message.message_id)
                    warning_msg = bot.send_message(chat_id, f"🚫 @{username}, channel or group promotions are not allowed here! Please share only useful coding resources. 👍")
                    time.sleep(10)
                    bot.delete_message(chat_id, warning_msg.message_id)
                except Exception: pass
                return 

    # 3. Smart AI Chatting
    if not is_boss:
        if text == "help" or text == "rules" or "help me" in text:
            msg_text = f"I am **CG**, here to help you, @{username}! 🤖\nPlease select an option below:"
            bot.reply_to(message, msg_text, reply_markup=get_main_menu())
            
        elif "update" in text or "new version" in text or "release" in text:
            update_text = (f"🔥 *Latest Update Info:*\n{DIVIDER}\n"
                           "A new preview release of Code on the Go (v26.08) is out!\n"
                           "It includes experimental support for *Kotlin LSP* and other major improvements.\n\n"
                           "Read full release notes on our official channel: @CodeOnTheGoOfficial")
            bot.reply_to(message, update_text)

        elif text in ['hi', 'hello', 'hey', 'good morning', 'hlo']:
            bot.reply_to(message, f"Hello @{username}! 👋 I am **CG**. How is your Android coding journey going today?")
            
        elif "good bot" in text or "thanks bot" in text or "thank you bot" in text or "thanks cg" in text:
            bot.reply_to(message, "You are welcome! 😇 I was programmed by **ARMAN** to keep this community awesome! 🚀")
        
        elif "who are you" in text or "what is your name" in text:
            bot.reply_to(message, "I am **CG**! The Official Smart AI Assistant for the Code on the Go community. 🤖✨")

# Server start
keep_alive()
print("V8 YouTube Update is running online...")
bot.polling(none_stop=True)
