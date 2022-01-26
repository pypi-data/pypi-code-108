import threading

class DriveMode:
    def __init__(self, _zumi):
        self.zumi = _zumi
        self.current_key = ''
        self.drive_thread = ''

    def __move_zumi(self):
        desired_angle = self.zumi.read_z_angle()

        while self.current_key != '':
            if self.current_key == "ArrowUp":
                k_p = 2.9
                k_i = 0.0
                k_d = 0.0
                accuracy = 5
                self.zumi.drive_at_angle(80, 40, desired_angle, k_p, k_d, k_i, accuracy)
            elif self.current_key == "ArrowDown":
                k_p = 2.9
                k_i = 0.0
                k_d = 0.0
                accuracy = 5
                self.zumi.drive_at_angle(80, -40, desired_angle, k_p, k_d, k_i, accuracy)
            elif self.current_key == "ArrowLeft":
                k_p = 0.6
                k_i = 0.000
                k_d = 0.0
                accuracy = 3
                self.zumi.drive_at_angle(10, 0, desired_angle + 360, k_p, k_d, k_i, accuracy)
            elif self.current_key == "ArrowRight":
                k_p = 0.6
                k_i = 0.0
                k_d = 0.0
                accuracy = 3
                self.zumi.drive_at_angle(10, 0, desired_angle - 360, k_p, k_d, k_i, accuracy)
            else:
                break
            self.zumi.play_note(0, 0)

        self.zumi.stop()

    def zumi_direction(self, input_key):
        if input_key != self.current_key:
            self.current_key = input_key
            self.drive_thread = threading.Thread(target=self.__move_zumi)
            self.drive_thread.start()

    def zumi_stop(self):
        self.current_key = ''
        if type(self.drive_thread) != str and self.drive_thread.isAlive():
            self.drive_thread.join()
        self.zumi.stop()


