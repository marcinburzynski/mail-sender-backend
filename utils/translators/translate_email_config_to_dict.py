def translate_email_config_to_dict(config_entry):
    return {
        'email': config_entry.email,
        'password': config_entry.password,
        'port': config_entry.port,
        'ssl': config_entry.ssl,
        'host': config_entry.host
    }
