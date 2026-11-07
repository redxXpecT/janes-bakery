from getpass import getpass

from app.database import SessionLocal
from app.models.administrator import Administrator
from app.services.security import hash_password


def create_admin():
    db = SessionLocal()

    try:
        full_name = input("Administrator full name: ").strip()
        email = input("Administrator email: ").strip().lower() 
        phone_number = input("Administrator phone number: ").strip()
        password = getpass("Administrator password: ")
        confirm_password = getpass("Confirm password: ")

        if not all([full_name, email, phone_number, password]):
            print("All fields are required.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        existing_admin = db.query(Administrator).filter(
            Administrator.email == email
        ).first()

        if existing_admin:
            print("An administrator with this email already exists.")
            return

        admin = Administrator(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=hash_password(password),
            role="ADMIN"
        )

        db.add(admin)
        db.commit()

        print("Administrator account created successfully.")

    except Exception as error:
        db.rollback()
        print("Could not create administrator:", error)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()