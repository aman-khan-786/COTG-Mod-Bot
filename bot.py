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

# === PILLOW FOR DYNAMIC STICKERS ===
from PIL import Image, ImageDraw, ImageFont
import io

# ================= CONFIGURATION =================
TOKEN = '8515104266:AAGtADm-4BxboHfNcTB6TVKcmE7nD03r74M'
GROQ_API_KEY = "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"

BOSS_ADMIN_RAW = 'Ben_ADFA'
BOSS_ADMIN_MD = 'Ben\_ADFA'          
BOT_NAME = "CG"

OFFICIAL_CHANNEL = "https://t.me/CodeOnTheGoOfficial"
OFFICIAL_WEBSITE = "http://appdevforall.org/codeonthego"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

try: BOT_ID = bot.get_me().id
except: BOT_ID = None

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

# ================= STICKER GENERATOR ENGINE =================
def generate_trophy_sticker(username, title="WEEKLY CHAMPION"):
    try:
        # Load Template (sticker_bg.png must be in the folder)
        img = Image.open("sticker_bg.png").convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # Load Font securely with fallback to system fonts
        try:
            font_large = ImageFont.truetype("font.ttf", 45)
            font_small = ImageFont.truetype("font.ttf", 35)
        except:
            try:
                # Fallback for Linux/Render servers
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

        img_w, img_h = img.size
        
        # Draw Title (Center of the Red/White Circle)
        title_text = title.upper()
        try:
            title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
            title_w = title_bbox[2] - title_bbox[0]
        except:
            title_w = 250

        # Draw text at Y=190 for circle center
        draw.text(((img_w - title_w) / 2, 190), title_text, fill="black", font=font_large)

        # Draw Username (Center of the Bottom Ribbon)
        name_text = username.upper()
        try:
            name_bbox = draw.textbbox((0, 0), name_text, font=font_small)
            name_w = name_bbox[2] - name_bbox[0]
        except:
            name_w = 120

        # Draw text at Y=385 for ribbon center
        draw.text(((img_w - name_w) / 2, 385), name_text, fill="black", font=font_small)

        # Export to WebP for Telegram Sticker compatibility
        bio = io.BytesIO()
        bio.name = 'sticker.webp'
        img.save(bio, 'WEBP')
        bio.seek(0)
        return bio
    except Exception as e:
        print(f"Sticker Generator Error: {e}")
        return None

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
            system_prompt = "You are a strict programming judge. If the submitted code correctly solves the task and is valid, reply strictly starting with 'PASS: <your short feedback>'. If it has syntax errors or fails the logic, reply strictly starting with 'FAIL: <your short feedback>'."
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

# ================= MEDIA & LINK FILTER =================
@bot.message_handler(content_types=['sticker', 'animation'])
def handle_media(message):
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)
    if not is_boss:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            if user_id in rankings:
                rankings[user_id]["points"] = max(0, rankings[user_id]["points"] - 5)
                save_json(rankings, RANK_FILE)
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

# ================= SECRET TEST COMMAND =================
@bot.message_handler(commands=['super'])
def secret_test_sticker(message):
    parts = message.text.split(maxsplit=1)
    test_name = parts[1] if len(parts) > 1 else message.from_user.first_name
    
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.reply_to(message, f"🛠️ **SECRET TEST RUN INITIATED**\nGenerating dynamic sticker for: `{test_name}`...")
    
    sticker_stream = generate_trophy_sticker(test_name, "TEST CHAMPION")
    
    if sticker_stream:
        bot.send_sticker(message.chat.id, sticker_stream)
    else:
        bot.send_message(message.chat.id, "❌ **Error:** Sticker generate nahi hua. Please check if `font.ttf` / `sticker_bg.png` are properly uploaded.")

# ================= COMMANDS =================
@bot.message_handler(commands=['announce_winner'])
def announce_weekly_winner(message):
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)
    if not is_boss: return bot.reply_to(message, "🚫 Only Boss Admin can announce the winner!")
    
    if not rankings: return bot.reply_to(message, "No active users to announce.")
    
    sorted_users = sorted(rankings.items(), key=lambda x: x[1].get('points', 0), reverse=True)
    top_user_id, top_user_data = sorted_users[0]
    winner_name = top_user_data['name']
    
    if "trophies" not in rankings[top_user_id]: rankings[top_user_id]["trophies"] = 0
    rankings[top_user_id]["trophies"] += 1
    save_json(rankings, RANK_FILE)
    
    bot.send_chat_action(message.chat.id, 'upload_photo')
    sticker_stream = generate_trophy_sticker(winner_name, "WEEKLY CHAMPION")
    
    announcement_text = f"🚨 **WEEKLY CHAMPION ANNOUNCEMENT!** 🚨\n━━━━━━━━━━━━━━━━━━━\n\nCongratulations to {winner_name} for dominating the leaderboard! 🏆\n\nYou have been awarded +1 Trophy for your outstanding contribution to the COTG community.\nKeep coding, keep inspiring! 💻🔥"
    
    bot.send_message(message.chat.id, announcement_text)
    if sticker_stream:
        bot.send_sticker(message.chat.id, sticker_stream)

@bot.message_handler(commands=['setbounty', 'bounty', 'submit', 'review'])
def handle_coding_commands(message):
    cmd = message.text.split()[0].lower()
    
    if cmd == '/setbounty':
        if message.from_user.username != BOSS_ADMIN_RAW: return bot.reply_to(message, "🚫 Only Boss Admin!")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: `/setbounty [task]`")
        bounty_data["current_bounty"] = parts[1]
        bounty_data["winners"] = [] 
        save_json(bounty_data, BOUNTY_FILE)
        bot.send_message(message.chat.id, f"🏆 **NEW BOUNTY!**\n{parts[1]}")
        
    elif cmd == '/submit':
        user_id = str(message.from_user.id)
        if user_id in bounty_data.get("winners", []): return bot.reply_to(message, "⚠️ Already solved!")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: `/submit [code]`")
        bot.send_chat_action(message.chat.id, 'typing')
        eval_result = get_grok_reply(user_id, parts[1], message.from_user.first_name, is_bounty_eval=True)
        if eval_result and eval_result.startswith("PASS"):
            bounty_data["winners"].append(user_id)
            save_json(bounty_data, BOUNTY_FILE)
            if user_id not in rankings: rankings[user_id] = {"points": 0, "name": message.from_user.first_name, "trophies": 0, "last_active_date": datetime.now().strftime("%Y-%m-%d")}
            rankings[user_id]["points"] += 200
            save_json(rankings, RANK_FILE)
            bot.reply_to(message, f"🎉 **BOUNTY CLEARED!**\n{eval_result}\n\n🏆 +200 XP earned!")
        else: bot.reply_to(message, f"❌ **BOUNTY FAILED!**\n{eval_result if eval_result else 'Syntax error.'}")

    elif cmd == '/review':
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: `/review [code]`")
        bot.send_chat_action(message.chat.id, 'typing')
        ai_review = get_grok_reply(str(message.from_user.id), parts[1], message.from_user.first_name, is_code_review=True)
        if ai_review: bot.reply_to(message, f"👨‍💻 **Code Review:**\n{ai_review}")

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
                    return 
                except: pass

    # --- 2. ACCEPTED ANSWER (XP BOOST) ---
    ACCEPT_WORDS = ['thanks', 'thank you', 'worked', 'solved', 'fix ho gaya', 'perfect']
    if message.reply_to_message and message.reply_to_message.from_user.id != message.from_user.id:
        if any(word in text_lower for word in ACCEPT_WORDS):
            helper_id = str(message.reply_to_message.from_user.id)
            helper_name = message.reply_to_message.from_user.first_name
            if helper_id != str(BOT_ID): 
                if helper_id not in rankings: rankings[helper_id] = {"points": 0, "name": helper_name, "trophies": 0, "last_active_date": datetime.now().strftime("%Y-%m-%d")}
                rankings[helper_id]["points"] += 50
                save_json(rankings, RANK_FILE)
                bot.reply_to(message.reply_to_message, f"🌟 **Accepted Answer!**\n@{username} marked this as helpful.\n🎉 **+50 XP** awarded to {helper_name}!")

    # --- 3. POINTS TRACKING ---
    if message.chat.type in ['group', 'supergroup']:
        current_time_str = datetime.now().strftime("%Y-%m-%d")
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username, "trophies": 0, "last_active_date": current_time_str}
        
        rankings[user_id]["last_active_date"] = current_time_str
        rankings[user_id]["name"] = username
        
        current_time = time.time()
        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 1  
            user_cooldown[user_id] = current_time
            
        save_json(rankings, RANK_FILE)
        interject_counter += 1

    # --- 4. RANK & LEADERBOARD ---
    if text_lower in ['my rank', 'rank']:
        data = rankings.get(user_id, {"points": 0, "trophies": 0})
        sorted_users = sorted(rankings.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        position = next((index for index, (uid, _) in enumerate(sorted_users) if uid == user_id), len(sorted_users)) + 1
        
        return bot.reply_to(message, f"🏆 *Your Rank Card*\n👤 {username}\n⭐ XP: **{data.get('points', 0)}**\n🥇 Position: **#{position}** out of {len(rankings)} devs\n🏆 Trophies: **{data.get('trophies', 0)}**\n🏅 Title: {get_title(data.get('points', 0))}")

    if text_lower in ['leaderboard', 'top']:
        sorted_users = sorted(rankings.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        lb_text = "🏅 *COTG Leaderboard*\n━━━━━━━━━━━━━━━━━━━\n"
        for i, (uid, data) in enumerate(sorted_users, 1): 
            trophy_str = f"({data.get('trophies', 0)}🏆)" if data.get('trophies', 0) > 0 else ""
            lb_text += f"**#{i}** {data['name']} {trophy_str} — {data.get('points', 0)} XP\n"
        return bot.reply_to(message, lb_text)

    # --- 5. SMART AI ---
    bot_triggered = False
    if "cg" in text_lower or f"@{BOT_NAME.lower()}" in text_lower or message.chat.type == 'private': bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID: bot_triggered = True
    elif interject_counter >= 20: bot_triggered = True; interject_counter = 0

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, text, username)
        if ai_reply: bot.reply_to(message, ai_reply, disable_web_page_preview=True)

try: bot.delete_webhook(drop_pending_updates=True); time.sleep(2)
except: pass
keep_alive()
print("V31 ULTIMATE MASTER BOT IS LIVE!")
bot.polling(none_stop=True)
