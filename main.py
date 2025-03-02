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
    return filename  # Return extracted folder path

def update_meta_files(folder):
    meta_files = ['meta.inf', 'DAMeta.inf']
    for meta_file in meta_files:
        meta_path = os.path.join(folder, meta_file)
        if os.path.exists(meta_path):
            with open(meta_path, 'rb+') as f:
                content = f.read()
                if b"DeviceAccess=1" not in content:
                    f.seek(0, io.SEEK_END)  # Move to the end of the file
                    f.write(b"DeviceAccess=1\n")
                    f.write(b"ProfileAccess=0,1,2")

def repackage_as_posix_tar(folder, output_tar):
    with tarfile.open(output_tar, 'w', format=tarfile.PAX_FORMAT) as tar:
        tar.add(folder, arcname=os.path.basename(folder))

def clean_up(folder, keep_files=False):
    if not keep_files:
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(folder)

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print("Usage: python main.py <TARGET_ID> [-d] [-i]")
    sys.exit(1)

TARGET_ID = sys.argv[1]
decrypt_flag = '-d' in sys.argv
integrate_flag = '-i' in sys.argv
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
                folder_path = extract_lf3(file_path)
                if integrate_flag:
                    print("Processing meta files... \n")
                    update_meta_files(folder_path)
                    posix_tar_path = f"{TARGET_ID}.tar"
                    repackage_as_posix_tar(folder_path, posix_tar_path)
                    print(f"Repackaged as {posix_tar_path}")
                    clean_up(folder_path, keep_files=decrypt_flag)
                print(f"\nID {TARGET_ID} Downloaded and Decrypted Successfully!")
            elif ext == 'lf3' and integrate_flag:
                print("Processing meta files... \n")
                folder_path = extract_lf3(file_path)
                update_meta_files(folder_path)
                posix_tar_path = f"{TARGET_ID}.tar"
                repackage_as_posix_tar(folder_path, posix_tar_path)
                print(f"Repackaged as {posix_tar_path}")
                clean_up(folder_path, keep_files=False)
            else:
                print(f"\nID {TARGET_ID} Downloaded Successfully!")
            break
        else:
            print("FAILED")
    except requests.RequestException as e:
        print(f"FAILED ({e})")
else:
    print(f"\nID {TARGET_ID} could not be downloaded.")
