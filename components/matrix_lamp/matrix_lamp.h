#pragma once

#include "esphome.h"
#include "esphome/components/template/number/template_number.h"

namespace esphome {
namespace matrix_lamp {

static const char *const TAG = "matrix_lamp";
static const char *const MATRIX_LAMP_VERSION = "2025.1.13";

class MatrixLamp : public Component {
#if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
  protected:
    bool random_settings = false;
#endif // #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
    esphome::template_::TemplateNumber *scale{nullptr};
    esphome::template_::TemplateNumber *speed{nullptr};

  public:
    void setup() override;
    void dump_config() override;

    void set_scale(esphome::template_::TemplateNumber *scale);
    void set_speed(esphome::template_::TemplateNumber *speed);

    // Reset the current effect, for example when changing the lamp state. 
    void ResetCurrentEffect();

#ifndef ORIENTATION
    // Set Matrix Orientation [1..8] instead of real matrix ORIENTATION [0..7]
    bool SetMatrixOrientation(uint8_t orientation);
#endif // #ifndef ORIENTATION

#ifndef MATRIX_TYPE
    // Set Matrix Type [1..2] instead of real matrix MATRIX_TYPE [0..1]
    bool SetMatrixType(uint8_t type);
#endif // #ifndef MATRIX_TYPE

    // Set scale for effect
    void SetScaleForEffect(uint8_t mode, uint8_t scale);

#if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)
    bool GetRandomSettings();

    void SetRandomSettings(bool b=false);
#endif // #if defined(RANDOM_SETTINGS_IN_CYCLE_MODE)

    void ShowFrame(uint8_t CurrentMode, esphome::Color current_color, light::AddressableLight *p_it);
}; // class MatrixLamp

}  // namespace matrix_lamp
}  // namespace esphome
