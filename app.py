import os
import requests
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from datetime import datetime

app = Flask(__name__)

# Environment Variables
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

    # 1. HELP / MENU
    if lower_text in ['/help', 'help', '/menu']:
        reply = "🔥 **NSFW Command Bot** 🔥\n\n• /help - Menu\n• /hello - Flirt\n• /meme - Dank Memes\n• /roll - Dice"
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="👋 Flirt", text="/hello")),
            QuickReplyButton(action=MessageAction(label="🖼️ Meme", text="/meme")),
            QuickReplyButton(action=MessageAction(label="🎲 Roll", text="/roll"))
        ])
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply, quick_reply=quick_reply))

    # 2. MEME COMMAND
    if lower_text == '/meme':
        try:
            r = requests.get("https://meme-api.com/gimme/dankmemes").json()
            image_url = r.get('url')
            if image_url and image_url.lower().endswith(('.jpg', '.png', '.jpeg')):
                return line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                )
            else:
                return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Found a GIF, try /meme again! 😏"))
        except:
            return line_bot_api.reply_message(event.reply_token, TextSendMessage(text="I'm too distracted for memes right now... 💦"))

    # 3. ROLL COMMAND
    if lower_text == '/roll':
        import random
        result = random.randint(1, 6)
        return line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"🎲 You rolled a {result}!"))

    # 4. CHAT LOGIC (Fallback)
    if any(word in lower_text for word in ["fuck", "sex", "dirty"]):
        reply = "Oh? You want to talk dirty? 😏"
    elif "hello" in lower_text or "hi" in lower_text:
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
