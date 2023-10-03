from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_key_hex = private_key.private_numbers().private_value
    public_key_hex = public_key.public_numbers().y

    return format(private_key_hex, 'x'), format(public_key_hex, 'x')

#Test
def main():
    private_key_hex, public_key_hex = generate_key_pair()

    print("Private Key (hex):")
    print(private_key_hex)

    print("\nPublic Key (hex):")
    print(public_key_hex)

if __name__ == "__main__":
    main()
