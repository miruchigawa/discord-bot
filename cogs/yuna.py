from discord.ext import commands
from lib.llm import LLMAgent

class Yuna(commands.GroupCog, group_name="yuna"):
    """Yuna is a bot that can help you with your problems."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.llm = LLMAgent()

    @commands.command(name="chat")
    async def chat(self, ctx: commands.Context, *, message: str) -> None:
        """Chat with Yuna."""
        response = self.llm.chat(ctx.author.id, message)
        await ctx.send(response)

    @commands.command(name="reset")
    async def reset(self, ctx: commands.Context) -> None:
        """Reset a session."""
        self.llm.reset_session(ctx.author.id)
        await ctx.send("(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Session reset!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Yuna(bot))