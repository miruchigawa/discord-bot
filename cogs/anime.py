import discord
from discord.ext import commands
from lib.waifuit import WaifuIt
from config import Config
from typing import Optional

class Anime(commands.Cog):
    """Collection of anime-themed commands using waifu.it API
    
    This cog provides various anime-themed interaction commands using the waifu.it API.
    It includes commands for sending anime GIFs and images, particularly for user interactions
    like hugging, patting, and kissing.

    Attributes:
        bot: The bot instance the cog is attached to
        waifu_client: WaifuIt API client instance for fetching anime images/GIFs

    Commands:
        hug: Send a hugging anime GIF, optionally mentioning another user
        pat: Send a headpatting anime GIF, optionally mentioning another user
        kiss: Send a kissing anime GIF, optionally mentioning another user
        cry: Send a crying anime GIF
        neko: Send a random neko (catgirl) image
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.waifu_client = WaifuIt(token=Config.WAIFU_IT_TOKEN)

    async def cog_unload(self):
        """Cleanup when cog is unloaded"""
        if self.waifu_client:
            await self.waifu_client.close()

    async def _send_anime_embed(self, ctx, url: str, footer_text: Optional[str] = None):
        """Creates and sends an embedded message with anime image/GIF"""
        if not url:
            await ctx.send("Failed to fetch image. Please try again later.")
            return
            
        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=url)
        if footer_text:
            embed.set_footer(text=footer_text)
        await ctx.send(embed=embed)

    async def _handle_interaction(self, ctx, interaction_type: str, member: Optional[discord.Member] = None):
        """Handle interaction commands with optional member mention"""
        response = await self.waifu_client.fetch(interaction_type)
        
        footer = None
        if member:
            actions = {
                "hug": "hugs",
                "pat": "pats",
                "kiss": "kisses"
            }
            action = actions.get(interaction_type, "interacts with")
            footer = f"{ctx.author.name} {action} {member.name}"
        elif interaction_type == "cry":
            footer = f"{ctx.author.name} is crying"
            
        await self._send_anime_embed(ctx, response.get("url"), footer)

    @commands.hybrid_command()
    async def hug(self, ctx, member: Optional[discord.Member] = None):
        """Sends a hugging anime GIF
        
        Parameters
        ----------
        member: The member to hug, if specified
        """
        await self._handle_interaction(ctx, "hug", member)

    @commands.hybrid_command()
    async def pat(self, ctx, member: Optional[discord.Member] = None):
        """Sends a headpatting anime GIF
        
        Parameters
        ----------
        member: The member to pat, if specified
        """
        await self._handle_interaction(ctx, "pat", member)

    @commands.hybrid_command()
    async def kiss(self, ctx, member: Optional[discord.Member] = None):
        """Sends a kissing anime GIF
        
        Parameters
        ----------
        member: The member to kiss, if specified
        """
        await self._handle_interaction(ctx, "kiss", member)

    @commands.hybrid_command()
    async def cry(self, ctx):
        """Sends a crying anime GIF"""
        await self._handle_interaction(ctx, "cry")

    @commands.hybrid_command()
    async def neko(self, ctx):
        """Sends a random neko image"""
        response = await self.waifu_client.fetch("neko")
        await self._send_anime_embed(ctx, response.get("url"))

async def setup(bot):
    await bot.add_cog(Anime(bot))