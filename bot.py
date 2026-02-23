import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os
import random
import re
import threading
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ================= CONFIGURATION =================
TOKEN = '8515104266:AAGtADm-4BxboHfNcTB6TVKcmE7nD03r74M'
GROQ_API_KEY = "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"

BOSS_ADMIN_RAW = 'Ben_ADFA'
BOSS_ADMIN_MD = 'Ben\_ADFA'          
BOT_NAME = "CG"

OFFICIAL_CHANNEL = "https://t.me/CodeOnTheGoOfficial"
OFFICIAL_WEBSITE = "http://appdevforall.org/codeonthego"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

try:
    BOT_ID = bot.get_me().id
except:
    BOT_ID = None

# ================= DATABASES =================
RANK_FILE = 'rankings.json'
BOUNTY_FILE = 'bounty.json'

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_json(data, file_path):
    with open(file_path, 'w') as f: json.dump(data, f, indent=2)

rankings = load_json(RANK_FILE)
bounty_data = load_json(BOUNTY_FILE)

if "current_bounty" not in bounty_data:
    bounty_data = {"current_bounty": "No active bounty yet. Ask admins to set one!", "winners": []}

user_cooldown = {} 
msg_counter = 0    
interject_counter = 0

def get_title(points):
    if points < 50: return "🟢 Junior Coder"
    elif points < 200: return "🔵 Bug Hunter"
    elif points < 500: return "🟣 Kotlin Pro"
    elif points < 1000: return "🟠 COTG Architect"
    else: return "🔴 Grandmaster"

ALLOWED_DOMAINS = ['github.com', 'stackoverflow.com', 'pastebin.com', 'appdevforall.org', 'developer.android.com', 't.me/CodeOnTheGoOfficial']
URL_PATTERN = re.compile(r'(https?://\S+|www\.\S+)')

# ================= LIVE WEBSITE SCRAPER =================
cached_website_data = ""
last_scrape_time = 0

def get_live_website_info():
    global cached_website_data, last_scrape_time
    if time.time() - last_scrape_time > 3600 or not cached_website_data:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(OFFICIAL_WEBSITE, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            text_data = " ".join([p.text.strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']) if p.text.strip()])
            cached_website_data = text_data[:800] 
            last_scrape_time = time.time()
        except: return f"Latest updates are posted on the official channel: {OFFICIAL_CHANNEL}"
    return cached_website_data

# ================= ADVANCED AI LOGIC =================
chat_memory = {}

def get_grok_reply(user_id, user_msg, username, is_code_review=False, is_bounty_eval=False):
    global chat_memory
    try:
        core_rules = f"IDENTITY: You are CG, expert dev assistant for COTG. Boss: @{BOSS_ADMIN_RAW}. Never call yourself an AI. Strictly English."
        
        if is_code_review:
            system_prompt = core_rules + " Review this Kotlin/Java code. Find bugs, roast mildly, give the fix."
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Review:\n{user_msg}"}]
        elif is_bounty_eval:
            system_prompt = "You are a strict programming judge. The user submitted code for the weekly bounty. If the code correctly solves the task and is valid, reply strictly starting with 'PASS: <your short feedback>'. If it has syntax errors or fails the logic, reply strictly starting with 'FAIL: <your short feedback>'."
            task = bounty_data.get("current_bounty", "")
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Task: {task}\nCode:\n{user_msg}"}]
        else:
            extra_context = f"\n[WEBSITE INFO: {get_live_website_info()}]"
            system_prompt = core_rules + extra_context
            if user_id not in chat_memory: chat_memory[user_id] = []
            chat_memory[user_id].append({"role": "user", "content": f"{username}: {user_msg}"})
            if len(chat_memory[user_id]) > 4: chat_memory[user_id] = chat_memory[user_id][-4:]
            messages = [{"role": "system", "content": system_prompt}] + chat_memory[user_id]

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.5, "max_tokens": 300}
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=12)
        if r.status_code == 200:
            reply = r.json()['choices'][0]['message']['content'].strip()
            if not is_code_review and not is_bounty_eval: chat_memory[user_id].append({"role": "assistant", "content": reply})
            return reply
        return None
    except: return None

# ================= BACKGROUND DECAY SYSTEM =================
def weekly_decay_job():
    while True:
        try:
            current_time_str = datetime.now().strftime("%Y-%m-%d")
            for uid, data in list(rankings.items()):
                last_active = data.get("last_active_date", current_time_str)
                days_inactive = (datetime.now() - datetime.strptime(last_active, "%Y-%m-%d")).days
                
                # Agar 7 din se inactive hai toh 10% XP cut
                if days_inactive >= 7:
                    penalty = int(data["points"] * 0.10)
                    if penalty > 0:
                        rankings[uid]["points"] -= penalty
                        rankings[uid]["last_active_date"] = current_time_str 
            save_json(rankings, RANK_FILE)
        except Exception as e:
            pass
        time.sleep(86400) # Check once every 24 hours

threading.Thread(target=weekly_decay_job, daemon=True).start()

# ================= MEDIA & LINK FILTER =================
@bot.message_handler(content_types=['sticker', 'animation'])
def handle_media(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)
    
    if not is_boss:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            if user_id in rankings:
                rankings[user_id]["points"] = max(0, rankings[user_id]["points"] - 5)
                save_json(rankings, RANK_FILE)
            
            media_type = "Stickers" if message.content_type == 'sticker' else "GIFs"
            warn_msg = bot.send_message(message.chat.id, f"🚫 @{username}, {media_type} are disabled! **(-5 XP)** 📉")
            time.sleep(4)
            bot.delete_message(message.chat.id, warn_msg.message_id)
        except: pass

# ================= UI KEYBOARDS =================
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url=OFFICIAL_CHANNEL))
    markup.row(InlineKeyboardButton("🚀 About COTG IDE", url=OFFICIAL_WEBSITE), InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN_RAW}"))
    markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "close_menu": bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['new_chat_members'])
def welcome_members(message):
    for member in message.new_chat_members:
        if BOT_ID and member.id == BOT_ID:
            bot.send_message(message.chat.id, f"🚀 *HELLO EVERYONE!* 🚀\nI am **CG**, the Official Assistant!\nMy Boss is @{BOSS_ADMIN_MD}.\n\n💡 Join {OFFICIAL_CHANNEL} for updates!", reply_markup=get_main_menu(), disable_web_page_preview=True)
            continue
        bot.send_message(message.chat.id, f"Welcome @{member.first_name}! 🎉\n💡 Please check the rules. No promo links allowed!", reply_markup=get_main_menu())

# ================= BOUNTY & CODE COMMANDS =================
@bot.message_handler(commands=['setbounty'])
def set_bounty(message):
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)
    if not is_boss: return bot.reply_to(message, "🚫 Only Boss Admin can set the bounty!")
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: `/setbounty [description of coding task]`")
    
    bounty_data["current_bounty"] = parts[1]
    bounty_data["winners"] = [] 
    save_json(bounty_data, BOUNTY_FILE)
    bot.send_message(message.chat.id, f"🏆 **NEW WEEKLY BOUNTY SET!**\n━━━━━━━━━━━━━━━━━━━\n{parts[1]}\n\n💻 Type `/submit [your code]` to solve it and win 200 XP!")

@bot.message_handler(commands=['bounty'])
def show_bounty(message):
    bot.reply_to(message, f"🏆 **Current Active Bounty:**\n{bounty_data.get('current_bounty', 'None')}\n\nType `/submit [code]` to attempt!")

@bot.message_handler(commands=['submit'])
def submit_bounty(message):
    user_id = str(message.from_user.id)
    username = message.from_user.first_name
    if user_id in bounty_data.get("winners", []):
        return bot.reply_to(message, "⚠️ You have already solved this bounty! Wait for the next one.")
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: `/submit [paste your code]`")
    
    bot.send_chat_action(message.chat.id, 'typing')
    eval_result = get_grok_reply(user_id, parts[1], username, is_bounty_eval=True)
    
    if eval_result and eval_result.startswith("PASS"):
        bounty_data["winners"].append(user_id)
        save_json(bounty_data, BOUNTY_FILE)
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username, "last_active_date": datetime.now().strftime("%Y-%m-%d")}
        rankings[user_id]["points"] += 200
        save_json(rankings, RANK_FILE)
        bot.reply_to(message, f"🎉 **BOUNTY CLEARED!**\n━━━━━━━━━━━━━━━━━━━\n{eval_result}\n\n🏆 Amazing job, {username}! You earned **+200 XP**!")
    else:
        reason = eval_result if eval_result else "Syntax error or incorrect logic."
        bot.reply_to(message, f"❌ **BOUNTY FAILED!**\n━━━━━━━━━━━━━━━━━━━\n{reason}\n\nTry debugging and submit again!")

@bot.message_handler(commands=['review'])
def code_reviewer(message):
    try:
        raw_text = message.text.strip()
        if len(raw_text) <= 7: return bot.reply_to(message, "⚠️ Usage: `/review [paste your code here]`")
        code_to_review = raw_text[7:].strip()
        bot.send_chat_action(message.chat.id, 'typing')
        ai_review = get_grok_reply(str(message.from_user.id), code_to_review, message.from_user.first_name, is_code_review=True)
        if ai_review: bot.reply_to(message, f"👨‍💻 **Code Review:**\n━━━━━━━━━━━━━━━━━━━\n{ai_review}")
        else: bot.reply_to(message, "⚠️ System overload. Try again.")
    except Exception as e: bot.reply_to(message, f"⚠️ Error in review: {str(e)}")

# ================= MAIN CHAT HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_chat_handler(message):
    global interject_counter
    if not message.text: return
        
    text = message.text.strip()
    text_lower = text.lower()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)

    # --- 1. LINK FILTER ---
    if not is_boss:
        found_urls = URL_PATTERN.findall(text)
        if found_urls:
            is_spam = False
            for url in found_urls:
                if not any(domain in url for domain in ALLOWED_DOMAINS): is_spam = True; break
            if is_spam:
                try:
                    bot.delete_message(chat_id, message.message_id)
                    if user_id in rankings:
                        rankings[user_id]["points"] = max(0, rankings[user_id]["points"] - 10)
                        save_json(rankings, RANK_FILE)
                    warn = bot.send_message(chat_id, f"🚫 @{username}, **Promo Links NOT allowed!**\nOnly official COTG, GitHub, or StackOverflow links are permitted.\n📉 Penalty: -10 XP.")
                    time.sleep(5); bot.delete_message(chat_id, warn.message_id)
                    return 
                except: pass

    # --- 2. ACCEPTED ANSWER SYSTEM (XP BOOST) ---
    ACCEPT_WORDS = ['thanks', 'thank you', 'worked', 'solved', 'fix ho gaya', 'perfect']
    if message.reply_to_message and message.reply_to_message.from_user.id != message.from_user.id:
        if any(word in text_lower for word in ACCEPT_WORDS):
            helper_id = str(message.reply_to_message.from_user.id)
            helper_name = message.reply_to_message.from_user.first_name
            if helper_id != str(BOT_ID): 
                if helper_id not in rankings: rankings[helper_id] = {"points": 0, "name": helper_name, "last_active_date": datetime.now().strftime("%Y-%m-%d")}
                rankings[helper_id]["points"] += 50
                save_json(rankings, RANK_FILE)
                bot.reply_to(message.reply_to_message, f"🌟 **Accepted Answer!**\n@{username} marked this as helpful.\n🎉 **+50 XP** awarded to {helper_name}!")

    # --- 3. POINTS & ACTIVITY TRACKING ---
    if message.chat.type in ['group', 'supergroup']:
        current_time_str = datetime.now().strftime("%Y-%m-%d")
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username, "last_active_date": current_time_str}
        
        rankings[user_id]["last_active_date"] = current_time_str
        rankings[user_id]["name"] = username
        
        # Give 1 XP per message (Max once per 60 seconds to avoid spam)
        current_time = time.time()
        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 1  
            user_cooldown[user_id] = current_time
            
        save_json(rankings, RANK_FILE)
        interject_counter += 1

    # --- 4. COMMANDS ---
    if text_lower in ['help', '/help', 'rules', '/rules', 'menu', 'hello', 'hi', 'start', '/start']:
        welcome_text = (f"Hello @{username}! I am **CG** 🤖\n"
                        f"Official COTG Bot. My boss is @{BOSS_ADMIN_MD}.\n\n"
                        f"📢 **Join Official Channel:** [CodeOnTheGoOfficial]({OFFICIAL_CHANNEL})\n"
                        f"🌐 **Website:** [{OFFICIAL_WEBSITE}]({OFFICIAL_WEBSITE})")
        return bot.reply_to(message, welcome_text, reply_markup=get_main_menu(), disable_web_page_preview=True)

    if text_lower in ['my rank', 'rank']:
        data = rankings.get(user_id, {"points": 0})
        return bot.reply_to(message, f"🏆 *Your Rank*\n👤 {username}\n⭐ XP: **{data['points']}**\n🏅 Title: {get_title(data['points'])}")

    if text_lower in ['leaderboard', 'top']:
        sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        lb_text = "🏅 *COTG Leaderboard*\n━━━━━━━━━━━━━━━━━━━\n"
        for i, (uid, data) in enumerate(sorted_users, 1): lb_text += f"{i}. **{data['name']}** — {data['points']} XP\n"
        return bot.reply_to(message, lb_text)

    # --- 5. SMART AI ---
    bot_triggered = False
    if "cg" in text_lower or f"@{BOT_NAME.lower()}" in text_lower or message.chat.type == 'private': bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID: bot_triggered = True
    elif any(word in text_lower for word in ['admin', 'boss', 'update']): bot_triggered = True
    elif interject_counter >= 20: bot_triggered = True; interject_counter = 0

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, text, username)
        if ai_reply: bot.reply_to(message, ai_reply, disable_web_page_preview=True)

try: bot.delete_webhook(drop_pending_updates=True); time.sleep(2)
except: pass
keep_alive()
print("V28 ALL-IN-ONE MASTER BOT IS LIVE!")
bot.polling(none_stop=True)
