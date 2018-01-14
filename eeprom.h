#pragma once

#include "bootloader.h"
#include <avr/eeprom.h>

#if 0
void writeToInternalEeprom(const uint16_t data){
  eeprom_write_byte (reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE+4),data>>8);
  eeprom_write_byte (reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE+5),data);
  boot_spm_busy_wait();
}
#endif // #if 0

void writeLatestApplicationTimestampToInternalEeprom(
    const uint32_t latest_timestamp) {
  eeprom_write_byte(
      reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE),
      latest_timestamp >> 24);
  eeprom_write_byte(
      reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE + 1),
      latest_timestamp >> 16);
  eeprom_write_byte(
      reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE + 2),
      latest_timestamp >> 8);
  eeprom_write_byte(
      reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE + 3),
      latest_timestamp);
  boot_spm_busy_wait();
}

uint32_t readLatestApplicationTimestampFromInternalEeprom() {
  uint32_t result =
      static_cast<uint32_t>(eeprom_read_byte(
          reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE)))
      << 24;
  result |= static_cast<uint32_t>(eeprom_read_byte(reinterpret_cast<uint8_t *>(
                EEPROM_CONFIGURATION_START_BYTE + 1)))
            << 16;
  result |= static_cast<uint32_t>(eeprom_read_byte(reinterpret_cast<uint8_t *>(
                EEPROM_CONFIGURATION_START_BYTE + 2)))
            << 8;
  result |= static_cast<uint32_t>(eeprom_read_byte(
      reinterpret_cast<uint8_t *>(EEPROM_CONFIGURATION_START_BYTE + 3)));
  boot_spm_busy_wait();
  return result;
}
