import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os

# ================= CONFIGURATION =================
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo'
GROQ_API_KEY = "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"
BOSS_ADMIN = 'Ben_ADFA'          
BOT_NAME = "CG"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# ================= RANKING SYSTEM =================
RANK_FILE = 'rankings.json'

def load_rankings():
    if os.path.exists(RANK_FILE):
        try:
            with open(RANK_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_rankings(data):
    with open(RANK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

rankings = load_rankings()

# ================= TEXTS & UI =================
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

# ================= ADVANCED AI LOGIC =================
SYSTEM_PROMPT = """You are CG, the friendly and helpful AI Assistant for the 'Code on the Go' (COTG) Android coding community.
Rules for you:
1. Speak ONLY in English.
2. Keep your replies SHORT, CRISP, and direct to save tokens.
3. If the user just says "cg", "hi cg", or calls your name, reply with something like "Yes brother! How can I help you?".
4. Motivate users and provide helpful coding tips if they ask.
Address the user directly using their name provided."""

def get_grok_reply(user_msg, username):
    """Returns AI response, or None if API fails."""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"User: {username}\nMessage: {user_msg}"}
            ],
            "temperature": 0.7,
            "max_tokens": 150  # Keep it short to save tokens
        }
        # 8 second timeout so bot doesn't hang if API is down
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                          json=payload, headers=headers, timeout=8)
        
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        else:
            return None
    except Exception:
        return None

# ================= COMMANDS =================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (f"Hello *{message.from_user.first_name}*! 👋\n{DIVIDER}\n"
            f"I am **CG**, the highly advanced AI Assistant for Code on the Go.\n\n"
            f"How can I assist you today? Select an option below:")
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['status'])
def bot_status(message):
    if message.from_user.username == BOSS_ADMIN:
        bot.reply_to(message, f"🟢 **CG System Status: ONLINE & ACTIVE**\n{DIVIDER}\nBoss @{BOSS_ADMIN}, AI and filters are running perfectly! 🚀")

@bot.message_handler(commands=['myrank'])
def my_rank(message):
    user_id = str(message.from_user.id)
    name = message.from_user.username if message.from_user.username else message.from_user.first_name
    data = rankings.get(user_id, {"points": 0, "name": name})
    bot.reply_to(message, f"🏆 *Your Rank*\n👤 {data['name']}\n⭐ Points: **{data['points']}**\nKeep helping others to climb the leaderboard! 🔥")

@bot.message_handler(commands=['top', 'leaderboard'])
def show_leaderboard(message):
    if not rankings:
        bot.reply_to(message, "No points tracked yet! Start chatting to earn points.")
        return
    sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
    text = f"🏅 *Top Active Members*\n{DIVIDER}\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        text += f"{i}. **{data['name']}** — {data['points']} pts\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['shoutout'])
def weekly_shoutout(message):
    if message.from_user.username != BOSS_ADMIN:
        return
    if not rankings:
        bot.reply_to(message, "No rankings yet!")
        return
    top = max(rankings.items(), key=lambda x: x[1]['points'])
    bot.send_message(message.chat.id, f"🎉 **WEEKLY SHOUTOUT** 🎉\n\n🏆 **{top[1]['name']}** is the TOP contributor with **{top[1]['points']} points**!\n\nThank you for making the COTG community awesome! Keep it up! 🔥")

@bot.message_handler(commands=['report'])
def report_message(message):
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, f"🚨 **REPORTED!**\nAdmin @{BOSS_ADMIN}, please review this message.")
        bot.delete_message(message.chat.id, message.message_id) 
    else:
        warning = bot.reply_to(message, "⚠️ To report someone, you must **reply** to their message and type `/report`.")
        time.sleep(5)
        bot.delete_message(message.chat.id, warning.message_id)
        bot.delete_message(message.chat.id, message.message_id)

# ================= BUTTON CLICKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=RULES_TEXT, reply_markup=get_back_button(), parse_mode='Markdown')
    elif call.data == "show_ide_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=IDE_INFO, reply_markup=get_back_button(), parse_mode='Markdown', disable_web_page_preview=True)
    elif call.data == "back_to_main":
        text = (f"Hello again! 👋\n{DIVIDER}\nI am **CG**, the highly advanced AI Assistant.\nHow can I assist you today?")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=text, reply_markup=get_main_menu(), parse_mode='Markdown')
    elif call.data == "close_menu":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

# ================= NEW MEMBER WELCOME =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id: continue
        name = new_member.username if new_member.username else new_member.first_name
        welcome_text = (f"Welcome to the community, @{name}! 🎉\n{DIVIDER}\n"
                        f"We are excited to have you here in *Code on the Go Discussions*.\n\n"
                        f"💡 I am **CG**, your AI assistant here.\nPlease click the buttons below to read our official rules and learn more.")
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# ================= MAIN MESSAGE HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_moderation_and_chat(message):
    if message.text is None: return
        
    text = message.text.lower().strip()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN)

    # --- 1. UPDATE RANKING POINTS ---
    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings:
            rankings[user_id] = {"points": 0, "name": username}
        rankings[user_id]["points"] += 2  # 2 points per message
        rankings[user_id]["name"] = username
        if message.reply_to_message:      # 10 points for helping/replying to someone
            rankings[user_id]["points"] += 10
        save_rankings(rankings)

    # --- 2. FILTERS (BAD WORDS & PROMO) ---
    bad_words = ['gali1', 'gali2', 'badword', 'spam', 'scam', 'fuck', 'shit', 'bitch', 'asshole']
    if any(word in text for word in bad_words) and not is_boss:
        try:
            bot.delete_message(chat_id, message.message_id)
            warning_msg = bot.send_message(chat_id, f"⚠️ @{username}, please keep the language clean! Refer to our community rules. 😇")
            time.sleep(10)
            bot.delete_message(chat_id, warning_msg.message_id)
        except: pass
        return 

    promo_links = ['t.me/', 'telegram.me/', 'discord.gg/', 'chat.whatsapp.com/']
    if any(promo in text for promo in promo_links) and not is_boss:
        if 'codeonthegoofficial' not in text and 'ben_adfa' not in text:
            try:
                bot.delete_message(chat_id, message.message_id)
                warning_msg = bot.send_message(chat_id, f"🚫 @{username}, channel or group promotions are not allowed here! Please share only safe project links. 👍")
                time.sleep(10)
                bot.delete_message(chat_id, warning_msg.message_id)
            except: pass
            return 

    # --- 3. SMART AI & FALLBACK LOGIC ---
    bot_triggered = False
    
    # Fast trigger for just saying "cg"
    if text == "cg":
        bot.reply_to(message, f"Yes brother! I am here. 🤖 How can I help you, @{username}?")
        return

    if "cg" in text or f"@{BOT_NAME.lower()}" in text or message.chat.type == 'private':
        bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        bot_triggered = True

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing') # Shows "CG is typing..."
        ai_reply = get_grok_reply(message.text, username)
        
        if ai_reply:
            bot.reply_to(message, ai_reply)
        else:
            # === FALLBACK LOGIC (IF API FAILS) ===
            if any(word in text for word in ['hi', 'hello', 'hey', 'hlo']):
                bot.reply_to(message, f"Hello @{username}! 👋 I am **CG**. How is your Android coding journey going today?")
            elif "who are you" in text or "your name" in text:
                bot.reply_to(message, "I am **CG**! The Official Smart AI Assistant for the Code on the Go community. 🤖✨")
            elif "thanks" in text or "good bot" in text:
                bot.reply_to(message, "You are welcome! 😇 I was programmed by **ARMAN** to keep this community awesome! 🚀")
            elif "error" in text or "bug" in text:
                bot.reply_to(message, "It looks like you are facing an issue. Please share your project details or logs so the community can help!")
            else:
                bot.reply_to(message, "Yes brother! I am currently operating in offline fallback mode. How can I help you today?")
        return

    # --- 4. QUICK HELP (Without Trigger) ---
    if not is_boss and not bot_triggered:
        if text == "help" or text == "rules" or "help me" in text:
            bot.reply_to(message, f"I am **CG**, here to help you, @{username}! 🤖\nPlease select an option below:", reply_markup=get_main_menu())
            
        elif "update" in text or "new version" in text or "release" in text:
            update_text = (f"🔥 *Latest Update Info:*\n{DIVIDER}\n"
                           "A new preview release of Code on the Go (v26.08) is out!\n"
                           "It includes experimental support for *Kotlin LSP* and other major improvements.\n\n"
                           "Read full release notes on our official channel: @CodeOnTheGoOfficial")
            bot.reply_to(message, update_text)

# Server start
keep_alive()
print("V11 Ultra Advanced CG Bot with Fail-Safe is LIVE!")
bot.polling(none_stop=True)
