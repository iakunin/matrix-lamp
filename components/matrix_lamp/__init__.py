"""Matrix Lamp component for ESPHome."""

import io
import logging
import os
import requests

import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.components.image as espImage
from esphome.core import CORE, HexInt
from esphome.cpp_generator import RawExpression
from esphome.components import display
from esphome.components.light.types import AddressableLightEffect
from esphome.components.light.effects import register_addressable_effect
from esphome.components.template.number import TemplateNumber
from esphome.const import CONF_ID, CONF_DISPLAY, CONF_FILE, CONF_URL, CONF_RESIZE, CONF_WIDTH, CONF_HEIGHT, CONF_NAME, CONF_MODE, CONF_RANDOM, CONF_RAW_DATA_ID
from .const import CONF_SCALE_ID, CONF_SPEED_ID, CONF_ICONS, CONF_CACHE, CONF_LAMEID, CONF_ORIENTATION, CONF_RGB565ARRAY, CONF_FRAMEDURATION, CONF_FRAMEINTERVAL, CONF_PINGPONG, CONF_MATRIX_TYPE, CONF_MATRIX_ID, EFF_DNA, MATRIX_LAMP_EFFECTS, MAXICONS, ICONWIDTH, ICONHEIGHT, ICONSIZE, MAXFRAMES


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
MATRIX_ICONS = matrix_lamp_ns.class_("MatrixLamp_Icon")

MATRIX_LAMP_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ID): cv.declare_id(MATRIX_LAMP),
        cv.Optional(CONF_DISPLAY): cv.use_id(display),
        cv.Optional(CONF_WIDTH, default="16"): cv.templatable(cv.positive_int),
        cv.Optional(CONF_HEIGHT, default="16"): cv.templatable(cv.positive_int),
        cv.Optional(CONF_RANDOM, default=False): cv.templatable(cv.boolean),
        cv.Optional(CONF_ORIENTATION): cv.templatable(cv.int_range(min=0, max=7)),
        cv.Optional(CONF_MATRIX_TYPE): cv.templatable(cv.int_range(min=0, max=1)),
        cv.Optional(CONF_SCALE_ID): cv.use_id(TemplateNumber),
        cv.Optional(CONF_SPEED_ID): cv.use_id(TemplateNumber),
        cv.Optional(CONF_ICONS): cv.All(
            cv.ensure_list(
                {
                    cv.Required(CONF_ID): cv.declare_id(MATRIX_ICONS),

                    cv.Exclusive(CONF_FILE,"uri"): cv.file_,
                    cv.Exclusive(CONF_URL,"uri"): cv.url,
                    cv.Exclusive(CONF_LAMEID,"uri"): cv.string,
                    cv.Exclusive(CONF_RGB565ARRAY,"uri"): cv.string,
                    cv.Optional(CONF_RESIZE): cv.dimensions,
                    cv.Optional(CONF_FRAMEDURATION, default="0"): cv.templatable(cv.positive_int),
                    cv.Optional(CONF_PINGPONG, default=False): cv.boolean,
                    cv.GenerateID(CONF_RAW_DATA_ID): cv.declare_id(cg.uint8),
                }
            ),
            cv.Length(max=MAXICONS),
        ),
        cv.Optional(CONF_CACHE, default=False): cv.templatable(cv.boolean),
        cv.Optional(CONF_FRAMEINTERVAL, default="192"): cv.templatable(cv.positive_int),
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
  
    if CONF_DISPLAY in config:
        cg.add_define("MATRIX_LAMP_USE_DISPLAY")
        disp = await cg.get_variable(config[CONF_DISPLAY])
        cg.add(var.set_display(disp))

    if CONF_DISPLAY in config:
        cg.add_define("MAXICONS", MAXICONS)

        from PIL import Image, ImageSequence

        def openImageFile(path):
            try:
                return Image.open(path)
            except Exception as e:
                raise core.EsphomeError(f"Icons: Could not load image file {path}: {e}")

        logging.info(f"Icons: Preparing icons, this may take some seconds.")

        yaml_string= ""

        for conf in config[CONF_ICONS]:
            if CONF_FILE in conf:
                path = CORE.relative_config_path(conf[CONF_FILE])
                try:
                    image = openImageFile(path)
                except Exception as e:
                    raise core.EsphomeError(f" Icons: Could not load image file {path}: {e}")

            elif CONF_LAMEID in conf:
                path = CORE.relative_config_path(".cache/icons/lameid/" + conf[CONF_LAMEID])
                if config[CONF_CACHE] and os.path.isfile(path):
                    try:
                        image = openImageFile(path)
                        logging.info(f" Icons: Load {conf[CONF_LAMEID]} from cache.")
                    except Exception as e:
                        raise core.EsphomeError(f" Icons: Could not load image file {path}: {e}")
                else:
                    r = requests.get("https://developer.lametric.com/content/apps/icon_thumbs/" + conf[CONF_LAMEID],
                                     headers = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"},
                                     timeout=4.0)
                    if r.status_code != requests.codes.ok:
                        raise core.EsphomeError(f" Icons: Could not download image file {conf[CONF_LAMEID]}: {conf[CONF_ID]}")
                    image = Image.open(io.BytesIO(r.content))

                    if config[CONF_CACHE]:
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        f = open(path,"wb")
                        f.write(r.content) 
                        f.close()
                        logging.info(f" Icons: Save {conf[CONF_LAMEID]} to cache.")

            elif CONF_URL in conf:
                a = urlparse(conf[CONF_URL])
                path = CORE.relative_config_path(".cache/icons/url/" + os.path.basename(a.path))
                if config[CONF_CACHE] and os.path.isfile(path):
                    try:
                        image = openImageFile(path)
                        logging.info(f" Icons: Load {conf[CONF_URL]} from cache.")
                    except Exception as e:
                        raise core.EsphomeError(f" Icons: Could not load image file {path}: {e}")
                else:
                    r = requests.get(conf[CONF_URL], 
                                     headers = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"},
                                     timeout=4.0)
                    if r.status_code != requests.codes.ok:
                        raise core.EsphomeError(f" Icons: Could not download image file {conf[CONF_URL]}: {conf[CONF_ID]}")
                    image = Image.open(io.BytesIO(r.content))

                    if config[CONF_CACHE]:
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        f = open(path,"wb")
                        f.write(r.content) 
                        f.close()
                        logging.info(f" Icons: Save {conf[CONF_URL]} to cache.")

            elif CONF_RGB565ARRAY in conf:
                r = list(json.loads(conf[CONF_RGB565ARRAY]))
                if len(r) == 64:
                    image = Image.new("RGB",[8,8])
                    for y in range(0,8):
                       for x in range(0,8):
                            image.putpixel((x,y),rgb565_888(r[x+y*8]))
                               
            width, height = image.size

            if CONF_RESIZE in conf:
                new_width_max, new_height_max = conf[CONF_RESIZE]
                ratio = min(new_width_max / width, new_height_max / height)
                width, height = int(width * ratio), int(height * ratio)

            if hasattr(image, 'n_frames'):
                frames = min(image.n_frames, MAXFRAMES)
                logging.info(f" Icons: Animation {conf[CONF_ID]} with { frames } frame(s)")
            else:
                frames = 1

            if (width != ICONWIDTH) and (height != ICONHEIGHT):
                logging.warning(f" Icons: Icon wrong size valid 8x8: {conf[CONF_ID]} skipped!")
            else:
                if (conf[CONF_FRAMEDURATION] == 0):
                    try:
                        duration = image.info['duration']         
                    except:
                        duration = config[CONF_FRAMEINTERVAL]
                else:
                    duration = conf[CONF_FRAMEDURATION]

                yaml_string += F"\"{conf[CONF_ID]}\","
                pos = 0 
                frameIndex = 0
                data = [0 for _ in range(ICONSIZE * frames)]
                if image.has_transparency_data:
                    logging.debug(f" Icons: icon {conf[CONF_ID]} has transparency!")
                
                for frameIndex in range(frames):
                    image.seek(frameIndex)
                    frame = image.convert("RGB")

                    if CONF_RESIZE in conf:
                        frame = frame.resize([width, height])
        
                    pixels = list(frame.getdata())
                    
                    i = 0
                    for pix in pixels:
                        R = pix[0] >> 3
                        G = pix[1] >> 2
                        B = pix[2] >> 3
                                                
                        x = (i % width)
                        y = i//width
                        i +=1
                        rgb = (R << 11) | (G << 5) | B
                        
                        data[pos] = rgb >> 8
                        pos += 1
                        data[pos] = rgb & 255
                        pos += 1
                        
                rhs = [HexInt(x) for x in data]
                
                logging.debug(f"Icons: icon {conf[CONF_ID]} {rhs}")

                prog_arr = cg.progmem_array(conf[CONF_RAW_DATA_ID], rhs)

                cg.new_Pvariable(
                    conf[CONF_ID],
                    prog_arr,
                    width,
                    height,
                    frames,
                    espImage.IMAGE_TYPE["RGB565"],
                    str(conf[CONF_ID]),
                    conf[CONF_PINGPONG],
                    duration,
                )

                cg.add(var.add_icon(RawExpression(str(conf[CONF_ID]))))
        
        logging.info("Icons: List of icons for e.g. blueprint:\n\n\r[" + yaml_string + "]\n")

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
