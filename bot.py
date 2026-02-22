import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time

# Tumhara API Token
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo' 
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

BOSS_ADMIN = 'Ben_ADFA'

# Advanced Filters
bad_words = ['gali1', 'gali2', 'badword', 'spam', 'scam', 'fuck', 'shit', 'bitch', 'asshole'] 

# Ab saare useful coding, google aur youtube links safe hain!
allowed_domains = [
    'github.com', 'developer.android.com', 'stackoverflow.com', 'pastebin.com', 
    'imgur.com', 'appdevforall.org', 'share.google', 'drive.google.com', 
    'docs.google.com', 'youtube.com', 'youtu.be', 't.me/CodeOnTheGoOfficial'
]

# --- STRINGS & INFO ---
RULES_TEXT = """📌 *Code on the Go - Official Rules:*

1️⃣ *Be respectful.* No harassment or personal attacks.
2️⃣ *Stay on topic.* Keep conversation focused on Code on the Go.
3️⃣ *English only.* So everyone can understand.
4️⃣ *No spam/ads.* Unauthorized links will be removed.
5️⃣ *Appropriate content.* No hateful or adult content.
6️⃣ *Protect privacy.* Don't share personal info.
7️⃣ *Admin moderation.* Severe violations result in removal.

Thank you for keeping the community clean! 😇"""

IDE_INFO = """🚀 *About Code on the Go (COTG):*

COTG is your ultimate standalone mobile IDE. Build real Android apps completely on your phone, even offline! 📱💻

🌐 *Official Website:* [appdevforall.org/codeonthego](https://www.appdevforall.org/codeonthego/)"""

# --- DYNAMIC MENUS ---
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("📜 Group Rules", callback_data="show_rules"),
        InlineKeyboardButton("📢 Official Channel", url="https://t.me/CodeOnTheGoOfficial")
    )
    markup.add(
        InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info"),
        InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN}")
    )
    return markup

# --- 1. /start COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (f"Hello *{message.from_user.first_name}*! 👋\n\n"
            f"I am the highly advanced AI Assistant for **Code on the Go**.\n"
            f"Please check out our menus below or type 'help' if you need assistance!")
    bot.reply_to(message, text, reply_markup=get_main_menu())

# --- 2. BUTTON CLICKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules":
        bot.answer_callback_query(call.id, "Loading rules...")
        bot.send_message(call.message.chat.id, RULES_TEXT)
    elif call.data == "show_ide_info":
        bot.answer_callback_query(call.id, "Loading IDE info...")
        bot.send_message(call.message.chat.id, IDE_INFO, disable_web_page_preview=True)

# --- 3. VIP WELCOME SYSTEM ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            continue
            
        name = new_member.username if new_member.username else new_member.first_name
        welcome_text = (f"Welcome to the discussions, @{name}! 🎉\n\n"
                        f"Please make sure to follow our Official Channel for all the latest release notes and updates: @CodeOnTheGoOfficial 📢\n\n"
                        f"Check out the buttons below to get started.")
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# --- 4. EXTREME AI MODERATION & CHAT ---
@bot.message_handler(func=lambda message: True)
def smart_moderation_and_chat(message):
    if message.text is None:
        return
        
    text = message.text.lower()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    is_boss = (message.from_user.username == BOSS_ADMIN)

    # --- STEP 1: SAFETY CHECKS (Runs first) ---
    # A. Check for Bad Words
    if any(word in text for word in bad_words):
        if not is_boss:
            try:
                bot.delete_message(chat_id, message.message_id)
                warning_msg = bot.send_message(chat_id, f"⚠️ @{username}, please keep the language clean! Refer to our community rules. 😇")
                time.sleep(10)
                bot.delete_message(chat_id, warning_msg.message_id)
            except Exception: pass
        return # Agar gaali hai toh aage ka AI chat nahi chalega

    # B. Check for Links
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
                return # Agar link safe nahi hai toh aage ka AI chat nahi chalega

    # --- STEP 2: SMART AI CHATTING (Agar message ekdum safe hai) ---
    if not is_boss:
        # User is asking for help or rules
        if text == "help" or text == "rules" or "help me" in text:
            bot.reply_to(message, f"I am here to help, @{username}! 🤖\nPlease select an option below, or join @CodeOnTheGoOfficial for updates.", reply_markup=get_main_menu())
            
        # User is asking about new updates (Mind Blowing Feature!)
        elif "update" in text or "new version" in text or "release" in text:
            update_text = ("🔥 *Latest Update Info:*\n"
                           "A new preview release of Code on the Go (v26.08) is out!\n"
                           "It includes experimental support for *Kotlin LSP* and other major improvements.\n\n"
                           "Read full release notes on our official channel: @CodeOnTheGoOfficial")
            bot.reply_to(message, update_text)

        # Basic greetings
        elif text in ['hi', 'hello', 'hey', 'good morning', 'hlo']:
            bot.reply_to(message, f"Hello @{username}! 👋 How is your Android coding journey going today?")
            
        elif "how are you" in text or "who are you" in text:
            bot.reply_to(message, "I am the advanced AI Assistant for COTG. I am functioning at 100% capacity! 🚀\nHow can I assist you today?")

# Server start
keep_alive()
print("V4 Ultra-Smart Bot is running online...")
bot.polling(none_stop=True)
