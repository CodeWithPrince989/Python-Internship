import string
import secrets

def generate_password(length=16):
    # Combine lowercase, uppercase, digits, and special punctuation symbols
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Securely pick characters and join them together
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Generate and print a random secure password
print(generate_password())