"""Pin definitions for the Rock Pi 4."""

from adafruit_blinka.microcontroller.rockchip.rk3399 import pin

D3 = pin.GPIO2_A7  # /I2C7_SDA/PIN 71/
D5 = pin.GPIO2_B0  # /I2C7_SCL/PIN 72/
D7 = pin.GPIO2_B3  # /SPI2_CLK/PIN 75/
D8 = pin.GPIO4_C4  # /UART2_TXD/PIN 148/
D10 = pin.GPIO4_C3  # /UART2_RXD/PIN 147/
D11 = pin.GPIO4_C2  # /PWM0/PIN 146/
D13 = pin.GPIO4_C6  # /PWM1/PIN 150/
D15 = pin.GPIO4_C5  # /SPDIF_TX/PIN 149/
D16 = pin.GPIO4_D2  # /PIN 154/
D17 = pin.GPIO4_D4  # /PIN 156/
D19 = pin.GPIO1_B0  # /UART4_TXD/SPI1_TXD/PIN 40/
D21 = pin.GPIO1_A7  # /UART4_RXD/SPI1_RXD/PIN 39/
D22 = pin.GPIO4_D5  # /PIN 157/
D23 = pin.GPIO1_B1  # /SPI1_CLK/PIN 41/
D24 = pin.GPIO1_B2  # /SPI1_CS/PIN 42/
D27 = pin.GPIO2_A0  # /I2C2_SDA/PIN 64/
D28 = pin.GPIO2_A1  # /I2C2_SCL/PIN 65/
D29 = pin.GPIO2_B2  # /I2C6_SCL/SPI2_TXD/PIN 74/
D31 = pin.GPIO2_B1  # /I2C6_SDA/SPI2_RXD/PIN 73/
D32 = pin.GPIO3_C0  # /SPDIF_TX/UART3_CTS/PIN 112/
D33 = pin.GPIO2_B4  # /SPI2_CS/PIN 76/
D35 = pin.GPIO4_A5  # /I2S1_LRCK_TX/PIN 133/
D36 = pin.GPIO4_A4  # /I2S1_LRCK_RX/PIN 132/
D37 = pin.GPIO4_D6  # /PIN 158/
D38 = pin.GPIO4_A6  # /I2S1_SDI/PIN 134/
D40 = pin.GPIO4_A7  # /I2S1_SDO/PIN 135/

SDA2 = D27
SCL2 = D28

SDA6 = D31
SCL6 = D29

SDA7 = D3
SCL7 = D5

SDA = SDA2
SCL = SCL2

SCLK = D7
MOSI = D29
MISO = D31
CS = D33
SCK = SCLK

UART2_TX = D8
UART2_RX = D10

UART4_TX = D19
UART4_RX = D21

UART_TX = UART2_TX
UART_RX = UART2_RX

PWM0 = pin.PWM0
PWM1 = pin.PWM1

ADC_IN0 = pin.ADC_IN0
