#include "esphome.h"
#include "common.h"
#include "constants.h"
#include "utility.h"
#include "effect_ticker.h"
#include "fastled_helper.h"

namespace esphome {
namespace matrix_lamp {

void MatrixLamp::setup() {
   memset(matrixValue, 0, sizeof(matrixValue)); // это массив для эффекта Огонь. странно, что его нужно залить нулями

  randomSeed(micros());
  restoreSettings();

  loadingFlag = true;
}  // setup()

void MatrixLamp::dump_config() {
  ESP_LOGCONFIG(TAG, "MatrixLamp version: %s", MATRIX_LAMP_VERSION);
  ESP_LOGCONFIG(TAG, "             Width: %s", WIDTH);
  ESP_LOGCONFIG(TAG, "            Height: %s", HEIGHT);
  #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
  ESP_LOGCONFIG(TAG, "Random mode enable: YES");
  #else
  ESP_LOGCONFIG(TAG, "Random mode enable: NO");
  #endif
  ESP_LOGCONFIG(TAG, "       Orientation: %s", ORIENTATION);
  ESP_LOGCONFIG(TAG, "       Matrix Type: %s", MATRIX_TYPE);
  ESP_LOGCONFIG(TAG, "   Number of modes: %s", MODE_AMOUNT);
}  // dump_config()

void MatrixLamp::set_scale(esphome::template_::TemplateNumber *scale) {
  this->scale = scale;
} // set_scale()

void MatrixLamp::set_speed(esphome::template_::TemplateNumber *speed) {
  this->speed = speed;
} // set_speed()

void MatrixLamp::ResetCurrentEffect()
{
  currentMode = MODE_AMOUNT;
}

void MatrixLamp::SetScaleForEffect(uint8_t mode, uint8_t scale)
{
  modes[mode].Scale = scale;
}

void MatrixLamp::SetSpeedForEffect(uint8_t mode, uint8_t speed)
{
  modes[mode].Speed = speed;
}

void MatrixLamp::SetScaleFromColorForEffect(uint8_t mode, Color color)
{
  if (color.red == 255 && color.green == 255 && color.blue == 255)
  {
    this->SetScaleForEffect(EFF_SCANNER, 0);
  }
  else
  {
    int hue;
    float saturation, value;
    rgb_to_hsv(color.red / 255, color.green / 255, color.blue / 255, hue, saturation, value);

    this->SetScaleForEffect(EFF_SCANNER, remap(hue, 0, 360, 1, 100));
  }
}

void MatrixLamp::SetCustomEffect(uint8_t mode)
{
  custom_eff = mode;
}

#ifndef ORIENTATION
bool MatrixLamp::SetMatrixOrientation(uint8_t orientation)
{
  if (orientation >= 1 && orientation <= 8)
  {
    ORIENTATION = orientation - 1;
    return true;
  }
  return false;
}
#endif // #ifndef ORIENTATION

#ifndef MATRIX_TYPE
bool MatrixLamp::SetMatrixType(uint8_t type)
{
  if (type >= 1 && type <= 2)
  {
    MATRIX_TYPE = type - 1;
    return true;
  }
  return false;
}
#endif // #ifndef MATRIX_TYPE

#if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
bool MatrixLamp::GetRandomSettings()
{
  return random_settings;
}

void MatrixLamp::SetRandomSettings(bool b)
{
  if (!b)
  {
    restoreSettings();
  }

  loadingFlag = true;

  random_settings = b;
  selectedSettings = b;
}
#endif // #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)

void MatrixLamp::ShowFrame(uint8_t CurrentMode, esphome::Color current_color, light::AddressableLight *p_it)
{
  InitLeds(p_it->size());

  if (currentMode != CurrentMode)
  {
    currentMode = CurrentMode;
    loadingFlag = true;

#ifdef DEF_SCANNER
    if (currentMode == EFF_SCANNER) {
      this->SetScaleFromColorForEffect(currentMode, current_color);
    }
#endif

#if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
    selectedSettings = random_settings;
    if (!random_settings)
#endif // #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
    {
      if (this->speed) {
        auto speed = this->speed->make_call();
        speed.set_value(modes[currentMode].Speed);
        speed.perform();
      }
      if (this->scale) {
        auto scale = this->scale->make_call();
        scale.set_value(modes[currentMode].Scale);
        scale.perform();
      }
    }
  }

  effectsTick();

#if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
  if (random_settings)
  {
    if (this->speed && (modes[currentMode].Speed != (int)this->speed->state))
    {
      auto speed = this->speed->make_call();
      speed.set_value(modes[currentMode].Speed);
      speed.perform();
    }
    if (this->scale && (modes[currentMode].Scale != (int)this->scale->state))
    {
      auto scale = this->scale->make_call();
      scale.set_value(modes[currentMode].Scale);
      scale.perform();
    }
  }
#endif // #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)

  for (int i = 0; i < p_it->size(); i++)
  {
    (*p_it)[i] = Color(leds[i].r, leds[i].g, leds[i].b);
  }

  #if defined delay
  delay(1);
  #else
  esphome::delay(1);
  #endif

  if (this->speed && (modes[currentMode].Speed != (int)this->speed->state))
  {
    modes[currentMode].Speed = (int)this->speed->state;
    loadingFlag = true; // без перезапуска эффекта ничего и не увидишь
  }
  if (this->speed && (modes[currentMode].Scale != (int)this->scale->state))
  {
    modes[currentMode].Scale = (int)this->scale->state;
    loadingFlag = true; // без перезапуска эффекта ничего и не увидишь
  }
}

}  // namespace matrix_lamp
}  // namespace esphome
