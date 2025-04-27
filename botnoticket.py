import discord
from discord.ext import commands
import json
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

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

# !report minúty - pre všetkých, okrem adminov s cooldownom
@bot.command()
async def report(ctx, minutes: int):
    user_id = str(ctx.author.id)
    data = load_data()

    if not ctx.author.guild_permissions.administrator:
        now = time.time()
        last_used = cooldowns.get(user_id, 0)
        cooldown_time = 1800  # 30 minút

        if now - last_used < cooldown_time:
            remaining = cooldown_time - (now - last_used)
            minutes_remain = int(remaining // 60)
            seconds = int(remaining % 60)
            await ctx.send(f"⏳ Si na cooldowne! Počkaj ešte {minutes_remain} minút a {seconds} sekúnd.")
            return
        cooldowns[user_id] = now

    if user_id not in data:
        data[user_id] = {"min": 0}

    data[user_id]["min"] += minutes
    save_data(data)

    await ctx.send(f"✅ Pridané {minutes} minút pre {ctx.author.display_name}.")

    # Cieľ
    goal_minutes = 180
    total = data[user_id]["min"]
    if total >= goal_minutes:
        await ctx.send(f"🎉 Gratulujem {ctx.author.display_name}, splnil si cieľ 180 minút! Máš {total} minút.")
    else:
        remaining = goal_minutes - total
        await ctx.send(f"📈 {ctx.author.display_name}, chýba ti ešte {remaining} minút do cieľa 180.")

        # !report_user @užívateľ minúty - len pre adminov
@bot.command(name="report_user")
@commands.has_permissions(administrator=True)
async def report_user(ctx, member: discord.Member, minutes: int):
    user_id = str(member.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"min": 0}

    data[user_id]["min"] += minutes
    save_data(data)

    await ctx.send(f"✅ Admin pridal {minutes} minút pre {member.display_name}.")

# !stats aj s @everyone
@bot.command()
async def stats(ctx, member: discord.Member = None):
    data = load_data()

    # @everyone špeciálne riešenie pre adminov
    if ctx.message.content.strip() == "!stats @everyone":
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Tento príkaz môžu používať len administrátori.")
            return

        if not data:
            await ctx.send("❌ Nikto ešte nejazdil.")
            return

        msg = "📊 **Štatistiky všetkých vodičov:**\n"
        for user_id, info in data.items():
            user = ctx.guild.get_member(int(user_id))
            if user:
                msg += f"• {user.display_name}: {info.get('min', 0)} minút\n"
        await ctx.send(msg)
        return

    # Ak nie je @everyone, zobrazíme štatistiky konkrétneho človeka
    if member is None:
        member = ctx.author

    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("❌ Tento vodič ešte nejazdil.")
        return

    minutes = data[user_id]["min"]
    await ctx.send(f"📊 **{member.display_name}** má odjazdené {minutes} minút.")

# !stats_all príkaz
@bot.command(name="stats_all")
@commands.has_permissions(administrator=True)
async def stats_all(ctx):
    data = load_data()

    if not data:
        await ctx.send("❌ Nikto ešte nejazdil.")
        return

    msg = "📊 **Štatistiky všetkých vodičov:**\n"
    for user_id, info in data.items():
        user = ctx.guild.get_member(int(user_id))
        if not user:
            continue

        # Ak nie je "km" kľúč, nastav na 0
        minutes = info.get("min", 0)
       
    msg += f"• {user.display_name}: {minutes} minút"

    await ctx.send(msg)
# !user - len admin
@bot.command()
@commands.has_permissions(administrator=True)
async def user(ctx, member: discord.Member):
    user_id = str(member.id)
    data = load_data()

    if user_id not in data:
        await ctx.send(f"❌ {member.display_name} ešte nejazdil.")
        return

    minutes = data[user_id]["min"]
    await ctx.send(f"📊 **{member.display_name}** má odjazdené {minutes} minút.")

# !remove @užívateľ minúty - len admin
@bot.command()
@commands.has_permissions(administrator=True)
async def remove(ctx, member: discord.Member, minutes: int):
    user_id = str(member.id)
    data = load_data()

    if user_id not in data or data[user_id]["min"] == 0:
        await ctx.send(f"❌ {member.display_name} ešte nejazdil alebo má 0 minút.")
        return

    data[user_id]["min"] = max(0, data[user_id]["min"] - minutes)
    save_data(data)

    await ctx.send(f"🗑️ Odobrané {minutes} minút z účtu {member.display_name}.")

# !delete_stats - len admin
@bot.command()
@commands.has_permissions(administrator=True)
async def delete_stats(ctx):
    save_data({})
    await ctx.send("⚠️ Všetky štatistiky boli vynulované.")

bot.run
