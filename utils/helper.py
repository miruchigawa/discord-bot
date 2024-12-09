import discord
from discord.ext import commands
from typing import Optional, Dict, List

class Help(commands.HelpCommand):
    """A cute-styled help command for the bot (◕‿◕✿)
    
    This help command provides an adorable and cute way to display
    command information using pretty embeds~
    """

    def __init__(self):
        super().__init__(command_attrs={
            'help': '(◕‿◕✿) Shows all my cute commands and what they do!',
            'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member)
        })

    async def send_bot_help(self, mapping: Dict[Optional[commands.Cog], List[commands.Command]]) -> None:
        """Send the main help page with all the cute commands ♪(๑ᴖ◡ᴖ๑)♪"""
        embed = discord.Embed(
            title="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Command List",
            description="Konnichiwa! Here are all my lovely commands~\nUse `!help <command>` to learn more about them! (◕‿◕✿)",
            color=discord.Color.pink()
        )

        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            if filtered:
                cog_name = getattr(cog, "qualified_name", "miscellaneous")
                command_list = [f"`{cmd.name}`" for cmd in filtered]
                if command_list:
                    embed.add_field(
                        name=f"🌸 {cog_name}",
                        value="・".join(command_list),
                        inline=False
                    )

        embed.set_footer(text="(｡♥‿♥｡) Thank you for using me! Let's be friends~")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command) -> None:
        """Send help for a specific command in an adorable way (◕ᴗ◕✿)"""
        embed = discord.Embed(
            title=f"(★‿★) About {command.name}",
            description=command.help or "(◕︿◕✿) Gomen ne, no description available~",
            color=discord.Color.pink()
        )

        if command.aliases:
            embed.add_field(
                name="✧ Other names I respond to~", 
                value="・".join(f"`{alias}`" for alias in command.aliases)
            )

        if command.signature:
            embed.add_field(
                name="✧ How to use me", 
                value=f"`{self.context.clean_prefix}{command.name} {command.signature}`"
            )
        else:
            embed.add_field(
                name="✧ How to use me", 
                value=f"`{self.context.clean_prefix}{command.name}`"
            )

        embed.set_footer(text="(｡◕‿◕｡) Hope this helps!")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """Send help for a category of commands ٩(◕‿◕｡)۶"""
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        
        embed = discord.Embed(
            title=f"(◕‿◕✿) {cog.qualified_name} Commands",
            description=cog.description or "(◕︿◕✿) Gomen ne, no description available~",
            color=discord.Color.pink()
        )

        for command in filtered:
            embed.add_field(
                name=f"✧ {command.name}",
                value=command.help or "(◕︿◕✿) No description yet~",
                inline=False
            )

        embed.set_footer(text="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Thanks for checking out my commands!")
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error: str) -> None:
        """Send an error message in a sweet way (｡•́︿•̀｡)"""
        embed = discord.Embed(
            title="(｡T ω T｡) Oopsie!",
            description=f"Something went wrong: {error}\nGomen nasai! (｡•́︿•̀｡)",
            color=discord.Color.pink()
        )
        await self.get_destination().send(embed=embed)


