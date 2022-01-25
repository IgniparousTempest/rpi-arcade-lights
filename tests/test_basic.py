import unittest
from unittest.mock import MagicMock, patch

MockBoard = MagicMock()
MockBusio = MagicMock()
MockPCA9685 = MagicMock()
modules = {
    "adafruit_pca9685": MockPCA9685,
    "adafruit_pca9685.PCA9685": MockPCA9685,
    "board": MockBoard,
    "board.SCL": MockBoard.SCL,
    "board.SDA": MockBoard.SDA,
    "busio": MockBusio,
    "busio.I2C": MockBusio.I2C,
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

import rpi_button_lights


class BasicTestCase(unittest.TestCase):
    def test_get_config(self):
        lights_configuration = rpi_button_lights.load_csv('../rpi_button_lights_database.csv')

        def lights(emulator, file_name):
            return rpi_button_lights.get_config(lights_configuration, emulator, file_name)

        self.assertEqual(lights('*', 'pacman.zip'), ['off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off'])
        self.assertEqual(lights('arcade', 'pacman.zip'), ['off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off', 'off'])
        self.assertEqual(lights('arcade', 'asterixaad.zip'), ['on', 'on', 'off', 'off', 'off', 'off', 'off', 'off', 'on', 'on', 'off', 'off', 'off', 'off', 'off', 'off'])
        self.assertEqual(lights('arcade', 'mslug.zip'), ['on', 'on', 'on', 'on', 'off', 'off', 'off', 'off', 'on', 'on', 'on', 'on', 'off', 'off', 'off', 'off'])
        self.assertEqual(lights('arcade', 'umk3.zip'), ['on', 'on', 'on', 'off', 'on', 'on', 'on', 'off', 'on', 'on', 'on', 'off', 'on', 'on', 'on', 'off'])
        self.assertEqual(lights('arcade', 'fake_game'), ['on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on'])

    def test_setting_lights(self):
        pca = rpi_button_lights.transmit_light_configuration('arcade', 'umk3.zip', csv_path='../rpi_button_lights_database.csv')
        output = [c.duty_cycle for c in pca.channels]
        for i in range(rpi_button_lights.NUMBER_OF_BUTTONS):
            self.assertEqual(output, [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0])


if __name__ == '__main__':
    unittest.main()
