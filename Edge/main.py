from connection import WifiConnection
import utime

utime.sleep(5)
print("Hello")
conn = WifiConnection("gHpFHJ3k", "5fmh573a", "192.168.0.24", 5000)
conn.connect()
while True:
    conn.send("", None)
    utime.sleep(1)