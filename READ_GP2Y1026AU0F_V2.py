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
                    VoutH = remaining_data[0]
                    VoutL = remaining_data[1]
                    VrefH = remaining_data[2]
                    VrefL = remaining_data[3]
                    checksum = remaining_data[4]
                    
                    # 計算校驗和
                    testSum = VoutH + VoutL + VrefH + VrefL
                    if checksum != (testSum & 0xFF):
                        print("校驗和錯誤，丟棄數據包")
                        continue
                    
                    # 計算電壓 Vout
                    vout = (VoutH * 256 + VoutL) / 1024.0 * 5.0
                    return vout
                else:
                    print("無效的數據包")
            else:
                continue
    
    def close(self):
        self.serial_port.close()

def calculate_dustDensity(voltage):
    # 計算粉塵濃度, 依據公式 V / (0.1 mg/m³)
    K = 100.0 / 0.35  # 每 0.35V 對應 100 µg/m³
    dust_density = K * voltage
    return dust_density

def main():
    com_port = input("請輸入COM端口 (例如 COM3): ")
    sensor = AirQualitySensor(com_port)
    
    try:
        while True:
            vout = sensor.read_data()
            dustDensity = calculate_dustDensity(vout)
            print(f"估算粉塵密度: {dustDensity:.4f} µg/m³")
            print("--------------------")
            time.sleep(5)  # 每5秒讀取一次數據
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        sensor.close()

if __name__ == "__main__":
    main()
