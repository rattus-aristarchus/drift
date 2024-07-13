import os

import yaml

DEFAULT_CONF = {
    "log_level": "info",
    "world": "nomads_vs_farmers"
}


def init_conf(conf_path):
    _prep_conf_file(conf_path)
    conf = _read_conf(conf_path)
    if _needs_update(conf, DEFAULT_CONF):
        conf = _update_conf(conf, DEFAULT_CONF)
        write_conf(conf, conf_path)
    return conf


def _prep_conf_file(path):
    if not os.path.exists(path):
        open(path, "x")


def _read_conf(path):
    return yaml.safe_load(open(path, "r", encoding="utf-8"))


def _needs_update(conf, default_conf):
    if conf is None or len(conf) == 0:
        return True
    return len(conf) != len(default_conf)


def _update_conf(conf, default_conf):
    output = conf
    if conf is None or len(conf) == 0:
        output = default_conf
    else:
        for key, value in default_conf.items():
            if key not in conf.keys():
                output[key] = value

    return output


def write_conf(conf, path):
    with open(path, "w", encoding="utf-8") as file:
        yaml.dump(conf, file)
