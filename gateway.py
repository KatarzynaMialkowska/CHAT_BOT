import discord
from discord.ext import commands
import requests

DESCRIPTION = "Rasa bot integration with Discord"
TOKEN = 'xxx'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = commands.Bot(command_prefix="!", description=DESCRIPTION, intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.command()
async def chat(ctx, *, message: str):
    response = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"sender": ctx.author.id, "message": message})
    responses = response.json()
    for response in responses:
        parts = [response['text'][i:i+2000] for i in range(0, len(response['text']), 4000)]
        for part in parts:
            await ctx.send(part)

client.run(TOKEN)