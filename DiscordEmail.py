import discord
import asyncio
import imaplib
import email
import os
from discord.ext import commands

# Email settings
IMAP_SERVER = os.getenv('IMAP_SERVER')
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
PASSWORD = os.getenv('PASSWORD')

# Discord bot settings
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# File to store processed email IDs and message ID
PROCESSED_EMAILS_FILE = 'processed_emails.txt'
MESSAGE_ID_FILE = 'message_id.txt'
ATTACHMENTS_DIR = 'attachments/'

# Ensure the attachments directory exists
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

# Set up Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Define your guild and channel IDs
GUILD_ID = int(os.getenv('GUILD_ID'))
EMAIL_CHANNEL_ID = 1265040965492801697
COUNTDOWN_CHANNEL_ID = 1266046599629508689

# Adjusted intervals
EMAIL_CHECK_INTERVAL = 1800  # Email check interval in seconds (30 minutes)
THREAD_UPDATE_INTERVAL = 300  # Thread update interval in seconds (5 minutes)
INITIAL_CHECK_DURATION = 30  # Duration for the initial check in seconds

def load_processed_emails():
    if os.path.exists(PROCESSED_EMAILS_FILE):
        with open(PROCESSED_EMAILS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_processed_email(email_id):
    with open(PROCESSED_EMAILS_FILE, 'a') as file:
        file.write(email_id + '\n')

def load_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, 'r') as file:
            return file.read().strip()
    return None

def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, 'w') as file:
        file.write(str(message_id))

def check_email(processed_emails):
    new_emails = []
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        mail.select('inbox')

        # Search for new emails
        status, data = mail.search(None, 'UNSEEN')
        if status != 'OK':
            print("Failed to search emails")
            return new_emails

        email_ids = data[0].split()
        if not email_ids:
            print("No new emails found")
            return new_emails

        for email_id in email_ids:
            email_id_str = email_id.decode()  # Convert byte to string
            if email_id_str in processed_emails:
                continue  # Skip already processed emails

            # Fetch the email by ID
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                print(f"Failed to fetch email ID {email_id_str}")
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Get email details
            from_ = msg.get('From')
            subject = msg.get('Subject')
            body = get_email_body(msg)
            attachments = get_attachments(msg)

            # Format email details with Markdown
            summary = summarize_body(body)
            email_info = (
                f"**From:** {from_}\n"
                f"**Subject:** {subject}\n\n"
                f"**Summary:**\n{summary}"
            )
            new_emails.append((email_id_str, email_info, attachments))

            # Mark this email as processed
            save_processed_email(email_id_str)

        mail.logout()
    except Exception as e:
        print(f"Error checking email: {e}")
    
    return new_emails

def get_email_body(msg):
    # Extract the email body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return "No content"

def summarize_body(body):
    # Limit the summary to 40 words
    words = body.split()
    summary = ' '.join(words[:40])
    if len(words) > 40:
        summary += '...'
    return summary

def get_attachments(msg):
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            filename = part.get_filename()

            if filename:
                filepath = os.path.join(ATTACHMENTS_DIR, filename)
                with open(filepath, 'wb') as file:
                    file.write(part.get_payload(decode=True))
                attachments.append(filepath)
    return attachments

async def send_email_notifications(email_infos):
    channel = bot.get_channel(EMAIL_CHANNEL_ID)
    for _, email_info, attachment_paths in email_infos:
        try:
            await channel.send(email_info)
            for attachment in attachment_paths:
                await channel.send(file=discord.File(attachment))
        except discord.HTTPException as e:
            if e.code == 429:  # Rate limit error
                print("Rate limit reached, backing off...")
                await asyncio.sleep(60)  # Wait before retrying
            else:
                print(f"Failed to send message: {e}")

async def update_countdown_message(channel, message_id, countdown_time):
    try:
        while countdown_time > 0:
            minutes, seconds = divmod(countdown_time, 60)
            message = await channel.fetch_message(message_id)
            await message.edit(content=f"Next email refresh in: {minutes:02}:{seconds:02}")
            await asyncio.sleep(THREAD_UPDATE_INTERVAL)  # Update every 5 minutes
            countdown_time -= THREAD_UPDATE_INTERVAL
    except discord.HTTPException as e:
        if e.code == 429:  # Rate limit error
            print("Rate limit reached for updating message, backing off...")
            await asyncio.sleep(60)  # Wait before retrying
        else:
            print(f"Failed to update message: {e}")

async def check_and_notify():
    processed_emails = load_processed_emails()
    channel = bot.get_channel(EMAIL_CHANNEL_ID)
    countdown_channel = bot.get_channel(COUNTDOWN_CHANNEL_ID)

    # Initial email check on startup
    print("Checking for new emails...")
    new_emails = check_email(processed_emails)
    if new_emails:
        await send_email_notifications([(email_id, email_info, attachments) for email_id, email_info, attachments in new_emails])

    # Retrieve or create countdown message
    message_id = load_message_id()
    if message_id:
        try:
            message = await countdown_channel.fetch_message(message_id)
        except discord.NotFound:
            # Message not found, create a new one
            message = await countdown_channel.send(f"Next email refresh in: 30:00")
            save_message_id(message.id)
    else:
        # No message ID, create a new one
        message = await countdown_channel.send(f"Next email refresh in: 30:00")
        save_message_id(message.id)

    # Start the countdown timer and subsequent updates
    await update_countdown_message(countdown_channel, message.id, EMAIL_CHECK_INTERVAL)
    await asyncio.sleep(INITIAL_CHECK_DURATION)  # Initial wait time before starting periodic updates

    while True:
        await asyncio.sleep(EMAIL_CHECK_INTERVAL)  # Wait before checking emails
        print("Checking for new emails...")
        new_emails = check_email(processed_emails)
        if new_emails:
            await send_email_notifications([(email_id, email_info, attachments) for email_id, email_info, attachments in new_emails])

        await update_countdown_message(countdown_channel, message.id, EMAIL_CHECK_INTERVAL)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(check_and_notify())

@bot.tree.command(name="setinterval", description="Set the email check interval")
async def setinterval(interaction: discord.Interaction, interval: int):
    global EMAIL_CHECK_INTERVAL
    EMAIL_CHECK_INTERVAL = interval
    await interaction.response.send_message(f"Email check interval set to {interval} seconds.", ephemeral=True)

async def setup_hook():
    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

bot.setup_hook = setup_hook

bot.run(DISCORD_TOKEN)
