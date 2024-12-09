import discord
from discord.ext import commands
import os
import sys
import textwrap
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
            title=f"Server Information: {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        stats: Dict[str, str] = {
            "Members": f"Total: {len(guild.members)}\n"
                      f"Humans: {len([m for m in guild.members if not m.bot])}\n"
                      f"Bots: {len([m for m in guild.members if m.bot])}",
            "Channels": f"Text: {len(guild.text_channels)}\n"
                       f"Voice: {len(guild.voice_channels)}\n"
                       f"Categories: {len(guild.categories)}",
            "Server Details": f"ID: {guild.id}\n"
                            f"Owner: {guild.owner.mention}\n"
                            f"Created: {guild.created_at.strftime('%Y-%m-%d')}"
        }

        for name, value in stats.items():
            embed.add_field(name=name, value=value, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='shell')
    @commands.is_owner()
    async def shell_command(self, ctx: commands.Context, *, command: str) -> None:
        """Execute shell commands (Owner only)"""
        try:
            output: str = os.popen(command).read()
            if not output:
                return await ctx.send("Command executed successfully.")
                
            if len(output) > 1990:
                output = f"{output[:1990]}..."
                
            await ctx.send(f"```\n{output}\n```")
            
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    @commands.command(name='debug')
    @commands.is_owner()
    async def debug(self, ctx: commands.Context, *, code: str) -> None:
        """Evaluate Python code (Owner only)"""
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
                await ctx.send(f"```python\n{result}```")
            if output:
                await ctx.send(f"```\n{output}```")
                
        except Exception as e:
            await ctx.send(f"```\nError: {str(e)}```")
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
            return await ctx.reply("(｡•́︿•̀｡) Gomen ne~ I can't ban someone with a higher or equal role to yours!")
            
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="(｡T ω T｡) Member Banned!",
                description=f"*sniff* I had to ban {member.mention}...\n💔 Reason: {reason}",
                color=discord.Color.pink()
            )
            embed.set_footer(text="Please follow the rules next time~ ♡")
            await ctx.reply(embed=embed)
        except discord.Forbidden:
            await ctx.reply("(╥﹏╥) Oh no! I don't have permission to ban this member...")
        except Exception as e:
            await ctx.reply(f"(｡•́︿•̀｡) Something went wrong: {str(e)}")

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
                    return await ctx.reply("(◕︿◕✿) Eh? I couldn't find this banned user...")

            await ctx.guild.unban(user_obj, reason=reason)
            embed = discord.Embed(
                title="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ User Unbanned!",
                description=f"Yatta! {user_obj.mention if hasattr(user_obj, 'mention') else user_obj} has been forgiven and unbanned!\n💕 Reason: {reason}",
                color=discord.Color.pink()
            )
            embed.set_footer(text="Welcome back~ Let's be friends again! ♡")
            await ctx.reply(embed=embed)
        except discord.NotFound:
            await ctx.reply("(◕︿◕✿) Eh? I couldn't find this user...")
        except discord.Forbidden:
            await ctx.reply("(｡T ω T｡) I don't have permission to unban users...")
        except Exception as e:
            await ctx.reply(f"(╥﹏╥) Oopsie! Something went wrong: {str(e)}")
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
