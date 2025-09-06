## Pin scheme

|       |ESP32  |ESP32C3 |ESP32S2 | ESP32S3 | 
|-------|-------|--------|--------|---------|
|LED    |GPIO3  |GPIO3   |GPIO3   |GPIO3    |
|Button |GPIO35 |GPIO10  |GPIO35  |GPIO35   |

## Settings override

If you need to change any settings, you can override them using `substitutions`, for example:

!!! example
    ``` { .yaml .copy .annotate }
    substitutions:
      pin_pullup: "false"
      pin_leds: "GPIO32"
      color_correct_bright: "70%"
    ```
