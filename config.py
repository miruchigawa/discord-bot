from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration manager for environment variables
    
    This class centralizes all environment variable configurations for the bot.
    It provides validation and easy access to configuration values across the application.
    
    Environment Variables:
        DISCORD_TOKEN: Authentication token for Discord bot
        MONGO_URI: MongoDB connection string
        DB_NAME: MongoDB database name
        WAIFU_IT_TOKEN: Authentication token for waifu.it API
        
    Usage:
        from config import Config
        
        # Access configuration values
        token = Config.DISCORD_TOKEN
        
        # Validate all required variables
        Config.validate()
        
    Note:
        All environment variables should be defined in a .env file
        in the project root directory.
    """
    
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    MONGO_URI = os.getenv('MONGO_URI')
    DB_NAME = os.getenv('DB_NAME')
    WAIFU_IT_TOKEN = os.getenv('WAIFU_IT_TOKEN')
    
    @classmethod
    def validate(cls) -> None:
        """Validates presence of all required environment variables
        
        Raises:
            ValueError: If any required environment variable is missing
            
        Example:
            Config.validate()  # Validates all required variables
        """
        required_vars = {
            'DISCORD_TOKEN': cls.DISCORD_TOKEN,
            'MONGO_URI': cls.MONGO_URI,
            'DB_NAME': cls.DB_NAME,
            'WAIFU_IT_TOKEN': cls.WAIFU_IT_TOKEN
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")