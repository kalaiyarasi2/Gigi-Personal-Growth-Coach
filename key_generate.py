#pip install google-generativeai chromadb sentence-transformers pydantic sqlalchemy redis cryptography
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Use this value