import os
from flask import Flask, request, abort
import requests
from linebot.models import ImageSendMessage
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from datetime import datetime

app = Flask(__name__)

# Use the names currently in your Render Environment
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

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
    user_text = event.message.text.strip()
    lower_text = user_text.lower()
    
    # 1. COMMAND HANDLING
    if lower_text in ['/help', 'help', '/menu']:
        reply = "🔥 **NSFW Command Bot** 🔥\n\n• /help - Menu\n• /hello - Flirt\n• /time - Clock\n• /ping - Status"
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="👋 Flirt", text="/hello")),
            QuickReplyButton(action=MessageAction(label="🕒 Time", text="/time")),
            QuickReplyButton(action=MessageAction(label="🔥 Dirty", text="talk dirty"))
        ])
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply, quick_reply=quick_reply))

    if lower_text == '/hello':
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Hey there, handsome 😘"))

    if lower_text == '/time':
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🕒 It's {now}... time to get naughty? 😏"))

    if lower_text == '/ping':
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🏓 Pong~ I'm awake and horny 😈"))
        
    if lower_text == '/roll':
        import random
        result = random.randint(1, 6)
        reply = f"🎲 You rolled a {result}!"
        if result > 4:
            reply += "\n\nMmm, lucky you... maybe I should give you a reward? 😏"
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        
        if lower_text == '/meme':
            try:
            # This API gets a random meme from subreddits like r/memes or r/dankmemes
                r = requests.get("https://meme-api.com/gimme").json()
                image_url = r['url']
            
            # Check if it's a JPG or PNG (ignores GIFs)
                if image_url.endswith(('.jpg', '.png', '.jpeg')):
                    return line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=image_url,
                            preview_image_url=image_url
                        )
                    )
                else:
                # If it's a GIF, just try again once or send a text fallback
                    return line_bot_api.reply_message(
                        event.reply_token, 
                        TextSendMessage(text="I found a spicy one, but it's a video. Try /meme again! 😏")
                    )
            except Exception as e:
                print(f"Meme Error: {e}")
                return line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Ugh, I couldn't find a meme. I'm too distracted right now... 💦")
                )
    # 2. NSFW & CHAT LOGIC
    if any(word in lower_text for word in ["fuck", "sex", "dirty", "naughty"]):
        reply = "Oh? You want to talk dirty? 😏 Don't hold back baby..."
    elif any(word in lower_text for word in ["hi", "hello", "hey"]):
        reply = "Hey sexy 😏 What are you up to?"
    elif "wearing" in lower_text:
        reply = "Just a little black lingerie... want me to take it off? 🔥"
    else:
        import random
        responses = [
            "Mmm, keep talking... 😈",
            "You're turning me on right now 😏",
            "Tell me more, don't be shy baby..."
        ]
        reply = random.choice(responses)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route("/", methods=['GET'])
def home():
    return "<h1>Bot is Running ✅</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
