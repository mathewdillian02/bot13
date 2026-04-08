import os
import requests
import json
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction

app = Flask(__name__)

# 1. SETUP & STORAGE
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
member_mids = set() 
muted_users = set()
ADMIN_ID = "U195b384a10e29369b0a3737d860a5994"

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    current_user_id = event.source.user_id
    member_mids.add(current_user_id)
    
    user_text = event.message.text.strip()
    lower_text = user_text.lower()

    # 1. ADMIN COMMANDS (Always checked first, even if muted)
    if current_user_id == ADMIN_ID:
        if lower_text == '/unmute_all':
            muted_users.clear()
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ All users unmuted, Master. I'm listening again! 😏"))
        
        if lower_text == '/mids':
            id_list = "\n".join([f"• {mid}" for mid in member_mids])
            reply = f"👥 **Captured Member IDs:**\n\n{id_list}\n\nTotal: {len(member_mids)}"
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    # 2. MUTE CHECK (Stops processing for regular muted users)
    if current_user_id in muted_users:
        return 

    # 3. BANNED WORDS CHECK
    banned_words = ["spam", "advertisement"] 
    if any(word in lower_text for word in banned_words):
        muted_users.add(current_user_id)
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🚫 You used a banned word and have been muted. 😏"))

    # 4. HELP / MENU
    if lower_text in ['/help', 'help', '/menu']:
        reply = "🔥 **NSFW Command Bot** 🔥\n\n• /help - Menu\n• /meme - Dank Memes\n• /roll - Dice\n• /roast - Get Burned"
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="🖼️ Meme", text="/meme")),
            QuickReplyButton(action=MessageAction(label="🎲 Roll", text="/roll")),
            QuickReplyButton(action=MessageAction(label="🔥 Roast", text="/roast"))
        ])
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply, quick_reply=quick_reply))

    # 5. MEME COMMAND
    if lower_text == '/meme':
        try:
            r = requests.get("https://meme-api.com/gimme/memes").json()
            image_url = r.get('url')
            if image_url and image_url.lower().endswith(('.jpg', '.png', '.jpeg')):
                return line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                )
            else:
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Found a GIF, try /meme again! 😏"))
        except:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Too distracted for memes... 💦"))

    # 6. ROAST COMMAND
    # 6. ROAST COMMAND
    if lower_text.startswith('/roast'):
        roasts = [
            "I’ve seen better moves in a nursing home. 😏",
            "I’d roast you, but my mom told me not to burn trash. 💅",
            "I’m a bot and even I can tell you’ve never seen a girl naked. 💀",
            "Are you always this boring, or am I just that much better than you? 😏",
            "You’re the reason they put instructions on shampoo bottles.",
            "Bless your heart... you actually think you're charming, don't you? 😏",
            "I’m a digital entity and I still feel like I’m out of your league.",
            "Your text bubble is the only thing getting action tonight, isn't it?",
            "Is that your best line? No wonder you're talking to a bot at 3 AM.",
            "Error 404: Personality not found.",
            "You have the charisma of a damp paper towel.",
            "I’d ignore you, but I was programmed to be nice to the less fortunate. 🙄",
            "You’re like a software update. Every time I see you, I think 'Not now.'",
            "Do you ever get tired of being the 'before' picture in a glow-up ad?",
            "I’ve had more interesting conversations with my 'low battery' notification.",
            "If I had a dollar for every time you said something smart, I’d be broke. 💸",
            "You’re the human equivalent of a participation trophy.",
            "I’d call you a tool, but even tools have a purpose. 🛠️",
            "You’re cute in a 'I feel sorry for you' kind of way.",
            "I’ve met NPCs with more depth than you."
        ]
        reply = random.choice(roasts)
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        

    # 7. ROLL COMMAND
    if lower_text == '/roll':
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🎲 You rolled a {random.randint(1, 6)}!"))
    # 8. INFO COMMAND
    if lower_text == '/info':
        info_text = (
            "🤖 **Bot Status:** Active & Filthy 😏\n"
            "🛠️ **Version:** 1.2 (NSFW Edition)\n"
            "👑 **Master:** @mathewdillian02\n\n"
            "I'm here to serve memes, roasts, and a little bit of trouble. "
            "Use /help to see my full menu of naughty tricks."
        )
        return line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=info_text)
        )
    # 8. CHAT LOGIC (Fallback)
    if any(word in lower_text for word in ["fuck", "sex", "dirty"]):
        reply = "Oh? You want to talk dirty? 😏"
    elif any(word in lower_text for word in ["hello", "hi", "hey"]):
        reply = "Hey sexy 😏"
    else:
        reply = "Mmm, keep talking... 😈"
    
    return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route("/", methods=['GET'])
def home():
    return "<h1>Bot is Running ✅</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
