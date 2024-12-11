import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
from typing import Optional, Dict, Any

class Economy(commands.Cog):
    """Economy system for managing user experience, levels and currency.
    
    This cog handles all economy-related features including:
    - Experience and leveling system 
    - Currency management
    - Daily rewards
    - User profiles and leaderboards
    """

    def __init__(self, bot: commands.Bot):
        """Initialize the Economy cog.
        
        Parameters
        ----------
        bot : commands.Bot
            The bot instance
        """
        self.bot = bot
        self.exp_range = (5, 15)
        self.daily_money = 500
        self.daily_exp = 1000
        self.daily_cooldown = timedelta(days=1)  # 24 hours cooldown

    async def _ensure_user_exists(self, user_id: int, guild_id: int) -> Dict[str, Any]:
        """Ensure a user exists in the database, create if not.
        
        Parameters
        ----------
        user_id : int
            Discord user ID
        guild_id : int
            Discord guild ID
            
        Returns
        -------
        Dict[str, Any]
            The user's data
        """
        data = await self.bot.db.get_user(user_id, guild_id)
        if not data:
            await self.bot.db.create_user(user_id, guild_id)
            data = await self.bot.db.get_user(user_id, guild_id)
        return data

    async def _handle_level_up(self, message: discord.Message, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> None:
        """Handle level up notifications.
        
        Parameters
        ----------
        message : discord.Message
            The message that triggered the level up
        old_data : Dict[str, Any]
            User's previous data
        new_data : Dict[str, Any]
            User's updated data
        """
        if old_data and new_data['level'] > old_data['level']:
            embed = discord.Embed(
                title="✧･ﾟ: *✧･ﾟ LEVEL UP! ･ﾟ✧*:･ﾟ✧",
                description=f"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Sugoi! {message.author.mention}-chan leveled up to level {new_data['level']}! Keep going~! ♪",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)

    async def _create_profile_embed(self, member: discord.Member, data: Dict[str, Any]) -> discord.Embed:
        """Create an embed for user profiles.
        
        Parameters
        ----------
        member : discord.Member
            The member whose profile to show
        data : Dict[str, Any]
            The member's data
            
        Returns
        -------
        discord.Embed
            The formatted profile embed
        """
        embed = discord.Embed(
            title=f"✧･ﾟ {member.display_name}'s Profile ･ﾟ✧",
            color=discord.Color.pink()
        )
        embed.add_field(name="✨ Level", value=f"Level {data['level']} desu~!")
        embed.add_field(name="⭐ Experience", value=f"{data['exp']} EXP collected!")
        embed.add_field(name="💰 Money", value=f"${data['money']} in the piggy bank!")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="(｡♥‿♥｡) Keep being amazing! ♪")
        return embed

    async def _create_leaderboard_embed(self, guild: discord.Guild, data: list) -> discord.Embed:
        """Create an embed for the server leaderboard.
        
        Parameters
        ----------
        guild : discord.Guild
            The guild to create leaderboard for
        data : list
            List of user data sorted by rank
            
        Returns
        -------
        discord.Embed
            The formatted leaderboard embed
        """
        embed = discord.Embed(
            title="✧･ﾟ: *✧･ﾟ Server Rankings! ･ﾟ✧*:･ﾟ✧",
            description="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Our amazing members~!",
            color=discord.Color.gold()
        )
        
        for idx, entry in enumerate(data, 1):
            user = guild.get_member(entry['user_id'])
            if user:
                crown = "👑" if idx == 1 else "✨"
                embed.add_field(
                    name=f"{crown} #{idx} {user.display_name}",
                    value=f"Level: {entry['level']} ⭐\nExp: {entry['exp']} ✨\nMoney: ${entry['money']} 💰",
                    inline=False
                )
        embed.set_footer(text="(｡♥‿♥｡) Everyone is doing their best! Ganbare~! ♪")
        return embed

    async def _check_daily_cooldown(self, user_id: int, guild_id: int) -> tuple[bool, Optional[timedelta]]:
        """Check if user can claim daily reward.
        
        Parameters
        ----------
        user_id : int
            Discord user ID
        guild_id : int
            Discord guild ID
            
        Returns
        -------
        tuple[bool, Optional[timedelta]]
            (can_claim, time_remaining)
        """
        data = await self._ensure_user_exists(user_id, guild_id)
        last_daily = data.get('last_daily')
        
        if not last_daily:
            return True, None
            
        now = datetime.utcnow()
        last_claim = datetime.fromisoformat(last_daily)
        time_passed = now - last_claim
        
        if time_passed >= self.daily_cooldown:
            return True, None
            
        time_remaining = self.daily_cooldown - time_passed
        return False, time_remaining

    async def _update_daily_timestamp(self, user_id: int, guild_id: int) -> None:
        """Update user's last daily claim timestamp.
        
        Parameters
        ----------
        user_id : int
            Discord user ID
        guild_id : int
            Discord guild ID
        """
        await self.bot.db.update_daily_timestamp(user_id, guild_id)

    @commands.Cog.listener()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def on_message(self, message: discord.Message):
        """Handles experience gain from user messages.
        
        This listener awards random experience points when users send messages,
        handles leveling up, and sends level up notifications.
        
        Parameters
        ----------
        message : discord.Message
            The message that triggered this event
        """
        if message.author.bot:
            return

        exp_gain = random.randint(*self.exp_range)
        user_data = await self._ensure_user_exists(message.author.id, message.guild.id)
        current_exp = user_data['exp'] + exp_gain
        updated_data = await self.bot.db.update_exp(message.author.id, message.guild.id, current_exp)
        await self._handle_level_up(message, user_data, updated_data)

    @commands.hybrid_command(name="profile", description="Show your or another user's profile~!")
    async def profile(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Shows the profile of a user including their level, exp and money.
        
        Parameters
        ----------
        ctx : commands.Context
            The invocation context
        member : Optional[discord.Member]
            The member whose profile to show. Defaults to command invoker
        """
        target = member or ctx.author
        data = await self._ensure_user_exists(target.id, ctx.guild.id)
        embed = await self._create_profile_embed(target, data)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", description="Check out our amazing server rankings~!")
    async def leaderboard(self, ctx: commands.Context):
        """Displays the server's leaderboard showing top users by level and wealth.
        
        Parameters
        ----------
        ctx : commands.Context
            The invocation context
        """
        data = await self.bot.db.get_leaderboard(ctx.guild.id)
        embed = await self._create_leaderboard_embed(ctx.guild, data)
        await ctx.send(embed=embed)

    class RewardButtons(discord.ui.View):
        """Button view for daily reward selection."""
        
        def __init__(self, cog, ctx):
            super().__init__(timeout=30)
            self.cog = cog
            self.ctx = ctx
            self.value = None

        async def _handle_reward_claim(self, interaction: discord.Interaction, is_money: bool) -> None:
            """Handle claiming of daily rewards.
            
            Parameters
            ----------
            interaction : discord.Interaction
                The button interaction
            is_money : bool
                Whether the reward is money (True) or exp (False)
            """
            if interaction.user.id != self.ctx.author.id:
                return await interaction.response.send_message(
                    "(｡•́︿•̀｡) Gomen ne~ This isn't your reward to claim!", 
                    ephemeral=True
                )

            if is_money:
                new_balance = await self.ctx.bot.db.add_money(
                    self.ctx.author.id, 
                    self.ctx.guild.id, 
                    self.cog.daily_money
                )
                embed = discord.Embed(
                    title="💰 Yatta! Daily Reward Get! 💰",
                    description=f"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ You received ${self.cog.daily_money}!\nNew balance: ${new_balance}",
                    color=discord.Color.green()
                )
            else:
                user_data = await self.ctx.bot.db.get_user(
                    self.ctx.author.id, 
                    self.ctx.guild.id
                )
                current_exp = user_data['exp'] + self.cog.daily_exp
                updated_data = await self.ctx.bot.db.update_exp(
                    self.ctx.author.id, 
                    self.ctx.guild.id, 
                    current_exp
                )
                embed = discord.Embed(
                    title="✨ Sugoi! Daily Reward Get! ✨",
                    description=f"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ You received {self.cog.daily_exp} EXP!\nLevel: {updated_data['level']}\nTotal EXP: {updated_data['exp']}",
                    color=discord.Color.blue()
                )

            await interaction.response.edit_message(embed=embed, view=None)
            self.value = True
            self.stop()

        @discord.ui.button(label="💰 Money ($500)", style=discord.ButtonStyle.green)
        async def money(self, interaction: discord.Interaction, button: discord.ui.Button):
            """Money reward button handler."""
            await self._handle_reward_claim(interaction, True)

        @discord.ui.button(label="✨ EXP (1000)", style=discord.ButtonStyle.blurple)
        async def exp(self, interaction: discord.Interaction, button: discord.ui.Button):
            """EXP reward button handler."""
            await self._handle_reward_claim(interaction, False)

    @commands.hybrid_command(name="daily", description="Claim your adorable daily reward~!")
    async def daily(self, ctx: commands.Context):
        """Claim your daily reward - choose between EXP or money.
        
        Parameters
        ----------
        ctx : commands.Context
            The invocation context
        """
        can_claim, time_remaining = await self._check_daily_cooldown(ctx.author.id, ctx.guild.id)
        
        if not can_claim:
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return await ctx.reply(
                f"(｡•́︿•̀｡) Gomen ne~ Please wait **{hours}h {minutes}m** before claiming your next daily reward!"
            )

        view = self.RewardButtons(self, ctx)
        embed = discord.Embed(
            title="🎁 Magical Daily Reward Time! 🎁",
            description=f"(◕‿◕✿) Choose your reward:\n💰 ${self.daily_money} Money\n✨ {self.daily_exp} EXP",
            color=discord.Color.gold()
        )
        
        message = await ctx.send(embed=embed, view=view)
        await view.wait()
        
        if view.value:
            await self._update_daily_timestamp(ctx.author.id, ctx.guild.id)
        else:
            embed.description = "(｡•́︿•̀｡) Oh no! The reward expired! Try again~!"
            await message.edit(embed=embed, view=None)

    @commands.hybrid_command(name="give", description="Share your money with friends~!")
    async def give(self, ctx: commands.Context, member: discord.Member, amount: int):
        """Give money to another user.
        
        Parameters
        ----------
        ctx : commands.Context
            The invocation context
        member : discord.Member
            The member to give money to
        amount : int
            Amount of money to give
        """
        if member.bot:
            return await ctx.reply("(｡•́︿•̀｡) Gomen ne~ You can't give money to bots!")
        
        if amount <= 0:
            return await ctx.reply("(｡•́︿•̀｡) The amount must be positive, silly~!")
        
        giver_data = await self._ensure_user_exists(ctx.author.id, ctx.guild.id)
        receiver_data = await self._ensure_user_exists(member.id, ctx.guild.id)

        if not receiver_data:
            return await ctx.reply("(◕︿◕✿) Eh? I couldn't find this user in my records~")
        
        if giver_data['money'] < amount:
            return await ctx.reply("(｡T ω T｡) You don't have enough money, poor thing~!")
        
        await self.bot.db.add_money(ctx.author.id, ctx.guild.id, -amount)
        await self.bot.db.add_money(member.id, ctx.guild.id, amount)
        
        embed = discord.Embed(
            title="💝 Generous Gift! 💝",
            description=f"(｡♥‿♥｡) {ctx.author.mention} gave ${amount} to {member.mention}! So kind~!",
            color=discord.Color.pink()
        )
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))