def get_label_lower(opts):
    if hasattr(opts, 'label_lower'):
        return opts.label_lower
    model_label = opts.model_name
    app_label = opts.app_label
    return "{app_label}.{model_label}".format(app_label=app_label,
                                              model_label=model_label)
