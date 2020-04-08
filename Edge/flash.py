from serial import Serial
import time
import re


class FlashException(Exception):
    pass


class ResponseBuffer:

    def __init__(self):
        self.buffer = ""
        self.output = ""
        self.garbage = ""

    def __drain(self, connection: Serial, retain: bool = True):
        n = connection.in_waiting
        while n > 0:
            data = connection.read(n).decode("utf-8")
            if retain:
                self.buffer += data
            n = connection.in_waiting

    def __extract_messages(self):
        while "\n" in self.buffer:
            cutoff = self.buffer.index("\n")
            message = self.buffer[:cutoff].replace("\r", "\n")
            self.buffer = self.buffer[cutoff + 1:]
            self.garbage += message
            if ">>>" not in message and "..." not in message:
                self.output += message

    def skip_input(self, connection: Serial):
        self.__drain(connection, False)

    def handle_input(self, connection: Serial):
        self.__drain(connection)
        self.__evaluate_buffer(connection)

    def wait_for(self, connection: Serial, expected: str, retain=True):
        accum = ""
        while True:
            n = connection.in_waiting
            accum += connection.read(n).decode("utf-8")
            if expected in accum:
                break
        if retain:
            self.buffer += accum
        self.__evaluate_buffer(connection)

    def __evaluate_buffer(self, connection: Serial):
        self.__extract_messages()

        if "Error" in self.output:
            time.sleep(1)
            self.__drain(connection)
            self.buffer += "\n"
            self.__extract_messages()
            print(self.garbage)
            raise FlashException(self.output)


class ESP:

    def __init__(self, port: str):
        self.con = Serial(port=port, baudrate=115200)
        self.buffer = ResponseBuffer()

    def terminate_current_program(self):
        self.con.write(b'\r\x03\x03')
        self.buffer.wait_for(self.con, ">>>", False)

    def __send_statement(self, statement: str):
        self.con.write([ord(char) for char in statement + "\r"])
        self.buffer.wait_for(self.con, ">>>")
        # time.sleep(0.5)

    def soft_reboot(self):
        self.con.write(b'\x04')
        self.buffer.skip_input(self.con)  # TODO: Wait for reboot message?

    @staticmethod
    def __dir_from_file(file: str):
        elements = re.split("[/\\\\]", file)
        elements.pop()
        return "/".join(elements)

    def upload_files(self, files: [str]):
        self.terminate_current_program()
        previous_directory = ""

        for file in files:
            current_directory = self.__dir_from_file(file)
            if current_directory != previous_directory:
                self.__make_directory(current_directory)
            previous_directory = current_directory

            self.__upload_file(file)

        self.soft_reboot()

    def __make_directory(self, directory: str):
        print("Making directory {}".format(directory))
        path = re.split("[/\\\\]", directory)
        previous_path = ""

        self.__send_statement("import os")
        for folder in path:
            new_path = previous_path + "/" + folder
            self.__send_statement("if not '{}' in os.listdir('{}'): os.mkdir('{}')\r".format(folder,
                                                                                             previous_path,
                                                                                             new_path))
            previous_path = new_path

    def __upload_file(self, file: str):
        print("Flashing file {}".format(file))
        with open(file, "rb") as local_file:
            self.__send_statement("file = open('{}', 'wb', encoding = 'utf-8')".format(file))
            while True:
                data = local_file.read(1024)
                if not data:
                    break
                self.__send_statement("file.write({})".format(data))
            self.__send_statement("file.close()")


esp = ESP("COM4")
esp.upload_files(["main.py", "drivers/__init__.py", "connection/connection.py", "connection/mqtt_connection.py",
                  "connection/umqttsimple.py", "connection/wifi_connection.py", "connection/__init__.py",
                  "drivers/bh1750/bh1750.py", "drivers/bh1750/__init__.py", "drivers/hts221/hts221.py",
                  "drivers/mpu6050/mpu6050.py", "drivers/mpu6050/__init__.py", "drivers/hts221/usmbus.py",
                  "drivers/hts221/__init__.py"])

# self.perform_write(["outfile=open('{}','wb',encoding='utf-8')".format("coolfile.py"), "outfile.write({})".format(data), "outfile.close()"])
