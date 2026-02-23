import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import time
import requests
import json
import os
import random
from bs4 import BeautifulSoup

# ================= CONFIGURATION =================
TOKEN = '8515104266:AAFV2a9-8Rx1RyxsLxW51t_-a1igs23trdo'
GROQ_API_KEY = "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"
BOSS_ADMIN = 'Ben_ADFA'          
BOT_NAME = "CG"

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# ================= RANKING & TITLES =================
RANK_FILE = 'rankings.json'

def load_rankings():
    if os.path.exists(RANK_FILE):
        try:
            with open(RANK_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_rankings(data):
    with open(RANK_FILE, 'w') as f: json.dump(data, f, indent=2)

rankings = load_rankings()
user_cooldown = {} # Anti-spam dict
msg_counter = 0    # For Auto-Quiz

def get_title(points):
    if points < 100: return "🟢 Beginner Coder"
    elif points < 300: return "🔵 Bug Hunter"
    elif points < 800: return "🟣 Kotlin Pro"
    else: return "🔴 COTG Legend"

# ================= QUIZ SYSTEM =================
QUIZ_QUESTIONS = [
    {"q": "Which programming language is officially recommended by Google for Android?", "a": "kotlin"},
    {"q": "What extension is used for Android UI layout files?", "a": ".xml"},
    {"q": "What is the name of the compiled Android application file format?", "a": "apk"},
    {"q": "What tool in Android shows you the console logs and errors?", "a": "logcat"},
    {"q": "Which component is used to navigate between different screens in Android?", "a": "intent"},
    {"q": "What is the base class for UI components in Android?", "a": "view"},
    {"q": "In which file do you declare Android permissions like INTERNET?", "a": "manifest"},
    {"q": "What Android layout arranges items vertically or horizontally?", "a": "linearlayout"},
    {"q": "What keyword is used in Java to inherit a class?", "a": "extends"},
    {"q": "What is the new modern UI toolkit for Android by Google?", "a": "jetpack compose"},
    {"q": "Which library is commonly used for loading images in Android?", "a": "glide"},
    {"q": "Which local database is officially recommended for Android?", "a": "room"},
    {"q": "What format is typically used for data parsing in REST APIs?", "a": "json"},
    {"q": "What Kotlin feature prevents NullPointerExceptions?", "a": "null safety"},
    {"q": "What keyword is used to declare a constant variable in Kotlin?", "a": "val"},
    {"q": "What executes background tasks in Kotlin efficiently?", "a": "coroutines"},
    {"q": "What file defines the build configurations in an Android project?", "a": "build.gradle"},
    {"q": "What Android component runs in the background without a UI?", "a": "service"},
    {"q": "Which standard layout replaces RelativeLayout for better performance?", "a": "constraintlayout"},
    {"q": "What method is called first when an Activity is created?", "a": "oncreate"}
]

current_quiz = None

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
        except:
            return "Latest info not available right now. Please check the official Telegram channel."
    return cached_website_data

# ================= TEXTS & UI =================
DIVIDER = "━━━━━━━━━━━━━━━━━━━"
RULES_TEXT = f"""📌 *Code on the Go - Official Rules*\n{DIVIDER}\n1️⃣ *Be respectful:* No harassment.\n2️⃣ *Stay on topic:* Keep conversation focused on COTG.\n3️⃣ *English only:* So everyone can understand.\n4️⃣ *No spam/ads:* Unauthorized promos will be removed.\n5️⃣ *Admin moderation:* Severe violations result in removal.\n{DIVIDER}"""
IDE_INFO = f"""🚀 *About Code on the Go (COTG)*\n{DIVIDER}\nBuild real Android apps completely on your phone, even offline! 📱💻\n🌐 *Website:* [appdevforall.org](https://www.appdevforall.org/codeonthego/)\n🎥 *YouTube:* [App Dev for All](https://youtube.com/@appdevforall)\n{DIVIDER}"""

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

        system_prompt = f"""You are CG, the friendly and highly intelligent AI Assistant for 'Code on the Go' (COTG) Android coding community.
Rules:
1. Speak ONLY in English. No other languages.
2. Keep replies SHORT and crisp. Avoid long paragraphs.
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

# ================= BUTTON CLICKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_rules":
        bot.edit_message_text(RULES_TEXT, call.message.chat.id, call.message.message_id, reply_markup=get_back_button(), parse_mode='Markdown')
    elif call.data == "show_ide_info":
        bot.edit_message_text(IDE_INFO, call.message.chat.id, call.message.message_id, reply_markup=get_back_button(), parse_mode='Markdown', disable_web_page_preview=True)
    elif call.data == "back_to_main":
        bot.edit_message_text(f"Hello again! 👋\n{DIVIDER}\nI am **CG**, the highly advanced AI Assistant.", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(), parse_mode='Markdown')
    elif call.data == "close_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)

# ================= GRAND ENTRY & WELCOME =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_members(message):
    for member in message.new_chat_members:
        # GRAND ENTRY: Jab Bot group mein add hoga!
        if member.id == bot.get_me().id:
            intro_text = (f"🚀 *HELLO EVERYONE!* 🚀\n{DIVIDER}\n"
                          f"I am **CG**, the Official Smart AI Assistant for the Code on the Go community! 🤖✨\n\n"
                          f"I was invited here by Admin @{BOSS_ADMIN} to help you all with coding, answer your questions, and keep this group awesome!\n\n"
                          f"💡 *What can I do?*\n"
                          f"• Ask me coding questions!\n"
                          f"• Type `my rank` to check your VIP Title.\n"
                          f"• Help others to earn points & climb the leaderboard!\n\n"
                          f"Please check out our rules and subscribe to our YouTube channel below. Let's build amazing Android apps together! 👨‍💻📱")
            bot.send_message(message.chat.id, intro_text, reply_markup=get_main_menu())
            continue
            
        # Normal User Welcome
        name = member.username if member.username else member.first_name
        text = (f"Welcome to the community, @{name}! 🎉\n{DIVIDER}\n"
                f"We are excited to have you in *Code on the Go*.\n"
                f"💡 I am **CG**, your AI assistant. Click below to read our rules!")
        bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

# ================= COMMANDS =================
@bot.message_handler(commands=['help', 'start', 'rules'])
def send_help(message):
    bot.reply_to(message, f"I am **CG**, here to help you! 🤖\nPlease select an option below:", reply_markup=get_main_menu())

@bot.message_handler(commands=['award'])
def award_points(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to someone's message with `/award 50` to give them 50 of your points for helping you!")
    
    try:
        points_to_give = int(message.text.split()[1])
        giver_id = str(message.from_user.id)
        receiver_id = str(message.reply_to_message.from_user.id)
        
        if giver_id == receiver_id:
            return bot.reply_to(message, "❌ You cannot award points to yourself!")
            
        if rankings.get(giver_id, {}).get("points", 0) < points_to_give:
            return bot.reply_to(message, "❌ You don't have enough points to give!")
            
        rankings[giver_id]["points"] -= points_to_give
        if receiver_id not in rankings: rankings[receiver_id] = {"points": 0, "name": message.reply_to_message.from_user.first_name}
        rankings[receiver_id]["points"] += points_to_give
        save_rankings(rankings)
        
        bot.reply_to(message, f"💸 **BOUNTY AWARDED!**\nYou gave **{points_to_give} points** to {rankings[receiver_id]['name']}! 🎉")
    except:
        bot.reply_to(message, "⚠️ Use format: `/award 50`")

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

    # --- 1. ANTI-SPAM & RANKING POINTS ---
    current_time = time.time()
    if message.chat.type in ['group', 'supergroup']:
        if user_id not in rankings: rankings[user_id] = {"points": 0, "name": username}
        
        # 60 Second Cooldown (Anti-Spam)
        if current_time - user_cooldown.get(user_id, 0) > 60:
            rankings[user_id]["points"] += 2  
            user_cooldown[user_id] = current_time
            
        if message.reply_to_message and message.reply_to_message.from_user.id != message.from_user.id: 
            rankings[user_id]["points"] += 5 # Bonus for replying/helping
            
        rankings[user_id]["name"] = username
        save_rankings(rankings)
        
        msg_counter += 1

    # --- 2. QUIZ ANSWER CHECKER ---
    if current_quiz and text == current_quiz["a"]:
        bot.reply_to(message, f"🎉 **WINNER WINNER!** 🎉\n@{username} gave the right answer first!\nAnswer: **{current_quiz['a'].upper()}**\n\n🎁 You get **+100 Points**!")
        rankings[user_id]["points"] += 100
        save_rankings(rankings)
        current_quiz = None
        return

    # --- 3. AUTO-QUIZ TRIGGER (Every 30 Messages) ---
    if msg_counter >= 30:
        msg_counter = 0
        current_quiz = random.choice(QUIZ_QUESTIONS)
        quiz_text = f"⏱️ **FASTEST FINGER FIRST!** ⏱️\n{DIVIDER}\n❓ *Question:* {current_quiz['q']}\n\n*Reply fast with the correct word to win 100 Points!*"
        bot.send_message(chat_id, quiz_text, parse_mode='Markdown')

    # --- 4. FILTERS ---
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

    # --- 5. PRIORITY COMMANDS (NO AI) ---
    if text in ['my rank', 'my ranking', '/myrank', 'rank']:
        pts = rankings.get(user_id, {"points": 0})["points"]
        title = get_title(pts)
        bot.reply_to(message, f"🏆 *Your Rank*\n👤 {username}\n⭐ Points: **{pts}**\n🏅 Title: {title}\nKeep coding to climb the leaderboard! 🔥")
        return

    if text in ['leaderboard', 'top', '/top', '/leaderboard']:
        if not rankings: return bot.reply_to(message, "No points tracked yet!")
        sorted_users = sorted(rankings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        lb_text = f"🏅 *Top Active Members*\n{DIVIDER}\n"
        for i, (uid, data) in enumerate(sorted_users, 1):
            lb_text += f"{i}. **{data['name']}** — {data['points']} pts ({get_title(data['points'])})\n"
        bot.reply_to(message, lb_text)
        return

    # --- 6. SMART AI & FALLBACK ---
    bot_triggered = False
    if text == "cg":
        bot.reply_to(message, f"Yes brother! I am here. 🤖 How can I help you, @{username}?")
        return

    if "cg" in text or f"@{BOT_NAME.lower()}" in text or message.chat.type == 'private': bot_triggered = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id: bot_triggered = True

    if bot_triggered:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_grok_reply(user_id, message.text, username)
        
        if ai_reply: bot.reply_to(message, ai_reply)
        else:
            if any(w in text for w in ['hi', 'hello', 'hey']): bot.reply_to(message, f"Hello @{username}! 👋 I am **CG**. How is your coding going today?")
            elif "who are you" in text: bot.reply_to(message, "I am **CG**! The Official Smart AI Assistant for the COTG community. 🤖✨")
            elif "thanks" in text: bot.reply_to(message, "You are welcome! 😇 I was programmed to keep this community awesome! 🚀")
            else: bot.reply_to(message, "Yes brother! I am currently operating in offline fallback mode. How can I help you?")

# Server start
keep_alive()
print("V15 The Grand Entry & Gaming Bot is LIVE!")
bot.polling(none_stop=True)
