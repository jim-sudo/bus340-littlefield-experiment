import discord
import asyncio
import os
import glob

# --- CONFIGURATION ---
BOT_TOKEN = 'adf'
CHANNEL_ID = 1440607232256507925  # Replace with your copied Channel ID
PLOT_DIR = './plots'

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def send_daily_report():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print(f"Error: Could not find channel {CHANNEL_ID}")
        await client.close()
        return

    print(f"Logged in as {client.user}. Preparing to send files...")

    # 1. Find the plots (We grab all .png files in the plots folder)
    # You can adjust this to find specific files if you want
    png_files = glob.glob(os.path.join(PLOT_DIR, '*.png'))
    
    if not png_files:
        print("No plots found to send!")
        await channel.send("⚠️ Analysis ran, but no plots were found.")
        await client.close()
        return

    # 2. Prepare the files for Discord
    # We limit to 10 files because Discord has a limit per message
    files_to_send = []
    for filename in png_files[:10]: 
        # Open file in binary mode
        files_to_send.append(discord.File(filename))

    # 3. Send the Message
    try:
        await channel.send(
            content="**📊 New Littlefield Analysis Update**\nHere are the latest charts:",
            files=files_to_send
        )
        print(f"Successfully sent {len(files_to_send)} charts.")
    except Exception as e:
        print(f"Failed to send charts: {e}")
    
    # 4. Close the connection
    await client.close()

# --- RUNNER ---
@client.event
async def on_ready():
    # When the bot logs in, immediately start the report task
    await send_daily_report()

if __name__ == "__main__":
    try:
        client.run(BOT_TOKEN)
    except Exception as e:
        print(f"Bot crashed: {e}")
