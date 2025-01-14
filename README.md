# ESPHome Matrix Lamp
[![esphome_badge](https://img.shields.io/static/v1?label=ESPHome&message=Components&color=blue&logo=esphome)](https://github.com/andrewjswan/esphome-components/)
[![esphome_badge](https://img.shields.io/static/v1?label=ESPHome&message=Config&color=blue&logo=esphome)](https://esphome.io/)
[![matrix-lamp_badge](https://img.shields.io/badge/Matrix-Lamp-orange.svg)](https://github.com/andrewjswan/matrix-lamp/)
[![esp32_arduino](https://img.shields.io/badge/ESP32-Arduino-darkcyan.svg)](https://esphome.io/)
[![Build](https://github.com/andrewjswan/matrix-lamp/actions/workflows/build.yaml/badge.svg)](https://github.com/andrewjswan/matrix-lamp/actions/workflows/build.yaml)
[![GitHub](https://img.shields.io/github/license/andrewjswan/matrix-lamp?color=blue)](https://github.com/andrewjswan/matrix-lamp/blob/main/LICENSE)
[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/andrewjswan/matrix-lamp?include_prereleases)](https://github.com/andrewjswan/matrix-lamp/releases)
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/downloads-pre/andrewjswan/matrix-lamp/latest/total?label=release@downloads)](https://github.com/andrewjswan/matrix-lamp/releases)
[![StandWithUkraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)

## Description
A compilation of firmware adaptations based on the original idea of Gyver Lamp, for ESPHome.

## Firmware
You can install the firmware using [ESPHome](https://esphome.io/) using one of the ready-made configuration files or use [**MatrixLamp - ESP Web Tools**](https://andrewjswan.github.io/matrix-lamp/) - a convenient tool for installing and updating the firmware of ESP32 devices in the browser.

## Hardware
|       |ESP32  |ESP32C3 |ESP32S2 | ESP32S3 | 
|-------|-------|--------|--------|---------|
|LED    |GPIO3  |GPIO3   |GPIO3   |GPIO3    |
|Button |GPIO35 |GPIO10  |GPIO35  |GPIO35   |

### Settings override

If you need to change any settings, you can override them using `substitutions`, for example:
```Yaml
substitutions:
  pin_pullup: "false"
  pin_leds: "GPIO32"
  color_correct_bright: "70%"
```

### Matrix Lamp Component
```Yaml
external_components:
  - source:
      type: git
      url: https://github.com/andrewjswan/matrix-lamp
      ref: main
    components: [matrix_lamp]

matrix_lamp:
  id: matrix
  width: 16               # Matrix width
  height: 16              # Matrix height
  random: true            # The effects will be turned on at random (but successful) Speed ​nd Scale settings
  scale_id: matrix_scale  # Template number identifier for scale control
  speed_id: matrix_speed  # Template number identifier for speed control
  matrix_orientation: 5   # Matrix orientation [0..7] If not specified, it will be possible to change it on the fly using the SetMatrixOrientation function
  matrix_type: 0          # Matrix type [0..1] If not specified, it will be possible to change it on the fly using the SetMatrixType function


light:
  - platform: ...
    effects:
...
      - matrix_lamp_effect:
          name: Peacock
          mode: RAINBOW_STRIPE

      - matrix_lamp_effect:
          name: Fire 2021
          mode: FIRE_2021
...
```

<br />

> [!TIP]
> ESPHome [configuration](https://github.com/andrewjswan/esphome-config)
