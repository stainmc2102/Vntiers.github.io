
import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

API_URL = "http://localhost:5000"

@bot.command()
async def result(ctx, mc_name: str, discord_name: str, mode: str, tier: str):
    payload = {
        "mc_name": mc_name,
        "discord_name": discord_name,
        "mode": mode.lower(),
        "tier": tier.upper()
    }
    try:
        res = requests.post(f"{API_URL}/submit", json=payload)
        if res.status_code == 200:
            await ctx.send(f"✅ Đã ghi tier `{tier}` cho `{mc_name}` trong mode `{mode}`.")
        else:
            await ctx.send("❌ Gửi thất bại: " + res.text)
    except Exception as e:
        await ctx.send(f"❌ Lỗi kết nối: {e}")

@bot.command()
async def profile(ctx, mc_name: str):
    try:
        res = requests.get(f"{API_URL}/profile/{mc_name}")
        if res.status_code != 200:
            await ctx.send("❌ Không tìm thấy player.")
            return
        data = res.json()
        embed = discord.Embed(title=f"📄 Profile của {mc_name}", color=0x00ffcc)
        embed.add_field(name="🧠 Overall", value=f"{data.get('overallScore')} - {data.get('overallTier')}", inline=False)
        for mode in ["nodebuff", "sumo", "axe"]:
            if mode in data:
                embed.add_field(name=f"📦 {mode}", value=f"{data[mode]} ({data.get(f'{mode}_score', '?')})", inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Lỗi khi truy vấn profile: {e}")

@bot.command()
async def deletetier(ctx, mc_name: str, mode: str):
    await ctx.send(f"⚠️ Bạn có chắc muốn xoá tier của `{mc_name}` trong mode `{mode}` không? (gõ `yes` để xác nhận)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=15)
        if msg.content.lower() != "yes":
            await ctx.send("❌ Đã huỷ xoá tier.")
            return

        res = requests.delete(f"{API_URL}/delete", json={"mc_name": mc_name, "mode": mode})
        if res.status_code == 200:
            await ctx.send(f"✅ Đã xoá tier `{mode}` cho `{mc_name}`.")
        else:
            await ctx.send("❌ Xoá thất bại: " + res.text)
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {e}")

bot.run("YOUR_DISCORD_BOT_TOKEN")
