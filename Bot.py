# Mafia-bot
import asyncio
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command

# Telegram Bot tokeningizni kiriting
TOKEN = "8821577641:AAHcshU_OBsxW8PTjjM0QXp8y_XvGOBA5c0"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# O'yin holatini saqlash uchun lug'at
# Real loyihalarda ma'lumotlar bazasidan (DB) foydalanilgani ma'qul
games = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "<b>Mafiya o'yiniga xush kelibsiz!</b>\n\n"
        "Guruhda o'yin yaratish uchun /create komandasini yuboring.",
        parse_mode="HTML"
    )

@dp.message(Command("create"))
async def create_game(message: types.Message):
    if message.chat.type == "private":
        await message.answer("O'yinni faqat guruhlarda o'ynash mumkin!")
        return

    chat_id = message.chat.id
    if chat_id in games and games[chat_id]["active"]:
        await message.answer("Bu guruhda allaqachon o'yin ketmoqda!")
        return

    games[chat_id] = {
        "active": False,
        "players": {},  # {user_id: {"name": str, "role": str, "alive": bool}}
    }
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Qo'shilish 🙋‍♂️", callback_data="join_game")],
            [types.InlineKeyboardButton(text="O'yinni boshlash 🚀", callback_data="start_game")]
        ]
    )
    await message.answer("<b>Yangi Mafiya o'yini yaratildi!</b>\nQatnashuvchilar tugmani bosing:", reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "join_game")
async def join_game(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in games:
        await callback.answer("Hali o'yin yaratilmadi!", show_alert=True)
        return

    if user.id in games[chat_id]["players"]:
        await callback.answer("Siz allaqachon qo'shilshgansiz!", show_alert=True)
        return

    games[chat_id]["players"][user.id] = {
        "name": user.full_name,
        "role": None,
        "alive": True
    }
    
    count = len(games[chat_id]["players"])
    await callback.answer("O'yinga qo'shildingiz!")
    await callback.message.edit_text(
        f"<b>Yangi Mafiya o'yini yaratildi!</b>\n\n"
        f"Qatnashchilar soni: <b>{count}</b> ta\n"
        f"Oxirgi qo'shilgan: {user.full_name}",
        reply_markup=callback.message.reply_markup,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "start_game")
async def start_game(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    game = games.get(chat_id)

    if not game or len(game["players"]) < 4:
        await callback.answer("O'yinni boshlash uchun kamida 4 ta o'yinchi kerak!", show_alert=True)
        return

    game["active"] = True
    players_ids = list(game["players"].keys())
    random.shuffle(players_ids)

    # Rollarni taqsimlash
    # 1 Mafiya, 1 Shifokor, 1 Komissar va qolganlar Fuqaro
    roles = ["Mafiya", "Shifokor", "Komissar"] + ["Fuqaro"] * (len(players_ids) - 3)
    random.shuffle(roles)

    for i, player_id in enumerate(players_ids):
        assigned_role = roles[i]
        game["players"][player_id]["role"] = assigned_role
        
        # O'yinchilarga shaxsiy xabar (DM) orqali rolini yuborish
        try:
            await bot.send_message(
                player_id,
                f"Sizning rolingiz: <b>{assigned_role}</b>",
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(f"⚠️ {game['players'][player_id]['name']} ga shaxsiy xabar yuborib bo'lmadi. Botga /start bosganiga ishonch hosil qiling!")

    await callback.message.edit_text("<b>O'yin boshlandi!</b>\n\nRollar o'yinchilarning shaxsiy xabarlariga yuborildi. Tun tushmoqda... 🌙", parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
