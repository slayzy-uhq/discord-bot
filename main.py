import discord
from discord.ext import commands
import asyncio
import os
from io import BytesIO

# =====================
# INTENTS
# =====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)

# =====================
# READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Connecté : {bot.user}")

# =====================
# +TOS
# =====================
@bot.command()
async def tos(ctx):
    embed = discord.Embed(
        title="📋 TOS",
        color=discord.Color.green(),
        description=(
            "🟢 FnF\n"
            "🟢 No note\n"
            "🟢 Screenshot payment : DETAILS\n\n"
            "**No respect = No refund**"
        )
    )

    embed.add_field(
        name="💳 PayPal",
        value="extazlemeilleur@gmail.com\nhaythemchl93380@gmail.com",
        inline=False
    )

    embed.add_field(
        name="₿ Litecoin (LTC)",
        value="LLn2rAf7jzttyabPKe38PjSrCnV5AKk8Kx",
        inline=False
    )

    await ctx.send(embed=embed)

# =====================
# +TICKET
# =====================
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):

    view = TicketView()

    embed = discord.Embed(
        title="🎟 Support System",
        description="Choisis une option pour ouvrir un ticket",
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed, view=view)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🎟 Choisis une option",
        options=[
            discord.SelectOption(label="Buy", description="Acheter un produit", emoji="🛒"),
            discord.SelectOption(label="Help", description="Support / aide", emoji="❓"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites
        )

        await channel.send(f"🎟 Ticket ouvert par {user.mention} | {select.values[0]}")

        await interaction.response.send_message(
            f"✅ Ticket créé : {channel.mention}",
            ephemeral=True
        )

# =====================
# +CLOSE (TRANSCRIPT)
# =====================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):

    if not ctx.channel.name.startswith("ticket-"):
        return await ctx.send("❌ Cette commande fonctionne uniquement dans un ticket.")

    await ctx.send("🔒 Fermeture + génération transcript...")

    messages = []
    async for msg in ctx.channel.history(limit=200, oldest_first=True):
        time = msg.created_at.strftime("%d/%m/%Y %H:%M")
        messages.append(f"[{time}] {msg.author}: {msg.content}")

    transcript = "\n".join(messages)

    file = discord.File(
        BytesIO(transcript.encode("utf-8")),
        filename=f"transcript-{ctx.channel.name}.txt"
    )

    user = None
    for member in ctx.channel.members:
        if member != ctx.guild.me:
            user = member
            break

    # staff
    try:
        await ctx.author.send("📜 Transcript ticket :", file=file)
    except:
        pass

    # user
    try:
        if user:
            await user.send("📜 Transcript de ton ticket :", file=file)
    except:
        pass

    await asyncio.sleep(2)
    await ctx.channel.delete()

# =====================
# RUN BOT (RAILWAY SAFE)
# =====================
bot.run(os.getenv("TOKEN"))
