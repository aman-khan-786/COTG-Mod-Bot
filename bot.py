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
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo'
GROQ_API_KEY = "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"
BOSS_ADMIN = 'Ben_ADFA'          
BOT_NAME = "CG"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# Bot ki ID pehle se save kar lo taaki Grand Entry miss na ho!
try:
    BOT_ID = bot.get_me().id
except:
    BOT_ID = None

# ================= DATABASES (Rankings & Vault) =================
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

def get_title(points):
    if points < 100: return "🟢 Beginner Coder"
    elif points < 300: return "🔵 Bug Hunter"
    elif points < 800: return "🟣 Kotlin Pro"
    else: return "🔴 COTG Legend"

# ================= QUIZ & BUG-BUSTER SYSTEM =================
QUIZ_QUESTIONS = [
    {"q": "Which programming language is officially recommended by Google for Android?", "a": "kotlin"},
    {"q": "What extension is used for Android UI layout files?", "a": ".xml"},
    {"q": "What tool in Android shows you the console logs and errors?", "a": "logcat"},
    {"q": "Which component is used to navigate between different screens in Android?", "a": "intent"},
    {"q": "What is the new modern UI toolkit for Android by Google?", "a": "jetpack compose"}
]
current_quiz = None

CRASH_DICT = {
    "nullpointerexception": "⚠️ **Crash Detected: NullPointerException**\nYou are trying to use an object that is empty (null). Check if you initialized your variables before using them!",
    "indexoutofboundsexception": "⚠️ **Crash Detected: IndexOutOfBoundsException**\nYou are trying to access an item in a list/array that doesn't exist. Check your list size!",
    "activitynotfoundexception": "⚠️ **Crash Detected: ActivityNotFoundException**\nYou forgot to declare your Activity in the `AndroidManifest.xml` file!",
    "networkonmainthreadexception": "⚠️ **Crash Detected: NetworkOnMainThreadException**\nYou cannot make API calls or network requests on the main UI thread. Use Coroutines!"
}

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
            text_data = " ".join([p.text.strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']) if p.text.strip()])
            cached_website_data = text_data[:800] 
            last_scrape_time = time.time()
        except: return "Latest info not available right now."
    return cached_website_data

# ================= TEXTS & UI =================
DIVIDER = "━━━━━━━━━━━━━━━━━━━"
RULES_TEXT = f"📌 *Code on the Go - Official Rules*\n{DIVIDER}\n1️⃣ *Be respectful:* No harassment.\n2️⃣ *English only:* So everyone understands.\n3️⃣ *No spam/ads:* Unauthorized promos will be removed.\n{DIVIDER}"
IDE_INFO = f"🚀 *About Code on the Go (COTG)*\n{DIVIDER}\nBuild real Android apps completely on your phone, even offline! 📱💻\n🌐 *Website:* [appdevforall.org](https://www.appdevforall.org/codeonthego/)\n{DIVIDER}"

def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/CodeOnTheGoOfficial"))
    markup.add(InlineKeyboardButton("🎥 Subscribe on YouTube", url="https://youtube.com/@appdevforall"))
    markup.row(InlineKeyboardButton("📜 Group Rules", callback_data="show_rules"), InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info"))
    markup.row(InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN}"), InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main"))
    return markup

# ================= ADVANCED AI LOGIC =================
chat_memory = {}

def get_grok_reply(user_id, user_msg, username):
    global chat_memory
    try:
        extra_context = ""
        msg_lower = user_msg.lower()
        if any(w in msg_lower for w in ['update', 'new', 'feature', 'latest', 'version']):
            extra_context = f"\n\n[LIVE INFO FROM OFFICIAL WEBSITE: {get_live_website_info()}]"

        system_prompt = f"""You are CG, the highly intelligent AI Assistant for 'Code on the Go' (COTG) Android coding community.
Rules:
1. Speak ONLY in English.
2. Keep replies SHORT and crisp.
3. Motivate users to build Android apps.{extra_context}"""

        if user_id not in chat_memory: chat_memory[user_id] = []
        chat_memory[user_id].append({"role": "user", "content": f"User: {username}\nMessage: {user_msg}"})
        if len(chat_memory[user_id]) > 4: chat_memory[user_id] = chat_memory[user_id][-4:]

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}] + chat_memory[user_id], "temperature": 0.7, "max_tokens": 150}
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            ai_reply = r.json()['choices'][0]['message']['content'].strip()
            chat_memory[user_id].append({"role": "assistant", "content": ai_reply})
            return ai_reply
        return None
    except: return None

# ================= COMMANDS =================
@bot.message_handler(commands=['savecode'])
def save_code(message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3: return bot.reply_to(message, "⚠️ Usage: `/savecode [name] [your_code_here]`")
        code_name = parts[1].lower()
        code_vault[code_name] = {"code": parts[2], "author": message.from_user.first_name}
        save_json(code_vault, VAULT_FILE)
        bot.reply_to(message, f"💾 **Code Saved!**\nAnyone can get it by typing: `/getcode {code_name}`")
    except: bot.reply_to(message, "Error saving code.")

@bot.message_handler(commands=['getcode'])
def get_code(message):
    try:
        code_name = message.text.split()[1].lower()
        if code_name in code_vault:
            data = code_vault[code_name]
            bot.reply_to(message, f"👨‍💻 **Code: {code_name}** (Saved by {data['author']})\n{DIVIDER}\n`{data['code']}`\n{DIVIDER}", parse_mode='Markdown')
        else: bot.reply_to(message, "❌ Code snippet not found in the vault.")
    except: bot.reply_to(message, "⚠️ Usage: `/getcode [name]`")

@bot.message_handler(commands=['vault'])
def list_vault(message):
    if not code_vault: return bot.reply_to(message, "🗄️ The Code Vault is empty.")
    text = "🗄️ **COTG Code Vault**\n" + DIVIDER + "\n"
    for name in code_vault.keys(): text += f"• `{name}`\n"
    text += f"\nTo view, type: `/getcode [name]`"
    bot.reply_to(message, text)

@bot.message_handler(commands=['award'])
def award_points(message):
    if not message.reply_to_message: return bot.reply_to(message, "⚠️ Reply to someone's message with `/award 50` to give them points!")
    try:
        pts = int(message.text.split()[1])
        g_id = str(message.from_user.id); r_id = str(message.reply_to_message.from_user.id)
        if g_id == r_id: return bot.reply_to(message, "❌ Cannot award points to yourself!")
        if rankings.get(g_id, {}).get("points", 0) < pts: return bot.reply_to(message, "❌ Not enough points!")
        rankings[g_id]["points"] -= pts
        if r_id not in rankings: rankings[r_id] = {"points": 0, "name": message.reply_to_message.from_user.first_name}
        rankings[r_id]["points"] += pts
        save_json(rankings, RANK_FILE)
        bot.reply_to(message, f"💸 **BOUNTY AWARDED!**\nYou gave **{pts} points** to {rankings[r_id]['name']}! 🎉")
    except: bot.reply_to(message, "⚠️ Use format: `/award 50`")

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
        # Grand Entry Fix (BOT_ID check)
        if BOT_ID and member.id == BOT_ID:
            bot.send_message(message.chat.id, f"🚀 *HELLO EVERYONE!* 🚀\n{DIVIDER}\nI am **CG**, your Official Smart AI Assistant!\nInvited by Admin @{BOSS_ADMIN}.\n\n💡 Try `/vault` to see saved code, or `my rank` to see your title!", reply_markup=get_main_menu())
            continue
        name = member.username if member.username else member.first_name
        bot.send_message(message.chat.id, f"Welcome to the community, @{name}! 🎉\n💡 I am **CG**, your AI assistant. Click below to read rules!", reply_markup=get_main_menu())

# ================= MAIN CHAT HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_chat_handler(message):
    global msg_counter, current_quiz
    if not message.text: return
        
    text = message.text.lower().strip()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN)

    # --- 1. DAILY STREAK & ANTI-SPAM ---
    current_time = time.time()
    today_str = datetime.now().strftime("%Y-%m-%d")

    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username, "streak": 0, "last_date": ""}
        
        last_date_str = rankings[user_id].get("last_date", "")
        if last_date_str != today_str:
            if last_date_str:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                if datetime.now().date() - last_date == timedelta(days=1):
                    rankings[user_id]["streak"] = rankings[user_id].get("streak", 0) + 1
                else: rankings[user_id]["streak"] = 1 
            else: rankings[user_id]["streak"] = 1
            
            rankings[user_id]["last_date"] = today_str
            rankings[user_id]["points"] += 50
            bot.reply_to(message, f"🔥 **DAILY LOGIN!**\nYour coding streak is now **{rankings[user_id]['streak']} Days**!\n🎁 +50 Bonus Points for being active today!")

        # 60 Second Cooldown (Anti-Spam)
        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 2  
            user_cooldown[user_id] = current_time
        if message.reply_to_message and message.reply_to_message.from_user.id != message.from_user.id: 
            rankings[user_id]["points"] += 5 
            
        rankings[user_id]["name"] = username
        save_json(rankings, RANK_FILE)
        msg_counter += 1

    # --- 2. BUG-BUSTER (Auto Error Detector) ---
    if "exception" in text or "error" in text:
        for err, fix in CRASH_DICT.items():
            if err in text:
                bot.reply_to(message, fix)
                return 

    # --- 3. QUIZ ANSWER CHECKER ---
    if current_quiz and text == current_quiz["a"]:
        bot.reply_to(message, f"🎉 **WINNER WINNER!** 🎉\n@{username} gave the right answer first!\nAnswer: **{current_quiz['a'].upper()}**\n🎁 You get **+100 Points**!")
        rankings[user_id]["points"] += 100
        save_json(rankings, RANK_FILE)
        current_quiz = None
        return

    # --- 4. AUTO-QUIZ TRIGGER ---
    if msg_counter >= 30:
        msg_counter = 0
        current_quiz = random.choice(QUIZ_QUESTIONS)
        bot.send_message(chat_id, f"⏱️ **FASTEST FINGER FIRST!** ⏱️\n{DIVIDER}\n❓ *Question:* {current_quiz['q']}\n\n*Reply fast with the correct word to win 100 Points!*", parse_mode='Markdown')

    # --- 5. FILTERS ---
    bad_words = ['gali1', 'spam', 'fuck', 'shit', 'bitch', 'asshole']
    if any(word in text for word in bad_words) and not is_boss:
        try:
            bot.delete_message(chat_id, message.message_id)
            warn = bot.send_message(chat_id, f"⚠️ @{username}, keep the language clean! 😇")
            time.sleep(10); bot.delete_message(chat_id, warn.message_id)
        except: pass
        return 

    if any(p in text for p in ['t.me/', 'discord.gg/']) and not is_boss and 'codeonthego' not in text:
        try:
            bot.delete_message(chat_id, message.message_id)
            warn = bot.send_message(chat_id, f"🚫 @{username}, promotions are not allowed here! 👍")
            time.sleep(10); bot.delete_message(chat_id, warn.message_id)
        except: pass
        return 

    # --- 6. PRIORITY COMMANDS ---
    if text in ['my rank', 'my ranking', '/myrank', 'rank', 'cg my rank']:
        data = rankings.get(user_id, {"points": 0, "streak": 0})
        bot.reply_to(message, f"🏆 *Your Rank*\n👤 {username}\n⭐ Points: **{data['points']}**\n🔥 Streak: **{data.get('streak', 0)} Days**\n🏅 Title: {get_title(data['points'])}\nKeep coding! 💻")
        return

    if text in ['leaderboard', 'top', '/top', '/leaderboard']:
        if not rankings: return bot.reply_to(message, "No points tracked yet!")
        sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        lb_text = f"🏅 *Top Active Members*\n{DIVIDER}\n"
        for i, (uid, data) in enumerate(sorted_users, 1): lb_text += f"{i}. **{data['name']}** — {data['points']} pts\n"
        bot.reply_to(message, lb_text)
        return

    # --- 7. SMART AI & FALLBACK ---
    bot_triggered = False
    if text == "cg": return bot.reply_to(message, f"Yes brother! I am here. 🤖 How can I help you, @{username}?")
    if "cg" in text or f"@{BOT_NAME.lower()}" in text or message.chat.type == 'private': bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id: bot_triggered = True

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, message.text, username)
        if ai_reply: bot.reply_to(message, ai_reply)
        else:
            if any(w in text for w in ['hi', 'hello', 'hey']): bot.reply_to(message, f"Hello @{username}! 👋 I am **CG**.")
            elif "who are you" in text: bot.reply_to(message, "I am **CG**! The Official Smart AI Assistant. 🤖✨")
            else: bot.reply_to(message, "Yes brother! I am operating in offline fallback mode right now.")

# ================= RUN SERVER (WITH ANTI-409 FIX) =================
try:
    bot.delete_webhook(drop_pending_updates=True) # This is the BRAMHASTRA for 409 errors!
    time.sleep(2)
except Exception as e:
    print(f"Webhook Clear Error: {e}")

keep_alive()
print("V17 The Ultimate Fix is LIVE!")
bot.polling(none_stop=True)
