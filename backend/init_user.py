from database import init_db, create_user

init_db()  # make sure tables exist

user = create_user(
    username="othman",
    email="othman@email.com",
    password="123456",
    name="Othman Salahi"
)

print(user)