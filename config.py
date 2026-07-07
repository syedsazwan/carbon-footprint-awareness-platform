import os
import logging

# Secret key for JWT signing
JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-eco-hub-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CarbonPlatform")
