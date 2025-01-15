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

  #if defined(MATRIX_LAMP_USE_DISPLAY)
  this->current_icon = MAXICONS;
  this->last_anim_time = 0;
  #if defined(USE_API)
  register_service(&MatrixLamp::show_icon, "show_icon", {"icon_name"});
  #endif
  #endif
}  // setup()

void MatrixLamp::dump_config() {
  ESP_LOGCONFIG(TAG, "MatrixLamp version: %s", MATRIX_LAMP_VERSION);
  ESP_LOGCONFIG(TAG, "             Width: %d", WIDTH);
  ESP_LOGCONFIG(TAG, "            Height: %d", HEIGHT);
  #if defined(MATRIX_LAMP_USE_DISPLAY)
  ESP_LOGCONFIG(TAG, "           Display: YES");
  ESP_LOGCONFIG(TAG, "   Number of icons: %d", this->icon_count);
  #endif
  #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
  ESP_LOGCONFIG(TAG, "Random mode enable: YES");
  #else
  ESP_LOGCONFIG(TAG, "Random mode enable: NO");
  #endif
  ESP_LOGCONFIG(TAG, "       Orientation: %d", ORIENTATION);
  ESP_LOGCONFIG(TAG, "       Matrix Type: %d", MATRIX_TYPE);
  ESP_LOGCONFIG(TAG, "   Number of modes: %d", MODE_AMOUNT);
}  // dump_config()

#if defined(MATRIX_LAMP_USE_DISPLAY)
void MatrixLamp::set_display(addressable_light::AddressableLightDisplay *display)
{
  this->display = display;
}

void MatrixLamp::add_icon(MatrixLamp_Icon *icon)
{
  this->icons[this->icon_count] = icon;
  ESP_LOGD(TAG, "Add Icon No.: %d name: %s frame_duration: %d ms", this->icon_count, icon->name.c_str(), icon->frame_duration);
  this->icon_count++;
}
#endif // #if defined(MATRIX_LAMP_USE_DISPLAY)

void MatrixLamp::set_scale(template_::TemplateNumber *scale) {
  this->scale = scale;
} // set_scale()

void MatrixLamp::set_speed(template_::TemplateNumber *speed) {
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

#if defined(MATRIX_LAMP_USE_DISPLAY)
uint8_t MatrixLamp::find_icon(std::string name)
{
  for (uint8_t i = 0; i < this->icon_count; i++)
  {
    if (strcmp(this->icons[i]->name.c_str(), name.c_str()) == 0)
    {
      ESP_LOGD(TAG, "Icon: %s found id: %d", name.c_str(), i);
      return i;
    }
  }
  ESP_LOGW(TAG, "Icon: %s not found", name.c_str());
  return MAXICONS;
}

void MatrixLamp::show_icon(std::string iconname)
{
  if (iconname == "clean_out")
  {
    this->current_icon = MAXICONS;
    this->display->set_enabled(false);
    return;
  }

  this->current_icon = this->find_icon(iconname);
  if (this->current_icon == MAXICONS)
  {
    ESP_LOGD(TAG, "Icon %d/%s not found => skip!", this->current_icon, iconname.c_str());
  }
  else
  {
    this->icons[this->current_icon]->set_frame(0);
    this->display->set_enabled(true);
  }
}

void MatrixLamp::update_screen()
{
  if (this->current_icon < this->icon_count)
  {
    if (millis() - this->last_anim_time >= this->icons[this->current_icon]->frame_duration)
    {
      this->icons[this->current_icon]->next_frame();
      this->last_anim_time = millis();
    }
  }
}

void MatrixLamp::Display()
{
  if (this->current_icon == MAXICONS)
  {
    return;
  }

  this->display->image(4, 4, this->icons[this->current_icon]);
  this->update_screen();
}
#endif // #if defined(MATRIX_LAMP_USE_DISPLAY)

}  // namespace matrix_lamp
}  // namespace esphome
