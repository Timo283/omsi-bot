import discord
from discord.ext import commands
import json
import time

# Intenty
intents = discord.Intents.default()
intents.message_content = True

# Inicializácia bota
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "jazdy.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

cooldowns = {}

@bot.event
async def on_ready():
    print(f'✅ Bot pripojený ako {bot.user}')

# Príkaz !report <minúty>
@bot.command()
async def report(ctx, minutes: float):
    user_id = str(ctx.author.id)
    data = load_data()

    if not ctx.author.guild_permissions.administrator:
        now = time.time()
        last_used = cooldowns.get(user_id, 0)
        cooldown_time = 1800  # 30 minút cooldown

        if now - last_used < cooldown_time:
            remaining = cooldown_time - (now - last_used)
            min_rem = int(remaining // 60)
            sec_rem = int(remaining % 60)
            await ctx.send(f"⏳ Si na cooldowne! Počkaj ešte {min_rem} minút a {sec_rem} sekúnd.")
            return
        cooldowns[user_id] = now

    minutes = int(round(minutes))  # Zaokrúhľujeme na celé minúty

    if user_id not in data:
        data[user_id] = {"minuty": 0}

    data[user_id]["minuty"] += minutes
    save_data(data)

    await ctx.send(f"✅ Pridané {minutes} minút pre {ctx.author.display_name}.")

# Príkaz !stats
@bot.command()
async def stats(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)
    data = load_data()

    if user_id not in data:
        await ctx.send("❌ Tento vodič ešte nejazdil.")
        return

    minuty = data[user_id]["minuty"]
    await ctx.send(f"📊 **{member.display_name}** má najazdené {minuty} minút.")

# Príkaz !user (len pre administrátorov)
@bot.command()
@commands.has_permissions(administrator=True)
async def user(ctx, member: discord.Member):
    user_id = str(member.id)
    data = load_data()

    if user_id not in data:
        await ctx.send(f"❌ {member.display_name} ešte nejazdil.")
        return

    minuty = data[user_id]["minuty"]
    await ctx.send(f"📊 **{member.display_name}** má najazdené {minuty} minút.")

# Príkaz na vynulovanie štatistík (len admini)
@bot.command()
@commands.has_permissions(administrator=True)
async def delete_stats(ctx):
    save_data({})
    await ctx.send("⚠️ Všetky štatistiky boli vynulované.")

# Príkaz !remove @user <minúty>
@bot.command()
@commands.has_permissions(administrator=True)
async def remove(ctx, member: discord.Member, minutes: float):
    user_id = str(member.id)
    data = load_data()

    minutes = int(round(minutes))  # Zaokrúhli na celé minúty

    if user_id not in data or data[user_id]["minuty"] == 0:
        await ctx.send(f"❌ {member.display_name} ešte nejazdil.")
        return

    data[user_id]["minuty"] = max(0, data[user_id]["minuty"] - minutes)
    save_data(data)

    await ctx.send(f"🗑️ Odobrané {minutes} minút z profilu **{member.display_name}**.")

    bot.run
