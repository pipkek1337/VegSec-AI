import time
import bcrypt
import hashlib
import os
import sqlite3
import imghdr
from db_utils import (
    DATABASE, username_exists, email_exists, save_user, get_user_by_username,
    get_user_by_email, get_verification_code, mark_account_verified,
    delete_verification_code, save_reset_token, get_reset_token,
    update_password, save_image_cache
)
from email_utils import (
    is_valid_email, send_verification_email, generate_verification_code,
    generate_reset_token, send_password_reset_email
)
from vegsecai_model import query_ai as model_query_ai

# Rate limiting data structures
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 15 * 60  # 15 minutes in seconds
IMAGE_DIR = 'images'

# Function declarations
# def check_rate_limit(username: str, ip_address: str) -> tuple[bool, str]: ...
# def login(username: str, password: str, ip_address: str) -> tuple[bool, str]: ...
# def verify_account(email: str, verification_code: str) -> tuple[bool, str]: ...
# def forgot_password(email: str) -> tuple[bool, str]: ...
# def reset_password(username: str, reset_token: str, new_password: str) -> tuple[bool, str]: ...
# def is_valid_image(image_data: bytes) -> bool: ...
# def handle_client(client_socket, client_address, semaphore): ...

def check_rate_limit(username, ip_address):
    """Enforce rate limiting for login attempts"""
    current_time = time.time()
    key = f"{username}:{ip_address}"

    if key in login_attempts:
        attempts, lockout_time = login_attempts[key]

        # Check if user is in lockout period
        if lockout_time > 0 and current_time < lockout_time:
            remaining = int(lockout_time - current_time)
            return False, f"Too many failed attempts. Try again in {remaining} seconds."

        # Reset if lockout period has passed
        if lockout_time > 0 and current_time >= lockout_time:
            login_attempts[key] = (0, 0)

        # Increment attempt counter
        login_attempts[key] = (attempts + 1, lockout_time)

        # Check if max attempts reached
        if attempts + 1 >= MAX_ATTEMPTS:
            lockout_until = current_time + LOCKOUT_TIME
            login_attempts[key] = (attempts + 1, lockout_until)
            return False, f"Too many failed attempts. Account locked for {LOCKOUT_TIME // 60} minutes."
    else:
        # First attempt
        login_attempts[key] = (1, 0)

    return True, "Rate limit check passed"


def login(username, password, ip_address):
    """Authenticate user login"""
    # Check rate limiting
    allowed, message = check_rate_limit(username, ip_address)
    if not allowed:
        return False, message

    user_data = get_user_by_username(username)

    if not user_data:
        print(f"[Server] Login failed for username: {username} - User not found")
        return False, "Login failed"

    password_hash, verified, _ = user_data

    # Check if email is verified
    if not verified:
        return False, "Account not verified. Please check your email for verification code."

    # Verify password using bcrypt
    if bcrypt.checkpw(password.encode(), password_hash.encode()):
        print(f"[Server] Login successful for username: {username}")
        # Reset failed attempts on successful login
        key = f"{username}:{ip_address}"
        if key in login_attempts:
            login_attempts[key] = (0, 0)
        return True, "Login successful"
    else:
        print(f"[Server] Login failed for username: {username} - Password mismatch")
        return False, "Login failed"


def verify_account(email, verification_code):
    """Verify an account using the provided verification code"""
    # Get the stored verification code
    verification_data = get_verification_code(email)

    if not verification_data:
        return False, "Verification code not found"

    stored_code, expiry = verification_data
    current_time = int(time.time())

    if current_time > expiry:
        return False, "Verification code has expired"

    if verification_code != stored_code:
        return False, "Incorrect verification code"

    # Mark user as verified
    mark_account_verified(email)

    # Remove the verification code
    delete_verification_code(email)

    return True, "Account successfully verified"


def forgot_password(email):
    """Generate a password reset token and send it via email"""
    # Check if email exists
    user_data = get_user_by_email(email)

    if not user_data:
        return False, "Email not found"

    username = user_data[0]
    reset_token = generate_reset_token()
    expiry_time = int(time.time()) + 30 * 60  # 30 minutes

    # Store the reset token in the database
    save_reset_token(username, reset_token, expiry_time)

    # Send the reset email
    if send_password_reset_email(email, reset_token):
        return True, f"Password reset token sent to {email}"
    else:
        return False, "Failed to send reset email"


def reset_password(username, reset_token, new_password):
    """Reset a user's password using the provided reset token"""
    token_data = get_reset_token(username)

    if not token_data:
        return False, "Username not found"

    stored_token, expiry = token_data
    current_time = int(time.time())

    if not stored_token or stored_token != reset_token:
        return False, "Invalid reset token"

    if current_time > expiry:
        return False, "Reset token has expired"

    # Hash the new password with bcrypt
    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    # Update the password and clear the reset token
    update_password(username, hashed_pw)

    return True, "Password successfully reset"


def is_valid_image(image_data):
    """Validate that the uploaded file is a valid image (JPEG or PNG)"""
    # Save to a temporary file for validation
    temp_path = os.path.join(IMAGE_DIR, "temp_validation")
    with open(temp_path, 'wb') as f:
        f.write(image_data)

    # Use imghdr to detect file type
    img_type = imghdr.what(temp_path)

    # Clean up temporary file
    os.remove(temp_path)

    # Check if it's a valid image type
    valid_types = ['jpeg', 'jpg', 'png']
    is_valid = img_type in valid_types

    return is_valid

def get_user_history(username):
    """Get the analysis history for a user"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, image_hash, question, answer 
        FROM image_cache 
        WHERE username = ? 
        ORDER BY timestamp DESC
    """, (username,))
    history = c.fetchall()
    conn.close()
    return history

def handle_client(client_socket, client_address, semaphore):
    with semaphore:
        try:
            print(f"[Server] Connection from {client_address} established.")
            request_type = client_socket.recv(1024).decode().strip()

            if request_type == "signup":
                # Receive signup details
                username = client_socket.recv(1024).decode().strip()
                password = client_socket.recv(1024).decode().strip()
                email = client_socket.recv(1024).decode().strip()

                if not is_valid_email(email):
                    client_socket.send("Signup failed: Invalid email".encode())
                    return

                # Check if username already exists
                if username_exists(username):
                    client_socket.send("Signup failed: Username already exists".encode())
                    return

                # Check if email already exists
                if email_exists(email):
                    client_socket.send("Signup failed: Email already in use".encode())
                    return

                # Generate and send verification code
                verification_code = generate_verification_code()
                send_verification_email(email, verification_code)
                print("[Server] Sent verification email, waiting for client verification input...")
                # Inform the client to enter the code
                client_socket.send("Verification code sent. Please enter the verification code:".encode())

                # Wait for the client's verification code
                client_verification = client_socket.recv(1024).decode().strip()

                # Hash password with bcrypt
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                # Save user to database
                save_user(username, hashed_pw, email, 0)

                # Verify the account
                verified, message = verify_account(email, client_verification)
                if verified:
                    print(f"[Server] Signup completed for username: {username}")
                    client_socket.send("Signup successful".encode())
                else:
                    client_socket.send(f"Signup failed: {message}".encode())

            elif request_type == "login":
                username = client_socket.recv(1024).decode().strip()
                password = client_socket.recv(1024).decode().strip()

                success, message = login(username, password, client_address[0])
                client_socket.send(message.encode())

                if success:
                    print(f"[Server] User {username} logged in successfully")
                    while True:
                        try:
                            length_bytes = client_socket.recv(4)
                            if not length_bytes or len(length_bytes) == 0:
                                break

                            if length_bytes == b'#bye':
                                print(f"[Server] User {username} logged out")
                                break

                            if len(length_bytes) != 4:
                                raise ValueError("Invalid length bytes received")

                            image_length = int.from_bytes(length_bytes, 'big')
                            image_data = b''

                            while len(image_data) < image_length:
                                chunk = client_socket.recv(min(1024, image_length - len(image_data)))
                                if not chunk:
                                    raise ValueError("Connection lost while receiving image data")
                                image_data += chunk

                            image_hash = client_socket.recv(1024).decode().strip()
                            question = client_socket.recv(1024).decode().strip()

                            # Validate image hash
                            calculated_hash = hashlib.sha256(image_data).hexdigest()
                            if calculated_hash != image_hash:
                                client_socket.send("Image hash mismatch.".encode())
                                continue

                            # Validate image type
                            if not is_valid_image(image_data):
                                client_socket.send("Invalid image format. Only JPEG and PNG are supported.".encode())
                                continue

                            image_file_path = os.path.join(IMAGE_DIR, f"{calculated_hash}.jpg")
                            with open(image_file_path, 'wb') as f:
                                f.write(image_data)

                            # Use the actual AI model query function from vegsecai_model.py
                            answer = model_query_ai(image_file_path, question)

                            # Cache the image and answer
                            save_image_cache(image_hash, username, question, answer, image_file_path)

                            client_socket.send(answer.encode())
                        except Exception as e:
                            print(f"[Server] Error processing image: {e}")
                            client_socket.send(f"Error: {str(e)}".encode())
                            break

            elif request_type == "forgot_password":
                email = client_socket.recv(1024).decode().strip()
                success, message = forgot_password(email)
                client_socket.send(message.encode())

                if success:
                    # Wait for user to enter reset information
                    username = client_socket.recv(1024).decode().strip()
                    reset_token = client_socket.recv(1024).decode().strip()
                    new_password = client_socket.recv(1024).decode().strip()

                    reset_success, reset_message = reset_password(username, reset_token, new_password)
                    client_socket.send(reset_message.encode())


            elif request_type == "get_history":

                username = client_socket.recv(1024).decode().strip()

                # Get history entries with timestamp

                conn = sqlite3.connect(DATABASE)

                c = conn.cursor()

                c.execute("""

                                SELECT datetime(timestamp, 'unixepoch', 'localtime') as formatted_timestamp, 

                                       image_hash, question, answer 

                                FROM image_cache 

                                WHERE username = ? 

                                ORDER BY timestamp DESC

                            """, (username,))

                history = c.fetchall()

                conn.close()

                # Send history entries

                if not history:

                    client_socket.send("END_HISTORY".encode())

                else:

                    if not history:
                        client_socket.send("END_HISTORY".encode())
                    else:
                        # Send each entry with END_HISTORY separator
                        for entry in history:
                            timestamp, image_hash, question, answer = entry
                            # Handle None values
                            answer = answer or "No answer available"  # Add default if None
                            entry_data = f"{timestamp}|{image_hash}|{question.replace('|', '&#124;')}|{answer.replace('|', '&#124;')}"
                            client_socket.send(f"{entry_data}END_HISTORY".encode())

            else:
                client_socket.send("Invalid request type".encode())

        except Exception as e:
            print(f"[Server] Error handling client: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            print(f"[Server] Connection from {client_address} closed.")