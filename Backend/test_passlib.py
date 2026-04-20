from passlib.context import CryptContext
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("testpassword")
    print(f"Hashed: {hashed}")
    print(f"Verify: {pwd_context.verify('testpassword', hashed)}")
except Exception as e:
    import traceback
    traceback.print_exc()
