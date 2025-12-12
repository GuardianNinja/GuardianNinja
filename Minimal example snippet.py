import os
admin_secret = os.getenv("ADMIN_SECRET")
if not admin_secret:
    raise RuntimeError("ADMIN_SECRET not set")
