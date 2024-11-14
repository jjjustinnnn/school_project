import os
import smbus
import time
import qrcode
from PIL import Image
import base64
import socket
import fcntl
import struct
import shutil

DEVICE_ADDRESS = 0x50  # EEPROM 的 I2C 地址
I2C_BUS = 1            # I2C 总线号，通常为 1

id = "test-YVNEbmZiUyZr"
pin = "908343"
xlh = "M0BVIbuI7NQFSPgeSQhuX60HlgswwmF881kwutF-orJ7iruu3tkL7ikhO_ApmATeuxyDCRIc-HxuoZYp_7PT0c1q7ZI2GbgsqMdybEGyLUTwBrZO9JTHCoWUBC4WWgxZMD6v3YrTn8Hm1Qf_nCZeGbV3PodMHCk7"

# 初始化 I2C 总线
try:
    bus = smbus.SMBus(I2C_BUS)
except Exception as e:
    print("初始化 I2C 总线时出错:", str(e))

def clear_folder(folder_path):
    # Make sure the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # List all files and subdirectories in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # If it's a file, remove it
            if os.path.isfile(file_path):
                os.remove(file_path)
            # If it's a directory, remove it recursively
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        print(f"Folder '{folder_path}' has been cleared.")
    else:
        print(f"Folder '{folder_path}' does not exist or is not a directory.")


def read_eeprom(address, num_bytes):
    try:
        data = bus.read_i2c_block_data(DEVICE_ADDRESS, address, num_bytes)
        return data
    except Exception as e:
        print(f"读取 EEPROM 时出错: 地址 {address}，字节数 {num_bytes}: {e}")
        raise

def data_to_string(data):
    ascii_string = ''.join(chr(byte) for byte in data)
    return ascii_string

def get_mac_address(interface='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes(interface[:15], 'utf-8')))
    return ':'.join(['%02x' % b for b in info[18:24]])

def generate_token():
    random_bytes = os.urandom(64)
    token = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    return token

def create_qrcode(data):
    # Use a relative path for saving QR code image within the Flask static folder
    qr_code_path = 'static/uploads/qrcode.png'  # Relative path
    qr_code_dir = os.path.dirname(qr_code_path)
    
    # Create directory if it does not exist
    if not os.path.exists(qr_code_dir):
        try:
            os.makedirs(qr_code_dir)
            print(f"Directory {qr_code_dir} created successfully.")
        except Exception as e:
            print(f"Error creating directory {qr_code_dir}: {e}")
            return None
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Save the QR code image
    try:
        img.save(qr_code_path)
        print(f"QR Code image saved to {qr_code_path}")
    except Exception as e:
        print(f"Error saving QR code image: {e}")
        return None
    
    return img

def main():
    clear_folder("/home/abc/Desktop/web2.0/static/uploads")
    try:
        print(f"使用的 I2C 地址: {DEVICE_ADDRESS}")
        print(f"使用的 I2C 总线: {I2C_BUS}")
        
        data = read_eeprom(0, 8)
        print(f"从 EEPROM 读取的原始数据: {data}")
        
        ascii_string = data_to_string(data)
        print("密码:", ascii_string)

    except Exception as e:
        print("错误:", str(e))

    try:
        mac_address = get_mac_address('eth0')
        print(f"MAC 地址: {mac_address}")
        
        token = generate_token()
        
        qrcode_url = f"https://tekpass.com.tw/sso?receiver=fcm://{mac_address}:TPYZU&token={token}"
        print("QR 码 URL:", qrcode_url)
        
        img = create_qrcode(qrcode_url)
        
        if img:
            with open('token.txt', 'w') as file:
                file.write(f"Token: {token}\n")
            print("URL 和 Token 已保存到 token.txt")

    except Exception as e:
        print("错误:", str(e))

# Run the main function
if __name__ == "__main__":
    main()
