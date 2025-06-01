# тг бот с базой данных(pgsql/mysql) и миграциями(alembic)
# Необходимо
# 1. создать и применить хотя бы 1 миграцию
# 2. создать тг бота который при /start заносит пользователя в базу при /del удаляет пользователя с базы

# from aiogram import executor, Dispatcher, Bot
# from database import execute_query, connect_db, create_user_table
# token = "7574161184:AAEketR8qHVNn7thhBJOWyEIm5Pp0ro7WtQ"
# bot = Bot(token=token)
# dp = Dispatcher(bot=bot)

# @dp.message_handler(commands=["start"])
# async def start(message):
#     await message.answer("Привет")
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute(f"INSERT INTO user_test (user_id) VALUES ({message.chat.id})")
#     conn.commit()
#     conn.close()

# @dp.message_handler(commands="del")
# async def delete(message):
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute(f"DELETE from user_test WHERE user_id = {message.chat.id}")
#     conn.commit()
#     conn.close()

# @dp.message_handler(commands="show")
# async def show(message):
#     co9nn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT * from user_test")
#     conn.commit()
#     await message.answer(cursor.fetchall())
#     conn.close()

# executor.start_polling(dispatcher=dp)

a = "fggffggffg"
x = list()
print(dir(a))
print()
print(dir(x))