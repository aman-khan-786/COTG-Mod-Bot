import telebot
import time
from keep_alive import keep_alive

# Yahan apna Telegram Bot Token dalna hai
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE' 
bot = telebot.TeleBot(TOKEN)

# Galiyon ki list (Bad words) - isme aur bhi words add kar sakte ho
bad_words = ['gali1', 'gali2', 'badword'] 

# Safe links jo delete NAHI karne hain (Whitelist)
allowed_domains = ['github.com', 'developer.android.com', 'stackoverflow.com', 'pastebin.com', 'imgur.com']

# 1. Welcome Message & Rules
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        welcome_text = f"Welcome @{new_member.username} to Code on the Go Discussions! 🎉\n\nPlease read our rules:\n1. Be respectful.\n2. Stay on topic.\n3. English only.\n4. No spam or promo links."
        bot.send_message(message.chat.id, welcome_text)

# 2. Message Filter (Gali aur Link check)
@bot.message_handler(func=lambda message: True)
def moderate_chat(message):
    text = message.text.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Gali Galauj Check (Mute for 1 hour)
    if any(word in text for word in bad_words):
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, f"⚠️ @{username}, Gali galauj allowed nahi hai! Rules follow karo.")
        try:
            # 1 hour = 3600 seconds mute
            bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 3600)
        except Exception as e:
            pass # Bot ko group mein Admin banana zaroori hai restrict karne ke liye
        return

    # Link Filter Check
    if 'http' in text or 'www.' in text or 't.me' in text:
        is_safe = False
        for domain in allowed_domains:
            if domain in text:
                is_safe = True
                break
        
        if not is_safe:
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"🚫 @{username}, Promotional links allowed nahi hain! Sirf project/assets ke safe links share karo.")
            return

# Server aur Bot ko 24/7 start karna
keep_alive()
print("Bot is running online...")
bot.polling(none_stop=True)
