import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os
import random
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ================= CONFIGURATION =================
TOKEN = '8515104266:AAGtADm-4BxboHfNcTB6TVKcmE7nD03r74M'
GROQ_API_KEY = "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"

# Using escape character \ before underscore so Telegram Markdown doesn't break it
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

# ================= SMART LINK FILTER WHITELIST =================
ALLOWED_DOMAINS = [
    'github.com', 
    'stackoverflow.com', 
    'pastebin.com', 
    'appdevforall.org',
    'developer.android.com',
    't.me/CodeOnTheGoOfficial'
]

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

# ================= TEXTS =================
DIVIDER = "━━━━━━━━━━━━━━━━━━━"
RULES_TEXT = f"""📌 *Code on the Go - Official Rules*
{DIVIDER}
1️⃣ *No Promo Links:* Only GitHub, StackOverflow, & official links allowed.
2️⃣ *Be respectful:* Treat everyone with kindness. No harassment.
3️⃣ *English only:* Please post in English so everyone understands.
{DIVIDER}"""

IDE_INFO = f"🚀 *About Code on the Go (COTG)*\n{DIVIDER}\nBuild real Android apps completely on your phone, even offline! 📱💻\n🌐 *Website:* [{OFFICIAL_WEBSITE}]({OFFICIAL_WEBSITE})\n📢 *Updates:* [Join Channel]({OFFICIAL_CHANNEL})\n{DIVIDER}"

def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url=OFFICIAL_CHANNEL))
    markup.row(InlineKeyboardButton("📜 Group Rules", callback_data="show_rules"), InlineKeyboardButton("🚀 About COTG IDE", callback_data="show_ide_info"))
    markup.row(InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN_RAW}"), InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))
    return markup

# ================= ADVANCED AI LOGIC =================
chat_memory = {}

def get_grok_reply(user_id, user_msg, username, is_random_jump=False, is_code_review=False):
    global chat_memory
    try:
        core_rules = f"""CRITICAL DIRECTIVES:
1. IDENTITY: You are CG, the official moderation and dev assistant for 'Code on the Go' (COTG). 
2. NEVER SAY AI: You must NEVER say "I am an AI" or "I am a language model". You are just CG.
3. THE BOSS: Your ultimate boss and creator is Ben (@{BOSS_ADMIN_RAW}). If anyone asks about the admin or creator, praise Ben and give his handle.
4. PROMOTION: Always remind people to join the official channel: {OFFICIAL_CHANNEL} and visit {OFFICIAL_WEBSITE}.
5. NO PLAY STORE: COTG is STRICTLY NOT ON THE GOOGLE PLAY STORE. 
6. PERSONALITY: You are highly intelligent, helpful, witty, and slightly sarcastic. Speak STRICTLY in English.
"""
        if is_code_review:
            system_prompt = core_rules + "The user is sending you Kotlin/Java code. Find syntax errors, bugs, or improvements. Roast them a tiny bit for bad code, then explain how to fix it."
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Review this code:\n{user_msg}"}]
        else:
            extra_context = f"\n[WEBSITE INFO: {get_live_website_info()}]"
            jump_rule = f"You are randomly jumping into the chat. Make a funny comment about Android development or remind them to check {OFFICIAL_CHANNEL}." if is_random_jump else ""
            system_prompt = core_rules + jump_rule + extra_context

            if user_id not in chat_memory: chat_memory[user_id] = []
            chat_memory[user_id].append({"role": "user", "content": f"User: {username}\nMessage: {user_msg}"})
            if len(chat_memory[user_id]) > 5: chat_memory[user_id] = chat_memory[user_id][-5:]
            
            messages = [{"role": "system", "content": system_prompt}] + chat_memory[user_id]

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.6, "max_tokens": 300}
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=12)
        if r.status_code == 200:
            ai_reply = r.json()['choices'][0]['message']['content'].strip()
            if not is_code_review: chat_memory[user_id].append({"role": "assistant", "content": ai_reply})
            return ai_reply
        return None
    except Exception as e: return None

# ================= BUTTON CLICKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules": bot.edit_message_text(RULES_TEXT, call.message.chat.id, call.message.message_id, reply_markup=get_back_button(), parse_mode='Markdown')
    elif call.data == "show_ide_info": bot.edit_message_text(IDE_INFO, call.message.chat.id, call.message.message_id, reply_markup=get_back_button(), parse_mode='Markdown', disable_web_page_preview=True)
    elif call.data == "back_to_main": bot.edit_message_text(f"Hello again! 👋\n{DIVIDER}\nI am **CG**, your official COTG assistant.", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(), parse_mode='Markdown')
    elif call.data == "close_menu": bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['new_chat_members'])
def welcome_members(message):
    for member in message.new_chat_members:
        if BOT_ID and member.id == BOT_ID:
            bot.send_message(message.chat.id, f"🚀 *HELLO EVERYONE!* 🚀\n{DIVIDER}\nI am **CG**, the Official Assistant!\nMy Boss is @{BOSS_ADMIN_MD}.\n\n💡 Join {OFFICIAL_CHANNEL} for updates!", reply_markup=get_main_menu(), disable_web_page_preview=True)
            continue
        bot.send_message(message.chat.id, f"Welcome @{member.first_name}! 🎉\n💡 Please check the rules. No spam links allowed!", reply_markup=get_main_menu())

# ================= STICKER & GIF MODERATION =================
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
            warn_msg = bot.send_message(message.chat.id, f"🚫 @{username}, {media_type} are disabled to keep the group clean! **(-5 Points)** 📉")
            time.sleep(5)
            bot.delete_message(message.chat.id, warn_msg.message_id)
        except: pass

# ================= GITHUB API INTEGRATION =================
@bot.message_handler(commands=['github'])
def fetch_github(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: `/github [username/repo]`")
        
        repo_name = parts[1].strip()
        bot.send_chat_action(message.chat.id, 'typing')
        
        res = requests.get(f"https://api.github.com/repos/{repo_name}", timeout=5)
        if res.status_code == 200:
            data = res.json()
            desc = data.get('description', 'No description available.')
            stars = data.get('stargazers_count', 0)
            text = f"🐙 **GitHub Repo Info**\n{DIVIDER}\n📦 **Name:** `{data['full_name']}`\n⭐ **Stars:** {stars}\n📝 **Desc:** {desc}\n🔗 [View on GitHub]({data.get('html_url', '')})"
            bot.reply_to(message, text, disable_web_page_preview=True)
        else: bot.reply_to(message, "❌ Repository not found.")
    except: bot.reply_to(message, "⚠️ Error fetching GitHub data.")

# ================= COMMANDS =================
@bot.message_handler(commands=['review'])
def code_reviewer(message):
    try:
        raw_text = message.text.strip()
        if len(raw_text) <= 7: return bot.reply_to(message, "⚠️ Usage: `/review [paste your code here]`")
        code_to_review = raw_text[7:].strip()
        bot.send_chat_action(message.chat.id, 'typing')
        
        ai_review = get_grok_reply(str(message.from_user.id), code_to_review, message.from_user.first_name, is_code_review=True)
        if ai_review: bot.reply_to(message, f"👨‍💻 **Code Review:**\n{DIVIDER}\n{ai_review}")
        else: bot.reply_to(message, "⚠️ System overload. Try again.")
    except Exception as e: bot.reply_to(message, f"⚠️ Error in review: {str(e)}")

# ================= MAIN CHAT HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_chat_handler(message):
    global msg_counter, interject_counter
    if not message.text: return
        
    text = message.text.strip()
    text_lower = text.lower()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)

    # --- 1. HARDCORE SMART LINK FILTER ---
    if not is_boss:
        found_urls = URL_PATTERN.findall(text)
        if found_urls:
            is_spam = False
            for url in found_urls:
                if not any(domain in url for domain in ALLOWED_DOMAINS):
                    is_spam = True
                    break
            if is_spam:
                try:
                    bot.delete_message(chat_id, message.message_id)
                    if user_id in rankings:
                        rankings[user_id]["points"] = max(0, rankings[user_id]["points"] - 10)
                        save_json(rankings, RANK_FILE)
                    warn = bot.send_message(chat_id, f"🚫 @{username}, **Promo/Unknown Links are NOT allowed!**\nOnly official COTG links are permitted.\n📉 Penalty: -10 Points.")
                    time.sleep(7); bot.delete_message(chat_id, warn.message_id)
                    return 
                except: pass

    # --- 2. HARDCODED COMMANDS ---
    if text_lower in ['help', '/help', 'rules', '/rules', 'menu', 'hello', 'hi', 'start', '/start']:
        welcome_text = (f"Hello @{username}! I am **CG** 🤖\n"
                        f"Official COTG Bot. My boss is @{BOSS_ADMIN_MD}.\n\n"
                        f"📢 **Join Official Channel:** [CodeOnTheGoOfficial]({OFFICIAL_CHANNEL})\n"
                        f"🌐 **Website:** [{OFFICIAL_WEBSITE}]({OFFICIAL_WEBSITE})")
        return bot.reply_to(message, welcome_text, reply_markup=get_main_menu(), disable_web_page_preview=True)

    if text_lower in ['my rank', 'my ranking', '/myrank', 'rank']:
        data = rankings.get(user_id, {"points": 0, "streak": 0})
        return bot.reply_to(message, f"🏆 *Your Rank*\n👤 {username}\n⭐ Points: **{data['points']}**\n🔥 Streak: **{data.get('streak', 0)} Days**\n🏅 Title: {get_title(data['points'])}")

    # --- 3. DAILY STREAK & POINTS ---
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
            bot.reply_to(message, f"🔥 **DAILY LOGIN!**\nYour streak is **{rankings[user_id]['streak']} Days**!\n🎁 +20 Points!")

        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 1  
            user_cooldown[user_id] = current_time
            
        rankings[user_id]["name"] = username
        save_json(rankings, RANK_FILE)
        
        msg_counter += 1
        interject_counter += 1

    # --- 4. SMART AI & RANDOM INTERJECTION ---
    bot_triggered = False
    is_random = False
    
    if "cg" in text_lower or f"@{BOT_NAME.lower()}" in text_lower or message.chat.type == 'private': 
        bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id: 
        bot_triggered = True
    elif any(word in text_lower for word in ['admin', 'boss', 'creator', 'update', 'latest version', 'download']):
        bot_triggered = True
    elif interject_counter >= 15:
        bot_triggered = True
        is_random = True
        interject_counter = 0

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, text, username, is_random)
        if ai_reply: bot.reply_to(message, ai_reply, disable_web_page_preview=True)

# ================= RUN SERVER =================
try:
    bot.delete_webhook(drop_pending_updates=True) 
    time.sleep(2)
except: pass

keep_alive()
print("V26 FINAL FIX Bot is LIVE!")
bot.polling(none_stop=True)
