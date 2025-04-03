import socket
import ssl
import threading
import time
import signal
import sys
import os
from dotenv import load_dotenv
from generate_cert import generate_self_signed_cert
from auth_utils import handle_client
from db_utils import init_db

load_dotenv()

HOST = "0.0.0.0"
PORT = 12378
MAX_THREADS = 5
IMAGE_DIR = 'images'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

semaphore = threading.Semaphore(MAX_THREADS)

# Global server socket for graceful shutdown
server_socket = None
# Flag to indicate server shutdown
shutdown_flag = False

# Function declarations:
# def signal_handler(sig: int, frame) -> None
# def start_server() -> None

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown"""
    global shutdown_flag
    print("\n[Server] Shutting down gracefully...")
    shutdown_flag = True

    # Close the server socket
    if server_socket:
        try:
            server_socket.close()
        except:
            pass

    # Wait a moment for threads to finish
    time.sleep(1)
    print("[Server] Server shutdown complete.")
    sys.exit(0)


def start_server():
    global server_socket

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    init_db()

    # Generate or load the certificate
    cert_file, key_file = generate_self_signed_cert()

    # Set up SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket = context.wrap_socket(server_socket, server_side=True)

    print(f"[Server] Listening on {HOST}:{PORT} with SSL...")

    client_threads = []

    try:
        while not shutdown_flag:
            try:
                # Set a timeout so we can check the shutdown flag periodically
                server_socket.settimeout(1.0)
                try:
                    client_socket, client_address = server_socket.accept()
                    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, semaphore))
                    client_thread.daemon = True  # Set as daemon so it won't block shutdown
                    client_thread.start()
                    client_threads.append(client_thread)

                    # Clean up completed threads
                    client_threads = [t for t in client_threads if t.is_alive()]
                except socket.timeout:
                    continue
            except Exception as e:
                if not shutdown_flag:
                    print(f"[Server] Error accepting connections: {e}")
                    time.sleep(1)
    finally:
        # Clean shutdown
        print("[Server] Closing server socket...")
        if server_socket:
            server_socket.close()

        # Wait for client threads to finish (with timeout)
        print("[Server] Waiting for client connections to close...")
        for t in client_threads:
            t.join(timeout=2.0)

        print("[Server] Server shutdown complete.")


if __name__ == '__main__':
    start_server()
