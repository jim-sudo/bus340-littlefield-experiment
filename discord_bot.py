import discord
import asyncio
import os
import glob
import discord_token
import json

# --- CONFIGURATION ---
BOT_TOKEN = discord_token.token()
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


    # 1. Read the Shared State File
    current_day = "Unknown" # Default if file is missing
    try:
        with open("sim_state.json", "r") as f:
            data = json.load(f)
            current_day = data.get("current_day", "Unknown")
    except FileNotFoundError:
        print("Warning: sim_state.json not found.")

    # 1. Find the plots (We grab all .png files in the plots folder)
    # You can adjust this to find specific files if you want
# 1. Find ALL .png files in the directory
    all_png_files = glob.glob(os.path.join(PLOT_DIR, '*.png'))
    
    if not all_png_files:
        print("No plots found to send!")
        await channel.send("⚠️ Analysis ran, but no plots were found.")
        await client.close()
        return

# 2. SORT by modification time (Newest first)
    # This ensures we get the files created 2 seconds ago, not 2 days ago
    all_png_files.sort(key=os.path.getmtime, reverse=True)

    # 3. SLICE the list to keep only the top 5
    newest_files = all_png_files[:5]

    print(f"Found {len(all_png_files)} total plots. Sending the top {len(newest_files)} newest.")

    # 4. Prepare the files for Discord
    files_to_send = []
    for filename in newest_files: 
        files_to_send.append(discord.File(filename))

    # 3. Send the Message
    try:
        await channel.send(
            # vvvvv SEE HERE vvvvv
            content=f"**📊 Littlefield Update: Day {current_day}**\nHere are the latest charts:",
            files=files_to_send
        )
        print("Successfully sent charts.")
    except Exception as e:
        print(f"Failed to send charts: {e}")

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
