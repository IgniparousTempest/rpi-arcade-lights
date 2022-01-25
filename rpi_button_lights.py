#!/usr/bin/env python3
import csv
import os
import sys
from typing import Dict, List

from adafruit_pca9685 import PCA9685
import board
import busio
from tabulate import tabulate

NUMBER_OF_BUTTONS = 8 * 2

PWM_OFF = 0x0000  # 0% duty cycle
PWM_ON = 0xFFFF  # 100% duty cycle

LightsConfiguration = Dict[str, Dict[str, List[str]]]


def load_csv(csv_path: str) -> LightsConfiguration:
    """
    Loads the CSV file containing the buttons used by each game.
    :param csv_path: path to the CSV file.
    :return: parsed button lights configuration.
    """
    global NUMBER_OF_BUTTONS
    configuration = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(reader)  # Skip header
        NUMBER_OF_BUTTONS = len(header) - 2
        for row in reader:
            system_name, rom_name = row[0:2]
            if system_name not in configuration:
                configuration[system_name] = {}
            configuration[system_name][rom_name] = row[2:]
    return configuration


def get_config(configuration: LightsConfiguration, system_name: str, rom_name: str) -> List[str]:
    """
    Read light config from configuration object.
    :param configuration: The parsed configuration object, read from CSV file.
    :param system_name: name of the system the game is native to.
    :param rom_name: file name of ROM.
    :return: button light configuration for specified game.
    """
    # Get roms on an system
    try:
        system = configuration[system_name]
    except:
        # Get game on any system
        try:
            return configuration['*'][rom_name]
        except:
            return ['on'] * NUMBER_OF_BUTTONS
    # Get game on that system
    try:
        return system[rom_name]
    except:
        return ['on'] * NUMBER_OF_BUTTONS


def print_debug_lights(lights: List[str], file=sys.stdout):
    """
    Prints the light configuration to the console to help debugging.
    :param lights: the lights from the config object.
    :param file: The file output for the print statements.
    """
    button_headers = [str(i) for i in range(1, NUMBER_OF_BUTTONS + 1)]
    print(tabulate([lights], headers=button_headers, tablefmt='orgtbl'), file=file)

    def character(state: str):
        return '●' if state == 'on' else '○'

    l = [character(btn) for btn in lights]

    print(f'┌───────────┐', file=file)
    print(f'│{l[0]}{l[1]}{l[2]}{l[3]}   {l[8]}{l[9]}{l[10]}{l[11]}│', file=file)
    print(f'│{l[4]}{l[5]}{l[6]}{l[7]}   {l[12]}{l[13]}{l[14]}{l[15]}│', file=file)
    print(f'└───────────┘', file=file)


def initialise_pca9685() -> PCA9685:
    """
    Sets up the I2C device.
    """
    # Initialisation
    i2c_bus = busio.I2C(board.SCL, board.SDA)  # Create the I2C bus interface.
    pca = PCA9685(i2c_bus)  # Create a simple PCA9685 class instance.
    pca.frequency = 60  # Set the PWM frequency to 60hz.

    return pca


def transmit_light_all_on() -> PCA9685:
    """
    Switches all the lights on. Intended to be run after the game is quit.
    """
    # Initialisation
    pca = initialise_pca9685()

    # Set PWM of lights
    for i, light in range(NUMBER_OF_BUTTONS):
        pca.channels[i].duty_cycle = PWM_ON

    return pca


def transmit_light_configuration(system_name: str, rom_filename: str, csv_path: str = 'rpi_button_lights_database.csv') -> PCA9685:
    """
    Main function to turn the appropriate lights on and off. Intended to be called from runcommand-onstart.sh
    :param system_name: name of the system the game is native to.
    :param rom_filename: file name of ROM.
    :param csv_path: path to the CSV file.
    """
    # Initialisation
    pca = initialise_pca9685()

    # Load configuration
    lights_configuration = load_csv(csv_path)
    lights = get_config(lights_configuration, system_name, rom_filename)
    print(f'setting button lights for "{rom_filename}" on "{system_name}"', file=sys.stderr)
    print_debug_lights(lights, file=sys.stderr)

    # Set PWM of lights
    for i, light in zip(range(len(lights)), lights):
        pca.channels[i].duty_cycle = PWM_ON if light == 'on' else PWM_OFF

    return pca


if __name__ == '__main__':
    # The parameters are provided by runcommand-onstart, see https://retropie.org.uk/docs/Runcommand/
    argc = len(sys.argv)
    system_name = sys.argv[1] if argc > 1 else ''
    emulator_name = sys.argv[2] if argc > 2 else ''
    rom_path = sys.argv[3] if argc > 3 else ''
    launch_command = sys.argv[4] if argc > 4 else ''
    rom_filename = os.path.basename(rom_path)

    if argc <= 1:
        exit(1)

    if argc == 1 and system_name == 'reset':
        transmit_light_all_on()
    else:
        transmit_light_configuration(system_name, rom_filename, csv_path='/usr/local/etc/rpi_button_lights_database.csv')
