from cryptography.hazmat.primitives.asymmetric import ec
import hashlib
from hashlib import sha256
from cryptography.hazmat.backends import default_backend

def generate_key_pair(private_key=None):
    #can use specific private key to generate public key by passing para
    if private_key is None:
        private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()  

    private_key_hex = private_key.private_numbers().private_value
    public_key_hex = public_key.public_numbers().y

    return format(private_key_hex, 'x'), format(public_key_hex, 'x')
def generate_key_pair_from_user_pw(user, pw):
    hash_value = sha256(user+pw).digest()
    priv_int = int.from_bytes(hash_value, byteorder='big')
    priv = ec.derive_private_key(priv_int, ec.SECP256R1(), default_backend())
    return generate_key_pair(priv)
#Test
def main():
    #private_key_hex, public_key_hex = generate_key_pair()

    #test gen from hash of user, pw:
    user = b"hieunguyen"
    pw = b"Thisizmypass"
    private_key_hex, public_key_hex = generate_key_pair_from_user_pw(user, pw)

    print("Private Key (hex):")
    print(private_key_hex)

    print("\nPublic Key (hex):")
    print(public_key_hex)

if __name__ == "__main__":
    main()
