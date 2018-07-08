import logging


def collector(name, fields, filepath, append=False, format_types=None, delimiter='|'):
    """
    Returns a function for collecting rows with fields :fields: (along with
    datetime information) in a CSV log file located at :filepath:.

    We often want to collect some data about choices we are making
    while processing and transforming data. This collector function provides
    a way to do that using python's logging standard library module.

    :name: the name to be given to the logger
    :fields: list of fields that you want to collect
    :filepath: target for the logfile
    :append: (default False) if True, will append to the given filepath. Default
        behavior is to overwrite it, with column headings in the first line.
    :format_types: optional dictionary from fields to format-string types
        (like 's' or '.6f') describing how fields should be formatted in the
        CSV. Any fields not included will default to 'f'.
    :delimiter: the delimiter in the CSV. Defaults to '|' to avoid collisions.
    """
    if not format_types:
        format_types = dict()

    if 'asctime' not in fields:
        fields = ['asctime'] + fields

    logger = logging.Logger(name)

    if not append:
        with open(filepath, 'w') as f:
            f.write(delimiter.join(fields) + '\n')
    handler = logging.FileHandler(filepath, mode='a')

    default_types = {field: 's' for field in fields}
    types = {**default_types, **format_types}
    formatted_fields = [f"%({field}){types[field]}" for field in fields]

    formatter = logging.Formatter(delimiter.join(
        formatted_fields), "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    def collect(**kwargs):
        logger.info("Collected data point for {vtd_splits}", extra=kwargs)

    return collect
