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

BOSS_ADMIN_RAW = "Ben_ADFA"
BOSS_ADMIN_DISPLAY = "@Ben\\_ADFA"
BOT_NAME = "CG"
OFFICIAL_CHANNEL = "https://t.me/CodeOnTheGoOfficial"
OFFICIAL_WEBSITE = "http://appdevforall.org/codeonthego"
CHANNEL_PHOTO = "https://i.imgur.com/8vL2k9P.png"  # Channel logo (green globe) — change if needed

bot = telebot.TeleBot(TOKEN, parse_mode='MarkdownV2')

try:
    me = bot.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username.lower()
except:
    BOT_ID = None
    BOT_USERNAME = None

# ================= DATABASES =================
RANK_FILE = 'rankings.json'
BOUNTY_FILE = 'bounty.json'

def load_json(file):
    if os.path.exists(file):
        try: return json.load(open(file))
        except: return {}
    return {}

def save_json(data, file):
    with open(file, 'w') as f: json.dump(data, f, indent=2)

rankings = load_json(RANK_FILE)
bounty_data = load_json(BOUNTY_FILE)

if "current_bounty" not in bounty_data:
    bounty_data = {"current_bounty": "No active bounty yet!", "winners": []}

chat_memory = {}

# ================= PERFECT TROPHY STICKER (FIXED TEXT) =================
def generate_trophy_sticker(name, title="WEEKLY CHAMPION"):
    try:
        img = Image.open("sticker_bg.png").convert("RGBA").resize((512, 512), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)

        try:
            font_big = ImageFont.truetype("font.ttf", 52)
            font_med = ImageFont.truetype("font.ttf", 38)
            font_small = ImageFont.truetype("font.ttf", 28)
        except:
            font_big = font_med = font_small = ImageFont.load_default()

        # Gold with shadow
        draw.text((256, 160), title.upper(), fill=(0,0,0,180), font=font_big, anchor="mm")
        draw.text((256, 160), title.upper(), fill=(255,215,0), font=font_big, anchor="mm")
        
        draw.text((256, 380), name.upper(), fill=(0,0,0,180), font=font_med, anchor="mm")
        draw.text((256, 380), name.upper(), fill=(255,215,0), font=font_med, anchor="mm")
        
        draw.text((256, 460), "CODE ON THE GO", fill=(255,255,255,200), font=font_small, anchor="mm")

        bio = io.BytesIO()
        bio.name = 'trophy.webp'
        img.save(bio, 'WEBP', quality=95)
        bio.seek(0)
        return bio
    except:
        return None

# ================= LIVE UPDATES SCRAPER =================
def get_live_updates():
    try:
        r = requests.get(OFFICIAL_WEBSITE, timeout=6)
        # Simple latest version detection (you can improve)
        if "26.08" in r.text: return "✅ Latest Preview: **26.08** available!\nDownload: https://www.appdevforall.org/codeonthego"
        return "Latest updates on website: " + OFFICIAL_WEBSITE
    except:
        return "Latest updates: Check official channel & website 🔥"

# ================= EXTREME FALLBACK + AI =================
def get_fallback_reply(text_lower, username):
    if any(w in text_lower for w in ['admin', 'boss', 'creator', 'made you', 'who is admin', 'ben']):
        return f"👑 My creator, admin & ultimate boss is **Ben {BOSS_ADMIN_DISPLAY}**.\nContact him directly for anything important!"
    if any(w in text_lower for w in ['hello', 'hi', 'hey', 'sup', 'namaste']):
        return f"Hello {username}! 👋 I'm active and ready to code with you. Type /help"
    if 'help' in text_lower or 'menu' in text_lower:
        return "📋 Full menu:\n/start - Welcome\n/help - This menu\n/rank - Your rank\n/leaderboard - Top devs\n/updates - Live COTG version\n/admin - Contact Ben"
    if 'rank' in text_lower:
        return "Type `/rank` or `my rank` to see your XP & position 🔥"
    return None

def get_grok_reply(user_id, user_msg, username):
    try:
        system = f"""You are CG — official bot of Code on the Go (offline Android IDE).
Creator & BOSS is ONLY Ben {BOSS_ADMIN_DISPLAY}. 
If anyone asks about admin, creator, boss or who made you → ALWAYS reply with Ben's name and @Ben_ADFA.
Be friendly, fun, helpful and talk like a real dev friend. Use emojis. Never say you are AI."""

        if user_id not in chat_memory: chat_memory[user_id] = []
        chat_memory[user_id].append({"role": "user", "content": user_msg})
        if len(chat_memory[user_id]) > 5: chat_memory[user_id] = chat_memory[user_id][-5:]

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": system}] + chat_memory[user_id],
            "temperature": 0.75,
            "max_tokens": 350
        }

        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=9)
        
        if r.status_code == 200:
            reply = r.json()['choices'][0]['message']['content'].strip()
            chat_memory[user_id].append({"role": "assistant", "content": reply})
            return reply
    except:
        return None
    return None

# ================= KEYBOARDS =================
def get_main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("📢 Official Channel", url=OFFICIAL_CHANNEL))
    m.add(InlineKeyboardButton("🌐 Website", url=OFFICIAL_WEBSITE))
    m.add(InlineKeyboardButton("👑 Contact Ben", url=f"https://t.me/{BOSS_ADMIN_RAW}"))
    m.add(InlineKeyboardButton("❌ Close", callback_data="close"))
    return m

# ================= AUTO WELCOME NEW MEMBER =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.id == BOT_ID: continue
        user_id = str(member.id)
        name = member.first_name
        
        if user_id not in rankings:
            rankings[user_id] = {"points": 50, "name": name, "trophies": 0}  # Welcome bonus
        else:
            rankings[user_id]["points"] += 50
        save_json(rankings, RANK_FILE)

        welcome_text = f"""🎉 *Welcome to COTG Family, {name}!* 🎉

You just got **+50 XP** welcome bonus!

📢 Join Official Channel: [CodeOnTheGoOfficial]({OFFICIAL_CHANNEL})
🌐 Website: {OFFICIAL_WEBSITE}

Type /help to see commands.
Happy coding! 💻🔥"""

        try:
            bot.send_photo(message.chat.id, CHANNEL_PHOTO, caption=welcome_text, parse_mode='MarkdownV2', reply_markup=get_main_menu())
        except:
            bot.reply_to(message, welcome_text, reply_markup=get_main_menu())

# ================= COMMANDS =================
@bot.message_handler(commands=['start', 'help', 'menu'])
def welcome(message):
    text = f"""👋 *Hello {message.from_user.first_name}!*

I am *CG* — Official Assistant of **Code on the Go**

My boss is **Ben {BOSS_ADMIN_DISPLAY}**

Use commands or just chat with me!"""
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    bot.reply_to(message, f"👑 **Bot Admin & Creator**\n\n**Ben {BOSS_ADMIN_DISPLAY}**\nDirect contact: @Ben_ADFA")

@bot.message_handler(commands=['updates'])
def live_updates(message):
    bot.reply_to(message, f"🔄 *Live COTG Updates*\n\n{get_live_updates()}")

@bot.message_handler(commands=['rules'])
def rules(message):
    bot.reply_to(message, """📜 *Group Rules*
1. No spam / off-topic
2. Respect everyone
3. Share code & help others
4. Only official links allowed
Enjoy coding! 🔥""")

@bot.message_handler(commands=['super'])
def test_trophy(message):
    name = message.from_user.first_name.upper()
    bot.reply_to(message, f"🛠️ Generating trophy for **{name}**...")
    sticker = generate_trophy_sticker(name, "TEST CHAMPION")
    if sticker: bot.send_sticker(message.chat.id, sticker)

@bot.message_handler(commands=['announce_winner'])
def announce_winner(message):
    if message.from_user.username != BOSS_ADMIN_RAW:
        return bot.reply_to(message, "❌ Only Ben can announce winner!")
    
    if not rankings: return bot.reply_to(message, "No users yet")
    
    top_id = max(rankings, key=lambda x: rankings[x].get('points', 0))
    data = rankings[top_id]
    name = data['name']
    
    data['trophies'] = data.get('trophies', 0) + 1
    save_json(rankings, RANK_FILE)
    
    sticker = generate_trophy_sticker(name, "WEEKLY CHAMPION")
    
    text = f"""🏆 *WEEKLY CHAMPION ANNOUNCED!* 🏆

Congratulations **{name}**! 
You are the **WEEKLY CHAMPION** +1 Trophy added!

Keep grinding bhai 🔥"""
    
    bot.send_message(message.chat.id, text)
    if sticker: bot.send_sticker(message.chat.id, sticker)

# ================= RANKING & LEADERBOARD =================
@bot.message_handler(func=lambda m: m.text and any(x in m.text.lower() for x in ['my rank', 'rank', 'cg my rank']))
def my_rank(message):
    uid = str(message.from_user.id)
    data = rankings.get(uid, {"points": 0, "trophies": 0})
    sorted_r = sorted(rankings.items(), key=lambda x: x[1].get('points',0), reverse=True)
    pos = next((i+1 for i,(u,d) in enumerate(sorted_r) if u==uid), len(rankings))
    
    bot.reply_to(message, f"""🏅 *YOUR RANK*
👤 {message.from_user.first_name}
⭐ XP: **{data['points']}**
📍 Rank: **#{pos}**
🏆 Trophies: **{data.get('trophies',0)}**""")

@bot.message_handler(func=lambda m: m.text and any(x in m.text.lower() for x in ['leaderboard', 'top', 'lb']))
def leaderboard(message):
    sorted_r = sorted(rankings.items(), key=lambda x: x[1].get('points',0), reverse=True)[:12]
    txt = "🏆 *COTG LEADERBOARD*\n\n"
    for i, (uid, d) in enumerate(sorted_r, 1):
        txt += f"`#{i:2}` {d['name']} — **{d['points']}** XP\n"
    bot.reply_to(message, txt)

# ================= MAIN CHAT HANDLER (EXTREME) =================
@bot.message_handler(func=lambda message: True)
def main_handler(message):
    if not message.text: return
    text = message.text.strip()
    text_lower = text.lower()
    uid = str(message.from_user.id)
    name = message.from_user.first_name

    # Ranking points
    if uid not in rankings:
        rankings[uid] = {"points": 0, "name": name, "trophies": 0}
    rankings[uid]["points"] += 2   # Fast points
    rankings[uid]["name"] = name
    save_json(rankings, RANK_FILE)

    # Fallback first (super reliable)
    fallback = get_fallback_reply(text_lower, name)
    if fallback:
        return bot.reply_to(message, fallback)

    # Trigger AI
    should_reply = (
        'cg' in text_lower or 'cotg' in text_lower or 
        (BOT_USERNAME and BOT_USERNAME in text_lower) or
        message.chat.type == 'private' or
        (message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID)
    )

    if should_reply:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_grok_reply(uid, text, name)
        if reply:
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Bhai thoda busy hoon... phir se bol na 🔥 Kya help chahiye?")

# Start
print("🚀 CG Bot ULTRA EXTREME V3.0 LIVE — Sab fixed!")
keep_alive()
bot.polling(none_stop=True)
