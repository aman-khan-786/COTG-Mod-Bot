import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os

# ================= CONFIG =================
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo'
GROQ_API_KEY = "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"
BOSS_ADMIN = 'Ben_ADFA'          # Only this username is real admin
BOT_NAME = "CG"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# Ranking file
RANK_FILE = 'rankings.json'

def load_rankings():
    if os.path.exists(RANK_FILE):
        with open(RANK_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_rankings(data):
    with open(RANK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

rankings = load_rankings()

# System Prompt (English only, Grok style)
SYSTEM_PROMPT = """You are CG, the official friendly, witty and highly motivational AI Assistant for 'Code on the Go' Android coding community.
Speak ONLY in English. Be short and crisp unless the question is technical/complex.
Motivate users to build real Android apps with COTG. Be fun like Grok. Never speak Hindi.
User's name is given at start of message."""

# ================= UI & TEXTS (same as before) =================
DIVIDER = "━━━━━━━━━━━━━━━━━━━"

RULES_TEXT = f"""📌 *Code on the Go - Official Rules*\n{DIVIDER}\n1️⃣ Be respectful...\n(tere purane rules same)"""

IDE_INFO = f"""🚀 *About Code on the Go (COTG)*\n{DIVIDER}\n... (same as your code)"""

def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/CodeOnTheGoOfficial"))
    markup.add(InlineKeyboardButton("🎥 Subscribe on YouTube", url="https://youtube.com/@appdevforall"))
    markup.row(InlineKeyboardButton("📜 Group Rules", callback_data="show_rules"),
               InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info"))
    markup.row(InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN}"),
               InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main"))
    markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

# ================= AI FUNCTION =================
def get_grok_reply(user_msg, username):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{username}: {user_msg}"}
            ],
            "temperature": 0.75,
            "max_tokens": 280   # short = low token use
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                          json=payload, headers=headers, timeout=12)
        
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        else:
            return None
    except:
        return None

# ================= COMMANDS =================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = f"Hello *{message.from_user.first_name}*! 👋\n{DIVIDER}\nI am **{BOT_NAME}**, your advanced AI Assistant for Code on the Go.\nHow can I help you today?"
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['status'])
def bot_status(message):
    if message.from_user.username == BOSS_ADMIN:
        bot.reply_to(message, f"🟢 **{BOT_NAME} System Status: ONLINE & ACTIVE**\n{DIVIDER}\nBoss @{BOSS_ADMIN}, everything running at 100%! 🚀")

@bot.message_handler(commands=['myrank'])
def my_rank(message):
    user_id = str(message.from_user.id)
    data = rankings.get(user_id, {"points": 0, "name": message.from_user.first_name})
    bot.reply_to(message, f"🏆 *Your Rank*\n👤 {data['name']}\n⭐ Points: **{data['points']}**\nKeep coding & helping others to climb up! 🔥")

@bot.message_handler(commands=['leaderboard', 'top'])
def leaderboard(message):
    sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
    text = "🏅 *Top Active Members*\n" + DIVIDER + "\n"
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
    name = top[1]['name']
    pts = top[1]['points']
    bot.send_message(message.chat.id, f"🎉 **WEEKLY SHOUTOUT**\n\n🏆 **{name}** is the TOP contributor with **{pts} points**!\n\nThank you for making COTG community awesome! 🔥\nKeep crushing it bhai!")

# ================= CALLBACKS (same as your code) =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # same as your original code (rules, ide, back, close)
    if call.data == "show_rules":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=RULES_TEXT, reply_markup=get_back_button())
    # ... baaki same (copy from your code)

# ================= WELCOME =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    # same as your code
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id: continue
        name = new_member.username or new_member.first_name
        welcome_text = f"Welcome @{name}! 🎉\n{DIVIDER}\nI am **{BOT_NAME}**, your AI assistant here.\nPlease read rules & enjoy coding!"
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# ================= MAIN SMART HANDLER =================
@bot.message_handler(func=lambda m: True)
def smart_handler(message):
    if not message.text: return
    text_lower = message.text.lower().strip()
    username = message.from_user.username or message.from_user.first_name
    user_id = str(message.from_user.id)
    chat_id = message.chat.id

    is_boss = (message.from_user.username == BOSS_ADMIN)

    # === RANKING POINTS ===
    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings:
            rankings[user_id] = {"points": 0, "name": username}
        rankings[user_id]["points"] += 5          # activity
        rankings[user_id]["name"] = username
        
        if message.reply_to_message:              # helping someone
            rankings[user_id]["points"] += 15
        save_rankings(rankings)

    # === BAD WORDS & PROMO (same as yours) ===
    # ... copy your bad_words & promo_links logic here ...

    # === CG MENTION / REPLY TO BOT / PRIVATE ===
    bot_mention = False
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        bot_mention = True
    if "cg" in text_lower or f"@{BOT_NAME.lower()}" in text_lower or message.chat.type == 'private':
        bot_mention = True

    if bot_mention:
        # Try Groq first
        ai_reply = get_grok_reply(message.text, username)
        
        if ai_reply:
            bot.reply_to(message, ai_reply)
        else:
            # FALLBACK to old style
            if text_lower in ['hi', 'hello', 'hey']:
                bot.reply_to(message, f"Hello @{username}! 👋 I am **{BOT_NAME}**. How is your Android coding journey going today?")
            elif "who are you" in text_lower:
                bot.reply_to(message, f"I am **{BOT_NAME}**! The Official Smart AI Assistant for Code on the Go community. 🤖✨")
            elif "thanks" in text_lower or "thank" in text_lower:
                bot.reply_to(message, "You are welcome! 😇 I was programmed by **ARMAN** to keep this community awesome! 🚀")
            else:
                bot.reply_to(message, "Yes brother! 🔥 How can I help you with coding or motivation today?")
        return

    # === OLD FALLBACK COMMANDS (help, update etc.) ===
    # copy your existing elif conditions here...

# ================= START =================
keep_alive()
print(f"🚀 {BOT_NAME} V9 with Groq + Ranking is LIVE!")
bot.polling(none_stop=True)
