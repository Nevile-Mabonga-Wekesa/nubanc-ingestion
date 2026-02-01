from datetime import datetime

class UserRepository:

    @staticmethod
    async def get_by_id(conn, user_id: str):
        return await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )

    @staticmethod
    async def activate_user(conn, user_id: str):
        await conn.execute(
            """
            UPDATE users
            SET status = 'ACTIVE',
                activated_at = $2
            WHERE id = $1
            """,
            user_id,
            datetime.utcnow()
        )
