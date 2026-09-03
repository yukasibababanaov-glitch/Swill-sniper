import asyncio
import os
import random
import sys
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest
from telethon.tl.types import ChatAdminRights
import aiohttp

# === ТВОИ ДАННЫЕ ===
API_ID = 30983598
API_HASH = 'e5eb04de245730b56839e5c796ff6f92'
BOT_TOKEN = '8669790448:AAHwC_SSTUqbGq-tnOAMImd5bmiKVztI-Dc'

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def get_dossier(target):
    async with aiohttp.ClientSession() as sess:
        if target.startswith('+'):
            url = f'https://phoneinfoga-api.onrender.com/scan?number={target}'
        else:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={target}'
        try:
            async with sess.get(url, timeout=10) as resp:
                data = await resp.json()
                return data
        except:
            try:
                entity = await bot.get_entity(target)
                return {
                    'id': entity.id,
                    'username': getattr(entity, 'username', None),
                    'phone': getattr(entity, 'phone', None),
                    'first_name': getattr(entity, 'first_name', None),
                    'last_name': getattr(entity, 'last_name', None)
                }
            except:
                return {'error': 'Не удалось получить данные'}

async def nuke(target_entity):
    reports = 0
    for _ in range(50):
        try:
            await bot(functions.messages.ReportRequest(
                peer=target_entity,
                id=[1],
                reason=types.InputReportReasonChildAbuse(),
                message='CSAM content'
            ))
            reports += 1
            await asyncio.sleep(random.uniform(1.5, 3.5))
        except:
            pass
    return {'reports_sent': reports}

@bot.on(events.NewMessage(pattern='/snip (.*)'))
async def snip_handler(event):
    target = event.pattern_match.group(1).strip()
    await event.reply('🔍 Пробиваю и запускаю снос...')
    
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
    await event.reply(f"✅ ГОТОВО:\n```json\n{str(result)[:3000]}\n```")

async def main():
    await bot.start()
    print('✅ SWILL-SNIPER запущен и готов к работе.')
    await bot.run_until_disconnected()

# === ЗАПУСК БЕЗ nest_asyncio (работает на Render) ===
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
