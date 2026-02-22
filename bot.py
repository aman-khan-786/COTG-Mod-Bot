import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time

# Tumhara API Token
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo' 
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

BOSS_ADMIN = 'Ben_ADFA'

# Filters
bad_words = ['gali1', 'gali2', 'badword', 'spam', 'scam', 'fuck', 'shit', 'bitch', 'asshole'] 
allowed_domains = [
    'github.com', 'developer.android.com', 'stackoverflow.com', 'pastebin.com', 
    'imgur.com', 'appdevforall.org', 'share.google', 'drive.google.com', 
    'docs.google.com', 'youtube.com', 'youtu.be', 't.me/CodeOnTheGoOfficial'
]

# --- PREMIUM UI STRINGS ---
DIVIDER = "━━━━━━━━━━━━━━━━━━━"

RULES_TEXT = f"""📌 *Code on the Go - Official Rules*
{DIVIDER}
1️⃣ *Be respectful:* No harassment or personal attacks.
2️⃣ *Stay on topic:* Keep conversation focused on COTG.
3️⃣ *English only:* So everyone can understand.
4️⃣ *No spam/ads:* Unauthorized links will be removed.
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

🌐 *Official Website:* [appdevforall.org/codeonthego](https://www.appdevforall.org/codeonthego/)
{DIVIDER}"""

# --- PREMIUM VIP BUTTON LAYOUT ---
def get_main_menu():
    markup = InlineKeyboardMarkup()
    # Row 1: Big prominent button for Channel
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/CodeOnTheGoOfficial"))
    
    # Row 2: Info buttons
    btn_rules = InlineKeyboardButton("📜 Group Rules", callback_data="show_rules")
    btn_ide = InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info")
    markup.row(btn_rules, btn_ide)
    
    # Row 3: Admin & Interactive Close button
    btn_admin = InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN}")
    btn_close = InlineKeyboardButton("❌ Close Menu", callback_data="close_menu")
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
            f"I am the highly advanced AI Assistant for **Code on the Go**.\n\n"
            f"How can I assist you today? Select an option below:")
    bot.reply_to(message, text, reply_markup=get_main_menu())

# --- INTERACTIVE BUTTON CLICKS (Callback Query) ---
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
                f"I am the highly advanced AI Assistant for **Code on the Go**.\n\n"
                f"How can I assist you today? Select an option below:")
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
                        f"💡 *Did you know?* COTG lets you build Android apps directly from your phone!\n\n"
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
    is_boss = (message.from_user.username == BOSS_ADMIN)

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

    # 2. Check for Links
    if 'http' in text or 'www.' in text or 't.me' in text:
        if not is_boss:
            is_safe = False
            for domain in allowed_domains:
                if domain in text:
                    is_safe = True
                    break
            
            if not is_safe:
                try:
                    bot.delete_message(chat_id, message.message_id)
                    warning_msg = bot.send_message(chat_id, f"🚫 @{username}, unauthorized links are not allowed. Please share project files via safe platforms (GitHub, Drive, etc). 👍")
                    time.sleep(10)
                    bot.delete_message(chat_id, warning_msg.message_id)
                except Exception: pass
                return 

    # 3. Smart AI Chatting
    if not is_boss:
        if text == "help" or text == "rules" or "help me" in text:
            msg_text = f"I am here to help, @{username}! 🤖\nPlease select an option below:"
            bot.reply_to(message, msg_text, reply_markup=get_main_menu())
            
        elif "update" in text or "new version" in text or "release" in text:
            update_text = (f"🔥 *Latest Update Info:*\n{DIVIDER}\n"
                           "A new preview release of Code on the Go (v26.08) is out!\n"
                           "It includes experimental support for *Kotlin LSP* and other major improvements.\n\n"
                           "Read full release notes on our official channel: @CodeOnTheGoOfficial")
            bot.reply_to(message, update_text)

        elif text in ['hi', 'hello', 'hey', 'good morning', 'hlo']:
            bot.reply_to(message, f"Hello @{username}! 👋 How is your Android coding journey going today?")
            
        elif "how are you" in text or "who are you" in text:
            bot.reply_to(message, f"I am the advanced AI Assistant for COTG. I am functioning at 100% capacity! 🚀\nHow can I assist you today?")

# Server start
keep_alive()
print("V5 Premium UI Bot is running online...")
bot.polling(none_stop=True)
