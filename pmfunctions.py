import psycopg
import os
from dotenv import load_dotenv
import cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from base64 import urlsafe_b64encode, urlsafe_b64decode

# Load environment variables from the .env file
load_dotenv()

# Get the database credentials from the environment variables
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

class PasswordManager:
    def __init__(self, master_password, salt=None):
        # Setting the backend to handle cryptographic operations, defaulting to OpenSSL
        self.backend = default_backend()
        
        # Use provided salt or generate a new one
        self.salt = salt or os.urandom(16)

        # Generate a key from the master password
        self.encryption_key = self.derive_key(master_password, self.salt)
    
    def derive_key(self, master_password, salt):
        # Derive a key from the salted master password
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )

        # Return the derived key
        return kdf.derive(master_password.encode())
    
    def encrypt(self, plaintext):
        # Generate a random initialization vector to ensure that the same plaintext
        # does not encrypt the same ciphertext
        iv = os.urandom(16)

        # Create a cipher object using the encryption key, the AES algo and the CFB mode
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CFB(iv), backend=self.backend)

        # Create an encryptor object
        encryptor = cipher.encryptor()

        # Encrypt the padded data
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

        # Return the initialization vector and the ciphertext
        return urlsafe_b64encode(iv + ciphertext).decode('utf-8')
    
    def decrypt(self, encrypted_text):
        # Decode the encoded text
        decoded_text = urlsafe_b64decode(encrypted_text)

        # Extract the iv (first 16 bytes)
        iv = decoded_text[:16]

        # Extract the ciphertext (remaining bytes after the iv)
        ciphertext = decoded_text[16:]

        # Create a cipher object using the encryption key, the AES algo and the CFB mode
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CFB(iv), backend=self.backend)

        # Create a decryptor object
        decryptor = cipher.decryptor()

        # Unpad the plaintext
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Decode the plaintext to a string and return it
        return plaintext.decode('utf-8')
    
    def add_password(self, site_name, username, password):
        # Connect to the database
        conn = psycopg.connect(dbname = 'passwordmanager',user=db_user, password=db_password, host=db_host, port=db_port)

        # Set the autocommit to True
        conn.autocommit = True

        # Create a cursor to execure queries
        cursor = conn.cursor()

        # Encrypt the password
        encrypted_password = self.encrypt(password)

        # Insert the password into the table while using parameterized queries to prevent SQL injections
        query = '''INSERT INTO passwords (username,password,site_name)
                VALUES (%s,%s,%s)'''
        data = (username,encrypted_password, site_name)
        cursor.execute(query,data)

        # Confirm the insertion of the password
        print("Password added successfully")

        # Close the cursor and the connection to the database
        cursor.close()
        conn.close()

    
    def retrieve_password(self, site_name):
        # Connect to the database
        conn = psycopg.connect(dbname='passwordmanager',user=db_user, password=db_password, host=db_host, port=db_port)

        # Set the autocommit to True
        conn.autocommit = True

        # Create a cursor to execure queries
        cursor = conn.cursor()

        # Select the password from the table using the site name while using parameterized queries to prevent SQL injections
        query = '''SELECT password FROM passwords WHERE site_name = %s'''
        data = (site_name, )
        cursor.execute(query,data)

        # Fetch the password
        password = cursor.fetchone()[0]

        # Decrypt the password
        decrypted_password = self.decrypt(password)

        # Confirm the retrival of the password
        print("Password retrieved successfully !! = {}".format(decrypted_password))

        # Close the cursor and the connection to the database
        cursor.close()
        conn.close()

    def delete_password(self, site_name):
        # Connect to the database
        conn = psycopg.connect(dbname='passwordmanager',user=db_user, password=db_password, host=db_host, port=db_port)

        # Set autocommit to True
        conn.autocommit = True

        # Create a cursor to execure queries
        cursor = conn.cursor()

        # Delete the password from the table 
        # while using parameterized queries to prevent SQL injections
        query = '''DELETE FROM passwords WHERE site_name = %s'''
        data = (site_name, )
        cursor.execute(query, data)

        # Confirm the deletion of the password
        print("Password deleted successfully")

        # Close the cursor and the connection to the database
        cursor.close()
        conn.close()