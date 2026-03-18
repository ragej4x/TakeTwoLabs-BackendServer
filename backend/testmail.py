import socket

try:
    print(socket.gethostbyname("db.vsdsygxnpexfjfjadolq.supabase.co"))
except Exception as e:
    print(f"DNS failed: {e}")