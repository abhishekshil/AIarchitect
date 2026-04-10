"""Local password hashing — replace with Argon2 or delegated auth in enterprise setups."""

import bcrypt


class BcryptPasswordHasher:
    """bcrypt has a 72-byte password limit; longer passwords are truncated by bcrypt."""

    def hash(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                password_hash.encode("ascii"),
            )
        except ValueError:
            return False
