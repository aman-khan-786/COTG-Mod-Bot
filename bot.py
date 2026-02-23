import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import urllib.request

# ================= CONFIG =================
TOKEN = '8515104266:AAGtADm-4BxboHfNcTB6TVKcmE7nD03r74M'
GROQ_API_KEY = "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"

BOSS_ADMIN_RAW = "Ben_ADFA"          # ← FIXED
BOSS_ADMIN_DISPLAY = "@Ben\\_ADFA"
BOT_NAME = "CG"
OFFICIAL_CHANNEL = "https://t.me/CodeOnTheGoOfficial"
OFFICIAL_WEBSITE = "http://appdevforall.org/codeonthego"

bot = telebot.TeleBot(TOKEN, parse_mode='MarkdownV2')

# Get bot username for proper mention detection
try:
    me = bot.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username
except:
    BOT_ID = None
    BOT_USERNAME = None

# ================= DATABASE =================
RANK_FILE = 'rankings.json'
BOUNTY_FILE = 'bounty.json'

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

rankings = load_json(RANK_FILE)
bounty_data = load_json(BOUNTY_FILE)

if "current_bounty" not in bounty_data:
    bounty_data = {"current_bounty": "No active bounty yet. Ask Ben to set one!", "winners": []}

user_cooldown = {}
chat_memory = {}

# ================= IMPROVED TROPHY STICKER =================
def generate_trophy_sticker(name, title="CHAMPION"):
    try:
        img = Image.open("sticker_bg.png").convert("RGBA")
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)

        try:
            font_large = ImageFont.truetype("font.ttf", 48)
            font_small = ImageFont.truetype("font.ttf", 38)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Gold text with shadow
        shadow = (0, 0, 0, 200)
        gold = (255, 215, 0, 255)

        draw.text((256, 180), title.upper(), fill=shadow, font=font_large, anchor="mm")
        draw.text((256, 180), title.upper(), fill=gold, font=font_large, anchor="mm")

        draw.text((256, 420), name.upper(), fill=shadow, font=font_small, anchor="mm")
        draw.text((256, 420), name.upper(), fill=gold, font=font_small, anchor="mm")

        bio = io.BytesIO()
        bio.name = 'trophy.webp'
        img.save(bio, 'WEBP', quality=95)
        bio.seek(0)
        return bio
    except Exception as e:
        print(f"Sticker Error: {e}")
        return None

# ================= SUPER POWERFUL AI =================
def get_grok_reply(user_id, user_msg, username):
    try:
        system_prompt = f"""You are CG — official expert assistant of **Code on the Go (COTG)**, an offline-first Android IDE.
Your creator, admin & ultimate boss is Ben {BOSS_ADMIN_DISPLAY}. 
Always mention him respectfully if asked about admin/creator.
You are extremely knowledgeable in Kotlin, Java, Android, Gradle, Jetpack Compose.
Be helpful, witty, professional and fun. Never say you are an AI model.

Current date: {datetime.now().strftime('%d %B %Y')}"""

        if user_id not in chat_memory:
            chat_memory[user_id] = []

        chat_memory[user_id].append({"role": "user", "content": f"{username}: {user_msg}"})
        if len(chat_memory[user_id]) > 6:
            chat_memory[user_id] = chat_memory[user_id][-6:]

        messages = [{"role": "system", "content": system_prompt}] + chat_memory[user_id]

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 400
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            timeout=10
        )

        if r.status_code == 200:
            reply = r.json()['choices'][0]['message']['content'].strip()
            chat_memory[user_id].append({"role": "assistant", "content": reply})
            return reply
    except:
        return "Bhai thoda load ho raha hai... 5-10 sec baad try kar 🔥"

    return None

# ================= MENU =================
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 Official Channel", url=OFFICIAL_CHANNEL),
        InlineKeyboardButton("🌐 Website", url=OFFICIAL_WEBSITE)
    )
    markup.add(
        InlineKeyboardButton("👑 Contact Ben", url=f"https://t.me/{BOSS_ADMIN_RAW}"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    )
    return markup

# ================= COMMANDS =================
@bot.message_handler(commands=['start', 'help', 'menu'])
def welcome(message):
    text = f"""👋 *Hello {message.from_user.first_name}!*

I am *CG* — Official Assistant of **Code on the Go**

My creator & admin is {BOSS_ADMIN_DISPLAY}

Type anything about Android dev or COTG IDE!"""
    bot.reply_to(message, text, reply_markup=get_main_menu(), disable_web_page_preview=True)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ['hello', 'hi', 'hey', 'sup', 'namaste', 'hii', 'hiii', 'help', 'menu'])
def greetings(message):
    text_lower = message.text.lower().strip()
    if 'help' in text_lower or 'menu' in text_lower:
        welcome(message)
        return

    replies = [
        f"Hello @{message.from_user.username or message.from_user.first_name}! 👋 I am active and ready!",
        "Arre waah bhai! Kya scene hai 🔥",
        "Hello ji! Ready for some serious coding? 💻"
    ]
    bot.reply_to(message, random.choice(replies) + "\n\nType /help for full menu.")

@bot.message_handler(commands=['admin', 'boss'])
def admin_info(message):
    bot.reply_to(message, f"""👑 *Bot Admin & Creator*

**Ben {BOSS_ADMIN_DISPLAY}**

He created me and maintains the entire Code on the Go project.
Contact him directly anytime.""")

@bot.message_handler(commands=['about'])
def about_cotg(message):
    bot.reply_to(message, f"""🚀 *Code on the Go (COTG)*

Offline-first Android IDE — real development on your phone, no internet needed after setup.

Official Links:
• Channel: {OFFICIAL_CHANNEL}
• Website: {OFFICIAL_WEBSITE}""", disable_web_page_preview=True)

# Trophy Test
@bot.message_handler(commands=['super'])
def secret_test(message):
    name = message.from_user.first_name.upper()
    bot.reply_to(message, f"🛠️ *TEST MODE ON*\nGenerating trophy for **{name}**...")
    sticker = generate_trophy_sticker(name, "TEST CHAMPION")
    if sticker:
        bot.send_sticker(message.chat.id, sticker)

# Weekly Winner Announcement
@bot.message_handler(commands=['announce_winner'])
def announce_winner(message):
    if message.from_user.username != BOSS_ADMIN_RAW:
        return bot.reply_to(message, "❌ Sirf Ben announce kar sakte hain!")
    
    if not rankings:
        return bot.reply_to(message, "Koi rankings nahi hain abhi.")

    top_user_id = max(rankings, key=lambda uid: rankings[uid].get('points', 0))
    data = rankings[top_user_id]
    name = data.get('name', 'Legend')

    if "trophies" not in data:
        data["trophies"] = 0
    data["trophies"] += 1
    save_json(rankings, RANK_FILE)

    sticker = generate_trophy_sticker(name, "WEEKLY CHAMPION")

    text = f"""🏆 *WEEKLY CHAMPION ANNOUNCED!* 🏆

Congratulations *{name}* for dominating the leaderboard!

You have earned the **WEEKLY CHAMPION** title +1 Trophy!

Keep grinding bhai! 🔥💻"""

    bot.send_message(message.chat.id, text)
    if sticker:
        bot.send_sticker(message.chat.id, sticker)

# ================= MAIN SMART HANDLER =================
@bot.message_handler(func=lambda message: True)
def smart_handler(message):
    if not message.text:
        return

    text = message.text.strip()
    text_lower = text.lower()
    user_id = str(message.from_user.id)
    username = message.from_user.first_name
    chat_id = message.chat.id

    # Ranking update
    if user_id not in rankings:
        rankings[user_id] = {"points": 0, "name": username, "trophies": 0, "last_active": str(datetime.now().date())}
    rankings[user_id]["points"] += 1
    rankings[user_id]["name"] = username
    save_json(rankings, RANK_FILE)

    # My Rank
    if any(x in text_lower for x in ['my rank', 'rank', 'cg my rank', 'myrank']):
        data = rankings[user_id]
        sorted_list = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)
        position = next((i+1 for i, (uid, _) in enumerate(sorted_list) if uid == user_id), len(rankings))

        reply = f"""🏅 *YOUR RANK CARD*

👤 *{username}*
⭐ *XP:* `{data['points']}`
📍 *Rank:* `#{position}` / {len(rankings)}
🏆 *Trophies:* `{data.get('trophies', 0)}`
🏷️ *Title:* {get_title(data['points'])}"""
        return bot.reply_to(message, reply)

    # Leaderboard
    if any(x in text_lower for x in ['leaderboard', 'top', 'lb']):
        sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        lb = "🏆 *COTG LEADERBOARD*\n\n"
        for i, (_, data) in enumerate(sorted_users, 1):
            lb += f"`#{i:2}` {data['name']} — *{data['points']}* XP\n"
        return bot.reply_to(message, lb)

    # AI Trigger (very powerful now)
    triggers = ['cg', 'cotg', 'code on the go', 'codeonthego', BOT_NAME.lower()]
    if BOT_USERNAME:
        triggers.append(BOT_USERNAME.lower())

    is_triggered = any(t in text_lower for t in triggers) or \
                   message.chat.type == 'private' or \
                   (message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID) or \
                   (BOT_USERNAME and f"@{BOT_USERNAME.lower()}" in text_lower)

    if is_triggered:
        bot.send_chat_action(chat_id, 'typing')
        reply = get_grok_reply(user_id, text, username)
        if reply:
            bot.reply_to(message, reply, disable_web_page_preview=True)

def get_title(points):
    if points < 100: return "Junior Dev 🟢"
    elif points < 300: return "Android Coder 🔵"
    elif points < 700: return "Kotlin Knight 🟣"
    elif points < 1500: return "COTG Architect 🟠"
    else: return "LEGENDARY DEVELOPER 🔥"

# ================= START BOT =================
print("🚀 CG Bot V2.0 - SUPER POWERFUL & FIXED VERSION LIVE!")
keep_alive()
bot.polling(none_stop=True)
