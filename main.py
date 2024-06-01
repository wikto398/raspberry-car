import paramiko
from pynput import keyboard
import json

class Controler:
    def __init__(self) -> None:
        self.hostname = "raspberrypi"
        self.port = 22
        with open("auth.json") as f:
            data = json.load(f)
            self.username = data["username"]
            self.password = data["password"]

        # Układ kół
        # 10 lewy tyl
        # 9 prawy przod
        # 22 lewo przod
        # 25 prawo tyl
        self.pins = {
            "w": [9, 22],
            "s": [10, 25],
            "d": [25, 22],
            "a": [10, 9]
        }

        self.control_pin = 14

        self.client = self.connect()

        self.pressed_key = None

        for key in self.pins:
            self.enable_pin(self.pins[key])

        

    # Connection and pin handling
    def enable_pin(self, number: list)  -> None:
        self.client.exec_command(f'raspi-gpio set {number[0]},{number[1]} op pn dl')

    def connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.hostname, self.port, self.username, self.password)
            print("Connection successful!")
            client.exec_command(f'raspi-gpio set {self.control_pin} op pn dh')
        except:
            print("Couldn't connect to target, ending...")
        return client
    
    
    def pin_control(self, pins, mode) -> None:
        self.client.exec_command(f'raspi-gpio set {pins} {mode}')

    # Keyboard handling 
    def on_press(self, key):
        try:
            if key == keyboard.Key.esc:
                return False
            if self.pressed_key is None and key.char in self.pins:
                self.pressed_key = key.char
                self.pin_control(f"{self.pins[key.char][0]},{self.pins[key.char][1]}", "dh")
        except AttributeError:
            # Handle special keys if needed
            pass

    def on_release(self, key):
        try:
            if key.char == self.pressed_key:
                self.pressed_key = None
                self.pin_control(f"{self.pins[key.char][0]},{self.pins[key.char][1]}", "dl")
        except AttributeError:
            # Handle special keys if needed
            pass

    # Driving function
    def drive(self):
        print("Car started!")
        print("Control with W, A, S and D")
        print("Press ESC to end")
        try:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()
        except:
            pass
        print("Car stopped...")
        for key in self.pins:
            self.pin_control(self.pins[key], "dl")
        self.client.exec_command(f'raspi-gpio set {self.control_pin} op pn dl')
        self.client.close()
        print("Disconnected...")

if __name__ == "__main__":
    car = Controler()
    car.drive()