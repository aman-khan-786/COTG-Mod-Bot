import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ================= CONFIGURATION =================
TOKEN = '8515104266:AAGtADm-4BxboHfNcTB6TVKcmE7nD03r74M'
GROQ_API_KEY = "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"
BOSS_ADMIN = 'Ben_ADFA'          
BOT_NAME = "CG"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

try:
    BOT_ID = bot.get_me().id
except:
    BOT_ID = None

# ================= DATABASES =================
RANK_FILE = 'rankings.json'
VAULT_FILE = 'vault.json'

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_json(data, file_path):
    with open(file_path, 'w') as f: json.dump(data, f, indent=2)

rankings = load_json(RANK_FILE)
code_vault = load_json(VAULT_FILE)

user_cooldown = {} 
msg_counter = 0    
interject_counter = 0

def get_title(points):
    if points < 50: return "🟢 Beginner Coder"
    elif points < 200: return "🔵 Bug Hunter"
    elif points < 500: return "🟣 Kotlin Pro"
    else: return "🔴 COTG Legend"

# ================= JOKES & QUIZ =================
DEV_JOKES = [
    "😂 Programmer's joke: My code works, I don't know why. My code doesn't work, I don't know why!",
    "🤓 Why do Java programmers wear glasses? Because they don't C#!",
    "🔥 Shayari: Arz kiya hai... Code likhte likhte subah se sham ho gayi, Ek error solve kiya toh dusri paida ho gayi!",
    "📱 Tip: Jetpack Compose makes UI development so much faster. Give it a try on COTG!"
]

QUIZ_POLLS = [
    {"q": "Which language is officially recommended by Google for Android?", "opts": ["Java", "Kotlin", "C++", "Python"], "ans": 1},
    {"q": "What extension is used for Android UI layout files?", "opts": [".java", ".kt", ".xml", ".apk"], "ans": 2},
    {"q": "What tool in Android shows you the console logs and errors?", "opts": ["Terminal", "Logcat", "Debugger", "Gradle"], "ans": 1},
    {"q": "What is the modern declarative UI toolkit for Android?", "opts": ["XML", "Flutter", "Jetpack Compose", "React Native"], "ans": 2}
]

active_polls = {}

@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    poll_id = pollAnswer.poll_id
    user_id = str(pollAnswer.user.id)
    user_name = pollAnswer.user.first_name
    selected_option = pollAnswer.option_ids[0]

    if poll_id in active_polls:
        if selected_option == active_polls[poll_id]["ans"]:
            if user_id not in rankings: rankings[user_id] = {"points": 0, "name": user_name}
            rankings[user_id]["points"] += 50
            rankings[user_id]["name"] = user_name
            save_json(rankings, RANK_FILE)
            bot.send_message(active_polls[poll_id]["chat_id"], f"🎉 BOOM! **{user_name}** selected the right answer and won **50 Points**!")

CRASH_DICT = {
    "nullpointerexception": "⚠️ **Crash: NullPointerException**\nYou are using an object that is empty (null). Check your variables!",
    "indexoutofboundsexception": "⚠️ **Crash: IndexOutOfBoundsException**\nYou are accessing an item in a list that doesn't exist!",
    "activitynotfoundexception": "⚠️ **Crash: ActivityNotFoundException**\nYou forgot to declare your Activity in `AndroidManifest.xml`!"
}

# ================= LIVE WEBSITE SCRAPER =================
cached_website_data = ""
last_scrape_time = 0

def get_live_website_info():
    global cached_website_data, last_scrape_time
    if time.time() - last_scrape_time > 3600 or not cached_website_data:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get("https://www.appdevforall.org/codeonthego", headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            text_data = " ".join([p.text.strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']) if p.text.strip()])
            cached_website_data = text_data[:800] 
            last_scrape_time = time.time()
        except: return "Latest updates are posted on the official Telegram channel or website."
    return cached_website_data

# ================= TEXTS =================
DIVIDER = "━━━━━━━━━━━━━━━━━━━"
RULES_TEXT = f"""📌 *Code on the Go - Official Rules*
{DIVIDER}
1️⃣ *Be respectful:* Treat everyone with kindness. No harassment.
2️⃣ *Stay on topic:* Keep conversation focused on COTG & Android Dev.
3️⃣ *English only:* Please post in English so everyone understands.
4️⃣ *No spam/ads:* Do not post ads or unrelated links.
{DIVIDER}"""
IDE_INFO = f"🚀 *About Code on the Go (COTG)*\n{DIVIDER}\nBuild real Android apps completely on your phone, even offline! 📱💻\n🌐 *Website:* [appdevforall.org](https://www.appdevforall.org/codeonthego/)\n{DIVIDER}"

def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/CodeOnTheGoOfficial"))
    markup.row(InlineKeyboardButton("📜 Group Rules", callback_data="show_rules"), InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info"))
    markup.row(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main"))
    return markup

# ================= ADVANCED AI LOGIC (GOD MODE PROMPT) =================
chat_memory = {}

def get_grok_reply(user_id, user_msg, username, is_random_jump=False, is_code_review=False):
    global chat_memory
    try:
        # STRICT ANTI-HALLUCINATION RULES
        core_rules = """CRITICAL RULES YOU MUST OBEY:
1. NEVER say "I am a large language model", "I am an AI", or mention your limitations. You are CG, an expert Android Developer Assistant.
2. COTG (Code on the Go) IS STRICTLY NOT ON THE PLAY STORE. Do NOT mention the Play Store. It is downloaded ONLY from the official website (appdevforall.org) or Telegram channel.
3. Keep replies SHORT, confident, and directly answer the question in English.
"""
        if is_code_review:
            system_prompt = core_rules + "The user is sending you Kotlin/Java code. Find syntax errors, bugs, or improvements and explain them briefly."
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Review this code:\n{user_msg}"}]
        else:
            extra_context = ""
            if any(w in user_msg.lower() for w in ['update', 'new', 'feature', 'version', 'download']):
                extra_context = f"\n[WEBSITE INFO: {get_live_website_info()}] Tell them COTG is NOT on Play Store, check the website/channel."
            
            jump_rule = "You are randomly interjecting to keep the group lively. Be witty." if is_random_jump else ""
            system_prompt = core_rules + jump_rule + extra_context

            if user_id not in chat_memory: chat_memory[user_id] = []
            chat_memory[user_id].append({"role": "user", "content": f"User: {username}\nMessage: {user_msg}"})
            if len(chat_memory[user_id]) > 4: chat_memory[user_id] = chat_memory[user_id][-4:]
            
            messages = [{"role": "system", "content": system_prompt}] + chat_memory[user_id]

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.6, "max_tokens": 150}
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=12)
        if r.status_code == 200:
            ai_reply = r.json()['choices'][0]['message']['content'].strip()
            if not is_code_review: chat_memory[user_id].append({"role": "assistant", "content": ai_reply})
            return ai_reply
        return None
    except Exception as e: 
        print(f"Groq Error: {e}")
        return None

# ================= BUTTON CLICKS & NEW MEMBER =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules": bot.edit_message_text(RULES_TEXT, call.message.chat.id, call.message.message_id, reply_markup=get_back_button(), parse_mode='Markdown')
    elif call.data == "show_ide_info": bot.edit_message_text(IDE_INFO, call.message.chat.id, call.message.message_id, reply_markup=get_back_button(), parse_mode='Markdown', disable_web_page_preview=True)
    elif call.data == "back_to_main": bot.edit_message_text(f"Hello again! 👋\n{DIVIDER}\nI am **CG**, the highly advanced AI.", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(), parse_mode='Markdown')
    elif call.data == "close_menu": bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['new_chat_members'])
def welcome_members(message):
    for member in message.new_chat_members:
        if BOT_ID and member.id == BOT_ID:
            bot.send_message(message.chat.id, f"🚀 *HELLO EVERYONE!* 🚀\n{DIVIDER}\nI am **CG**, your Official Smart AI Assistant!\nInvited by Admin @{BOSS_ADMIN}.\n\n💡 Try `/review [code]` or `/vault`!", reply_markup=get_main_menu())
            continue
        bot.send_message(message.chat.id, f"Welcome @{member.first_name}! 🎉\n💡 I am **CG**, your AI assistant. Click below to read rules!", reply_markup=get_main_menu())

# ================= COMMANDS =================
@bot.message_handler(commands=['review'])
def code_reviewer(message):
    try:
        code_to_review = message.text.split(maxsplit=1)[1]
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, "🔍 **Analyzing your code...**")
        ai_review = get_grok_reply(str(message.from_user.id), code_to_review, message.from_user.first_name, is_code_review=True)
        if ai_review: bot.reply_to(message, f"👨‍💻 **Code Review:**\n{DIVIDER}\n{ai_review}")
        else: bot.reply_to(message, "⚠️ Couldn't review right now. Try again.")
    except: bot.reply_to(message, "⚠️ Usage: `/review [paste your kotlin/java code here]`")

@bot.message_handler(commands=['savecode'])
def save_code(message):
    try:
        parts = message.text.split(maxsplit=2)
        code_name = parts[1].lower()
        code_vault[code_name] = {"code": parts[2], "author": message.from_user.first_name}
        save_json(code_vault, VAULT_FILE)
        bot.reply_to(message, f"💾 **Code Saved!**\nGet it by typing: `/getcode {code_name}`")
    except: bot.reply_to(message, "⚠️ Usage: `/savecode [name] [code]`")

@bot.message_handler(commands=['getcode'])
def get_code(message):
    try:
        code_name = message.text.split()[1].lower()
        if code_name in code_vault: bot.reply_to(message, f"👨‍💻 **Code: {code_name}** (By {code_vault[code_name]['author']})\n{DIVIDER}\n`{code_vault[code_name]['code']}`", parse_mode='Markdown')
        else: bot.reply_to(message, "❌ Code not found.")
    except: pass

@bot.message_handler(commands=['vault'])
def list_vault(message):
    if not code_vault: return bot.reply_to(message, "🗄️ Vault is empty.")
    text = "🗄️ **Code Vault**\n" + DIVIDER + "\n" + "\n".join([f"• `{n}`" for n in code_vault.keys()])
    bot.reply_to(message, text)

# ================= MAIN CHAT HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_chat_handler(message):
    global msg_counter, interject_counter
    if not message.text: return
        
    text = message.text.lower().strip()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN)

    # --- 1. HARDCODED COMMANDS ---
    if text in ['help', '/help', 'rules', '/rules', 'menu', 'hello', 'hi', 'start', '/start']:
        return bot.reply_to(message, f"Hello @{username}! I am **CG** 🤖\nHow can I help you today?", reply_markup=get_main_menu())

    if text in ['my rank', 'my ranking', '/myrank', 'rank', 'cg my rank']:
        data = rankings.get(user_id, {"points": 0, "streak": 0})
        return bot.reply_to(message, f"🏆 *Your Rank*\n👤 {username}\n⭐ Points: **{data['points']}**\n🔥 Streak: **{data.get('streak', 0)} Days**\n🏅 Title: {get_title(data['points'])}")

    if text in ['leaderboard', 'top', '/top', '/leaderboard']:
        if not rankings: return bot.reply_to(message, "No points tracked yet!")
        sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        lb_text = f"🏅 *Top Active Members*\n{DIVIDER}\n"
        for i, (uid, data) in enumerate(sorted_users, 1): lb_text += f"{i}. **{data['name']}** — {data['points']} pts\n"
        return bot.reply_to(message, lb_text)

    # --- 2. DAILY STREAK & POINTS ---
    current_time = time.time()
    today_str = datetime.now().strftime("%Y-%m-%d")

    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username, "streak": 0, "last_date": ""}
        
        last_date_str = rankings[user_id].get("last_date", "")
        if last_date_str != today_str:
            if last_date_str and datetime.strptime(last_date_str, "%Y-%m-%d").date() == datetime.now().date() - timedelta(days=1):
                rankings[user_id]["streak"] += 1
            else: rankings[user_id]["streak"] = 1 
            
            rankings[user_id]["last_date"] = today_str
            rankings[user_id]["points"] += 20  
            bot.reply_to(message, f"🔥 **DAILY LOGIN!**\nYour streak is **{rankings[user_id]['streak']} Days**!\n🎁 +20 Points!\n\n{random.choice(DEV_JOKES)}")

        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 1  
            user_cooldown[user_id] = current_time
        if message.reply_to_message and message.reply_to_message.from_user.id != message.from_user.id: 
            rankings[user_id]["points"] += 2  
            
        rankings[user_id]["name"] = username
        save_json(rankings, RANK_FILE)
        
        msg_counter += 1
        interject_counter += 1

    # --- 3. BUG-BUSTER ---
    if "exception" in text or "error" in text:
        for err, fix in CRASH_DICT.items():
            if err in text: return bot.reply_to(message, fix)

    # --- 4. AUTO-QUIZ (TELEGRAM POLLS) ---
    if msg_counter >= 25:
        msg_counter = 0
        qp = random.choice(QUIZ_POLLS)
        poll_msg = bot.send_poll(chat_id, question=f"⏱️ FASTEST FINGER FIRST!\n{qp['q']}", options=qp['opts'], type='quiz', correct_option_id=qp['ans'], is_anonymous=False, explanation="Winner gets 50 Points!")
        active_polls[poll_msg.poll.id] = {"ans": qp['ans'], "chat_id": chat_id}

    # --- 5. FILTERS ---
    if any(word in text for word in ['gali1', 'fuck', 'shit', 'bitch', 'asshole']) and not is_boss:
        try:
            bot.delete_message(chat_id, message.message_id)
            warn = bot.send_message(chat_id, f"⚠️ @{username}, keep the language clean! 😇")
            time.sleep(10); bot.delete_message(chat_id, warn.message_id)
        except: pass
        return 

    # --- 6. SMART AI & RANDOM INTERJECTION ---
    bot_triggered = False
    is_random = False
    
    if "cg" in text or f"@{BOT_NAME.lower()}" in text or message.chat.type == 'private': 
        bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id: 
        bot_triggered = True
    elif interject_counter >= 15:
        bot_triggered = True
        is_random = True
        interject_counter = 0

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, message.text, username, is_random)
        if ai_reply: bot.reply_to(message, ai_reply)

# ================= RUN SERVER =================
try:
    bot.delete_webhook(drop_pending_updates=True) 
    time.sleep(2)
except: pass

keep_alive()
print("V20 THE GOD MODE Bot is LIVE!")
bot.polling(none_stop=True)
