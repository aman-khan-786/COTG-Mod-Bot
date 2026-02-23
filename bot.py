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

# ================= NEW CONFIG =================
TOKEN = '8515104266:AAF_hv7wTh238-mjnYkKeLGL0Q5tcC2ykks'

# DUAL GROQ KEYS (Auto Fallback)
GROQ_KEYS = [
    "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",  # NEW KEY
    "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"   # OLD KEY (backup)
]

BOSS_ADMIN_RAW = "Ben_ADFA"
BOSS_ADMIN_DISPLAY = "@Ben\\_ADFA"
BOT_NAME = "CG"
OFFICIAL_CHANNEL = "https://t.me/CodeOnTheGoOfficial"
OFFICIAL_WEBSITE = "http://appdevforall.org/codeonthego"

bot = telebot.TeleBot(TOKEN, parse_mode='MarkdownV2')

try:
    me = bot.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username.lower()
except:
    BOT_ID = None
    BOT_USERNAME = None

# ================= DATABASE =================
RANK_FILE = 'rankings.json'

def load_json(file):
    if os.path.exists(file):
        try: return json.load(open(file))
        except: return {}
    return {}

def save_json(data, file):
    with open(file, 'w') as f: json.dump(data, f, indent=2)

rankings = load_json(RANK_FILE)
chat_memory = {}

# ================= PERFECT TROPHY STICKER =================
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

        draw.text((256, 160), title.upper(), fill=(0,0,0,180), font=font_big, anchor="mm")
        draw.text((256, 160), title.upper(), fill=(255,215,0), font=font_big, anchor="mm")
        draw.text((256, 380), name.upper(), fill=(0,0,0,180), font=font_med, anchor="mm")
        draw.text((256, 380), name.upper(), fill=(255,215,0), font=font_med, anchor="mm")
        draw.text((256, 460), "CODE ON THE GO", fill=(255,255,255,220), font=font_small, anchor="mm")

        bio = io.BytesIO()
        bio.name = 'trophy.webp'
        img.save(bio, 'WEBP', quality=95)
        bio.seek(0)
        return bio
    except:
        return None

# ================= MULTI-KEY GROQ AI =================
def get_grok_reply(user_id, user_msg, username):
    for api_key in GROQ_KEYS:   # Try both keys automatically
        try:
            system = f"""You are CG, the official English-only assistant of Code on the Go (offline Android IDE).
Your creator and boss is Ben {BOSS_ADMIN_DISPLAY}. 
Always answer in clean English. Be friendly, fun and helpful like a real dev friend."""

            if user_id not in chat_memory:
                chat_memory[user_id] = []
            chat_memory[user_id].append({"role": "user", "content": user_msg})
            if len(chat_memory[user_id]) > 6:
                chat_memory[user_id] = chat_memory[user_id][-6:]

            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system}] + chat_memory[user_id],
                "temperature": 0.7,
                "max_tokens": 400
            }

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=8
            )

            if r.status_code == 200:
                reply = r.json()['choices'][0]['message']['content'].strip()
                chat_memory[user_id].append({"role": "assistant", "content": reply})
                return reply
        except:
            continue  # Try next key
    return "Hey bro, my brain is a bit busy right now... Try again in 5 seconds! 🔥"

# ================= MENU =================
def get_main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("📢 Official Channel", url=OFFICIAL_CHANNEL))
    m.add(InlineKeyboardButton("🌐 Website", url=OFFICIAL_WEBSITE))
    m.add(InlineKeyboardButton("👑 Contact Ben", url=f"https://t.me/{BOSS_ADMIN_RAW}"))
    m.add(InlineKeyboardButton("❌ Close", callback_data="close"))
    return m

# ================= COMMANDS =================
@bot.message_handler(commands=['start', 'help', 'menu'])
def welcome(message):
    text = f"""👋 Hello {message.from_user.first_name}!

I am **CG** — Official Assistant of Code on the Go.

My boss is **Ben {BOSS_ADMIN_DISPLAY}**

Just chat with me or use commands!"""
    bot.reply_to(message, text, reply_markup=get_main_menu())

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    bot.reply_to(message, f"👑 **Admin & Creator**\n\n**Ben {BOSS_ADMIN_DISPLAY}**\nContact: @Ben_ADFA")

@bot.message_handler(commands=['super'])
def test_trophy(message):
    name = message.from_user.first_name.upper()
    bot.reply_to(message, f"🛠️ Generating trophy for **{name}**...")
    sticker = generate_trophy_sticker(name, "TEST CHAMPION")
    if sticker:
        bot.send_sticker(message.chat.id, sticker)

@bot.message_handler(commands=['announce_winner'])
def announce_winner(message):
    if message.from_user.username != BOSS_ADMIN_RAW:
        return bot.reply_to(message, "❌ Only Ben can announce winner!")
    if not rankings:
        return bot.reply_to(message, "No users yet.")
    
    top_id = max(rankings, key=lambda x: rankings[x].get('points', 0))
    name = rankings[top_id]['name']
    rankings[top_id]['trophies'] = rankings[top_id].get('trophies', 0) + 1
    save_json(rankings, RANK_FILE)
    
    sticker = generate_trophy_sticker(name, "WEEKLY CHAMPION")
    text = f"🏆 **WEEKLY CHAMPION!**\n\nCongratulations **{name}**! You won +1 Trophy!\nKeep grinding 🔥"
    bot.send_message(message.chat.id, text)
    if sticker: bot.send_sticker(message.chat.id, sticker)

# ================= RANK & LEADERBOARD =================
@bot.message_handler(func=lambda m: m.text and any(x in m.text.lower() for x in ['my rank', 'rank', 'cg my rank']))
def my_rank(message):
    uid = str(message.from_user.id)
    if uid not in rankings:
        rankings[uid] = {"points": 0, "name": message.from_user.first_name, "trophies": 0}
    data = rankings[uid]
    sorted_r = sorted(rankings.items(), key=lambda x: x[1].get('points', 0), reverse=True)
    pos = next((i+1 for i, (u, _) in enumerate(sorted_r) if u == uid), len(rankings))
    
    bot.reply_to(message, f"""🏅 **YOUR RANK**
👤 {message.from_user.first_name}
⭐ XP: **{data['points']}**
📍 Rank: **#{pos}**
🏆 Trophies: **{data.get('trophies', 0)}**""")

@bot.message_handler(func=lambda m: m.text and any(x in m.text.lower() for x in ['leaderboard', 'top', 'lb']))
def leaderboard(message):
    sorted_r = sorted(rankings.items(), key=lambda x: x[1].get('points', 0), reverse=True)[:10]
    txt = "🏆 **COTG LEADERBOARD**\n\n"
    for i, (_, d) in enumerate(sorted_r, 1):
        txt += f"`#{i}` {d['name']} — **{d['points']}** XP\n"
    bot.reply_to(message, txt)

# ================= MAIN HANDLER (FIXED TRIGGERS) =================
@bot.message_handler(func=lambda message: True)
def main_handler(message):
    if not message.text: return
    text = message.text.strip()
    text_lower = text.lower()
    uid = str(message.from_user.id)
    name = message.from_user.first_name

    # Give points
    if uid not in rankings:
        rankings[uid] = {"points": 0, "name": name, "trophies": 0}
    rankings[uid]["points"] += 2
    rankings[uid]["name"] = name
    save_json(rankings, RANK_FILE)

    # Strong trigger for "Cg", "Hay", "Ch", "Hello" etc.
    short_triggers = ['cg', 'hay', 'ch', 'hello', 'hi', 'help']
    is_triggered = (
        text_lower in short_triggers or
        text_lower.startswith('cg ') or
        ' cg ' in f" {text_lower} " or
        (BOT_USERNAME and BOT_USERNAME in text_lower) or
        message.chat.type == 'private' or
        (message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID)
    )

    if is_triggered:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Quick English replies for short messages
        if text_lower in ['cg', 'hay', 'ch', 'hello', 'hi']:
            bot.reply_to(message, f"Hello {name}! 👋 I'm active and ready. How can I help you with Code on the Go today?")
            return
        if 'help' in text_lower:
            bot.reply_to(message, "Type /help for full menu or just ask me anything about Android development!")
            return

        # Full AI
        reply = get_grok_reply(uid, text, name)
        if reply:
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, "Hey bro, give me 5 seconds... my brain is loading 🔥")

print("🚀 CG Bot V4.0 — New Token + Dual Groq Keys + Fixed Replies LIVE!")
keep_alive()
bot.polling(none_stop=True)
