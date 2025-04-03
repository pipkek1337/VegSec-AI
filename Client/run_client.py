import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import socket
import ssl
import hashlib
import threading
import time
from getpass import getpass
import io
import queue
from camera_window import *
from functools import partial


# Constants
BACKGROUND_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#4a7abc"
SECONDARY_COLOR = "#2a4d7f"
TEXT_COLOR = "#333333"
BUTTON_TEXT_COLOR = "#ffffff"
FONT_FAMILY = "Helvetica"
LOGO_PATH = "logo.png"  # Create a logo file or replace this

# Main class initialization
# def __init__(self) -> None

# UI related functions
# def show_login_frame(self) -> None
# def show_username_password_login(self) -> None
# def show_face_id_login(self) -> None
# def show_signup_frame(self) -> None
# def show_forgot_password_frame(self) -> None
# def show_main_app(self) -> None
# def show_history_view(self) -> None

# Server connection function
# def connect_to_server(self) -> bool

# Authentication functions
# def process_login(self) -> None
# def _process_login_thread(self, username: str, password: str) -> None
# def process_signup(self) -> None
# def _process_signup_thread(self, username: str, email: str, password: str) -> None
# def _show_verification_form(self) -> None
# def verify_signup_code(self) -> None
# def _verify_signup_code_thread(self, verification_code: str) -> None
# def send_reset_token(self) -> None
# def _send_reset_token_thread(self, email: str) -> None
# def process_reset_password(self) -> None
# def _process_reset_password_thread(self, username: str, reset_token: str, new_password: str) -> None

# Image handling functions
# def upload_image(self) -> None
# def display_image(self, image_path: str) -> None
# def send_image_to_server(self) -> None
# def _send_image_to_server_thread(self, image_path: str, question: str) -> None

# Session management
# def logout(self) -> None

class VegSecAIApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("VegSecAI - Vegetable Recognition System")
        self.geometry("800x600")
        self.configure(bg=BACKGROUND_COLOR)
        self.resizable(True, True)

        # Application state
        self.client_socket = None
        self.is_logged_in = False
        self.current_user = None
        self.current_image = None
        self.current_image_path = None

        # Create and show the login frame
        self.show_login_frame()

        self.history_data = []  # Store history entries locally
        self.history_frame = None  # Reference to history view frame

    def show_login_frame(self):
        # Clear any existing frames
        for widget in self.winfo_children():
            widget.destroy()

        # Create login frame
        login_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        login_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Add logo if available
        try:
            logo_img = Image.open(LOGO_PATH)
            logo_img = logo_img.resize((200, 200), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(login_frame, image=logo_photo, bg=BACKGROUND_COLOR)
            logo_label.image = logo_photo
            logo_label.pack(pady=20)
        except:
            # If logo is not available, show text header
            header_label = tk.Label(
                login_frame,
                text="VegSecAI",
                font=(FONT_FAMILY, 30, "bold"),
                fg=PRIMARY_COLOR,
                bg=BACKGROUND_COLOR
            )
            header_label.pack(pady=20)

        # Welcome text
        welcome_label = tk.Label(
            login_frame,
            text="Welcome to VegSecAI - Vegetable Recognition System",
            font=(FONT_FAMILY, 14),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        welcome_label.pack(pady=10)

        description_label = tk.Label(
            login_frame,
            text="Identify vegetables with AI-powered recognition",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        description_label.pack(pady=5)

        # Login options
        options_frame = tk.Frame(login_frame, bg=BACKGROUND_COLOR)
        options_frame.pack(pady=30)

        # Username & Password Login Button
        login_button = tk.Button(
            options_frame,
            text="Login with Username & Password",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=20,
            pady=10,
            command=self.show_username_password_login
        )
        login_button.grid(row=0, column=0, padx=10, pady=10)

        # Signup Button
        signup_button = tk.Button(
            login_frame,
            text="Create New Account",
            font=(FONT_FAMILY, 12),
            bg=SECONDARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=20,
            pady=10,
            command=self.show_signup_frame
        )
        signup_button.pack(pady=10)

        # Forgot Password Link
        forgot_password_link = tk.Label(
            login_frame,
            text="Forgot Password?",
            font=(FONT_FAMILY, 10, "underline"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR,
            cursor="hand2"
        )
        forgot_password_link.pack(pady=5)
        forgot_password_link.bind("<Button-1>", lambda e: self.show_forgot_password_frame())

        # Server configuration
        server_frame = tk.Frame(login_frame, bg=BACKGROUND_COLOR)
        server_frame.pack(side="bottom", fill="x", pady=20)

        server_label = tk.Label(
            server_frame,
            text="Server IP:",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        server_label.pack(side="left", padx=5)

        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        server_entry = tk.Entry(
            server_frame,
            textvariable=self.server_ip_var,
            font=(FONT_FAMILY, 10),
            width=15
        )
        server_entry.pack(side="left", padx=5)

    def show_username_password_login(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        login_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Back button
        back_button = tk.Button(
            login_frame,
            text="← Back",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=PRIMARY_COLOR,
            bd=0,
            command=self.show_login_frame
        )
        back_button.pack(anchor="nw", pady=10)

        # Login header
        header_label = tk.Label(
            login_frame,
            text="Login with Username & Password",
            font=(FONT_FAMILY, 18, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=20)

        # Login form
        form_frame = tk.Frame(login_frame, bg=BACKGROUND_COLOR)
        form_frame.pack(pady=20)

        # Username
        username_label = tk.Label(
            form_frame,
            text="Username:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            form_frame,
            textvariable=self.username_var,
            font=(FONT_FAMILY, 12),
            width=25
        )
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        password_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            form_frame,
            textvariable=self.password_var,
            font=(FONT_FAMILY, 12),
            width=25,
            show="*"
        )
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Login button
        login_button = tk.Button(
            login_frame,
            text="Login",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=30,
            pady=10,
            command=self.process_login
        )
        login_button.pack(pady=20)

        # Status message
        self.login_status_var = tk.StringVar()
        login_status_label = tk.Label(
            login_frame,
            textvariable=self.login_status_var,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg="red"
        )
        login_status_label.pack(pady=10)

    def show_history_view(self):
        """Display the user's history of image analyses using threading"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create history frame
        self.history_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        self.history_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Back button
        back_button = tk.Button(
            self.history_frame,
            text="← Back",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=PRIMARY_COLOR,
            bd=0,
            command=self.show_main_app
        )
        back_button.pack(anchor="nw", pady=10)

        # Header
        header_label = tk.Label(
            self.history_frame,
            text="Analysis History",
            font=(FONT_FAMILY, 18, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=20)

        # Show loading indicator
        self.loading_label = tk.Label(
            self.history_frame,
            text="Loading history...",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        self.loading_label.pack(pady=20)

        # Start background thread for fetching history
        self.history_queue = queue.Queue()
        self.history_thread = threading.Thread(
            target=self.fetch_history_thread,
            daemon=True
        )
        self.history_thread.start()

        # Start periodic check for history
        self.after(100, self.check_history_thread)

    def fetch_history_thread(self):
        """Background thread to fetch history from server"""
        try:
            # Establish a new socket connection
            history_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            history_socket = ssl.wrap_socket(history_socket)
            history_socket.connect((self.server_ip_var.get(), 12378))

            # Send get_history request
            history_socket.send("get_history".encode())
            history_socket.send(self.current_user.encode())

            # Receive history entries with proper buffering
            history_data = []
            buffer = ""
            delimiter = "END_HISTORY"
            delimiter_length = len(delimiter)

            while True:
                try:
                    chunk = history_socket.recv(1024).decode()
                    if not chunk:
                        break

                    buffer += chunk

                    # Process all complete entries in buffer
                    while delimiter in buffer:
                        delimiter_pos = buffer.find(delimiter)
                        entry = buffer[:delimiter_pos].strip()
                        buffer = buffer[delimiter_pos + delimiter_length:]

                        if entry:
                            # Clean and validate entry
                            cleaned_entry = entry.replace('&#124;', '|')
                            if cleaned_entry.count('|') == 3:  # Ensure proper format
                                history_data.append(cleaned_entry)
                            else:
                                print(f"Skipping malformed entry: {cleaned_entry}")

                except socket.error as e:
                    print(f"Socket error receiving history: {e}")
                    break

            # Handle any remaining data in buffer
            if buffer.strip() and buffer.strip() != delimiter:
                print(f"Unexpected trailing data: {buffer}")

            # Put results in queue
            self.history_queue.put(history_data if history_data else "No history found")

        except Exception as e:
            error_msg = f"Failed to fetch history: {str(e)}"
            print(error_msg)
            self.history_queue.put(error_msg)
        finally:
            try:
                history_socket.close()
            except:
                pass
    def check_history_thread(self):
        """Check if history thread has completed"""
        try:
            # Check if queue has data with non-blocking get
            try:
                history_data = self.history_queue.get(block=False)

                # Remove loading label
                if hasattr(self, 'loading_label'):
                    self.loading_label.destroy()

                # Handle error case
                if isinstance(history_data, str) and history_data.startswith("Error"):
                    error_label = tk.Label(
                        self.history_frame,
                        text=history_data,
                        font=(FONT_FAMILY, 12),
                        bg=BACKGROUND_COLOR,
                        fg="red"
                    )
                    error_label.pack(pady=20)
                    return

                # Display history entries
                self.display_history_entries(history_data)

            except queue.Empty:
                # If no data yet, check again soon
                self.after(100, self.check_history_thread)

        except Exception as e:
            # Fallback error handling
            print(f"Error checking history: {e}")
            if hasattr(self, 'loading_label'):
                self.loading_label.config(text=f"Error loading history: {e}", fg="red")

    def display_history_entries(self, history_data):
        """Display the history entries in the history view"""
        # Clear existing history entries except back button
        for widget in self.history_frame.winfo_children():
            if not (isinstance(widget, tk.Button) and widget.cget('text') == "← Back"):
                widget.destroy()

        # Header
        header_label = tk.Label(
            self.history_frame,
            text="Analysis History",
            font=(FONT_FAMILY, 18, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=20)

        # Handle empty history
        if not history_data or (isinstance(history_data, str) and history_data.startswith("No history")):
            no_history_label = tk.Label(
                self.history_frame,
                text="No history found" if isinstance(history_data, str) else history_data,
                font=(FONT_FAMILY, 12),
                bg=BACKGROUND_COLOR,
                fg=TEXT_COLOR
            )
            no_history_label.pack(pady=20)
            return

        # Handle error messages
        if isinstance(history_data, str) and history_data.startswith("Error"):
            error_label = tk.Label(
                self.history_frame,
                text=history_data,
                font=(FONT_FAMILY, 12),
                bg=BACKGROUND_COLOR,
                fg="red"
            )
            error_label.pack(pady=20)
            return

        # Create scrollable frame
        canvas = tk.Canvas(self.history_frame, bg=BACKGROUND_COLOR)
        scrollbar = tk.Scrollbar(self.history_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BACKGROUND_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        # Display each history entry
        for entry in history_data:
            try:
                # Validate entry format
                if not isinstance(entry, str) or entry.count('|') != 3:
                    print(f"Skipping malformed entry: {entry}")
                    continue

                timestamp, image_hash, question, answer = entry.split('|', 3)

                # Create entry frame
                entry_frame = tk.Frame(scrollable_frame, bg=BACKGROUND_COLOR,
                                       highlightbackground=PRIMARY_COLOR,
                                       highlightthickness=1)
                entry_frame.pack(fill="x", padx=10, pady=5)

                # Left side - image preview
                image_frame = tk.Frame(entry_frame, bg=BACKGROUND_COLOR)
                image_frame.pack(side="left", padx=10, pady=5)

                try:
                    image_path = os.path.join("images", f"{image_hash}.jpg")
                    if os.path.exists(image_path):
                        img = Image.open(image_path)
                        img.thumbnail((100, 100), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label = tk.Label(image_frame, image=photo, bg=BACKGROUND_COLOR)
                        img_label.image = photo
                        img_label.pack()
                    else:
                        no_image_label = tk.Label(
                            image_frame,
                            text="[Image not found]",
                            font=(FONT_FAMILY, 8),
                            bg=BACKGROUND_COLOR,
                            fg="gray"
                        )
                        no_image_label.pack()
                except Exception as img_error:
                    print(f"Error loading image: {img_error}")

                # Right side - text info
                text_frame = tk.Frame(entry_frame, bg=BACKGROUND_COLOR)
                text_frame.pack(side="left", fill="x", expand=True)

                # Timestamp
                timestamp_label = tk.Label(
                    text_frame,
                    text=timestamp,
                    font=(FONT_FAMILY, 10),
                    bg=BACKGROUND_COLOR,
                    fg=TEXT_COLOR
                )
                timestamp_label.pack(anchor="w")

                # Question
                question_label = tk.Label(
                    text_frame,
                    text=f"Question: {question}",
                    font=(FONT_FAMILY, 12),
                    bg=BACKGROUND_COLOR,
                    fg=TEXT_COLOR,
                    wraplength=500,
                    justify="left"
                )
                question_label.pack(anchor="w")

                # Answer (handle None/empty answers)
                answer_text = answer if answer and answer.lower() != "none" else "No answer available"
                answer_label = tk.Label(
                    text_frame,
                    text=f"Answer: {answer_text}",
                    font=(FONT_FAMILY, 12),
                    bg=BACKGROUND_COLOR,
                    fg=TEXT_COLOR,
                    wraplength=500,
                    justify="left"
                )
                answer_label.pack(anchor="w")

            except Exception as e:
                print(f"Error displaying history entry: {e}")
    def process_single_entry(self, entry, parent_frame):
        """Helper method to process individual entries"""
        entry_data = entry.split("|")
        if len(entry_data) != 4:
            print(f"Skipping malformed entry: {entry}")
            return

        timestamp, image_hash, question, answer = entry_data

    def show_signup_frame(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        signup_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        signup_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Back button
        back_button = tk.Button(
            signup_frame,
            text="← Back",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=PRIMARY_COLOR,
            bd=0,
            command=self.show_login_frame
        )
        back_button.pack(anchor="nw", pady=10)

        # Signup header
        header_label = tk.Label(
            signup_frame,
            text="Create New Account",
            font=(FONT_FAMILY, 18, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=20)

        # Signup form
        form_frame = tk.Frame(signup_frame, bg=BACKGROUND_COLOR)
        form_frame.pack(pady=20)

        # Username
        username_label = tk.Label(
            form_frame,
            text="Username (2-32 chars):",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.signup_username_var = tk.StringVar()
        username_entry = tk.Entry(
            form_frame,
            textvariable=self.signup_username_var,
            font=(FONT_FAMILY, 12),
            width=25
        )
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Email
        email_label = tk.Label(
            form_frame,
            text="Email:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        email_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.signup_email_var = tk.StringVar()
        email_entry = tk.Entry(
            form_frame,
            textvariable=self.signup_email_var,
            font=(FONT_FAMILY, 12),
            width=25
        )
        email_entry.grid(row=1, column=1, padx=10, pady=10)

        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        password_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.signup_password_var = tk.StringVar()
        password_entry = tk.Entry(
            form_frame,
            textvariable=self.signup_password_var,
            font=(FONT_FAMILY, 12),
            width=25,
            show="*"
        )
        password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Confirm Password
        confirm_password_label = tk.Label(
            form_frame,
            text="Confirm Password:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        confirm_password_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = tk.Entry(
            form_frame,
            textvariable=self.confirm_password_var,
            font=(FONT_FAMILY, 12),
            width=25,
            show="*"
        )
        confirm_password_entry.grid(row=3, column=1, padx=10, pady=10)

        # Signup button
        signup_button = tk.Button(
            signup_frame,
            text="Create Account",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=30,
            pady=10,
            command=self.process_signup
        )
        signup_button.pack(pady=20)

        # Status message
        self.signup_status_var = tk.StringVar()
        signup_status_label = tk.Label(
            signup_frame,
            textvariable=self.signup_status_var,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg="red"
        )
        signup_status_label.pack(pady=10)

    def show_forgot_password_frame(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        forgot_pw_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        forgot_pw_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Back button
        back_button = tk.Button(
            forgot_pw_frame,
            text="← Back",
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg=PRIMARY_COLOR,
            bd=0,
            command=self.show_login_frame
        )
        back_button.pack(anchor="nw", pady=10)

        # Header
        header_label = tk.Label(
            forgot_pw_frame,
            text="Reset Password",
            font=(FONT_FAMILY, 18, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=20)

        # Form frame
        form_frame = tk.Frame(forgot_pw_frame, bg=BACKGROUND_COLOR)
        form_frame.pack(pady=20)

        # Email
        email_label = tk.Label(
            form_frame,
            text="Email:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        email_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.reset_email_var = tk.StringVar()
        email_entry = tk.Entry(
            form_frame,
            textvariable=self.reset_email_var,
            font=(FONT_FAMILY, 12),
            width=25
        )
        email_entry.grid(row=0, column=1, padx=10, pady=10)

        # Send Reset Token button
        send_token_button = tk.Button(
            forgot_pw_frame,
            text="Send Reset Token",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=30,
            pady=10,
            command=self.send_reset_token
        )
        send_token_button.pack(pady=10)

        # Divider
        ttk.Separator(forgot_pw_frame, orient='horizontal').pack(fill='x', pady=20)

        # Reset password section (hidden initially)
        self.reset_section_frame = tk.Frame(forgot_pw_frame, bg=BACKGROUND_COLOR)
        self.reset_section_frame.pack(pady=10)
        self.reset_section_frame.pack_forget()  # Hide initially

        # Username
        username_label = tk.Label(
            self.reset_section_frame,
            text="Username:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.reset_username_var = tk.StringVar()
        username_entry = tk.Entry(
            self.reset_section_frame,
            textvariable=self.reset_username_var,
            font=(FONT_FAMILY, 12),
            width=25
        )
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Reset Token
        token_label = tk.Label(
            self.reset_section_frame,
            text="Reset Token:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        token_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.reset_token_var = tk.StringVar()
        token_entry = tk.Entry(
            self.reset_section_frame,
            textvariable=self.reset_token_var,
            font=(FONT_FAMILY, 12),
            width=25
        )
        token_entry.grid(row=1, column=1, padx=10, pady=10)

        # New Password
        new_password_label = tk.Label(
            self.reset_section_frame,
            text="New Password:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        new_password_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.new_password_var = tk.StringVar()
        new_password_entry = tk.Entry(
            self.reset_section_frame,
            textvariable=self.new_password_var,
            font=(FONT_FAMILY, 12),
            width=25,
            show="*"
        )
        new_password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Confirm New Password
        confirm_new_password_label = tk.Label(
            self.reset_section_frame,
            text="Confirm New Password:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        confirm_new_password_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        self.confirm_new_password_var = tk.StringVar()
        confirm_new_password_entry = tk.Entry(
            self.reset_section_frame,
            textvariable=self.confirm_new_password_var,
            font=(FONT_FAMILY, 12),
            width=25,
            show="*"
        )
        confirm_new_password_entry.grid(row=3, column=1, padx=10, pady=10)

        # Reset Password button
        reset_button = tk.Button(
            self.reset_section_frame,
            text="Reset Password",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=30,
            pady=10,
            command=self.process_reset_password
        )
        reset_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Status message
        self.reset_status_var = tk.StringVar()
        reset_status_label = tk.Label(
            forgot_pw_frame,
            textvariable=self.reset_status_var,
            font=(FONT_FAMILY, 10),
            bg=BACKGROUND_COLOR,
            fg="red"
        )
        reset_status_label.pack(pady=10)

    def show_main_app(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create main application frame
        main_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill="both")

        # Create top bar with user info and logout button
        top_bar = tk.Frame(main_frame, bg=SECONDARY_COLOR, height=50)
        top_bar.pack(fill="x")

        # User info
        user_label = tk.Label(
            top_bar,
            text=f"Logged in as: {self.current_user}",
            font=(FONT_FAMILY, 10),
            bg=SECONDARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=10
        )
        user_label.pack(side="left", pady=10)

        # View History Button
        history_button = tk.Button(
            top_bar,
            text="View History",
            font=(FONT_FAMILY, 10),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=10,
            command=self.show_history_view
        )
        history_button.pack(side="left", padx=10, pady=10)

        # Logout button
        logout_button = tk.Button(
            top_bar,
            text="Logout",
            font=(FONT_FAMILY, 10),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=10,
            command=self.logout
        )
        logout_button.pack(side="right", padx=10, pady=10)

        # Create content area
        content_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # App header
        header_label = tk.Label(
            content_frame,
            text="VegSecAI - Vegetable Recognition",
            font=(FONT_FAMILY, 18, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=10)

        # App description
        description_label = tk.Label(
            content_frame,
            text="Upload an image of a vegetable, and the AI will identify it for you.",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        description_label.pack(pady=5)

        # Image upload area
        upload_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR, bd=2, relief="groove")
        upload_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Image display area
        self.image_frame = tk.Frame(upload_frame, bg=BACKGROUND_COLOR, height=300)
        self.image_frame.pack(pady=20, fill="both", expand=True)

        # Default image display message
        self.image_label = tk.Label(
            self.image_frame,
            text="No image selected",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        self.image_label.pack(expand=True)

        # Image selection buttons
        button_frame = tk.Frame(upload_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=10)

        upload_button = tk.Button(
            button_frame,
            text="Upload Image",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=20,
            pady=5,
            command=self.upload_image
        )
        upload_button.grid(row=0, column=0, padx=10)

        camera_button = tk.Button(
            button_frame,
            text="Take Photo",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=20,
            pady=5,
            command=self.take_photo
        )
        camera_button.grid(row=0, column=1, padx=10)

        # Question entry
        question_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
        question_frame.pack(pady=10, fill="x")

        question_label = tk.Label(
            question_frame,
            text="Your Question:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        question_label.pack(anchor="w", padx=40)

        self.question_var = tk.StringVar(value="What vegetable is this?")
        question_entry = tk.Entry(
            question_frame,
            textvariable=self.question_var,
            font=(FONT_FAMILY, 12),
            width=50
        )
        question_entry.pack(padx=40, pady=5, fill="x")

        # Submit button
        submit_button = tk.Button(
            content_frame,
            text="Identify Vegetable",
            font=(FONT_FAMILY, 14),
            bg=SECONDARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=30,
            pady=10,
            command=self.send_image_to_server
        )
        submit_button.pack(pady=20)

        # Result area
        result_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
        result_frame.pack(pady=10, fill="x")

        result_label = tk.Label(
            result_frame,
            text="Result:",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        result_label.pack(anchor="w", padx=40)

        self.result_var = tk.StringVar()
        result_text = tk.Label(
            result_frame,
            textvariable=self.result_var,
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            wraplength=700,
            justify="left"
        )
        result_text.pack(padx=40, pady=5, fill="x")

    def connect_to_server(self):
        """Connect to server using SSL, reusing existing connection if possible"""
        if self.client_socket:
            return True

        server_ip = self.server_ip_var.get()
        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, 12378))
            self.client_socket = context.wrap_socket(client_socket)
            return True
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Failed to connect to server: {e}"))
            return False

    def show_error(self, message):
        """Show error message and remove loading indicator"""
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()

        error_label = tk.Label(
            self.history_frame,
            text=message,
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg="red",
            wraplength=600
        )
        error_label.pack(pady=20)

    def process_login(self):
        """Process login request in a separate thread"""
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            self.login_status_var.set("Please enter both username and password")
            return

        # Update UI to indicate processing
        self.login_status_var.set("Connecting to server...")

        # Create thread for login process
        login_thread = threading.Thread(target=self._process_login_thread, args=(username, password))
        login_thread.daemon = True
        login_thread.start()

    def _process_login_thread(self, username, password):
        """Background thread for processing login"""
        # Connect to server
        if not self.connect_to_server():
            # Use after method to update UI from thread
            self.after(0, lambda: self.login_status_var.set("Failed to connect to server"))
            return

        try:
            # Send login request
            self.client_socket.send("login".encode())
            self.client_socket.send(username.encode())
            self.client_socket.send(password.encode())

            # Receive response
            response = self.client_socket.recv(1024).decode()

            if response == "Login successful":
                self.current_user = username
                self.is_logged_in = True
                # Update UI from thread
                self.after(0, self.show_main_app)
            else:
                # Update UI from thread
                self.after(0, lambda: self.login_status_var.set(response))
                self.client_socket.close()
                self.client_socket = None
        except Exception as e:
            # Update UI from thread
            error_message = str(e)  # Capture the error message as a string
            self.after(0, lambda msg=error_message: self.login_status_var.set(f"Error: {msg}"))
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    def process_signup(self):
        """Process signup request in a separate thread"""
        username = self.signup_username_var.get()
        email = self.signup_email_var.get()
        password = self.signup_password_var.get()
        confirm_password = self.confirm_password_var.get()

        # Validate input
        if not username or not email or not password or not confirm_password:
            self.signup_status_var.set("Please fill in all fields")
            return

        if len(username) < 2 or len(username) > 32:
            self.signup_status_var.set("Username must be between 2 and 32 characters")
            return

        if password != confirm_password:
            self.signup_status_var.set("Passwords do not match")
            return

        # Update UI to indicate processing
        self.signup_status_var.set("Processing signup request...")

        # Create thread for signup process
        signup_thread = threading.Thread(target=self._process_signup_thread,
                                         args=(username, email, password))
        signup_thread.daemon = True
        signup_thread.start()

    def _process_signup_thread(self, username, email, password):
        """Background thread for processing signup"""
        # Connect to server
        if not self.connect_to_server():
            # Update UI from thread
            self.after(0, lambda: self.signup_status_var.set("Failed to connect to server"))
            return

        try:
            # Send signup request
            self.client_socket.send("signup".encode())
            self.client_socket.send(username.encode())
            self.client_socket.send(password.encode())
            self.client_socket.send(email.encode())

            # Receive response
            response = self.client_socket.recv(1024).decode()

            if response.startswith("Verification code sent"):
                # Update UI from thread
                self.after(0, lambda: self.signup_status_var.set("Please check your email for verification code"))
                self.after(0, self._show_verification_form)
            else:
                # Update UI from thread
                self.after(0, lambda: self.signup_status_var.set(response))
                self.client_socket.close()
                self.client_socket = None
        except Exception as e:
            # Update UI from thread
            self.after(0, lambda: self.signup_status_var.set(f"Error: {str(e)}"))
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

    def _show_verification_form(self):
        """Show verification code entry form"""
        verification_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        verification_frame.pack(pady=10)

        verification_label = tk.Label(
            verification_frame,
            text="Verification Code:",
            font=(FONT_FAMILY, 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
        )
        verification_label.grid(row=0, column=0, padx=10, pady=10)

        self.verification_code_var = tk.StringVar()
        verification_entry = tk.Entry(
            verification_frame,
            textvariable=self.verification_code_var,
            font=(FONT_FAMILY, 12),
            width=15
        )
        verification_entry.grid(row=0, column=1, padx=10, pady=10)
        verification_entry.focus()  # Set focus to verification code entry

        verify_button = tk.Button(
            verification_frame,
            text="Verify",
            font=(FONT_FAMILY, 12),
            bg=PRIMARY_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=10,
            pady=5,
            command=self.verify_signup_code
        )
        verify_button.grid(row=0, column=2, padx=10, pady=10)

    def verify_signup_code(self):
        """Verify the signup code in a separate thread"""
        verification_code = self.verification_code_var.get()

        if not verification_code:
            self.signup_status_var.set("Please enter the verification code")
            return

        # Update UI to indicate processing
        self.signup_status_var.set("Verifying code...")

        # Create thread for verification process
        verify_thread = threading.Thread(target=self._verify_signup_code_thread,
                                         args=(verification_code,))
        verify_thread.daemon = True
        verify_thread.start()

    def _verify_signup_code_thread(self, verification_code):
        """Background thread for verification process"""
        try:
            # Send verification code
            self.client_socket.send(verification_code.encode())

            # Receive response
            response = self.client_socket.recv(1024).decode()

            if response == "Account created successfully":
                # Update UI from thread
                self.after(0,
                           lambda: messagebox.showinfo("Success", "Account created successfully! You can now login."))
                self.after(0, self.show_login_frame)
            else:
                # Update UI from thread
                self.after(0, lambda: self.signup_status_var.set(response))
        except Exception as e:
            # Update UI from thread
            self.after(0, lambda: self.signup_status_var.set(f"Error: {str(e)}"))
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

    def send_reset_token(self):
        """Send a password reset token to the user's email in a separate thread"""
        email = self.reset_email_var.get()

        if not email:
            self.reset_status_var.set("Please enter your email")
            return

        # Update UI to indicate processing
        self.reset_status_var.set("Sending reset token...")

        # Create thread for reset token process
        reset_thread = threading.Thread(target=self._send_reset_token_thread, args=(email,))
        reset_thread.daemon = True
        reset_thread.start()

    def _send_reset_token_thread(self, email):
        """Background thread for sending reset token"""
        # Connect to server
        if not self.connect_to_server():
            # Update UI from thread
            self.after(0, lambda: self.reset_status_var.set("Failed to connect to server"))
            return

        try:
            # Send forgot password request
            self.client_socket.send("forgot_password".encode())
            self.client_socket.send(email.encode())

            # Receive response
            response = self.client_socket.recv(1024).decode()

            if response.startswith("Password reset token sent"):
                # Update UI from thread
                self.after(0, lambda: self.reset_status_var.set("Reset token sent to your email"))
                self.after(0, lambda: self.reset_section_frame.pack_forget())  # Hide the email form
                self.after(0, lambda: self.reset_section_frame.pack())  # Show the reset section
            else:
                # Update UI from thread
                self.after(0, lambda: self.reset_status_var.set(response))
                self.client_socket.close()
                self.client_socket = None
        except Exception as e:
            # Update UI from thread
            self.after(0, lambda: self.reset_status_var.set(f"Error: {str(e)}"))
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

    def process_reset_password(self):
        """Process password reset in a separate thread"""
        username = self.reset_username_var.get()
        reset_token = self.reset_token_var.get()
        new_password = self.new_password_var.get()
        confirm_new_password = self.confirm_new_password_var.get()

        # Validate input
        if not username or not reset_token or not new_password or not confirm_new_password:
            self.reset_status_var.set("Please fill in all fields")
            return

        if new_password != confirm_new_password:
            self.reset_status_var.set("Passwords do not match")
            return

        # Update UI to indicate processing
        self.reset_status_var.set("Processing password reset...")

        # Create thread for reset password process
        reset_pwd_thread = threading.Thread(target=self._process_reset_password_thread,
                                            args=(username, reset_token, new_password))
        reset_pwd_thread.daemon = True
        reset_pwd_thread.start()

    def _process_reset_password_thread(self, username, reset_token, new_password):
        """Background thread for processing password reset"""
        # Make sure we have an active connection
        if not self.client_socket:
            if not self.connect_to_server():
                self.after(0, lambda: self.reset_status_var.set("Failed to connect to server"))
                return

        try:
            # We're already in the forgot_password flow on the server side
            # Send the reset information in the expected order
            self.client_socket.send(username.encode())
            self.client_socket.send(reset_token.encode())
            self.client_socket.send(new_password.encode())

            # Receive response
            response = self.client_socket.recv(1024).decode()

            if response == "Password reset successful":
                # Update UI from thread
                self.after(0, lambda: messagebox.showinfo("Success",
                                                          "Password has been reset successfully! You can now login."))
                self.after(0, self.show_login_frame)
            else:
                # Update UI from thread
                self.after(0, lambda: self.reset_status_var.set(response))
                self.client_socket.close()
                self.client_socket = None
        except Exception as e:
            # Update UI from thread
            self.after(0, lambda: self.reset_status_var.set(f"Error: {str(e)}"))
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

    def upload_image(self):
        """Upload an image from the file system"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
        )

        if file_path:
            self.display_image(file_path)
            self.current_image_path = file_path
    def take_photo(self):
        """Open camera window for photo capture in a separate thread."""

        def run_camera_window():
            camera_window = CameraWindow(self, self.display_image)

        thread = threading.Thread(target=run_camera_window)
        thread.start()

    def display_image(self, image_path):
        """Display the selected image"""
        try:
            # Clear existing widgets in image frame
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            # Load and resize image
            image = Image.open(image_path)

            # Calculate resize dimensions to fit in frame while keeping aspect ratio
            width, height = image.size
            max_width = 400
            max_height = 300

            # Calculate scaling factor
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)

            # Resize image
            image = image.resize((new_width, new_height), Image.LANCZOS)
            self.current_image = ImageTk.PhotoImage(image)

            # Display image
            image_label = tk.Label(self.image_frame, image=self.current_image, bg=BACKGROUND_COLOR)
            image_label.image = self.current_image
            image_label.pack(expand=True)

            # Set the current image path so it can be sent to server
            self.current_image_path = image_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {e}")

    def send_image_to_server(self):
        """Send the current image to the server for analysis in a separate thread"""
        if not self.is_logged_in:
            messagebox.showwarning("Not Logged In", "You need to be logged in to use this feature.")
            return

        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please upload or take a photo first.")
            return

        # Get user's question
        question = self.question_var.get()
        if not question.strip():
            question = "What vegetable is this?"

        # Update UI to indicate processing
        self.result_var.set("Processing image... please wait")

        # Create thread for image processing
        image_thread = threading.Thread(target=self._send_image_to_server_thread,
                                        args=(self.current_image_path, question))
        image_thread.daemon = True
        image_thread.start()

    def _send_image_to_server_thread(self, image_path, question):
        """Background thread for sending image to server"""
        # Read the image file
        try:
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()

            # Calculate image hash
            image_hash = hashlib.sha256(image_data).hexdigest()

            # Send to server
            try:
                self.client_socket.send(len(image_data).to_bytes(4, "big"))
                self.client_socket.send(image_data)
                self.client_socket.send(image_hash.encode())
                self.client_socket.send(question.encode())

                # Receive response
                answer = self.client_socket.recv(1024).decode()

                # Update UI from thread
                if answer == "Image hash mismatch.":
                    self.after(0, lambda: messagebox.showerror("Error",
                                                               "Image verification failed. Please try uploading again."))
                elif answer.startswith("Invalid image format"):
                    self.after(0, lambda: messagebox.showerror("Error", answer))
                else:
                    self.after(0, lambda: self.result_var.set(answer))
            except Exception as e:
                # Update UI from thread
                self.after(0,
                           lambda: messagebox.showerror("Connection Error", f"Failed to communicate with server: {e}"))
                self.after(0, self.logout)
        except Exception as e:
            # Update UI from thread
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to process image: {e}"))

    def logout(self):
        """Log the user out and return to login screen"""
        if self.client_socket:
            try:
                self.client_socket.send("#bye".encode())
                self.client_socket.close()
            except:
                pass
            self.client_socket = None

        self.is_logged_in = False
        self.current_user = None
        self.current_image = None
        self.current_image_path = None
        self.show_login_frame()


if __name__ == "__main__":
    app = VegSecAIApp()
    app.mainloop()