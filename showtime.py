from machine import UART, Pin
import utime, time

# WIFI information
SSID = 'my_home_network_SSID'
password = 'my_home_network_password'

# NTP server information
ntp_server = 'pool.ntp.org'
ntp_port = 123

# Brussels timezone information
std_time_offset = 1 * 3600  # Standard time offset for Brussels is UTC+1
dst_time_offset = 2 * 3600  # Daylight saving time offset for Brussels is UTC+2

# Daylight saving time start and end dates for Brussels (last Sunday in March to last Sunday in October)
def is_dst(date):
    print(date)
    year, month, day, hour, minute, second, weekday, yearday = date
    # DST starts on the last Sunday in March
    if month == 3:
        last_sunday = max(week for week in range(25, 32) if utime.localtime(utime.mktime((year, month, week, 0, 0, 0, 0, 0)))[6] == 6)
        return day >= last_sunday
    # DST ends on the last Sunday in October
    elif month == 10:
        last_sunday = max(week for week in range(25, 32) if utime.localtime(utime.mktime((year, month, week, 0, 0, 0, 0, 0)))[6] == 6)
        return day < last_sunday
    # DST is in effect from April to September
    return 4 <= month <= 9

# Configure UART for communication with ESP8285
esp_uart = UART(0, 115200)

# Function to send AT commands
def esp_sendCMD(cmd, ack, timeout=5000):
    esp_uart.write(cmd + '\r\n')
    i_t = utime.ticks_ms()
    while (utime.ticks_ms() - i_t) < timeout:
        s_get = esp_uart.read()
        if s_get:
            try:
                s_get = s_get.decode()
                print(s_get)
                if s_get.find(ack) >= 0:
                    return True
            except UnicodeError:
                continue  # Handle binary data without decoding
    return False

# Function to initialize ESP8285 and connect to WiFi
def esp_init():
    esp_uart.write('+++')   # Exit transparent mode if in it
    time.sleep(1)
    if esp_uart.any() > 0:
        esp_uart.read()
    if not esp_sendCMD("AT", "OK"):
        print("ESP8285 not responding")
        return False
    if not esp_sendCMD("AT+CWMODE=1", "OK"):
        print("Failed to set WiFi mode")
        return False
    if not esp_sendCMD(f'AT+CWJAP="{SSID}","{password}"', "OK", 20000):
        print("Failed to connect to WiFi")
        return False
    if not esp_sendCMD("AT+CIPMODE=0", "OK"):  # Ensure normal mode is set
        print("Failed to set normal mode")
        return False
    return True

# Function to get time from NTP server
def get_ntp_time():
    # Close any previous connections
    esp_sendCMD("AT+CIPCLOSE", "OK")

    if not esp_sendCMD(f'AT+CIPSTART="UDP","{ntp_server}",{ntp_port}', "OK", 10000):
        print("Failed to start UDP connection")
        return None

    ntp_packet = bytearray(48)
    ntp_packet[0] = 0x1B  # Set the first byte to 0x1B for NTP request

    if not esp_sendCMD(f'AT+CIPSEND={len(ntp_packet)}', ">"):
        print("Failed to initiate sending data")
        return None

    esp_uart.write(ntp_packet)
    print("NTP request sent")

    # Wait for response
    i_t = utime.ticks_ms()
    response = b''
    while (utime.ticks_ms() - i_t) < 5000:
        s_get = esp_uart.read()
        if s_get:
            response += s_get
            if len(response) >= 48:
                # Find the actual NTP data start
                start_index = response.find(b'\x1c')
                if start_index == -1:
                    print("NTP data not found in response")
                    return None
                
                ntp_data = response[start_index:start_index + 48]
                if len(ntp_data) < 48:
                    print("Incomplete NTP data")
                    return None

                # Parse the NTP time from the response
                ntp_time = int.from_bytes(ntp_data[40:44], 'big')
                # Convert NTP time to UNIX time
                unix_time = ntp_time - 2208988800

                # Determine if DST is in effect and adjust the time offset
                if is_dst(utime.localtime(unix_time)):
                    local_time = unix_time + dst_time_offset
                else:
                    local_time = unix_time + std_time_offset

                return local_time

    print("Failed to get NTP response")
    return None

# Function to format time
def format_time(timestamp):
    t = utime.localtime(timestamp)
    return '{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[3], t[4], t[5])

# Main program
if __name__ == "__main__":
    if esp_init():
        print("ESP8285 initialized and connected to WiFi")
        ntp_time = get_ntp_time()
        if ntp_time:
            print("Current time:", format_time(ntp_time))
        else:
            print("Failed to get time from NTP server")
    else:
        print("Failed to initialize ESP8285")

