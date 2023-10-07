import ecdsa
from hashlib import sha256

def hex_string_to_private_key(hex_string):
    private_key_bytes = bytes.fromhex(hex_string)
    private_key = ecdsa.keys.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1, hashfunc=sha256)
    return private_key

def sign(message, private_key_hex_string=None):
    if private_key_hex_string is None:
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha256)
    else :
        private_key = hex_string_to_private_key(private_key_hex_string)
    signature = private_key.sign(message)
    return signature, private_key

def verify(message, signature, public_key_hex):
    try:
        public_key = bytes.fromhex(public_key_hex)
        vk = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1, hashfunc=sha256)
        return vk.verify(signature, message)
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

#test
def main():
    message = b"Hieu write something for Alice.."
    signature, private_key = sign(message)
    print(type (signature), type (private_key))
    
    print("Private key:", private_key.to_string().hex())
    print("Signature:", signature.hex())
    print("size of signature:", len(signature.hex()))

    public_key_hex = private_key.get_verifying_key().to_string().hex()
    is_verified = verify(message, signature, public_key_hex)
    if is_verified:
        print("Signature verified successfully.")
    else:
        print("Signature verification failed.")

    existing_public_key = '98cedbb266d9fc38e41a169362708e0509e06b3040a5dfff6e08196f8d9e49cebfb4f4cb12aa7ac34b19f3b29a17f4e5464873f151fd699c2524e0b7843eb383'
    existing_signature = '740894121e1c7f33b174153a7349f6899d0a1d2730e9cc59f674921d8aef73532f63edb9c5dba4877074a937448a37c5c485e0d53419297967e95e9b1bef630d'

    is_existing_verified = verify(message, bytes.fromhex(existing_signature), existing_public_key)
    if is_existing_verified:
        print("Existing Signature verified successfully.")
    else:
        print("Existing Signature verification failed.")

if __name__ == "__main__":
    main()
