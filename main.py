import discord
from discord.ext import commands
import os
from utils.logger import Logger
from utils.helper import Help
from typing import Dict
from utils.database import Database
from config import Config

class DiscordBot:
    """A Discord bot class that handles events, commands, and CLI operations.
    
    Attributes:
        token (str): The Discord bot token from environment variables
        bot (commands.Bot): The main Discord bot instance
        logger (Logger): Custom logger instance for bot operations
    """
    
    def __init__(self) -> None:
        self._validate_config()
        self._setup_bot()
        self.bot.db = None
        
    def _validate_config(self) -> None:
        """Validate configuration"""
        Config.validate()
        self.token: str = Config.DISCORD_TOKEN

    def _setup_bot(self) -> None:
        """Set up bot instance and configurations"""
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True 
        intents.members = True

        self.bot: commands.Bot = commands.Bot(
            command_prefix='!', 
            intents=intents,
            help_command=Help()
        )
        self.logger: Logger = Logger()
        self.setup_events()

    def setup_events(self) -> None:
        """Set up bot event handlers for error handling and ready state."""
        @self.bot.event
        async def on_command_error(ctx: commands.Context, error: Exception) -> None:
            error_messages: Dict[type, str] = {
                commands.CommandNotFound: "(｡•́︿•̀｡) Oopsie! Command not found. Try checking available commands~",
                commands.MissingPermissions: "(｡T ω T｡) Gomen ne~ You don't have permission to use this command!",
                commands.MissingRequiredArgument: "(◕︿◕✿) Ah! You're missing something important. Please check the command usage~"
            }
            message: str = error_messages.get(type(error), f"(╥﹏╥) Oh no! Something went wrong: {str(error)}")
            await ctx.send(message)

        @self.bot.event
        async def on_ready() -> None:
            self.logger.info(f'✨ Logged in as {self.bot.user.name}')
            self.logger.info('🚀 Bot is ready')
            await self._initialize_bot()

    async def _initialize_bot(self) -> None:
        """Initialize bot components"""
        self.bot.db = Database()
        await self.bot.db.connect()
        self.logger.info('✨ Successfully connected to MongoDB')

        await self.load_cogs()
        await self.sync_commands()

    async def sync_commands(self) -> None:
        """Sync slash commands globally."""
        try:
            synced = await self.bot.tree.sync()
            self.logger.info(f'✨ Successfully synced {len(synced)} slash commands')
        except Exception as e:
            self.logger.error(f'❌ Failed to sync slash commands: {str(e)}')

    async def _manage_extension(self, extension: str, action: str) -> bool:
        """Manage cog extension loading/unloading
        
        Args:
            extension (str): The extension name
            action (str): Either 'load' or 'unload'
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if action == 'load':
                await self.bot.load_extension(extension)
            else:  
                await self.bot.unload_extension(extension)
            self.logger.info(f'✨ Successfully {action}ed cog: {extension}')
            return True
        except Exception as e:
            self.logger.error(f'❌ Failed to {action} cog {extension}: {str(e)}')
            return False

    async def load_cogs(self) -> None:
        """Load all cog extensions from the cogs directory.""" 
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                extension = f'cogs.{filename[:-3]}'
                await self._manage_extension(extension, 'load')

    async def unload_cogs(self) -> None:
        """Unload all currently loaded cog extensions."""
        for extension in list(self.bot.extensions):
            await self._manage_extension(extension, 'unload')

    def run(self) -> None:
        """Start the Discord bot."""
        self.bot.run(self.token)

def main() -> None:
    """Main entry point for the Discord bot application."""
    bot: DiscordBot = DiscordBot()
    bot.run()

if __name__ == "__main__":
    main()