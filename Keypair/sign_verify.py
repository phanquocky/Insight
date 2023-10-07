import ecdsa
from hashlib import sha256
try:
    from hash import sha256_hash
except ModuleNotFoundError:
    from Keypair.hash    import sha256_hash

def checkHex(s):
    if len(s) % 2 != 0:
        return False
    
    for ch in s:
        if ((ch < '0' or ch > '9') and
            (ch < 'A' or ch > 'F')):
        
            return False
    return True

def hex_string_to_private_key(hex_string):      
    private_key_bytes = bytes.fromhex(hex_string)
    private_key = ecdsa.keys.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1, hashfunc=sha256)
    return private_key

def hex_string_to_public_key(hex_string):
    public_key_bytes = bytes.fromhex(hex_string)
    public_key = ecdsa.keys.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1, hashfunc=sha256)
    return public_key

def hex_string_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def sign(message, private_key=None):
    if private_key == None:
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha256)
    
    signature = private_key.sign(message)
    return signature, private_key

def verify(message, signature, public_key):
    public_key_bytes = public_key.to_string()
    try:
        vk = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1, hashfunc=sha256)
        return vk.verify(signature, message)
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

#test
def main():
    message = b"Hieu write something for Alice.."
    message_hash_hex = sha256_hash(message) 
    print("message_hash_hex:", message_hash_hex)
    message_hash = hex_string_to_bytes(message_hash_hex) #to bytes

    signature, private_key = sign(message_hash)
    
    print("Private key:", private_key.to_string().hex())
    print("Signature:", signature.hex())
    print("size of signature:", len(signature.hex()))

    public_key = private_key.get_verifying_key()
    print("Public key:", public_key.to_string().hex())
    is_verified = verify(hex_string_to_bytes(message_hash_hex), signature, public_key)
    if is_verified:
        print("Signature verified successfully.")
    else:
        print("Signature verification failed.")

    existing_public_key_hex = '98cedbb266d9fc38e41a169362708e0509e06b3040a5dfff6e08196f8d9e49cebfb4f4cb12aa7ac34b19f3b29a17f4e5464873f151fd699c2524e0b7843eb383'
    existing_signature_hex = '740894121e1c7f33b174153a7349f6899d0a1d2730e9cc59f674921d8aef73532f63edb9c5dba4877074a937448a37c5c485e0d53419297967e95e9b1bef630d'

    is_existing_verified = verify(message, hex_string_to_bytes(existing_signature_hex), hex_string_to_public_key(existing_public_key_hex))
    if is_existing_verified:
        print("Existing Signature verified successfully.")
    else:
        print("Existing Signature verification failed.")

if __name__ == "__main__":
    main()
