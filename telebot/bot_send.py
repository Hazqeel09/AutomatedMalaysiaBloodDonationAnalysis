import httpx
import logging
import os

TOKEN = os.environ.get("TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

async def send_telegram_message(chat_id, message):
    json_msg = {"chat_id": chat_id, "text": message}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TELEGRAM_API_URL}/sendMessage", json=json_msg
            )
            response.raise_for_status()
            logging.info("Message sent to Telegram successfully.")
        except Exception as e:
            logging.error(f"An error occurred while sending message to Telegram: {e}")


async def send_telegram_photo(chat_id, photo_stream, caption_text=None):
    files = {"photo": ("plot.png", photo_stream)}
    json_msg = {"chat_id": chat_id}

    if caption_text:
        json_msg["caption"] = caption_text

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TELEGRAM_API_URL}/sendPhoto", data=json_msg, files=files
            )
            response.raise_for_status()
            logging.info("Photo with caption sent to Telegram successfully.")
        except Exception as e:
            logging.error(
                f"An error occurred while sending photo with caption to Telegram: {e}"
            )

async def try_send_three_times(id, image, caption=None):
    attempts = 0
    while attempts < 3:
        try:
            if caption:
                await send_telegram_photo(id, image, caption)
            else:
                await send_telegram_photo(id, image)
            break
        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts} failed with error: {e}")
            if attempts == 3:
                print("Failed to send after 3 attempts.")
