import discord
from discord.ext import commands
from lib.stablediffusion import StableDiffusion, SDConfig
import io
from typing import Dict, Set
from config import Config
import asyncio


class Wfx(commands.GroupCog, group_name="wfx"):
    """AI image generator using Stable Diffusion."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Wfx cog.
        
        Parameters
        ----------
        bot : commands.Bot
            The Discord bot instance
        """
        self.bot = bot
        self.sd_client = StableDiffusion(Config.STABLE_DIFFUSION_URL)
        self.active_users: Set[int] = set()
        self.generation_cost = 100

    async def _check_user_eligibility(self, ctx: commands.Context) -> bool:
        """Check if user can generate an image.
        
        Parameters
        ----------
        ctx : commands.Context
            The command context
            
        Returns
        -------
        bool
            Whether user is eligible to generate
        """
        if ctx.author.id in self.active_users:
            await ctx.send("(｡T ω T｡) Please wait for your current generation to finish!", ephemeral=True)
            return False

        user_data = await self.bot.db.get_user(ctx.author.id, ctx.guild.id)
        if not user_data or user_data['money'] < self.generation_cost:
            await ctx.send(f"(｡•́︿•̀｡) You need {self.generation_cost} money to generate an image!", ephemeral=True)
            return False

        return True

    async def _create_response_embed(
        self, 
        title: str, 
        color: discord.Color,
        fields: Dict[str, str]
    ) -> discord.Embed:
        """Create a formatted embed response.
        
        Parameters
        ----------
        title : str
            The embed title
        color : discord.Color
            The embed color
        fields : Dict[str, str]
            Dictionary of field names and values
            
        Returns:
            discord.Embed: Formatted embed with fields
        """
        embed = discord.Embed(title=title, color=color)
        for name, value in fields.items():
            if value:
                embed.add_field(name=name, value=value, inline=False)
        return embed

    async def _handle_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle and send error messages.
        
        Parameters
        ----------
        ctx : commands.Context
            The command context
        error : Exception
            The exception that occurred
        """
        await ctx.send(
            f"(｡•́︿•̀｡) Oopsie! Something went wrong: {str(error)}", 
            ephemeral=True
        )

    def quality_echancher(self, prompt: str, type: str = "high") -> Dict[str, str]:
        """Enhance the quality of the prompt.

        Parameters
        ----------
        prompt : str
            The prompt to enhance
        type : str
            The type of enhancement

        Returns
        -------
        Dict[str, str]
            The enhanced prompt and negative prompt
        """

        list_of_quality = {
            "low": {
                "prompt": "{},  masterpiece, best quality, very aesthetic, absurdres".format(prompt),
                "negative_prompt": "nsfw, lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"
            },
            "medium": {
                "prompt": "{}, (masterpiece), best quality, very aesthetic, perfect face".format(prompt),
                "negative_prompt": "nsfw, (low quality, worst quality:1.2), very displeasing, 3d, watermark, signature, ugly, poorly drawn"
            },
            "high": {
                "prompt": "{}, (masterpiece), (best quality), (ultra-detailed), very aesthetic, illustration, disheveled hair, perfect composition, moist skin, intricate details".format(prompt),
                "negative_prompt": "nsfw, longbody, lowres, bad anatomy, bad hands, missing fingers, pubic hair, extra digit, fewer digits, cropped, worst quality, low quality, very displeasing"
            },
            "none": {
                "prompt": prompt,
                "negative_prompt": "nsfw, lowres"
            }
        }

        return list_of_quality.get(type, list_of_quality["none"])
    
    def image_ratio(self, ratio: str = "1:1") -> Dict[str, int]:
        """Set the image ratio.

        Parameters
        ----------
        ratio : str
            The image ratio

        Returns
        -------
        Dict[str, int]
            The image width and height
        """

        list_of_ratio = {
            "1:1": {"width": 1024, "height": 1024},
            "9:7": {"width": 1152, "height": 896},
            "7:9": {"width": 896, "height": 1152},
            "19:13": {"width": 1216, "height": 832},
            "13:19": {"width": 832, "height": 1216},
            "7:4": {"width": 1344, "height": 768},
            "4:7": {"width": 768, "height": 1344},
            "12:5": {"width": 1536, "height": 640},
            "5:12": {"width": 640, "height": 1536}
        }

        return list_of_ratio.get(ratio, list_of_ratio["1:1"])

    @commands.hybrid_command(
        description="Generate an image using Stable Diffusion"
    )
    async def generate(
        self, 
        ctx: commands.Context, 
        prompt: str,
        quality: str = "high",
        ratio: str = "1:1",
        steps: int = 24,
        cfg_scale: float = 4.5,
    ) -> None:
        """Generate an image using Stable Diffusion.
        
        Parameters
        ----------
        ctx: commands.Context
            The command context
        prompt: str
            The main prompt describing desired image
        quality: str
            The quality of the image (optional, default: high, low, medium)
        ratio: str
            The image ratio (optional, default: 1:1, 9:7, 7:9, 19:13, 13:19, 7:4, 4:7, 12:5, 5:12)
        steps: int
            Number of denoising steps (optional, default: 24)
        cfg_scale: float
            Classifier free guidance scale (optional, default: 4.5)
        """
        loading_message = None
        if not ctx.interaction:
            loading_message = await ctx.send("(๑•̀ㅂ•́)و✧ Processing your request...")
        else:
            await ctx.defer()

        if not await self._check_user_eligibility(ctx):
            if loading_message:
                await loading_message.delete()
            return

        try:
            self.active_users.add(ctx.author.id)
            
            await self.bot.db.add_money(ctx.author.id, ctx.guild.id, -self.generation_cost)

            quality_data = self.quality_echancher(prompt, quality)
            ratio_data = self.image_ratio(ratio)

            config = SDConfig(
                prompt=quality_data["prompt"],
                negative_prompt=quality_data["negative_prompt"],
                width=ratio_data["width"],
                height=ratio_data["height"],
                steps=steps,
                cfg_scale=cfg_scale
            )

            images = await self.sd_client.text2img(config)
            
            image_data = io.BytesIO(images[0])
            file = discord.File(image_data, filename="generated.png")
            
            embed = await self._create_response_embed(
                title="✨ Your Kawaii Image is Ready! ✨",
                color=discord.Color.pink(),
                fields={
                    "🎀 Prompt": quality_data["prompt"],
                    "🌸 Negative Prompt": quality_data["negative_prompt"], 
                    "✨ Image Ratio": ratio,
                    "💫 Image Size": f"{ratio_data['width']}x{ratio_data['height']}",
                    "⭐ Steps": steps,
                    "🌟 CFG Scale": cfg_scale,
                    "🎭 Quality": quality,
                    "🌈 Model": "AnimagineXL 3.1",
                    "💰 Cost": f"{self.generation_cost} money"
                }
            )

            if loading_message:
                await loading_message.delete()
            
            await ctx.send("(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Here's your generated image~!", embed=embed, file=file)

        except Exception as e:
            await self.bot.db.add_money(ctx.author.id, ctx.guild.id, self.generation_cost)
            if loading_message:
                await loading_message.delete()
            await self._handle_error(ctx, e)
        finally:
            self.active_users.remove(ctx.author.id)

    @commands.hybrid_command(
        description="Show available Stable Diffusion models"
    )
    async def models(self, ctx: commands.Context) -> None:
        """List all available Stable Diffusion models.
        
        Parameters
        ----------
        ctx : commands.Context
            The command context
        """
        await ctx.defer()

        try:
            models = await self.sd_client.get_models()
            fields = {
                model["title"]: model["model_name"] 
                for model in models
            }
            
            embed = await self._create_response_embed(
                title="🌟 Available Models 🌟",
                color=discord.Color.pink(),
                fields=fields
            )
            
            await ctx.send("(◕‿◕✿) Here are all the models I can use~!", embed=embed)

        except Exception as e:
            await self._handle_error(ctx, e)

    async def cog_unload(self) -> None:
        """Cleanup when cog is unloaded."""
        await self.sd_client.close()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Wfx(bot))
