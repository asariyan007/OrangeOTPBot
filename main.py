# main.py
import os
import asyncio
import requests
import phonenumbers
from phonenumbers import geocoder
from datetime import datetime, timedelta, timezone
from telegram import Bot
from telegram.helpers import escape_markdown

# 🔑 Config
BOT_TOKEN = "8287430542:AAFeqOBR-KlZU0TbnvV1tx6-XFTcEpEZv2o"
CHAT_ID = "-1002825600269"
API_URL = "https://trydifferent.2cloud.top/ariapi.php"

bot = Bot(token=BOT_TOKEN)

# ✅ Used OTP storage (to prevent duplicate posting)
sent_otps = set()

# 🌍 Bangladesh timezone (+6)
BD_TZ = timezone(timedelta(hours=6))

async def fetch_and_send():
    while True:
        try:
            # API কল
            response = requests.get(API_URL, timeout=5)

            if response.status_code == 200:
                data = response.json()  # JSON response
                
                for entry in data:
                    number = entry.get("number", "")
                    otp = entry.get("OTP", "")
                    time_str = entry.get("time", "")

                    unique_key = f"{number}_{otp}_{time_str}"

                    # ✅ আগে না পাঠানো হলে পাঠাবে
                    if unique_key not in sent_otps:
                        sent_otps.add(unique_key)

                        # Convert time → BD Time
                        try:
                            utc_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                            bd_time = utc_time.replace(tzinfo=timezone.utc).astimezone(BD_TZ)
                            time_bd_str = bd_time.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            time_bd_str = time_str

                        # Detect country from number
                        try:
                            parsed_number = phonenumbers.parse("+" + number)
                            country_name = geocoder.description_for_number(parsed_number, "en")
                            if not country_name:
                                country_name = "Unknown"
                        except Exception:
                            country_name = "Unknown"

                        # 🔒 Safe escape for MarkdownV2
                        time_safe = escape_markdown(time_bd_str, version=2)
                        country_safe = escape_markdown(country_name, version=2)
                        number_safe = escape_markdown(number, version=2)
                        otp_safe = escape_markdown(otp, version=2)

                        # 📩 মেসেজ ডিজাইন
                        message = (
                            "*🔥 NEW CALL RECEIVED ✨*\n\n"
                            f"> ⏰ Time: `{time_safe}`\n\n"
                            f"> 🌍 Country: `{country_safe}`\n\n"
                            f"> ☎️ Number: `{number_safe}`\n\n"
                            f"> 🔑 OTP: `{otp_safe}`\n\n"
                            f"> *📝 Note: Wait at least 15 seconds to get your requested OTP code *\n\n"
                            "*Pᴏᴡᴇʀᴇᴅ ʙʏ 𝙏𝙀𝘼𝙈 𝙀𝙇𝙄𝙏𝙀 𝙓*"
                        )

                        # ✅ গ্রুপে পাঠানো
                        try:
                            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="MarkdownV2")
                        except Exception as e:
                            print("Telegram send error:", e)  # Debugging দেখাবে
            # ❌ কোনো error হলে skip করবে
        except Exception as e:
            print("Fetch error:", e)

        await asyncio.sleep(3)  # প্রতি ৩ সেকেন্ড পরপর চেক করবে

async def main():
    await fetch_and_send()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
