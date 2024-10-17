'''
data = '{"id":"test-YVNEbmZiUyZr","pin":"908343","xlh":"M0BVIbuI7NQFSPgeSQhuX60HlgswwmF881kwutF-orJ7iruu3tkL7ikhO_ApmATeuxyDCRIc-HxuoZYp_7PT0c1q7ZI2GbgsqMdybEGyLUTwBrZO9JTHCoWUBC4WWgxZMD6v3YrTn8Hm1Qf_nCZeGbV3PodMHCk7"}'
hex_data = data.encode("utf-8").hex()  # 轉換為十六進制
print(hex_data)
'''
# 將 Hex 字串轉換為二進制並保存為 .bin 檔案
hex_data = '7b226964223a22746573742d59564e45626d5a6955795a72222c2270696e223a22393038333433222c22786c68223a224d30425649627549374e51465350676553516875583630486c677377776d463838316b777574462d6f724a376972757533746b4c37696b684f5f41706d41546575787944435249632d4878756f5a59705f37505430633171375a493247626773714d6479624547794c55547742725a4f394a5448436f5755424334575767785a4d443676335972546e38486d3151665f6e435a6547625633506f644d48436b37227d'

# 將十六進制數據轉換為二進制數據
bin_data = bytes.fromhex(hex_data)

# 將二進制數據寫入 .bin 檔案
with open('eepromdata.bin', 'wb') as bin_file:
    bin_file.write(bin_data)

# 如果需要保存為 .mem 檔案，可以將擴展名改為 .mem
with open('eepromdata.mem', 'wb') as mem_file:
    mem_file.write(bin_data)

print("Conversion complete! The file is saved as 'output.bin' and 'output.mem'.")
