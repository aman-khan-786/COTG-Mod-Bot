import telebot
import time
from keep_alive import keep_alive

# Tumhara asli Bot API Token
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo' 
bot = telebot.TeleBot(TOKEN)

# Galiyon ki list (Bad words) - isme aur bhi words apne hisaab se add kar lena baad mein
bad_words = ['gali1', 'gali2', 'badword', 'spam', 'scam'] 

# Safe links jo delete NAHI karne hain (Whitelist)
allowed_domains = ['github.com', 'developer.android.com', 'stackoverflow.com', 'pastebin.com', 'imgur.com']

# 1. Welcome Message & Rules
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        # Username agar nahi hai toh first name use karega
        name = new_member.username if new_member.username else new_member.first_name
        welcome_text = f"Welcome @{name} to Code on the Go Discussions! 🎉\n\nPlease read our rules:\n1. Be respectful.\n2. Stay on topic.\n3. English only.\n4. No spam or promo links."
        bot.send_message(message.chat.id, welcome_text)

# 2. Message Filter (Gali aur Link check)
@bot.message_handler(func=lambda message: True)
def moderate_chat(message):
    if message.text is None:
        return
        
    text = message.text.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name

    # Gali Galauj Check (Delete message & Mute for 1 hour)
    if any(word in text for word in bad_words):
        try:
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"⚠️ @{username}, Gali galauj allowed nahi hai! Rules follow karo.")
            # 1 hour = 3600 seconds mute
            bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 3600)
        except Exception as e:
            print("Error muting user (maybe bot is not admin):", e)
        return

    # Link Filter Check
    if 'http' in text or 'www.' in text or 't.me' in text:
        is_safe = False
        for domain in allowed_domains:
            if domain in text:
                is_safe = True
                break
        
        # Agar link safe nahi hai toh delete karo
        if not is_safe:
            try:
                bot.delete_message(chat_id, message.message_id)
                bot.send_message(chat_id, f"🚫 @{username}, Promotional links allowed nahi hain! Sirf project/assets ke safe links share karo.")
            except Exception as e:
                print("Error deleting link:", e)
            return

# Server aur Bot ko 24/7 start karna
keep_alive()
print("Bot is running online...")
bot.polling(none_stop=True)
