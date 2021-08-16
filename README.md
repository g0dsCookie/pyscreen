# pyscreen

Extensible script to run a screen on your device (i.e. RPI via GPIO).

Currently only tested with [RackPi](https://www.thingiverse.com/thing:3022136).
However your setup shouldn't matter as you can configure PINs and display you
want to use.

## Configuration

An example configuration can be found in *example.yml*.

A short description of most configuration values will be in the following sections.

### Pyscreen

**Section:** pyscreen

**Type:** Dictionary

| Name | Type | Default Value | Description |
| ---- | ---- | ------------- | ----------- |
| loglevel | string | INFO | Set log level to use. (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| interval | float | 0.1 | Main loop interval in seconds |
| standby | float | 120 | Time in seconds to poweroff display |
| plugins.folders | List[string] | ["\<sys.prefix\>/share/pyscreen/plugins", "\<site.USER_BASE\>/share/pyscreen/plugins"] | Path to plugin directories |

### Display

**Section:** display

**Type:** Dictionary

| Name | Type | Default Value | Description |
| ---- | ---- | ------------- | ----------- |
| type | string | | Name of display to use |
| width | int | 128 | Display Width |
| height | int | 32 | Display Height |
| rotation | int | 2 | Display rotation |
| padding.top | int | 0 | Text padding top |
| padding.left | int | 0 | Text padding left |
| font.name | string | | TrueType font to use |
| font.size | int | 10 | Font size |

There may be additional options depending on your display plugin.

### Menus

**Section:** menus

**Type:** List

| Name | Type | Default Value | Description |
| ---- | ---- | ------------- | ----------- |
| name | string | | Name of menu plugin |
| interval | int | 5 | Interval to redraw menu |
| led | string | | Name of status led for this menu |

There may be additional options depending on your menu plugin.

### GPIOs

**Section:** gpio

**Type:** Dictionary

| Name | Type | Default Value | Description |
| ---- | ---- | ------------- | ----------- |
| name | string | | Unique identifier for this gpio |
| type | string | | Name of GPIO plugin |
| pin | int | | PIN for this GPIO |

There may be additional options depending on your GPIO plugin.

## Installation

Requirements:
* I2C enabled (for ssd1306)
  * /boot/config.txt -> *dtparam=i2c_arm=on*
  * /etc/modules-load.d/i2c.conf -> *i2c-dev*
* SPI enabled
  * /boot/config.txt -> *dtparam=spi=on*

### Bare Metal

Requirements:
* python >=3.8

```
git clone https://git.copr.icu/g0dsCookie/pyscreen.git
cd pyscreen
pip install -r requirements.txt
# optional to use plugins
pip install -r requirements_plugins.txt
```

Now you may run pyscreen with `python -m pyscreen.cli`

### Docker

`docker run --privileged --net=host ghcr.io/g0dscookie/pyscreen`

**--privileged** is required to access GPIO ports.

**--net=host** is required for NetMenu to display correct hostname and ip address.

## Plugins

Your plugin with all components should be one file.
Within your plugin file there should be at most one class deriving from *pyscreen.plugin.Plugin*.

You may specify one or more components. Depending on the type of component the
component must derive from one of the following classes:

| Component | Class |
| --------- | ----- |
| Display   | pyscreen.display.Display |
| Menu      | pyscreen.menu.Menu |
| GPIO      | pyscreen.GPIO.GPIO |

Examples can be found in **pyscreen/plugins/\*.py** and **pyscreen/internal**. 