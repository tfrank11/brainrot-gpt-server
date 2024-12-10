
from supabase import Client


def get_uid_from_token(supabase: Client, token: str) -> str:
    user = supabase.auth.get_user(token)
    if not user:
        raise ValueError("Invalid or expired token")
    return user.user.id
