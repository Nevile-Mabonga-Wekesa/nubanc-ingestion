async def emit_user_activated(conn, *, user_id: str, org_id: str, actor: str):
    await conn.execute(
        """
        INSERT INTO audit_events (
            event_type,
            entity_type,
            entity_id,
            org_id,
            actor
        )
        VALUES ('USER_ACTIVATED', 'USER', $1, $2, $3)
        """,
        user_id,
        org_id,
        actor
    )
