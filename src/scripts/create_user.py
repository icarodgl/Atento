import getpass

from app.database import SessionLocal
from app.models.models import User
from app.security import hash_password

username = input("Usuário: ").strip()
password = getpass.getpass("Senha: ")
is_admin = input("É administrador (dashboard)? s/n: ").strip().lower() == "s"

with SessionLocal() as db:
    db.add(User(username=username, hashed_password=hash_password(password), is_admin=is_admin))
    db.commit()
print("Usuário criado.")