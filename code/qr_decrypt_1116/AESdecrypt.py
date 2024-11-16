from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json
#from getmacaddress import get_mac_address

# AES 加密數據（密文）
encrypted_data_hex = "eba053d6e85ea6748aa34b721e32b1f82cc708bcaf3251a8b446e9bf9548d6c9c27f737389af9e2871476a65b51902201e31e258654d502e39a793b486d7df97e13e654c62bdf88211e04c659df63f84f1f5a242b421a6e5dab48e2edfecb7af2f2ca02295fe1d39596daac0ff13fb02c881c7648c72866d7a6c66d045c1fb93ce62bab000cda05b7b309b07a754681c5b800b60f1945e16f60d501da1da7b84c82a6f40228033004ae27bcc6cb55aa960047af8b926a8dfa8d983f71d70c742828d2c6313f1f710dae2cec5cb74205dbd69ed0327fe1816f840a45fd445b834"  # e.g., "5e...a9" (以 Hex 表示的密文)
encrypted_data = bytes.fromhex(encrypted_data_hex)

#金鑰
key_hex = "dc:a6:32:88:96:07"
#key_hex = get_mac_address('eth0')

# 將十六進位密鑰轉為字節並填充至 16 字節
key = bytes.fromhex(key_hex.replace(":", "")).ljust(16, b'\0')

# 使用 AES 解密
cipher = AES.new(key, AES.MODE_ECB)  # 使用 ECB 模式
decrypted_data_padded = cipher.decrypt(encrypted_data)

# 移除填充，還原原始數據
decrypted_data_bytes = unpad(decrypted_data_padded, AES.block_size)
decrypted_data = json.loads(decrypted_data_bytes.decode('utf-8'))  # 將 JSON 字節轉回 Python 字典

# 輸出解密結果
print("Decrypted Data:", decrypted_data)
