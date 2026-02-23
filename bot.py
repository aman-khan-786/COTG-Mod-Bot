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
import urllib.request

# === PILLOW FOR DYNAMIC STICKERS ===
from PIL import Image, ImageDraw, ImageFont
import io

# ================= NEW CONFIG =================
TOKEN = '8515104266:AAF_hv7wTh238-mjnYkKeLGL0Q5tcC2ykks'

GROQ_KEYS = [
    "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",
    "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"
]

BOSS_ADMIN_RAW = 'Ben_ADFA'
OFFICIAL_CHANNEL = "https://t.me/CodeOnTheGoOfficial"
OFFICIAL_CHANNEL_ID = "@CodeOnTheGoOfficial" # For checking membership
OFFICIAL_WEBSITE = "http://appdevforall.org/codeonthego"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

try: BOT_ID = bot.get_me().id
except: BOT_ID = None

# ================= DATABASES =================
RANK_FILE = 'rankings.json'
BOUNTY_FILE = 'bounty.json'
CONFIG_FILE = 'group_config.json' # To save group ID for morning messages

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
group_config = load_json(CONFIG_FILE)

if "current_bounty" not in bounty_data:
    bounty_data = {"current_bounty": "No active bounty yet. Ask admins to set one!", "winners": []}

user_cooldown = {} 
interject_counter = 0

def get_title(points):
    if points < 50: return "🟢 Junior Coder"
    elif points < 200: return "🔵 Bug Hunter"
    elif points < 500: return "🟣 Kotlin Pro"
    elif points < 1000: return "🟠 COTG Architect"
    else: return "🔴 Grandmaster"

ALLOWED_DOMAINS = ['github.com', 'stackoverflow.com', 'pastebin.com', 'appdevforall.org', 'developer.android.com', 't.me/CodeOnTheGoOfficial']
URL_PATTERN = re.compile(r'(https?://\S+|www\.\S+)')
BAD_WORDS = ['fuck', 'shit', 'bitch', 'asshole', 'cunt', 'dick', 'pussy', 'chut', 'bc', 'madarchod', 'randi']

# ================= IMPROVED TROPHY STICKER =================
def generate_trophy_sticker(username, title="WEEKLY CHAMPION"):
    try:
        img_original = Image.open("sticker_bg.png").convert("RGBA")
        img = img_original.resize((512, 512), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        font_path = "font.ttf"
        fallback_path = "roboto.ttf"
        if not os.path.exists(font_path):
            try: urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf", fallback_path)
            except: pass
            font_path = fallback_path if os.path.exists(fallback_path) else "font.ttf"

        try:
            font_large = ImageFont.truetype(font_path, 48)
            font_small = ImageFont.truetype(font_path, 36)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text((256, 190), title.upper(), fill=(0,0,0,180), font=font_large, anchor="mm")
        draw.text((256, 190), title.upper(), fill=(255,215,0), font=font_large, anchor="mm")
        draw.text((256, 420), username.upper(), fill=(0,0,0,180), font=font_small, anchor="mm")
        draw.text((256, 420), username.upper(), fill=(255,215,0), font=font_small, anchor="mm")
        
        try:
            small_fnt = ImageFont.truetype(font_path, 26)
        except:
            small_fnt = ImageFont.load_default()
            
        draw.text((256, 470), "CODE ON THE GO", fill=(255,255,255,220), font=small_fnt, anchor="mm")

        bio = io.BytesIO()
        bio.name = 'sticker.webp'
        img.save(bio, 'WEBP', quality=95)
        bio.seek(0)
        return bio
    except Exception as e:
        print(f"Sticker Error: {e}")
        return None

# ================= DUAL KEY AI + FALLBACK =================
chat_memory = {}

def get_grok_reply(user_id, user_msg, username, is_code_review=False, is_matchmaker=False):
    for api_key in GROQ_KEYS: 
        try:
            # STRICT ADMIN RULE APPLIED HERE
            core_rules = f"IDENTITY: You are CG, expert dev assistant for COTG. Your creator and ONLY Admin/Boss is EXACTLY @{BOSS_ADMIN_RAW} (Ben). If anyone asks about admin, boss, or creator, reply with: 'My boss and admin is Ben (@{BOSS_ADMIN_RAW}).' Do not use any other username. Strictly English."
            
            if is_code_review:
                system_prompt = core_rules + " Review this Android/Kotlin code. Roast mildly, give the fix."
                messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Review:\n{user_msg}"}]
            elif is_matchmaker:
                system_prompt = core_rules + " A user is asking a technical question. Briefly explain the concept in 2 lines."
                messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}]
            else:
                system_prompt = core_rules
                if user_id not in chat_memory: chat_memory[user_id] = []
                chat_memory[user_id].append({"role": "user", "content": f"{username}: {user_msg}"})
                if len(chat_memory[user_id]) > 4: chat_memory[user_id] = chat_memory[user_id][-4:]
                messages = [{"role": "system", "content": system_prompt}] + chat_memory[user_id]

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.6, "max_tokens": 300}
            
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=9)
            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content'].strip()
                if not is_code_review and not is_matchmaker: chat_memory[user_id].append({"role": "assistant", "content": reply})
                return reply
        except:
            continue
    return None

# ================= DAILY MORNING ROUTINE (NextGen) =================
def morning_scheduler():
    while True:
        # Check time (Running UTC, so approx 2:30 AM UTC = 8:00 AM IST)
        now = datetime.utcnow()
        if now.hour == 2 and now.minute == 30:
            group_id = group_config.get("main_group_id")
            if group_id:
                try:
                    # 1. Motivational Message
                    msg = "🌅 **Good Morning Devs!** ☕\n\nWake up, grab your coffee, and let's build something amazing today! Whether it's fixing that UI bug in Jetpack Compose or publishing a new app, keep grinding on Code on the Go! 💻🔥"
                    bot.send_message(group_id, msg)
                    
                    # 2. Daily Quiz
                    quizzes = [
                        {"q": "What is the primary language used for Jetpack Compose?", "o": ["Java", "Kotlin", "C++", "Dart"], "a": 1},
                        {"q": "Which modifier is used to make a Composable clickable?", "o": ["Modifier.click()", "Modifier.clickable()", "Modifier.tap()", "Modifier.press()"], "a": 1},
                        {"q": "What is Android's latest UI toolkit called?", "o": ["XML Views", "Flutter", "Jetpack Compose", "React Native"], "a": 2}
                    ]
                    quiz = random.choice(quizzes)
                    bot.send_poll(group_id, quiz["q"], quiz["o"], is_anonymous=False, type='quiz', correct_option_id=quiz["a"])
                except Exception as e:
                    print(f"Morning routine failed: {e}")
            time.sleep(60) # Sleep 1 minute to avoid sending twice
        time.sleep(30)

threading.Thread(target=morning_scheduler, daemon=True).start()

# ================= KEYBOARDS & MENU =================
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Official Channel", url=OFFICIAL_CHANNEL))
    markup.row(InlineKeyboardButton("🚀 About COTG IDE", url=OFFICIAL_WEBSITE), InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{BOSS_ADMIN_RAW}"))
    markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "close_menu": bot.delete_message(call.message.chat.id, call.message.message_id)

# ================= ORDERED HANDLERS (CRITICAL FOR WELCOME MSG) =================

# 1. NEW MEMBER WELCOME (Must be at the top)
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_members(message):
    for member in message.new_chat_members:
        if member.id == BOT_ID: continue
        uid = str(member.id)
        name = member.first_name
        
        if uid not in rankings:
            rankings[uid] = {"points": 0, "name": name, "skills": {"compose": 0, "kotlin": 0}, "last_active_date": datetime.now().strftime("%Y-%m-%d")}
            save_json(rankings, RANK_FILE)
            
        welcome_text = (f"🎉 *Welcome to COTG, {name}!* 🎉\n\n"
                        f"We build Android apps right on our phones! 📱💻\n\n"
                        f"🎁 **NEW USER TASK:** Join our official channel {OFFICIAL_CHANNEL_ID} and then type `/claim` here to get a free **+100 XP** bonus!\n\n"
                        f"Type `/help` to see what I can do.")
        bot.reply_to(message, welcome_text, reply_markup=get_main_menu())

# 2. MEDIA HANDLER
@bot.message_handler(content_types=['sticker', 'animation', 'video_note'])
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

# 3. COMMANDS
@bot.message_handler(commands=['setgroup'])
def set_morning_group(message):
    if message.from_user.username == BOSS_ADMIN_RAW:
        group_config["main_group_id"] = message.chat.id
        save_json(group_config, CONFIG_FILE)
        bot.reply_to(message, "✅ **Group ID Saved!** I will now send the Daily Morning message and Quiz here.")
    else:
        bot.reply_to(message, "🚫 Only Boss Admin can set this.")

@bot.message_handler(commands=['claim'])
def claim_channel_reward(message):
    user_id = message.from_user.id
    uid_str = str(user_id)
    try:
        # Check if user is in channel
        member = bot.get_chat_member(OFFICIAL_CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            if uid_str not in rankings: rankings[uid_str] = {"points": 0, "name": message.from_user.first_name}
            
            # Check if already claimed (prevent spam)
            if rankings[uid_str].get("claimed_bonus"):
                return bot.reply_to(message, "⚠️ You have already claimed your welcome bonus!")
                
            rankings[uid_str]["points"] += 100
            rankings[uid_str]["claimed_bonus"] = True
            save_json(rankings, RANK_FILE)
            bot.reply_to(message, f"🎉 **AWESOME!** Thank you for joining the channel.\n\nYou have received **+100 XP**! Check your `/rank`.")
        else:
            bot.reply_to(message, f"❌ You haven't joined the channel yet!\nPlease join {OFFICIAL_CHANNEL_ID} first, then type `/claim`.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ensure I am an admin in the channel so I can check your membership, or channel ID is correct.")

@bot.message_handler(commands=['start', 'help', 'menu', 'rules'])
def welcome_command(message):
    welcome_text = (f"Hello @{message.from_user.username or message.from_user.first_name}! I am **CG** 🤖\n"
                    f"Official COTG Bot. My boss is @{BOSS_ADMIN_RAW}.\n\n"
                    f"📢 **Join Official Channel:** {OFFICIAL_CHANNEL_ID}\n"
                    f"🌐 **Website:** [{OFFICIAL_WEBSITE}]({OFFICIAL_WEBSITE})")
    bot.reply_to(message, welcome_text, reply_markup=get_main_menu(), disable_web_page_preview=True)

@bot.message_handler(commands=['super'])
def secret_test_sticker(message):
    parts = message.text.split(maxsplit=1)
    test_name = parts[1] if len(parts) > 1 else message.from_user.first_name
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.reply_to(message, f"🛠️ **SECRET TEST RUN INITIATED**\nGenerating dynamic sticker for: `{test_name}`...")
    sticker_stream = generate_trophy_sticker(test_name, "TEST CHAMPION")
    if sticker_stream: bot.send_sticker(message.chat.id, sticker_stream)
    else: bot.send_message(message.chat.id, "❌ Sticker generate nahi hua.")

@bot.message_handler(commands=['announce_winner'])
def announce_weekly_winner(message):
    if message.from_user.username != BOSS_ADMIN_RAW: return bot.reply_to(message, "🚫 Only Boss Admin!")
    if not rankings: return bot.reply_to(message, "No active users.")
    sorted_users = sorted(rankings.items(), key=lambda x: x[1].get('points', 0), reverse=True)
    top_user_id, top_user_data = sorted_users[0]
    
    if "trophies" not in rankings[top_user_id]: rankings[top_user_id]["trophies"] = 0
    rankings[top_user_id]["trophies"] += 1
    save_json(rankings, RANK_FILE)
    
    sticker_stream = generate_trophy_sticker(top_user_data['name'], "WEEKLY CHAMPION")
    bot.send_message(message.chat.id, f"🚨 **WEEKLY CHAMPION!** 🚨\n\nCongrats {top_user_data['name']}! 🏆 (+1 Trophy)\nKeep coding!")
    if sticker_stream: bot.send_sticker(message.chat.id, sticker_stream)

# 4. MAIN TEXT HANDLER
@bot.message_handler(content_types=['text'])
def smart_chat_handler(message):
    global interject_counter
    text = message.text.strip()
    text_lower = text.lower()
    chat_id = message.chat.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = str(message.from_user.id)
    is_boss = (message.from_user.username == BOSS_ADMIN_RAW)

    # --- BAD WORDS & LINKS ---
    if not is_boss:
        if any(bad in text_lower for bad in BAD_WORDS):
            try: bot.delete_message(chat_id, message.message_id); bot.reply_to(message, "⚠️ Watch your language!")
            except: pass
            return
            
        found_urls = URL_PATTERN.findall(text)
        if found_urls:
            is_spam = False
            for url in found_urls:
                if not any(domain in url for domain in ALLOWED_DOMAINS): is_spam = True; break
            if is_spam:
                try:
                    bot.delete_message(chat_id, message.message_id)
                    if user_id in rankings: rankings[user_id]["points"] = max(0, rankings[user_id]["points"] - 10)
                    save_json(rankings, RANK_FILE)
                except: pass
                return 

    # --- SMART DEV MATCHMAKER (NextGen Feature) ---
    if "?" in text and any(k in text_lower for k in ["error", "bug", "crash", "compose", "kotlin", "how to"]):
        # Find top expert
        expert_name = None
        expert_points = -1
        for uid, data in rankings.items():
            if uid != user_id and data.get("points", 0) > expert_points:
                expert_points = data.get("points", 0)
                expert_name = data.get("name", "A Pro Dev")
        
        if expert_name and expert_points > 10:
            ai_hint = get_grok_reply(user_id, text, username, is_matchmaker=True)
            match_msg = f"🔍 **Dev Matchmaker Activated!**\n\nLooks like a tricky question! I'm tagging our top dev **{expert_name}** to help you out.\n\n*CG's quick hint:* {ai_hint if ai_hint else 'Check your syntax or logs!'}"
            bot.reply_to(message, match_msg)
            return

    # --- ACCEPTED ANSWER ---
    ACCEPT_WORDS = ['thanks', 'thank you', 'worked', 'solved', 'fix ho gaya', 'perfect']
    if message.reply_to_message and message.reply_to_message.from_user.id != message.from_user.id:
        if any(word in text_lower for word in ACCEPT_WORDS):
            helper_id = str(message.reply_to_message.from_user.id)
            helper_name = message.reply_to_message.from_user.first_name
            if helper_id != str(BOT_ID): 
                if helper_id not in rankings: rankings[helper_id] = {"points": 0, "name": helper_name}
                rankings[helper_id]["points"] += 50
                save_json(rankings, RANK_FILE)
                bot.reply_to(message.reply_to_message, f"🌟 **Accepted Answer!**\n@{username} marked this helpful.\n🎉 **+50 XP** to {helper_name}!")

    # --- POINTS TRACKING ---
    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username}
        rankings[user_id]["name"] = username
        current_time = time.time()
        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 1  
            user_cooldown[user_id] = current_time
        save_json(rankings, RANK_FILE)
        interject_counter += 1

    # --- RANK & LEADERBOARD ---
    if text_lower in ['my rank', 'rank', 'cg my rank']:
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

    # --- AI TRIGGER ---
    bot_triggered = False
    if "cg" in text_lower or f"@{BOT_NAME.lower()}" in text_lower or message.chat.type == 'private': bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID: bot_triggered = True
    elif any(word in text_lower for word in ['admin', 'boss', 'update', 'creator']): bot_triggered = True
    elif interject_counter >= 15: bot_triggered = True; interject_counter = 0

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, text, username)
        if ai_reply: bot.reply_to(message, ai_reply, disable_web_page_preview=True)

try: bot.delete_webhook(drop_pending_updates=True); time.sleep(2)
except: pass
keep_alive()
print("🚀 CG Bot V5.0 - NEXTGEN FEATURES LIVE!")
bot.polling(none_stop=True)
