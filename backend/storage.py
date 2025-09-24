import os
from supabase import create_client, Client


def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")  # Use service role key
    if not url or not key:
        raise RuntimeError("Supabase credentials not configured")
    print(f"Initializing Supabase client with URL: {url}")
    return create_client(url, key)


