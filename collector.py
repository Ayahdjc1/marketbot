
from telethon import TelegramClient, events
from datetime import datetime
from database import insert_engagement_data, create_engagement_table
from config import API_TOKEN
# === ЗАМЕНИ на своё ===
api_id = 
api_hash = ''
channel = ''  # ID или username канала, например 'my_channel'

# Создание таблицы вовлеченности (если ещё не создана)
create_engagement_table()

# Инициализация Telethon-клиента
client = TelegramClient('telethon_session', api_id, api_hash).start(bot_token=API_TOKEN)


@client.on(events.NewMessage(chats=channel))
async def handler(event):
    msg = event.message
    post_id = str(msg.id)
    date = msg.date.isoformat() 
    
    # Статистика
    likes = msg.views or 0
    shares = msg.forwards or 0
    comments = msg.replies.replies if msg.replies else 0

    # Запись в базу данных
    insert_engagement_data(
        post_id=post_id,
        likes=likes,
        comments=comments,
        shares=shares,
        channel=str(event.chat_id),
        date=date
    )
    print(f"[✓] Пост {post_id} сохранён ({likes} просмотров, {comments} комментариев, {shares} репостов)")
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - COLLECTOR - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.info("collector.py успешно запущен")

if __name__ == '__main__':
    print("📡 Подключаемся к Telegram...")
    client.start()
    print(f"✅ Подключено. Ожидаем посты из канала {channel}...\n")
    client.run_until_disconnected()

    
    
