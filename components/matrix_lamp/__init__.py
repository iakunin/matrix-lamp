"""Matrix Lamp component for ESPHome."""

import logging

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components.template.number import TemplateNumber
from esphome.const import CONF_ID, CONF_WIDTH, CONF_HEIGHT, CONF_RANDOM 

_LOGGER = logging.getLogger(__name__)

CODEOWNERS = ["@andrewjswan"]

DEPENDENCIES = ["light"]

AUTO_LOAD = ["matrix_lamp"]

logging.info("")
logging.info("Load Matrix Lamp component https://github.com/andrewjswan/matrix-lamp")
logging.info("")

matrix_lamp_ns = cg.esphome_ns.namespace("matrix_lamp")
MATRIX_LAMP_ = matrix_lamp_ns.class_("MatrixLamp", cg.Component)

CONF_SCALE_ID = "scale_id"
CONF_SPEED_ID = "speed_id"

MATRIX_LAMP_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_ID): cv.declare_id(MATRIX_LAMP_),
        cv.Required(CONF_SCALE_ID): cv.use_id(TemplateNumber),
        cv.Required(CONF_SPEED_ID): cv.use_id(TemplateNumber),
        cv.Optional(CONF_WIDTH, default="16"): cv.templatable(cv.positive_int),
        cv.Optional(CONF_HEIGHT, default="16"): cv.templatable(cv.positive_int),
        cv.Optional(CONF_RANDOM, default=False): cv.templatable(cv.boolean),
    },
)

CONFIG_SCHEMA = cv.All(MATRIX_LAMP_SCHEMA)


async def to_code(config) -> None:  # noqa: ANN001
    """Code generation entry point."""
    var = cg.new_Pvariable(config[CONF_ID])

    scale_number = await cg.get_variable(config[CONF_SCALE_ID])
    cg.add(var.set_scale(scale_number))
    speed_number = await cg.get_variable(config[CONF_SPEED_ID])
    cg.add(var.set_speed(speed_number))

    cg.add_define("WIDTH", config[CONF_WIDTH])
    cg.add_define("HEIGHT", config[CONF_HEIGHT])
    if config[CONF_RANDOM]:
        cg.add_define("RANDOM_SETTINGS_IN_CYCLE_MODE")
  
    await cg.register_component(var, config)
