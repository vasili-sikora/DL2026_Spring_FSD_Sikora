import argparse
import sys

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.models.user import UserCreate
from app.backend.repositories.user_repo import UserRepo
from app.backend.services.exceptions import AuthenticationError, UserNotFoundError
from app.backend.services.user_service import UserService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Promote an existing user to admin or create a new admin user "
            "when a password is provided."
        )
    )
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument(
        "--password",
        help="Create a new admin with this password if the user does not exist",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = UserService(UserRepo(SQLiteConnection()))

    try:
        user = service.promote_user_to_admin(args.email)
        print(f"User {user['email']} promoted to admin (id={user['id']}).")
        return 0
    except UserNotFoundError:
        if not args.password:
            print(
                "User not found. Pass --password to create a new admin user.",
                file=sys.stderr,
            )
            return 1
    except AuthenticationError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        user = service.create_admin_user(
            UserCreate(email=args.email, password=args.password)
        )
    except AuthenticationError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Admin user {user['email']} created (id={user['id']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
