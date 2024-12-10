from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
from datetime import datetime

class Database:
    """Database management class for user data.
    
    This class handles all database operations for the Discord bot, including user data
    management, experience tracking, and economy features.
    
    Attributes:
        client (AsyncIOMotorClient): MongoDB client instance
        db (AsyncIOMotorDatabase): Reference to the bot's database
        mongo_uri (str): MongoDB connection URI from env vars
        db_name (str): Name of the database to use
        
    Note:
        Requires MONGO_URI and DB_NAME environment variables to be set.
        Falls back to defaults if not provided.
    """
    
    def __init__(self) -> None:
        """Initialize database connection settings."""
        load_dotenv()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.mongo_uri: str = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.db_name: str = os.getenv('DB_NAME', 'discord_bot')

    async def connect(self) -> None:
        """Create database connection and set up indexes.
        
        Creates a compound index on user_id and guild_id to ensure
        unique user entries per guild.
        """
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        await self.db.users.create_index([("user_id", 1), ("guild_id", 1)], unique=True)

    async def _get_user_query(self, user_id: int, guild_id: int) -> Dict[str, int]:
        """Helper method to generate the standard user query.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            
        Returns:
            Dict containing the query parameters
        """
        return {"user_id": user_id, "guild_id": guild_id}

    async def get_user(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            
        Returns:
            User document without MongoDB _id field, or None if not found
        """
        query = await self._get_user_query(user_id, guild_id)
        return await self.db.users.find_one(query, {'_id': 0})

    async def create_user(self, user_id: int, guild_id: int) -> None:
        """Create new user entry in database.
        
        Creates a new user document with default values if one doesn't exist.
        Uses upsert to prevent duplicate entries.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
        """
        query = await self._get_user_query(user_id, guild_id)
        default_data = {
            **query,
            "exp": 0,
            "level": 1,
            "money": 0,
            "last_daily": None
        }
        await self.db.users.update_one(
            query,
            {"$setOnInsert": default_data},
            upsert=True
        )

    async def update_exp(self, user_id: int, guild_id: int, exp: int) -> Dict[str, Any]:
        """Update user experience and calculate new level.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            exp: New total experience points
            
        Returns:
            Updated user document
            
        Note:
            Level calculation uses a 1.5x multiplier for each level
        """
        level = 1
        exp_needed = 100
        
        while exp >= exp_needed:
            level += 1
            exp_needed = int(exp_needed * 1.5)
        
        query = await self._get_user_query(user_id, guild_id)
        await self.db.users.update_one(
            query,
            {"$set": {"exp": exp, "level": level}}
        )
        
        return await self.get_user(user_id, guild_id)

    async def add_money(self, user_id: int, guild_id: int, amount: int) -> int:
        """Modify user's money balance.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            amount: Amount to add (positive) or subtract (negative)
            
        Returns:
            New money balance after modification
        """
        query = await self._get_user_query(user_id, guild_id)
        result = await self.db.users.find_one_and_update(
            query,
            {"$inc": {"money": amount}},
            return_document=True
        )
        return result["money"]

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get server experience leaderboard.
        
        Args:
            guild_id: Discord guild ID
            limit: Maximum number of users to return (default: 10)
            
        Returns:
            List of user documents sorted by experience (highest first)
        """
        cursor = self.db.users.find(
            {"guild_id": guild_id},
            {'_id': 0}
        ).sort("exp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)

    async def update_daily_timestamp(self, user_id: int, guild_id: int) -> None:
        """Update user's last daily claim timestamp.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
        """
        query = {"user_id": user_id, "guild_id": guild_id}
        now = datetime.utcnow().isoformat()
        await self.db.users.update_one(
            query,
            {"$set": {"last_daily": now}}
        )