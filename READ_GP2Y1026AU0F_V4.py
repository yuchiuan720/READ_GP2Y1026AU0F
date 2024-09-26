import serial
import time

class AirQualitySensor:
    def __init__(self, com_port, baud_rate=2400):
        self.serial_port = serial.Serial(com_port, baud_rate, timeout=1)
        self.error_count = 0  # 用來計算異常狀態
        self.max_errors = 5  # 設置異常次數閾值
    
    def read_data(self):
        # 清空緩衝區，以防有殘留的數據
        self.serial_port.reset_input_buffer()
        
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
                        self.error_count += 1
                        if self.error_count >= self.max_errors:
                            print("傳感器異常：連續多次校驗錯誤")
                            return None  # 返回異常狀態
                        continue
                    
                    # 如果校驗成功，重置異常計數
                    self.error_count = 0
                    
                    # 計算電壓 Vout
                    vout = (VoutH * 256 + VoutL) / 1024.0 * 5.0
                    return vout
                else:
                    print("無效的數據包")
                    self.error_count += 1
                    if self.error_count >= self.max_errors:
                        print("傳感器異常：多次無效數據包")
                        return None  # 返回異常狀態
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
    # 設置預設的COM端口
    default_com_port = "COM5"
    
    com_port = input(f"請輸入COM端口 (預設: {default_com_port}): ")
    
    # 如果沒有輸入，使用預設的COM端口
    if not com_port:
        com_port = default_com_port
        print(f"使用預設COM端口: {com_port}")
    
    sensor = AirQualitySensor(com_port)
    
    try:
        while True:
            vout = sensor.read_data()
            if vout is None:  # 檢查是否存在傳感器異常
                print("傳感器異常，停止讀取")
                break
            dustDensity = calculate_dustDensity(vout)
            print(f"估算粉塵密度: {dustDensity:.4f} µg/m³")
            print("--------------------")
            time.sleep(1)  # 每5秒讀取一次數據
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        sensor.close()

if __name__ == "__main__":
    main()
