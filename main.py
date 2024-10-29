import requests
import sys
import os
import tarfile
import io
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

KEY = b'\x44\xee\x33\x41\x4a\x56\x48\xe1\x5e\x1c\x7e\x15\x85\xb1\x07\x38'

def decrypt_lf3(path):
    with open(path, 'rb') as f:
        IV = f.read(16)
        cipher = Cipher(algorithms.AES(KEY), modes.CTR(IV), backend=default_backend())
        ENC_DATA = f.read()
        decryptor = cipher.decryptor()
        DEC_DATA = decryptor.update(ENC_DATA) + decryptor.finalize()
    return DEC_DATA

def extract_lf3(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    tar_data = decrypt_lf3(path)
    if not os.path.exists(filename):
        os.makedirs(filename)
    with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
        tar.extractall(filename)

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python main.py <TARGET_ID> [-d]")
    sys.exit(1)

TARGET_ID = sys.argv[1]
decrypt_flag = '-d' in sys.argv
target_code = TARGET_ID.split('-')[1]
base_url = f"https://digitalcontent.leapfrog.com/packages/{target_code}/{TARGET_ID}"

for ext in ['lfp', 'lf2', 'lf3']:
    url = f"{base_url}.{ext}"
    print(f"Trying {url}..... ", end="")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            print("SUCCESS \n")
            file_path = f"{TARGET_ID}.{ext}"
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            if ext == 'lf3' and decrypt_flag:
                print("Decrypting... \n")
                extract_lf3(file_path)
                print(f"\nID {TARGET_ID} Downloaded and Decrypted Successfully!")
            else:
                print(f"\nID {TARGET_ID} Downloaded Successfully!")
            break
        else:
            print("FAILED")
    except requests.RequestException as e:
        print(f"FAILED ({e})")
else:
    print(f"\nID {TARGET_ID} could not be downloaded.")
