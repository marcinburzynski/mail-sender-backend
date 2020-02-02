def validate_request(data, required_fields):
    errors = []

    for required_field in required_fields:
        if required_field not in data:
            errors.append(f'{required_field} not provided')

    return errors
