import secrets

# Generate a secure random token
token = secrets.token_hex(16)  # 16 bytes (32 characters in hexadecimal)
print("Generated Token:", token)
