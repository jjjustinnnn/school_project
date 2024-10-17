#學長+最新
import smbus
import time

# 設定 I²C 相關參數
DEVICE_ADDRESS = 0x50  # EEPROM的I2C地址（根據你的地址設置，通常是 0x50 到 0x57）
I2C_BUS = 1            # I2C總線號，通常是1
START_MEMORY_ADDRESS = 0x00  # EEPROM的內部地址（從0開始）
NUM_BYTES = 128        # 讀取的字節數

# 初始化I2C總線
try:
    bus = smbus.SMBus(I2C_BUS)
    print(f"I2C bus {I2C_BUS} initialized.")
except Exception as e:
    print(f"Error initializing I2C bus {I2C_BUS}: {e}")
    exit(1)

# 定義一個函數來從指定內存地址讀取資料
def read_eeprom(address, mem_address, length):
    data = []
    for i in range(mem_address, mem_address + length):
        try:
            # 從每個記憶體地址讀取 1 字節資料
            byte = bus.read_byte_data(address, i)
            data.append(byte)
        except Exception as e:
            print(f"Error reading address {i}: {e}")
            break
    return data

# 將數據轉換為字串
def data_to_string(data):
    return ''.join(chr(byte) for byte in data)

# 主程式
def main():
    try:
        # 調試信息
        print(f"Using I2C address: {DEVICE_ADDRESS}")
        print(f"Using I2C bus: {I2C_BUS}")
        
        # 讀取 EEPROM 中的數據
        data = read_eeprom(DEVICE_ADDRESS, START_MEMORY_ADDRESS, NUM_BYTES)
        
        # 打印讀取到的原始數據
        print(f"Raw data read from EEPROM: {data}")
        
        # 將數據轉換為 ASCII 字串並打印
        ascii_string = data_to_string(data)
        print("Data from EEPROM:", ascii_string)

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()

#學長eeprom
'''
import smbus
import time

DEVICE_ADDRESS = 0x50  # EEPROM的I2C地址
I2C_BUS = 1            # I2C总线号，通常为1

# 初始化I2C总线
try:
    bus = smbus.SMBus(I2C_BUS)
    print(f"I2C bus {I2C_BUS} initialized.")
except Exception as e:
    print(f"Error initializing I2C bus {I2C_BUS}: {e}")
    exit(1)

def read_eeprom(address, num_bytes):
    try:
        # 读取EEPROM数据
        data = bus.read_i2c_block_data(DEVICE_ADDRESS, address, num_bytes)
        return data
    except Exception as e:
        print(f"Error reading EEPROM at address {address} with {num_bytes} bytes: {e}")
        raise

def data_to_string(data):
    # 将数据转换为ASCII字符串
    ascii_string = ''.join(chr(byte) for byte in data)
    return ascii_string

def main():
    try:
        # 打印调试信息
        print(f"Using I2C address: {DEVICE_ADDRESS}")
        print(f"Using I2C bus: {I2C_BUS}")
        
        # 读取EEPROM的前8个字节
        data = read_eeprom(0, 8)
        
        # 打印读取到的原始数据
        print(f"Raw data read from EEPROM: {data}")
        
        # 将数据转换为ASCII字符串
        ascii_string = data_to_string(data)
        print("Password:", ascii_string)

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()
'''

#最新
'''
import smbus
import time

# I²C bus (通常是1)
bus = smbus.SMBus(1)

# HT24LC16 的 I²C 地址（根據你的地址設置，通常是 0x50 到 0x57）
eeprom_address = 0x50

# EEPROM 的內部地址（從0開始的內存位置）
start_memory_address = 0x00

# 讀取的字節數（例如，讀取 128 字節）
num_bytes = 128

# 定義一個函數來從指定內存地址讀取資料
def read_eeprom(address, mem_address, length):
    # 創建一個空列表來存儲讀取到的資料
    data = []
    
    # HT24LC16 分頁模式，因為這款 EEPROM 一頁是16字節，所以可能需要分頁讀取
    for i in range(mem_address, mem_address + length):
        try:
            # 從每個記憶體地址讀取 1 字節資料
            byte = bus.read_byte_data(address, i)
            data.append(byte)
        except Exception as e:
            print(f"Error reading address {i}: {e}")
            break
    
    return data

# 從 EEPROM 中讀取資料
data_read = read_eeprom(eeprom_address, start_memory_address, num_bytes)

# 將資料轉換為字串形式 (如果之前存入的是可解碼的字串資料)
data_string = ''.join([chr(byte) for byte in data_read])

print("Read data from EEPROM:")
print(data_string)

'''