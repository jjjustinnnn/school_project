import smbus
import time
import os
import json
import base64
import subprocess
from Crypto.Cipher import AES
from getmacaddress import get_mac_address

# 設定 I²C 相關參數
DEVICE_ADDRESS = 0x50  # EEPROM的I2C地址
I2C_BUS = 1            # I2C總線號
START_MEMORY_ADDRESS = 0x00  # EEPROM的內部地址
NUM_BYTES = 210      # 讀取的字節數

# 初始化I2C總線
try:
    bus = smbus.SMBus(I2C_BUS)
    print(f"I2C bus {I2C_BUS} initialized.")
except Exception as e:
    print(f"Error initializing I2C bus {I2C_BUS}: {e}")
    exit(1)

# 定義從EEPROM讀取資料的函數
def read_eeprom(address, mem_address, length):
    data = []
    for i in range(mem_address, mem_address + length):
        try:
            byte = bus.read_byte_data(address, i)
            data.append(byte)
        except Exception as e:
            print(f"Error reading address {i}: {e}")
            break
    return data

# 將數據轉換為字串
def data_to_string(data):
    return ''.join(chr(byte) for byte in data)

# URL-safe Base64 解碼
def urlsafe_b64decode_nopad(data):
    padding = 4 - (len(data) % 4)
    data = data + ("=" * padding)
    return base64.urlsafe_b64decode(data)

def decrypt(ciphertext, key, iv, mode):
    encobj = AES.new(key, mode, iv)
    return encobj.decrypt(ciphertext)


# 執行並驗證
def execute_and_check(ascii_string):
    ascii_string = json.loads(ascii_string)
    # 提取 "id", "pin", 和 "xlh"
    server_id = ascii_string['id']
    server_pin = ascii_string["pin"]
    server_xlh = ascii_string["xlh"]
    
    print("server_id =", server_id)
    print("server_pin =", server_pin)
    print("server_xlh =", server_xlh)

    # 讀取 sso_id 和 sso_token
    with open('sso_id.txt', 'r') as file:
        sso_id_base64url = file.read().strip()

    with open('sso_token.txt', 'r') as file:
        user_token = file.read().strip()

    # 讀取和解析 token 用作解密密鑰和 IV
    with open('token.txt', 'r') as file:
        parmas_token = urlsafe_b64decode_nopad(file.read().strip())

    # 解密 sso_id 以获取 user_id
    key = parmas_token[:32]  # token 前 32bytes 当 key
    iv = parmas_token[32:48]  # token 接续 16bytes 当 iv

    sso_id = urlsafe_b64decode_nopad(sso_id_base64url)
    user_id_bytes = decrypt(sso_id, key, iv, AES.MODE_GCM)
    user_id = user_id_bytes[:27].decode('utf-8')  # 使用解密出的前 27 bytes 作为 user_id


    # 打印解密信息（可选）
    print("user_id:" ,user_id)
    print("user_token:", user_token)

    # 组合命令并执行
    command = [
        "/home/a70640/rpi/sso-backend-arm64",
        server_id,
        server_xlh,
        server_pin,
        user_id,
        user_token
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid output format"}
    
    return output

# 主程式
def main():
    # 讀取 EEPROM 中的數據
    eeprom_data = read_eeprom(DEVICE_ADDRESS, START_MEMORY_ADDRESS, NUM_BYTES)
    
    # 將數據轉換為 ASCII 字串並打印
    ascii_string = data_to_string(eeprom_data)
    print("Data from EEPROM:", ascii_string)

    mac_address = get_mac_address('eth0')
    print(f"MAC address: {mac_address}")
    
    os.system(f'node index.js {mac_address}')
    
    for attempt in range(6):
        start_time = time.time()  # 記錄開始時間      
        result = execute_and_check(ascii_string)

        if result.get("result") == True:
            print('{"result": true},"驗證成功"')
            return True
        elif "error" in result and result["error"]:
            print(f"嘗試第 {attempt + 1} 次失敗，錯誤訊息: {result['error']}")
        elif result.get("result") == False:
            print(f"嘗試第 {attempt + 1} 次失敗，result 為 false")
            
        elapsed_time = time.time() - start_time  # 計算執行時間
        if elapsed_time > 10:
            print(f"超時，嘗試第 {attempt + 1} 次失敗")
            
    print('{"result": false}, "請重新驗證"')
    return False

if __name__ == "__main__":
    main()
