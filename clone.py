import os
import time
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

# Pushing network retries to the absolute limit for unstable, high-speed connections
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, connection_retries=50, request_retries=50)

# THE 50 MB/S TRIGGER: 8 heavy files processed at the exact same time
CONCURRENT_TRANSFERS = 8
semaphore = asyncio.Semaphore(CONCURRENT_TRANSFERS)
copied_count = 0
start_time = time.time()

async def aggressive_transfer(client, message):
    global copied_count
    async with semaphore:
        try:
            # Telethon + cryptg handles the parallel chunk decryption natively
            file_path = await client.download_media(message)
            
            if file_path and os.path.getsize(file_path) > 0:
                await client.send_file('me', file_path, caption=message.text or "")
                os.remove(file_path)
                copied_count += 1
                
                # Extreme speed requires extreme silence. Pinging only every 10 files.
                if copied_count % 10 == 0:
                    elapsed = time.time() - start_time
                    await client.send_message('me', f"⚡ **GOD MODE SPEED UPDATE:** {copied_count} massive files violently transferred in {int(elapsed)} seconds!")
                    
        except Exception as e:
            if 'file_path' in locals() and file_path and os.path.exists(file_path):
                os.remove(file_path)

@client.on(events.NewMessage(pattern=r'\.ping', outgoing=True))
async def ping_test(event):
    await event.reply("🏓 **Pong!** 50 MB/s God Mode Server is awake!")

@client.on(events.NewMessage(pattern=r'\.clone (.*)', outgoing=True))
async def clone_history(event):
    global copied_count, start_time
    copied_count = 0
    start_time = time.time()
    
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        return await event.reply("⚠️ Please provide a channel ID.")
        
    try:
        target_chat_id = int(args[1].strip())
    except ValueError:
        return await event.reply("⚠️ Invalid ID.")

    await event.reply(f"🚀 **ENGAGING 50 MB/S SWARM FOR `{target_chat_id}`**\n\n⚠️ Pushing CPU, Disk I/O, and Telegram API to absolute breaking point. Stand by for impact.")
    
    tasks = []
    try:
        async for msg in client.iter_messages(target_chat_id, reverse=True):
            if msg.media and (hasattr(msg, 'document') or hasattr(msg, 'video')):
                if hasattr(msg, 'file') and msg.file and msg.file.size:
                    # Target only files over 50MB to maximize bandwidth saturation
                    size_mb = msg.file.size / (1048576) 
                    if size_mb > 50: 
                        task = asyncio.create_task(aggressive_transfer(client, msg))
                        tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
                            
    except Exception as e:
        await client.send_message('me', f"⚠️ Swarm Sequence Terminated by Error: {e}")
        return
        
    await client.send_message('me', f"✅ **Channel Eradicated!**\n📥 Transferred: {copied_count} massive files")

print("🚀 Booting up 50 MB/s God Mode Engine...")
client.start()
client.run_until_disconnected()
          
