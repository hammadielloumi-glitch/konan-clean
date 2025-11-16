import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.security import hash_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.user import User, PlanType  # noqa: E402

TEST_EMAIL = "test@konan.ai"
TEST_PASSWORD = "Test123!"
TEST_NAME = "Test User"
TEST_ROLE = "standard"


def ensure_role(user: User) -> None:
    """Set optional attributes safely."""
    if hasattr(user, "plan") and user.plan is None:
        user.plan = PlanType.FREE
if hasattr(user, "role"):
    setattr(user, "role", TEST_ROLE)


def main() -> None:
    session = SessionLocal()
    try:
        existing = session.query(User).filter(User.email == TEST_EMAIL).first()
        if existing:
            print(f"✅ Utilisateur déjà présent : {TEST_EMAIL}")
            return

        user = User(
            email=TEST_EMAIL,
            full_name=TEST_NAME,
            hashed_password=hash_password(TEST_PASSWORD),
        )
        ensure_role(user)

        session.add(user)
        session.commit()
        print("🎉 Utilisateur de test créé avec succès !")
        print(f"   Email    : {TEST_EMAIL}")
        print(f"   Password : {TEST_PASSWORD}")
        if hasattr(user, "role"):
            print(f"   Rôle     : {TEST_ROLE}")
        print("Vous pouvez maintenant vous authentifier via l'app mobile.")
    except Exception as exc:  # pragma: no cover
        session.rollback()
        raise exc
    finally:
        session.close()


if __name__ == "__main__":
    main()
