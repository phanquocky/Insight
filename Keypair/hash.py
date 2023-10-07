import hashlib

def sha256_hash(message):
    sha256_hasher = hashlib.sha256()
    sha256_hasher.update(message)
    hashed_message = sha256_hasher.hexdigest()
    return hashed_message

def main():
    message = b"Hello, I am Hieu!"

    # Hash the message using SHA-256
    hashed_message = sha256_hash(message)

    print(f"Original Message: {message.decode()}")
    print(f"Hashed Message (SHA-256): {hashed_message}")

if __name__ == "__main__":
    main()
