CONTROL_TYPES = ["STRING", "DATETIME"]
FIELD_TYPES = ["DATETIME", "DATE"]

def ScreenControl(object):

    optional_kwargs = {
            'finder': ('view_id', 'on_finder_ok', 'on_finder_cancel',
                       'finder_filter', 'finder_display_fields',
                       'finder_return_fields'),
            'view_id': ('finder', ),
            'on_finder_ok': ('finder', ),
            'on_finder_cancel': ('finder', ),
            'finder_filter': ('finder', ),
            'finder_display_fields': ('finder', ),
            'finder_return_fields': ('finder', ),
            'on_change': tuple(),
    }

    def __init__(self, control_type, field_type, caption, **kwargs):
        self.control_type = control_type
        self.field_type = field_type
        self.caption = caption
        self.kwargs = kwargs
        self.validate_kwargs()

    def _validate_kwargs(self):
        unknown = set()
        missing = set()

        for arg in self.kwargs.keys():
            dependents = self.optional_args.get(arg)
            if not arg:
                unknown.add(arg)
            else:
                diff = set(dependents) - set(self.kwargs.keys)
                missing.add((arg, diff, ))

        if unknown or missing:
            raise ValueError(
                "Invalid arguments: missing({}), unknown({})".format(
                    missing, unknown, ))

    def add_to_ui(self, ui):
        f = ui.addUIField(self.field_name)
        f.controlType = self.control_type
        f.fieldType = self.field_type
        f.caption = self.caption
        f.size = self.size
        if self.kwargs['finder']:
            f.hasFinder = True
            # Register on click/change handlers
            f.onChange = self.kwargs.get("on_change")
            f.onClick = ui.finder_on_click_for(
                    self.kwargs.get('view_id'),
                    self.kwargs.get('on_finder_ok'),
                    self.kwargs.get('on_finder_cancel'),
                    self.kwargs.get('finder_filter'),
                    self.kwargs.get('finder_display_fields'),
                    self.kwargs.get('finder_return_fields'),
             )
        return f
