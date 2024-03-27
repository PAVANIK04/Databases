import secrets

secret_key = secrets.token_hex(16)
print("Generated Secret Key:", secret_key)