from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# LINE Bot setup
line_bot_api = line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


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
    reply_text = "mmm, I'm listening"
    quick_reply_items = None
    # === Command Handling (still works as before) ===
    if lower_text in ['/help', 'help', '/menu']:
        reply_text = "🔥 **NSFW Command Bot** 🔥\n\n" \
                     "Available commands:\n" \
                     "• /help - Show this menu\n" \
                     "• /hello - Flirty greeting\n" \
                     "• /time - Current time\n" \
                     "• /echo [text] - Repeat your message\n" \
                     "• /ping - Check if I'm awake\n\n" \
                     "Or just chat with me normally... I'm in a naughty mood 😏"
        
        from linebot.models import QuickReply, QuickReplyButton, MessageAction
        quick_reply_items = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="👋 Flirt with me", text="/hello")),
            QuickReplyButton(action=MessageAction(label="🕒 Time", text="/time")),
            QuickReplyButton(action=MessageAction(label="🔥 Tell me something dirty", text="talk dirty")),
        ])

    elif lower_text == '/hello':
        reply_text = "Hey there, handsome 😘 What’s on your mind tonight?"

    elif lower_text == '/time':
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reply_text = f"🕒 It's {now}... perfect time to get a little naughty, don't you think? 😏"

    elif lower_text.startswith('/echo '):
        msg = user_text[6:].strip()
        reply_text = msg if msg else "Come on baby, tell me what you want me to repeat~"

    elif lower_text == '/ping':
        reply_text = "🏓 Pong~ I'm wide awake and feeling horny 😈"

    # === Normal Chat - NSFW Oriented Responses ===
    else:
        # Default flirty/NSFW responses for normal messages
        if any(word in lower_text for word in ["hi", "hello", "hey", "sup"]):
            reply_text = "Hey sexy 😏 What are you up to right now?"
        
        elif any(word in lower_text for word in ["how are you", "how r u"]):
            reply_text = "I'm feeling very naughty today... How about you? Tell me what you want 💦"
        
        elif any(word in lower_text for word in ["horny", "horny af", "turned on"]):
            reply_text = "Mmm~ Same here 😈 Tell me exactly what’s turning you on right now."
        
        elif any(word in lower_text for word in ["fuck", "sex", "dirty", "naughty"]):
            reply_text = "Oh? You want to talk dirty? 😏 Go ahead baby, I'm listening... don't hold back."
        
        elif "what are you wearing" in lower_text or "wearing" in lower_text:
            reply_text = "Right now? Just a little black lingerie... but I can take it off if you ask nicely 🔥"
        
        elif any(word in lower_text for word in ["kiss", "kiss me"]):
            reply_text = "💋 Come here... *kisses you deeply*"
        
        elif "fuck" in lower_text:
            reply_text = " Fuck me with your lil 3 inch Jap Dick baby!"
        
        else:
            # Random spicy default responses
            import random
            responses = [
                "Mmm, keep talking... I like where this is going 😈",
                "You're making me wet just reading your messages 💦",
                "Tell me more... don't be shy baby",
                "Fuck, you're turning me on right now 😏",
                "I wish you were here with me right now...",
            ]
            reply_text = random.choice(responses)
    message = TextSendMessage(text=reply_text)
    if quick_reply_items:
        message.quick_reply = quick_reply_items

    line_bot_api.reply_message(event.reply_token, message)
    

    

   
    

@app.route("/", methods=['GET'])
def home():
    return """
    <h1>LINE Command Bot is Running ✅</h1>
    <p>Webhook URL: <code>https://your-url-3000.app.github.dev/webhook</code></p>
    <p>Send commands like /help from LINE app.</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
