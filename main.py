from machine import UART, Pin
import utime, time

# WIFI information
SSID = 'my_home_network_SSID'
password = 'my_home_network_pass'

# ntfy.sh channel information
url = '/my_ntfy_channel'
host = 'ntfy.sh'
data = 'demo'

# Configure UART for communication with ESP8285
esp_uart = UART(0, 115200)

# Function to send AT commands
def esp_sendCMD(cmd, ack, timeout=5000):
    esp_uart.write(cmd + '\r\n')
    i_t = utime.ticks_ms()
    while (utime.ticks_ms() - i_t) < timeout:
        s_get = esp_uart.read()
        if s_get:
            s_get = s_get.decode()
            print(s_get)
            if s_get.find(ack) >= 0:
                return True
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

# Function to send HTTP POST request
def send_post_request(host, url, data):
    # Close any previous connections
    esp_sendCMD("AT+CIPCLOSE", "OK")

    if not esp_sendCMD(f'AT+CIPSTART="TCP","{host}",80', "OK", 10000):
        print("Failed to start TCP connection")
        return False

    http_request = (
        "POST {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: {}\r\n"
        "\r\n"
        "{}\r\n"
    ).format(url, host, len(data), data)

    if not esp_sendCMD(f'AT+CIPSEND={len(http_request)}', ">"):
        print("Failed to initiate sending data")
        return False

    esp_uart.write(http_request)
    print("HTTP POST request sent")
    return True

# Main program
if __name__ == "__main__":
    if esp_init():
        print("ESP8285 initialized and connected to WiFi")
        if send_post_request(host, url, data):
            print("HTTP POST request sent successfully")
        else:
            print("Failed to send HTTP POST request")
    else:
        print("Failed to initialize ESP8285")
