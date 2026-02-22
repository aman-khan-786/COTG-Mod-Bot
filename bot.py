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
allowed_domains = ['github.com', 'developer.android.com', 'stackoverflow.com', 'pastebin.com', 'imgur.com', 'appdevforall.org']

# --- STRINGS & INFO ---
RULES_TEXT = """📌 *Code on the Go - Official Rules:*

1️⃣ *Be respectful.* Treat all members with respect. No harassment, discrimination, or personal attacks.
2️⃣ *Stay on topic.* Keep conversation focused on Code on the Go.
3️⃣ *English only, please.* Please post in English so everyone can participate and understand the conversation.
4️⃣ *No spam, solicitation, or self-promotion.* Do not post ads, repeated messages, or unrelated links.
5️⃣ *Use appropriate content.* No hateful, illegal, or adult content will be tolerated.
6️⃣ *Protect privacy.* Don’t share anyone’s personal or private information.
7️⃣ *Admin moderation.* Admins will typically issue a warning before removing a member, but severe violations may result in immediate removal.

Thanks to all of you for using the app and providing feedback! I appreciate it!"""

IDE_INFO = """🚀 *About Code on the Go (COTG) IDE:*

COTG is your ultimate mobile IDE to build Android applications directly from your phone! 📱💻

✨ *Features & Info:*
• Write, compile, and run real Android apps on the go.
• Support for modern Android development (Kotlin, Java, UI design).
• Perfect for testing ideas and coding without a PC.
• Built for the community, by the community.

🔔 *Notice:* Awesome new updates are coming very soon! Please keep supporting the developers to make COTG even better. ❤️

🌐 *Official Website:* [appdevforall.org/codeonthego](https://www.appdevforall.org/codeonthego/)"""

# --- MENUS ---
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("📜 Group Rules", callback_data="show_rules"),
        InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info")
    )
    markup.add(InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN}"))
    return markup

# --- 1. /start & /help ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user.first_name
    text = (f"Hello *{user}*! 👋\n\n"
            f"I am the Official Assistant for the **Code on the Go** community.\n"
            f"How can I help you today?")
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

# --- 3. NEW USER WELCOME (ADVANCED) ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            continue
            
        name = new_member.username if new_member.username else new_member.first_name
        welcome_text = (f"Welcome to the community, @{name}! 🎉\n\n"
                        f"We are excited to have you here in *Code on the Go Discussions*.\n\n"
                        f"💡 *Did you know?* COTG lets you build Android apps directly from your phone! **New updates are coming soon**, so please support the developers and share your feedback.\n\n"
                        f"Please click the buttons below to read our official rules and learn more about the IDE.")
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# --- 4. SMART MODERATION & CHAT (NO MUTES) ---
@bot.message_handler(func=lambda message: True)
def smart_moderation_and_chat(message):
    if message.text is None:
        return
        
    text = message.text.lower()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name

    # VIP Check
    is_boss = (message.from_user.username == BOSS_ADMIN)

    # --- A. SMART CHATTING AI ---
    if not is_boss:
        if any(word in text for word in ["what is cotg", "ide feature", "app info", "website"]):
            bot.reply_to(message, IDE_INFO, disable_web_page_preview=True)
            return
            
        elif any(word in text for word in ["bug", "error", "crash", "help", "not working"]):
            bot.reply_to(message, f"Hey @{username}, thanks for providing feedback! 🛠️\nOur Admin @{BOSS_ADMIN} and the dev team will look into this issue. We appreciate your support!")
            
        elif text in ['hi', 'hello', 'hey', 'good morning']:
            bot.reply_to(message, f"Hello @{username}! 👋 Hope you are having a great time coding with COTG!")
            return

        elif "who made you" in text or "creator" in text or "who is your boss" in text:
            bot.reply_to(message, f"I am the Official AI Assistant for this group, managed by our Admin @{BOSS_ADMIN}. I am here to help you with the COTG IDE! 🚀")
            return

    # --- B. WARNING SYSTEM FOR BAD WORDS (NO MUTE) ---
    if any(word in text for word in bad_words):
        if not is_boss:
            try:
                bot.delete_message(chat_id, message.message_id)
                warning_msg = bot.send_message(chat_id, f"⚠️ @{username}, please remember Rule #1 and #5: Use appropriate content and be respectful. Let's keep the chat clean! 😇")
                time.sleep(10) # 10 second baad warning delete ho jayegi taaki chat clean rahe
                bot.delete_message(chat_id, warning_msg.message_id)
            except Exception as e:
                pass
        return

    # --- C. WARNING SYSTEM FOR LINKS (NO MUTE) ---
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
                    warning_msg = bot.send_message(chat_id, f"🚫 @{username}, as per Rule #4, please do not post unauthorized or promotional links. Thanks for understanding! 👍")
                    time.sleep(10) # 10 second baad warning delete ho jayegi
                    bot.delete_message(chat_id, warning_msg.message_id)
                except Exception as e:
                    pass
                return

# Server start
keep_alive()
print("V3 Final Bot is running online...")
bot.polling(none_stop=True)
