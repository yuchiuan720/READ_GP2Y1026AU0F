import serial
import time

class AirQualitySensor:
    def __init__(self, com_port, baud_rate=2400):
        self.serial_port = serial.Serial(com_port, baud_rate, timeout=1)
        
    def read_data(self):
        while True:
            # 尋找起始字節 0xAA
            start_byte = self.serial_port.read(1)
            if start_byte == b'\xAA':
                # 讀取剩餘的6字節
                remaining_data = self.serial_port.read(6)
                if len(remaining_data) == 6 and remaining_data[-1] == 0xFF:  # 檢查完整數據包和結束字節
                    # 將高位和低位轉換為 ASCII 字符
                    VoutH = remaining_data[0]
                    VoutL = remaining_data[1]
                    VrefH = remaining_data[2]
                    VrefL = remaining_data[3]
                    checksum = remaining_data[4]
                    dataEnd = remaining_data[5]
                    
                    testSum = VoutH + VoutL + VrefH + VrefL
                    # print(f"testSum: {testSum}")
                    if checksum != (testSum & 0xFF) :
                        print("校驗和錯誤，丟棄數據包")
                        continue
                    
                    # 轉換 ASCII 字符到數字 (假設是數字的 ASCII)
                    vout_h = ord(chr(VoutH))
                    vout_l = ord(chr(VoutL))
                    #vref_h = ord(chr(VrefH))
                    #vref_l = ord(chr(VrefL))
                    
                    # 計算電壓 Vout
                    vout = (vout_h * 256 + vout_l) / 1024.0 * 5.0
                    vout_mv = vout * 1000.0
                    #return vout, vout_h, vout_l, vref_h, vref_l, checksum, vout_mv
                    return vout
                else:
                    print("無效的數據包")
            else:
                # 如果不是起始字節，繼續讀取下一個字節
                continue
    
    def close(self):
        self.serial_port.close()

def calculate_dustDensity(voltage):
    # 依據公式 V / (0.1 mg/m^3)
    K = 100.0 / 0.35
    _dustDensity = K * voltage
    return _dustDensity

def main():
    com_port = input("請輸入COM端口 (例如 COM3): ")
    sensor = AirQualitySensor(com_port)
    
    try:
        while True:
            vout = sensor.read_data()
            dustDensity = calculate_dustDensity(vout)
            #print(f"Vout(H): 0x{vout_h:02X}, Decimal: {vout_h}")
            #print(f"Vout(L): 0x{vout_l:02X}, Decimal: {vout_l}")
            #print(f"Vref(H): 0x{vref_h:02X}, Decimal: {vref_h}")
            #print(f"Vref(L): 0x{vref_l:02X}, Decimal: {vref_l}")
            #print(f"checksum: {checksum}")
            #print(f"vout: {vout:.4f}V")
            #print(f"vout_mv: {vout_mv:.4f}mV")
            print(f"估算粉塵密度: {dustDensity:.4f} ug/m³")
            print("--------------------")
            time.sleep(5)  # 每秒讀取一次數據
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        sensor.close()

if __name__ == "__main__":
    main()
