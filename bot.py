import discord
from discord.ext import commands
import json
import time

# Intenty - povolenie pre čítanie obsahu správ
intents = discord.Intents.default()
intents.message_content = True

# Inicializácia bota
bot = commands.Bot(command_prefix="!", intents=intents)

# Súbor kde sa ukladajú údaje
DATA_FILE = "jazdy.json"

# Načítanie dát zo súboru
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Uloženie dát do súboru
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Slovník na cooldown
cooldowns = {}

# Keď sa bot pripojí
@bot.event
async def on_ready():
    print(f'✅ Bot pripojený ako {bot.user}')

# Príkaz !report <km>
@bot.command()
async def report(ctx, km: float):
    user_id = str(ctx.author.id)
    data = load_data()

    # Ak nie je admin, kontrolujeme cooldown
    if not ctx.author.guild_permissions.administrator:
        now = time.time()
        last_used = cooldowns.get(user_id, 0)
        cooldown_time = 1800  # 30 minút

        if now - last_used < cooldown_time:
            remaining = cooldown_time - (now - last_used)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            await ctx.send(f"⏳ Si na cooldowne! Počkaj ešte {minutes} minút a {seconds} sekúnd.")
            return
        cooldowns[user_id] = now  # aktualizuj čas

    # Ukladáme kilometre
    if user_id not in data:
        data[user_id] = {"km": 0}

    data[user_id]["km"] += km
    save_data(data)

    await ctx.send(f"✅ Pridané {km:.1f} km pre {ctx.author.display_name}.")

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

    km = data[user_id]["km"]
    await ctx.send(f"📊 **{member.display_name}** má najazdené {km:.1f} km.")

# Príkaz !user (len pre administrátorov)
@bot.command()
@commands.has_permissions(administrator=True)
async def user(ctx, member: discord.Member):
    user_id = str(member.id)
    data = load_data()

    if user_id not in data:
        await ctx.send(f"❌ {member.display_name} ešte nejazdil.")
        return

    km = data[user_id]["km"]
    await ctx.send(f"📊 **{member.display_name}** má najazdené {km:.1f} km.")

# Príkaz na vynulovanie štatistík (len admini)
@bot.command()
@commands.has_permissions(administrator=True)
async def delete_stats(ctx):
    save_data({})  # Predpokladáme, že táto funkcia existuje
    await ctx.send("⚠️ Všetky štatistiky boli vynulované.")
 
# Spustenie bota 
bot.run("MTM2MzE1MzU1Njk0MDY1MjYwNA.Gxv0DW.1Xh4ZZvTPJHCJh9KHIHZNMN-KPoVYfKYHxz9Pc")
