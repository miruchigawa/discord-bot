import discord
from discord.ext import commands
import os
import sys
import textwrap
import psutil
from io import StringIO
from typing import Dict, Any, Optional

class Admin(commands.Cog):
    """Administrative commands for bot management"""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='serverinfo')
    @commands.has_permissions(administrator=True)
    async def server_info(self, ctx: commands.Context) -> None:
        """Display detailed server information"""
        guild: discord.Guild = ctx.guild
        
        embed: discord.Embed = discord.Embed(
            title=f"✧･ﾟ: *✧･ﾟ Server Info for {guild.name} ･ﾟ✧*:･ﾟ✧",
            color=discord.Color.pink()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        stats: Dict[str, str] = {
            "🌸 Members": f"Total: {len(guild.members)}\n"
                      f"Humans: {len([m for m in guild.members if not m.bot])} 👥\n"
                      f"Bots: {len([m for m in guild.members if m.bot])} 🤖",
            "💫 Channels": f"Text: {len(guild.text_channels)} 📝\n"
                       f"Voice: {len(guild.voice_channels)} 🎤\n"
                       f"Categories: {len(guild.categories)} 📁",
            "✨ Server Details": f"ID: {guild.id}\n"
                            f"Owner: {guild.owner.mention} 👑\n"
                            f"Created: {guild.created_at.strftime('%Y-%m-%d')} 🎂"
        }

        for name, value in stats.items():
            embed.add_field(name=name, value=value, inline=True)

        embed.set_footer(text="(｡♥‿♥｡) Thanks for checking our server info!")
        await ctx.send(embed=embed)

    @commands.command(name='sysinfo')
    @commands.has_permissions(administrator=True)
    async def system_info(self, ctx: commands.Context) -> None:
        """Display system resource information"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        embed = discord.Embed(
            title="(◕‿◕✿) System Information Desu~",
            color=discord.Color.pink()
        )
        
        embed.add_field(
            name="💻 CPU-chan Usage",
            value=f"{cpu_percent}% *\*working hard\**",
            inline=False
        )
        
        embed.add_field(
            name="🎀 Memory-chan Status",
            value=f"Total: {memory.total // (1024**3)}GB\n"
                  f"Used: {memory.used // (1024**3)}GB ({memory.percent}%) *\*ganbarimasu\**\n"
                  f"Free: {memory.free // (1024**3)}GB *\*still available\**",
            inline=False
        )
        
        embed.add_field(
            name="💾 Disk-chan Space",
            value=f"Total: {disk.total // (1024**3)}GB\n"
                  f"Used: {disk.used // (1024**3)}GB ({disk.percent}%) *\*nom nom\**\n"
                  f"Free: {disk.free // (1024**3)}GB *\*still hungry\**",
            inline=False
        )
        
        embed.set_footer(text="(｡◕‿◕｡) Your system is doing its best!")
        await ctx.send(embed=embed)

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload_cog(self, ctx: commands.Context, cog: str) -> None:
        """Reload a specific cog
        
        Parameters
        ----------
        cog: The name of the cog to reload
        """
        try:
            extension = f"cogs.{cog}" if not cog.startswith("cogs.") else cog
            await self.bot.reload_extension(extension)
            await ctx.send(f"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Yatta! Successfully reloaded {cog}! Time for more fun~!")
        except Exception as e:
            await ctx.send(f"(｡•́︿•̀｡) Uwaaah! Failed to reload {cog}: {str(e)}")

    @commands.command(name='shell')
    @commands.is_owner()
    async def shell_command(self, ctx: commands.Context, *, command: str) -> None:
        """Execute shell commands (Owner only)"""
        try:
            output: str = os.popen(command).read()
            if not output:
                return await ctx.send("(◕‿◕✿) Command executed successfully, Master!")
                
            if len(output) > 1990:
                output = f"{output[:1990]}..."
                
            await ctx.send(f"```\n{output}\n```\n(｡♥‿♥｡) Here's your output, Master!")
            
        except Exception as e:
            await ctx.send(f"(╥﹏╥) Gomenasai Master! There was an error: {str(e)}")

    @commands.command(name='debug')
    @commands.is_owner()
    async def debug(self, ctx: commands.Context, *, code: str) -> None:
        """
        Evaluate Python code (Owner only)
        
        Parameters
        ----------
        code: The Python code to evaluate
        """
        env: Dict[str, Any] = {
            'bot': self.bot,
            'ctx': ctx,
            'discord': discord,
            'commands': commands,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author
        }

        stdout: StringIO = StringIO()
        
        try:
            wrapped_code: str = f'async def _eval_expr():\n{textwrap.indent(code.strip("` "), "    ")}'
            
            sys.stdout = stdout
            exec(wrapped_code, env)
            result: Any = await eval('_eval_expr()', env)
            
            output: str = stdout.getvalue()
            
            if result is not None:
                await ctx.send(f"```python\n{result}```\n(✿◠‿◠) Code executed successfully, Master!")
            if output:
                await ctx.send(f"```\n{output}```\n(◕‿◕✿) Here's your output, Master!")
                
        except Exception as e:
            await ctx.send(f"```\n(｡•́︿•̀｡) Gomenasai! Error: {str(e)}```")
        finally:
            sys.stdout = sys.__stdout__

    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: commands.Context,
        member: discord.Member,
        reason: Optional[str] = "No reason provided"
    ) -> None:
        """Ban a member from the server
        
        Parameters
        ----------
        member: The member to ban
        reason: The reason for the ban
        """
        if member.top_role >= ctx.author.top_role:
            return await ctx.reply("(｡•́︿•̀｡) Gomen ne~ I can't ban someone with a higher or equal role to yours! That would be rude >.<")
            
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="(｡T ω T｡) Member Banned! *sniff sniff*",
                description=f"I had to use my special ban hammer on {member.mention}...\n💔 Reason: {reason}\n\n*wipes tears* I hope they learn their lesson...",
                color=discord.Color.pink()
            )
            embed.set_footer(text="(｡♥‿♥｡) Please follow the rules next time~ We'll miss you! ♡")
            await ctx.reply(embed=embed)
        except discord.Forbidden:
            await ctx.reply("(╥﹏╥) Uwaaah! I don't have permission to ban this member... My powers aren't strong enough!")
        except Exception as e:
            await ctx.reply(f"(｡•́︿•̀｡) Oopsie woopsie! Something went wrong: {str(e)}")

    @commands.hybrid_command(name="unban", description="Unban a user from the server")
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: commands.Context,
        user: str,
        reason: Optional[str] = "No reason provided"
    ) -> None:
        """Unban a user from the server
        
        Parameters
        ----------
        user: The user ID or username to unban (format: username#discriminator)
        reason: The reason for the unban
        """
        try:
            try:
                user_id = int(user)
                user_obj = discord.Object(id=user_id)
            except ValueError:
                bans = [ban_entry async for ban_entry in ctx.guild.bans()]
                user_obj = None
                for ban_entry in bans:
                    if str(ban_entry.user) == user:
                        user_obj = ban_entry.user
                        break
                if user_obj is None:
                    return await ctx.reply("(◕︿◕✿) Eh? I couldn't find this banned user... Did they disappear? (。_。)")

            await ctx.guild.unban(user_obj, reason=reason)
            embed = discord.Embed(
                title="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Unban Success!",
                description=f"Yatta! {user_obj.mention if hasattr(user_obj, 'mention') else user_obj} has been forgiven!\n💕 Reason: {reason}\n\n*jumps with joy* Time to celebrate!",
                color=discord.Color.pink()
            )
            embed.set_footer(text="(｡♥‿♥｡) Welcome back~ Let's be the best of friends again! ♡")
            await ctx.reply(embed=embed)
        except discord.NotFound:
            await ctx.reply("(◕︿◕✿) Eh? I couldn't find this user... Maybe they're playing hide and seek? (。_。)")
        except discord.Forbidden:
            await ctx.reply("(｡T ω T｡) Gomenasai! I don't have permission to unban users... My magic isn't strong enough!")
        except Exception as e:
            await ctx.reply(f"(╥﹏╥) Uwaaah! Something went wrong: {str(e)}")

    @commands.command(name='addmoney')
    @commands.is_owner()
    async def add_money(
        self,
        ctx: commands.Context,
        member: Optional[discord.Member] = None,
        amount: int = 0
    ) -> None:
        """Add money to a member's balance
        
        Parameters
        ----------
        member: The member to give money to (optional, defaults to self)
        amount: The amount of money to add
        """
        if amount <= 0:
            return await ctx.reply("(｡•́︿•̀｡) Oopsie! The amount must be positive!")

        try:
            target = member or ctx.author
            new_balance = await self.bot.db.add_money(target.id, ctx.guild.id, amount)
            
            embed = discord.Embed(
                title="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Money Added Successfully!",
                description=f"Added {amount} 💰 to {target.mention}'s balance!\nNew balance: {new_balance} 💰\n\n*throws confetti*",
                color=discord.Color.pink()
            )
            embed.set_footer(text="(｡♥‿♥｡) Spend it wisely~!")
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"(╥﹏╥) Uwaaah! Something went wrong: {str(e)}")
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
