from datetime import datetime
import os

class CoolPrinter:
    def __init__(self, save_file=None, show_time=False, show_file=False):
        self.figures = {
            "Pause": "||",
            "Success": '✔',
            "Error": '✖',
            "Important": '★',
            "Debug": '◼',
            "Stop": '◼',
            "Start": '▶',
            "Bullet": '●',
            "Ellipsis": '…',
            "PointerSmall": '›',
            "Info": 'ℹ',
            "Warning": '⚠',
            "Heart": '♥',
            "RadioOn": '◉',
            "RadioOff": '◯'
        }

        self.colors = {
            "green": "\u001b[32;1m",
            "grey": "\u001b[38;5;240m",
            "red": "\u001b[38;5;196m",
            "yellow": "\u001b[38;5;11m",
            "purple": "\u001b[38;5;127m",
            "dark blue": "\u001b[38;5;33m",
            "cyan": "\u001b[36;1m",
            "blue": "\u001b[38;5;39m",
            "pink": "\u001b[38;5;198m",
            "reset": "\u001b[0m"
        }
        self.reset = self.colors.get("reset")

        self.txt_decorations = {
            "bold": "\u001b[1m",
            "underline": "\u001b[4m",
            "reversed": "\u001b[7m"
        }

        self.show_time = show_time
        self.show_file = show_file

        if save_file != None:
            self.save_file = open(save_file, "w")
            self.info("文件将保存在",save_file,"中\n")
        else:
            self.save_file = None


    def colors_text(self, text, colored):
        color = self.colors[colored]
        message_colored = f"{color}{text}{self.reset}"
        return message_colored

    def prefix_icon(self, text, colored):
        icon = self.figures[text]
        msg = f"[{icon} {text}]:  "
        colored_msg = self.colors_text(msg, colored)
        return colored_msg

    def print(self, prefix_icon, *values):

        if self.save_file:
            print(*values,file=self.save_file)
        if self.show_time:
            msg = datetime.now().strftime("%m.%d-%H:%M:%S")
            cur_time = self.colors_text(msg,"cyan")
            print(cur_time,end=" ")
        if self.show_file:
            cur_file = self.colors_text(__file__, 'cyan')
            print(cur_file,end=" ")

        print(prefix_icon, *values)


    def warning(self, *values):
        prefix_icon = self.prefix_icon("Warning", "yellow")
        self.print(prefix_icon, *values)

    def error(self, *values):
        prefix_icon = self.prefix_icon("Error", "red")
        self.print(prefix_icon, *values)

    def info(self, *values):
        prefix_icon = self.prefix_icon("Info", "blue")
        self.print(prefix_icon, *values)

    def debug(self, *values):
        prefix_icon = self.prefix_icon("Debug", "blue")
        self.print(prefix_icon, *values)

    def start(self, *values):
        prefix_icon = self.prefix_icon("Start", "green")
        self.print(prefix_icon, *values)

    def stop(self, *values):
        prefix_icon = self.prefix_icon("Stop", "red")
        self.print(prefix_icon, *values)

    def success(self, *values):
        prefix_icon = self.prefix_icon("Success", "green")
        self.print(prefix_icon, *values)

    def important(self, *values):
        prefix_icon = self.prefix_icon("Important", "dark blue")
        self.print(prefix_icon, *values)


    def __del__(self):
        if self.save_file:
            self.save_file.close()

    def __str__(self):
        print("I'am a cool printer")

if __name__ == "__main__":
    printer = CoolPrinter(save_file="log.txt",show_time=True,show_file=True)

    printer.warning("我是一个警告")
    printer.error("哦不! 出现了一些错误")
    printer.start("准备就绪,开始启动!")
    printer.debug("慢慢Debug中")
    printer.success("启动成功!")
    printer.important("出现了一个重大事件!")
    printer.stop("运行结束!")
