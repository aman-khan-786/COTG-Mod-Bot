import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os
from bs4 import BeautifulSoup

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

# ================= LIVE WEBSITE SCRAPER =================
cached_website_data = ""
last_scrape_time = 0

def get_live_website_info():
    global cached_website_data, last_scrape_time
    if time.time() - last_scrape_time > 3600 or not cached_website_data:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get("https://www.appdevforall.org/codeonthego", headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            text_data = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
            cached_website_data = text_data[:800] 
            last_scrape_time = time.time()
        except Exception:
            return "Latest info not available right now. Please check the official Telegram channel."
    return cached_website_data

# ================= TEXTS & UI =================
DIVIDER = "━━━━━━━━━━━━━━━━━━━"

RULES_TEXT = f"""📌 *Code on the Go - Official Rules*
{DIVIDER}
1️⃣ *Be respectful:* Treat all members with respect. No harassment, discrimination, or personal attacks.
2️⃣ *Stay on topic:* Keep conversation focused on Code on the Go.
3️⃣ *English only:* Please post in English so everyone can participate and understand.
4️⃣ *No spam/ads:* Do not post ads, repeated messages, or unrelated links.
5️⃣ *Appropriate content:* No hateful, illegal, or adult content will be tolerated.
6️⃣ *Protect privacy:* Don't share anyone's personal or private information.
7️⃣ *Admin moderation:* Severe violations may result in immediate removal.
{DIVIDER}
*Thank you for keeping our community clean!* 😇"""

IDE_INFO = f"""🚀 *About Code on the Go (COTG)*
{DIVIDER}
COTG is your ultimate standalone mobile IDE. Build real Android apps completely on your phone, even offline! 📱💻

✨ *Key Features:*
• Real-time Android app compilation.
• Modern Kotlin & Java support.
• Perfect for testing ideas without a PC.

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

# ================= ADVANCED AI LOGIC (WITH MEMORY) =================
# Ab bot aakhri 4 messages yaad rakhega per user
chat_memory = {}

def get_grok_reply(user_id, user_msg, username):
    global chat_memory
    try:
        extra_context = ""
        msg_lower = user_msg.lower()
        if any(w in msg_lower for w in ['update', 'new', 'feature', 'latest', 'version']):
            live_data = get_live_website_info()
            extra_context = f"\n\n[LIVE INFO FROM OFFICIAL WEBSITE: {live_data}]\nUse this info to answer if relevant."

        system_prompt = f"""You are CG, the friendly and highly intelligent AI Assistant for the 'Code on the Go' (COTG) Android coding community.
Rules:
1. Speak ONLY in English.
2. Keep replies SHORT and crisp.
3. Motivate users to build Android apps.{extra_context}"""

        # Memory initialization for user
        if user_id not in chat_memory:
            chat_memory[user_id] = []

        # Add current user message to memory
        chat_memory[user_id].append({"role": "user", "content": f"User: {username}\nMessage: {user_msg}"})

        # Keep only last 4 messages to save tokens (2 from user, 2 from bot)
        if len(chat_memory[user_id]) > 4:
            chat_memory[user_id] = chat_memory[user_id][-4:]

        messages_payload = [{"role": "system", "content": system_prompt}] + chat_memory[user_id]

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages_payload,
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            ai_reply = r.json()['choices'][0]['message']['content'].strip()
            # Save bot's reply to memory
            chat_memory[user_id].append({"role": "assistant", "content": ai_reply})
            return ai_reply
        else:
            return None
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# ================= COMMANDS =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (f"Hello *{message.from_user.first_name}*! 👋\n{DIVIDER}\n"
            f"I am **CG**, the highly advanced AI Assistant for Code on the Go.\n\n"
            f"How can I assist you today? Select an option below:")
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['status'])
def bot_status(message):
    if message.from_user.username == BOSS_ADMIN:
        bot.reply_to(message, f"🟢 **CG System Status: ONLINE**\n{DIVIDER}\nBoss @{BOSS_ADMIN}, everything is 100% active! Memory & AI functional. 🚀")

@bot.message_handler(commands=['shoutout'])
def weekly_shoutout(message):
    if message.from_user.username != BOSS_ADMIN: return
    if not rankings: return bot.reply_to(message, "No rankings yet!")
    top = max(rankings.items(), key=lambda x: x[1]['points'])
    bot.send_message(message.chat.id, f"🎉 **WEEKLY SHOUTOUT** 🎉\n\n🏆 **{top[1]['name']}** is the TOP contributor with **{top[1]['points']} points**!\n\nThank you for making the COTG community awesome! Keep it up! 🔥")

# ================= BUTTON CLICKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=RULES_TEXT, reply_markup=get_back_button(), parse_mode='Markdown')
    elif call.data == "show_ide_info":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=IDE_INFO, reply_markup=get_back_button(), parse_mode='Markdown', disable_web_page_preview=True)
    elif call.data == "back_to_main":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Hello again! 👋\n{DIVIDER}\nI am **CG**, the highly advanced AI Assistant.", reply_markup=get_main_menu(), parse_mode='Markdown')
    elif call.data == "close_menu":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

# ================= NEW MEMBER WELCOME =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id: continue
        name = member.username if member.username else member.first_name
        text = (f"Welcome to the community, @{name}! 🎉\n{DIVIDER}\n"
                f"We are excited to have you in *Code on the Go*.\n"
                f"💡 I am **CG**, your AI assistant. Click below to read our rules!")
        bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

# ================= MAIN MESSAGE HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_chat_handler(message):
    if not message.text: return
        
    text = message.text.lower().strip()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN)

    # --- 1. UPDATE RANKING POINTS ---
    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username}
        rankings[user_id]["points"] += 2  # Msg point
        rankings[user_id]["name"] = username
        if message.reply_to_message: rankings[user_id]["points"] += 10 # Help point
        save_rankings(rankings)

    # --- 2. FILTERS (BAD WORDS & PROMO) ---
    bad_words = ['gali1', 'badword', 'spam', 'fuck', 'shit', 'bitch', 'asshole']
    if any(word in text for word in bad_words) and not is_boss:
        try:
            bot.delete_message(chat_id, message.message_id)
            warn = bot.send_message(chat_id, f"⚠️ @{username}, please keep the language clean! 😇")
            time.sleep(10); bot.delete_message(chat_id, warn.message_id)
        except: pass
        return 

    promo_links = ['t.me/', 'discord.gg/', 'chat.whatsapp.com/']
    if any(promo in text for promo in promo_links) and not is_boss:
        if 'codeonthegoofficial' not in text and 'ben_adfa' not in text:
            try:
                bot.delete_message(chat_id, message.message_id)
                warn = bot.send_message(chat_id, f"🚫 @{username}, channel or group promotions are not allowed here! 👍")
                time.sleep(10); bot.delete_message(chat_id, warn.message_id)
            except: pass
            return 

    # --- 3. HARDCODED COMMAND INTERCEPTS (ABSOLUTE PRIORITY - NO AI) ---
    if any(cmd == text for cmd in ['help', '/help', 'rules', '/rules', 'menu', 'cg help']):
        bot.reply_to(message, f"I am **CG**, here to help you, @{username}! 🤖\nPlease select an option below:", reply_markup=get_main_menu())
        return

    if any(cmd == text for cmd in ['my rank', 'my ranking', '/myrank', 'rank', 'cg my rank', 'cg rank']) or text.startswith('cg my rank'):
        data = rankings.get(user_id, {"points": 0, "name": username})
        bot.reply_to(message, f"🏆 *Your Rank*\n👤 {data['name']}\n⭐ Points: **{data['points']}**\nKeep helping others to climb the leaderboard! 🔥")
        return

    if any(cmd == text for cmd in ['leaderboard', 'top', '/top', '/leaderboard', 'ranking', 'cg leaderboard']):
        if not rankings:
            bot.reply_to(message, "No points tracked yet! Start chatting to earn points.")
            return
        sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        lb_text = f"🏅 *Top Active Members*\n{DIVIDER}\n"
        for i, (uid, data) in enumerate(sorted_users, 1):
            lb_text += f"{i}. **{data['name']}** — {data['points']} pts\n"
        bot.reply_to(message, lb_text)
        return

    # --- 4. SMART AI & FALLBACK LOGIC ---
    bot_triggered = False
    
    if text == "cg":
        bot.reply_to(message, f"Yes brother! I am here. 🤖 How can I help you, @{username}?")
        return

    if "cg" in text or f"@{BOT_NAME.lower()}" in text or message.chat.type == 'private':
        bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        bot_triggered = True

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        # Ab hum API ko user_id bhi bhej rahe hain taaki memory kaam kare
        ai_reply = get_grok_reply(user_id, message.text, username)
        
        if ai_reply:
            bot.reply_to(message, ai_reply)
        else:
            # === OFFLINE FALLBACK ===
            if any(w in text for w in ['hi', 'hello', 'hey']):
                bot.reply_to(message, f"Hello @{username}! 👋 I am **CG**. How is your coding going today?")
            elif "who are you" in text or "your name" in text:
                bot.reply_to(message, "I am **CG**! The Official Smart AI Assistant for the COTG community. 🤖✨")
            elif "thanks" in text or "good bot" in text:
                bot.reply_to(message, "You are welcome! 😇 I was programmed to keep this community awesome! 🚀")
            else:
                bot.reply_to(message, "Yes brother! I am currently operating in offline fallback mode. How can I help you?")
        return

# Server start
keep_alive()
print("V14 Memory & Priority AI Bot is LIVE!")
bot.polling(none_stop=True)
