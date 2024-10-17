from getmacaddress import get_mac_address
import os
import json
import base64
import subprocess
from Crypto.Cipher import AES
import time #for count 10 seconds

mac_address = get_mac_address('eth0')
print(f"mac_address: {mac_address}")

#run test-index.js
os.system(f'node index.js {mac_address}')

# URL-safe Base64 解碼
def urlsafe_b64decode_nopad(data):
    padding = 4 - (len(data) % 4)
    data = data + ("=" * padding)
    return base64.urlsafe_b64decode(data)

# AES 解密函數
def decrypt(ciphertext, key, iv, mode):
    encobj = AES.new(key, mode, iv)
    return encobj.decrypt(ciphertext)

def execute_and_check():
    #寫讀取eepromdata###################################################
    server_id = ""
    server_xlh = ""
    server_pin = ""


    # 讀取 sso_id 和 sso_token
    with open('sso_id.txt', 'r') as file:
        sso_id_base64url = file.read().strip()

    with open('sso_token.txt', 'r') as file:
        user_token = file.read().strip()

    # 讀取和解析 token 用作解密密鑰和 IV
    with open('token.txt', 'r') as file:
        parmas_token = file.read().strip()

    # 解密 sso_id 以獲取 user_id
    key = parmas_token[:32]  # token 前 32bytes 當 key
    iv = parmas_token[32:48]  # token 接續 16bytes 當 iv

    sso_id = urlsafe_b64decode_nopad(sso_id_base64url)
    user_id_bytes = decrypt(sso_id, key, iv, AES.MODE_GCM)
    user_id = user_id_bytes[:27].decode('utf-8')  # 使用解密出的前 27 bytes 作為 user_id

    # 組合命令並執行
    command = [
        "/home/a70640/rpi3/sso-backend-arm64",
        server_id,
        server_xlh,
        server_pin,
        user_id,
        user_token
    ]

    # 執行命令並獲取輸出
    result = subprocess.run(command, capture_output=True, text=True)
    
    # 解析輸出 (假設輸出為 JSON 格式)
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid output format"}
    
    return output

def main():
    for attempt in range(6):
        start_time = time.time()  # 記錄開始時間
        result = execute_and_check()

        if result.get("result") == True:
            print('{"result": true},"驗證成功"')
            return True
        elif "error" in result and result["error"]:  # 確認 "error" 中有值
            print(f"嘗試第 {attempt + 1} 次失敗，錯誤訊息: {result['error']}")
            
        elif result.get("result") == False:
            print(f"嘗試第 {attempt + 1} 次失敗，result 為 false")
            
        elapsed_time = time.time() - start_time  # 計算執行時間
        if elapsed_time > 10:  # 檢查是否超過10秒
            print(f"超時，嘗試第 {attempt + 1} 次失敗")
            
    print('{"result": false}, "請重新驗證"')
    return False

# 執行主程式
if __name__ == "__main__":
    main()

'''
執行最多六次操作：這個函式會透過 for 迴圈最多執行六次操作。
在每次迴圈中，它都會呼叫一個名為 execute_and_check() 的函式，該函式會執行一些處理並返回一個結果 result。
檢查 result 的結果：
檢查 result 為 True：表示驗證成功，程式會輸出「驗證成功」並返回 True，然後跳出迴圈。

檢查是否有錯誤：
"error" in result：確保 result 裡確實包含 error 這個欄位。
result["error"]：確認 error 欄位中有具體的錯誤訊息。 error 中有值且不是空字串、None 或其他空的狀態。

檢查 result 為 False：會輸出嘗試失敗的訊息，並在第六次嘗試後同樣要求重新驗證並返回 False。
'''


