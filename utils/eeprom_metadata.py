#!/usr/bin/env python3

# By Michael Bartlett, https://github.com/bartlettmic
"""
USAGE: Provide a compiled .bin file with -f
(can be generated with something like
avr-objcopy -I ihex $HEX_FILE -O binary $BIN_FILE )

But providing a .hex will run that command for you,
given that avr-objcopy is present on your device

This will prepend the necessary miniboot-header
bytes to a resulting .eeprom file which can be streamed
directly into an external EEPROM without further changes
to operate with miniboot.

This can also nicely print out the generated header data 
in human readable format.
"""

from time import time
from binascii import crc32, hexlify, unhexlify
from os import stat
from os.path import splitext
from subprocess import run as subrun

MINIBOOT_HEADER_PREAMBLE = "ABminiboot"
DEFAULT_APP_NAME = "APPNAME"
DEFAULT_OUTPUT_FILE = "output.eeprom"


def generate_miniboot_header(
    binary_file,
    application_name=DEFAULT_APP_NAME,
    output_file=DEFAULT_OUTPUT_FILE,
    print_header_result=False
):

    if not binary_file:
        return ""

    (mode, ino, dev, nlink, uid, gid, size,
     atime, mtime, ctime) = stat(binary_file)

    # Header protocol:
    #  0-9   = miniboot header (ABminiboot)
    #  10-19 = payload name (provided in arguments)
    #  20-23 = timestamp of sketch creation (creation time epoch)
    #  24-27 = timestamp of eeprom write (current timestamp epoch)
    #  28-31 = CRC32 (Checksum hex value)
    #  32-33 = Length (size of binary in Hex)

    with open(binary_file, "rb") as binary:
        payload = binary.read()

        payload_size = len(payload)

        # Truncase size to 2 bytes big-endian, i.e. uint16_t
        payload_size_hex = hexlify(payload_size.to_bytes(2, "big"))

        crc = crc32(payload)
        crc_hex = hexlify(crc.to_bytes(4, "big"))

        header_string = MINIBOOT_HEADER_PREAMBLE
        header_hex = hexlify(bytes(header_string, "utf-8"))

        # App name string can only be 10 bytes long
        app_name = str(application_name).ljust(10, " ")[:10]
        app_hex = hexlify(bytes(app_name, "utf-8"))

        # Unix epoch timestamp of payload"s creation time
        ctime_hex = hexlify(ctime.to_bytes(4, "big"))

        current_epoch = int(time())
        epoch_hex = hexlify(current_epoch.to_bytes(4, "big"))

        eeprom_metadata = header_hex + app_hex + \
            ctime_hex + epoch_hex + crc_hex + payload_size_hex

        eeprom_metadata = unhexlify(eeprom_metadata)

        eeprom_payload = eeprom_metadata + payload

        with open(output_file, "w+b") as firmware:
            firmware.write(eeprom_payload)

        if print_header_result:
            print("Miniboot header:   ", header_string)
            print("Application name:  ", app_name)
            print("Created timestamp: ", ctime)
            print("Current timestamp: ", current_epoch)
            print("CRC32:             ", crc)
            print("Original binary size:", payload_size)
            print("EEPROM payload size: ", len(eeprom_payload))
            print(f"{binary_file} -> {output_file}")


def parserArguments():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate miniboot header from a compiled binary.')
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='path to binary file from which to generate a header',
        required=True
    )

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='output file path to write streamable header+binary payload bytes',
        default=DEFAULT_OUTPUT_FILE,
        required=False
    )

    parser.add_argument(
        '-a',
        '--appname',
        type=str,
        help='string to bake into miniboot header as the applicaiton name (justified to exactly 10 chars)',
        default=DEFAULT_APP_NAME,
        required=False
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='also print the generated header data in human-readable format',
    )
    
    parser.add_argument(
        '-d',
        '--dont_convert',
        action='store_true',
        help='don\'t convert a .hex to a .bin with avr-objcopy automatically',
    )
    return parser


def getArguments():
    binary_file = args["file"]
    application_name = args['appname']
    output_file = args['output']
    print_header_result = args['verbose']
    dont_auto_convert = args['dont_convert']
    return binary_file, application_name, output_file, print_header_result, dont_auto_convert

def check_if_binary(check):
    file_name, file_ext = splitext(check)
    if file_ext == ".bin":
        return True, check
    elif file_ext == ".hex":
        if not dont_auto_convert:
            subrun(['avr-objcopy', '-I', 'ihex', binary_file, '-O', 'binary', file_name+'.bin'], check=True)
            return True, (file_name+'.bin')
        else:
            raise ValueError('Given file was .hex, but not allowed to convert')
    else:
        return False, check

if __name__ == "__main__":
    parser = parserArguments()

    args = vars(parser.parse_args())

    binary_file, application_name, output_file, print_header_result, dont_auto_convert = getArguments()
    
    is_valid, new_filepath = check_if_binary(binary_file)
    if not is_valid:
        raise TypeError('Given file was not a .bin or a .hex')

    generate_miniboot_header(
        new_filepath, application_name, output_file, print_header_result)
