"""Usage: python make_admin.py <username>"""
import sys

from app import app, db
from models import User


def make_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found.")
            sys.exit(1)
        user.is_admin = True
        db.session.commit()
        print(f"'{username}' is now admin.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username>")
        sys.exit(1)
    make_admin(sys.argv[1])
