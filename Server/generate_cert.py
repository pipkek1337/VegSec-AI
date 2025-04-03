from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os

CERT_FILE = "server.crt"
KEY_FILE = "server.key"

def generate_self_signed_cert():
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print("[Certificate] Certificate already exists.")
        return CERT_FILE, KEY_FILE

    print("[Certificate] Generating new certificate...")
    # Use a fixed Common Name instead of a dynamic IP
    cn = "my-server"

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IL"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Central"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Rishon Lezion"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VEGSECAI"),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    with open(CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(KEY_FILE, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    print("[Certificate] Certificate generated successfully.")
    return CERT_FILE, KEY_FILE

if __name__ == "__main__":
    generate_self_signed_cert()