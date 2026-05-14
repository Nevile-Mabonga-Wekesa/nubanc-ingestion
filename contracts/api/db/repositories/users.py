from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """
    User repository for async database operations.
    
    All timestamps use timezone-aware UTC for consistency
    and Python 3.12+ compatibility.
    """

    @staticmethod
    async def get_by_id(conn, user_id: str) -> dict:
        """
        Retrieve user by ID.
        
        Args:
            conn: Async database connection
            user_id: User identifier
            
        Returns:
            User record dict or None if not found
        """
        return await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )

    @staticmethod
    async def activate_user(conn, user_id: str) -> None:
        """
        Activate user account and record activation timestamp.
        
        Args:
            conn: Async database connection
            user_id: User identifier to activate
        """
        activated_at = datetime.now(timezone.utc)
        
        await conn.execute(
            """
            UPDATE users
            SET status = 'ACTIVE',
                activated_at = $2
            WHERE id = $1
            """,
            user_id,
            activated_at
        )
        
        logger.info(
            "User activated",
            extra={
                "user_id": user_id,
                "activated_at": activated_at.isoformat()
            }
        )
