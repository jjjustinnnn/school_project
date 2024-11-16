import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
#from getmacaddress import get_mac_address

# 設定標準輸出為 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 原始數據
data = {
    "id": "test-YVNEbmZiUyZr",
    "pin": "908343",
    "xlh": "M0BVIbuI7NQFSPgeSQhuX60HlgswwmF881kwutF-orJ7iruu3tkL7ikhO_ApmATeuxyDCRIc-HxuoZYp_7PT0c1q7ZI2GbgsqMdybEGyLUTwBrZO9JTHCoWUBC4WWgxZMD6v3YrTn8Hm1Qf_nCZeGbV3PodMHCk7"
}
#金鑰
key_hex = "dc:a6:32:88:96:07"
#key_hex = get_mac_address('eth0')

# 將數據轉為 JSON 並編碼為字節
data_bytes = json.dumps(data).encode('utf-8')

# 將十六進位密鑰轉為字節並填充至 16 字節
key = bytes.fromhex(key_hex.replace(":", "")).ljust(16, b'\0')

# 使用 AES 加密
cipher = AES.new(key, AES.MODE_ECB)  # 使用 ECB 模式
encrypted_data = cipher.encrypt(pad(data_bytes, AES.block_size))  # 填充數據

# 輸出結果
print("Original data:", data)
print("Original Key:", key.hex())
print("AES Encrypted Data:", encrypted_data.hex())
