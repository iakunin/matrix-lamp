#pragma once

#undef delay

#define FASTLED_INTERNAL // remove annoying pragma messages

#include "FastLED.h"

namespace esphome {
namespace matrix_lamp {

// *****************************************************************************************************************************************************************
static CRGB* leds;

// *****************************************************************************************************************************************************************
static void InitLeds(int size)
{
  if (leds == NULL) 
  {
    leds = new CRGB[size];
  }
}

// *****************************************************************************************************************************************************************
static void FreeLeds()
{
  delete [] leds;
  leds = nullptr;
}

}  // namespace matrix_lamp
}  // namespace esphome
