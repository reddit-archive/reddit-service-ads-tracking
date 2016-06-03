from baseplate import config


def parse_config(app_config):
    return config.parse_config(app_config, {
        "ads_tracking": {
            "click_secret": config.Base64,
            "max_click_age": config.Timespan,
        },
    })
