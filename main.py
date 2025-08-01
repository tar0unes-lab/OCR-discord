import discord
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import re
import os

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
tess_config = r'--oem 3 --psm 6 -l jpn'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                response = requests.get(attachment.url)
                img = Image.open(BytesIO(response.content))
                text = pytesseract.image_to_string(img, config=tess_config)
                formatted = format_text(text)
                await message.channel.send(f"📝 OCR結果:\n```{formatted}```")

def format_text(text):
    date = re.search(r"\d{4}/\d{1,2}/\d{1,2}", text)
    price = re.search(r"(\d{3,5})円", text)
    ku = re.search(r"(新宿|渋谷|千代田|港|中央|台東|豊島|中野|文京|品川|目黒|世田谷|杉並|足立)区", text)
    people = re.search(r"(\d)名", text)
    style = re.search(r"(流し|つけまち|無線|スマ配)", text)

    return (
        f"【営業記録】\n"
        f"🕒 日時: {date.group(0) if date else '不明'}\n"
        f"🧭 区: {ku.group(0) if ku else '不明'}\n"
        f"👥 人数: {people.group(1) if people else '不明'}名\n"
        f"🚕 営業形態: {style.group(1) if style else '不明'}\n"
        f"💴 単価: {price.group(1) if price else '不明'}円"
    )

client.run(TOKEN)
