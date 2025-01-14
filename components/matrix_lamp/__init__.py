"""Matrix Lamp component for ESPHome."""

import logging

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components.light.types import AddressableLightEffect
from esphome.components.light.effects import register_addressable_effect
from esphome.components.template.number import TemplateNumber
from esphome.const import CONF_ID, CONF_WIDTH, CONF_HEIGHT, CONF_NAME, CONF_MODE, CONF_RANDOM 
from .const import EFF_DNA, MATRIX_LAMP_EFFECTS

_LOGGER = logging.getLogger(__name__)

CODEOWNERS = ["@andrewjswan"]

DEPENDENCIES = ["light"]

AUTO_LOAD = ["matrix_lamp"]

logging.info("")
logging.info("Load Matrix Lamp component https://github.com/andrewjswan/matrix-lamp")
logging.info("")

matrix_lamp_ns = cg.esphome_ns.namespace("matrix_lamp")
MATRIX_LAMP = matrix_lamp_ns.class_("MatrixLamp", cg.Component)
MATRIX_EFECT = matrix_lamp_ns.class_("MatrixLampLightEffect", AddressableLightEffect)

CONF_SCALE_ID = "scale_id"
CONF_SPEED_ID = "speed_id"
CONF_ORIENTATION = "matrix_orientation"
CONF_MATRIX_TYPE = "matrix_type"
CONF_MATRIX_ID = "matrix_lamp_id"

MATRIX_LAMP_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ID): cv.declare_id(MATRIX_LAMP),
        cv.Optional(CONF_WIDTH, default="16"): cv.templatable(cv.positive_int),
        cv.Optional(CONF_HEIGHT, default="16"): cv.templatable(cv.positive_int),
        cv.Optional(CONF_RANDOM, default=False): cv.templatable(cv.boolean),
        cv.Optional(CONF_ORIENTATION): cv.templatable(cv.int_range(min=0, max=7)),
        cv.Optional(CONF_MATRIX_TYPE): cv.templatable(cv.int_range(min=0, max=1)),
        cv.Optional(CONF_SCALE_ID): cv.use_id(TemplateNumber),
        cv.Optional(CONF_SPEED_ID): cv.use_id(TemplateNumber),
    },
)

CONFIG_SCHEMA = cv.All(MATRIX_LAMP_SCHEMA)

async def to_code(config) -> None:  # noqa: ANN001
    """Code generation entry point."""
    var = cg.new_Pvariable(config[CONF_ID])

    cg.add_library("fastled/FastLED", "3.6.0")

    cg.add_define("WIDTH", config[CONF_WIDTH])
    cg.add_define("HEIGHT", config[CONF_HEIGHT])

    if CONF_SCALE_ID in config:
        scale_number = await cg.get_variable(config[CONF_SCALE_ID])
        cg.add(var.set_scale(scale_number))
    if CONF_SPEED_ID in config:
        speed_number = await cg.get_variable(config[CONF_SPEED_ID])
        cg.add(var.set_speed(speed_number))

    if CONF_ORIENTATION in config:
        cg.add_define("ORIENTATION", config[CONF_ORIENTATION])
    if CONF_MATRIX_TYPE in config:
        cg.add_define("MATRIX_TYPE", config[CONF_MATRIX_TYPE])

    if config[CONF_RANDOM]:
        cg.add_define("RANDOM_SETTINGS_IN_CYCLE_MODE")
  
    await cg.register_component(var, config)


@register_addressable_effect(
    "matrix_lamp_effect",
    MATRIX_EFECT,
    "Matrix Lamp",
    {
        cv.GenerateID(CONF_MATRIX_ID): cv.use_id(MATRIX_LAMP),
        cv.Optional(CONF_MODE, default=EFF_DNA): cv.one_of(*MATRIX_LAMP_EFFECTS, upper=True),
    },
)


async def matrix_lamp_light_effect_to_code(config, effect_id) -> AddressableLightEffect:
    """Effect registration entry point."""
    parent = await cg.get_variable(config[CONF_MATRIX_ID])

    effect = cg.new_Pvariable(effect_id, config[CONF_NAME])

    cg.add(effect.set_mode(MATRIX_LAMP_EFFECTS.index(config[CONF_MODE])))
    cg.add_define("DEF_" + config[CONF_MODE])
    cg.add(effect.set_matrix_lamp(parent))
    return effect
