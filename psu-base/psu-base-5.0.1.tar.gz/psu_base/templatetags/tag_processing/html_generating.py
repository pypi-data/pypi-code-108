from django import template
from psu_base.classes.Log import Log
from psu_base.services import (
    utility_service,
    auth_service,
    error_service,
    message_service,
)
from psu_base.services import banner_service, validation_service
import psu_base.templatetags.tag_processing.supporting_functions as support
from psu_base.context_processors import util as util_context
from django.urls import reverse

log = Log()


class JsAlert(template.Node):
    def __init__(self, nodelist, tokens):
        self.nodelist = nodelist
        self.tokens = tokens

    def render(self, context):
        log.trace()
        attrs, body = support.get_tag_params(self.nodelist, self.tokens, context)
        content = [
            "$.alert({",
            f"""content: `{body}`,""",
            f"""icon: 'fa {attrs.get("icon", "fa-bell-o")}',""",
            f"""title: '{attrs.get("title", "Alert")}',""",
            f"""backgroundDismiss: {attrs.get("backgroundDismiss", 'true')},""",
        ]
        # Add any other specified attributes
        for kk, vv in attrs.items():
            if kk not in ["icon", "title", "backgroundDismiss"]:
                # jquery uses camelCase, but psu-base makes keys lowercase. Convert _ keys to camelCase
                attr_name = utility_service.camelize(kk)
                attr_val = (
                    vv if vv in ["true", "false"] or vv.isnumeric() else f"'{vv}'"
                )
                content.append(
                    f"""{attr_name}: {attr_val},""",
                )
        # Close the $.alert command
        content.append("});")

        return "".join(content)


class JsConfirm(template.Node):
    def __init__(self, nodelist, tokens):
        self.nodelist = nodelist
        self.tokens = tokens

    def render(self, context):
        log.trace()
        attrs, body = support.get_tag_params(self.nodelist, self.tokens, context)
        content = [
            "$.confirm({",
            f"""content: `{body}`,""",
            f"""icon: 'fa {attrs.get("icon", "fa-bell-o")}',""",
            f"""title: '{attrs.get("title", "Alert")}',""",
            "buttons: {",
            f"""'{attrs.get("confirm", "Yes")}':""",
            "{ action: function(){",
            attrs.get("onconfirm", ""),
            "},",
            f"""btnClass: '{attrs.get("confirm_btn_class", "btn-success")}',""",
            "},",
            f"""'{attrs.get("cancel", "No")}':""",
            "{ action: function(){",
            attrs.get("oncancel", ""),
            "},",
            f"""btnClass: '{attrs.get("cancel_btn_class", "btn-danger")}',""",
            "},",
            "},",
        ]
        # Add any other specified attributes
        for kk, vv in attrs.items():
            if kk not in [
                "icon",
                "title",
                "confirm",
                "onconfirm",
                "confirm_btn_class",
                "cancel",
                "oncancel",
                "cancel_btn_class",
            ]:
                # jquery uses camelCase, but psu-base makes keys lowercase. Convert _ keys to camelCase
                attr_name = utility_service.camelize(kk)
                attr_val = (
                    vv if vv in ["true", "false"] or vv.isnumeric() else f"'{vv}'"
                )
                content.append(
                    f"""{attr_name}: {attr_val},""",
                )
        # Close the $.alert command
        content.append("});")

        return "".join(content)


class SelectNode(template.Node):
    """Generates a select menu with automated option selection"""

    def __init__(self, args):
        self.args = args

    def render(self, context):
        # Prepare attributes
        attrs = support.process_args(self.args, context)

        # Attributes that need special processing are 'options' and 'value'
        options = value = None

        # Make nullable by default
        nullable = True
        if "nullable" in attrs:
            nullable_str = str(attrs.get("nullable")).lower()
            # Menus may be nullable only until a value is selected
            if "null" in nullable_str:  # when_null, if_null, on_null, etc...
                val = str(attrs.get("value")).strip()
                nullable = val in ["None", ""]
            else:
                nullable = nullable_str not in ["n", "no", "false", "none"]

        # Allow default null label to be overwritten
        null_label = (
            attrs.get("null_label") if "null_label" in attrs else "Select an Option"
        )

        # Expect options to be provided
        if "options" in attrs:
            options = attrs.get("options")
        elif "banner_options" in attrs:
            # Get options from Finti.
            # If not found, error will be logged and empty dict will be returned
            options = banner_service.finti_get_menu_options(attrs.get("banner_options"))
        else:
            log.error("You must provide a dict of options for the select menu")
            options = {}

        # Could be multiple-select
        multiple = str(attrs.get("multiple")).lower() in ["multiple", "true", "y"]
        # Expect a value or values to be provided
        value = attrs.get("value")
        values = attrs.get("values")

        # Remove special attrs that should not appear in the HTML element
        for ii in ["multiple", "values", "value", "null_label", "nullable", "options"]:
            if ii in attrs:
                del attrs[ii]

        pieces = ["<select"]
        for attr_key, attr_val in attrs.items():
            pieces.append(f'{attr_key}="{attr_val}"')
        if multiple:
            pieces.append("multiple")
        pieces.append(">")

        # Options may be a dict, or a list of {id:, value:} dicts
        if type(options) is list:
            # Convert the list to one big dict
            options = utility_service.options_list_to_dict(options)

        # Now also accepting strings that refer to common option sets
        elif type(options) is str:
            # Yes-No menus in each order (for defaulting to Y or N)
            if options.upper() == "YN":
                options = {"Y": "Yes", "N": "No"}
            elif options.upper() == "NY":
                options = {"N": "No", "Y": "Yes"}

            # True/False menus in each order (for defaulting to True or False)
            elif options.upper() in ["TF", 'BOOL', 'BOOLEAN']:
                options = {"True": "True", "False": "False"}
            elif options.upper() == "FT":
                options = {"False": "False", "True": "True"}

            # Ranges of numbers
            elif ".." in options:
                ll = options.split("..")
                if len(ll) == 2 and ll[0].isnumeric() and ll[1].isnumeric():
                    n1 = int(ll[0])
                    n2 = int(ll[1])
                    rev = n2 < n1
                    if rev:
                        options = {
                            str(ii): str(ii) for ii in reversed(range(n2 + 1, n1))
                        }
                    else:
                        options = {str(ii): str(ii) for ii in range(n1, n2 + 1)}

            # If still a string, there will be issues. (this should be caught during development)
            if type(options) is str:
                error_service.record(
                    f"Invalid options given to %select_menu% tag", debug_info=options
                )

        if nullable:
            pieces.append(
                f"<option value=\"\">{null_label if null_label else 'Select One'}</option>"
            )

        str_values = [str(x) for x in values] if values else None
        for option_key, option_val in options.items():
            pieces.append(f'<option value="{option_key}"')
            if str(value) == str(option_key):
                pieces.append("selected")
            elif multiple and str_values and str(option_key) in str_values:
                pieces.append("selected")
            pieces.append(f">{option_val}</option>")
        pieces.append("</select>")

        return " ".join(pieces)


class BannerNameNode(template.Node):
    """Generates an input that cleans a name for entry into Banner"""

    def __init__(self, args):
        self.args = args

    def render(self, context):
        # Prepare attributes
        attrs = support.process_args(self.args, context)

        # Value needs special processing
        value, changed = validation_service.clean_name(attrs.get("value"))
        attrs["value"] = value if value else ""

        # Onchange needs special processing
        _onchange = attrs.get("onchange")
        if _onchange:
            onchange = "clean_banner_name($(this), function(){" + _onchange + "});"
        else:
            onchange = "clean_banner_name($(this));"
        attrs["onchange"] = onchange

        pieces = ["<input"]
        for attr_key, attr_val in attrs.items():
            pieces.append(f'{attr_key}="{attr_val}"')
        pieces.append(" />")

        # This requires the clean_banner_name() JS function. Warn in development if not loaded
        if utility_service.is_development() and not utility_service.get_session_var(
            "banner_character_functions"
        ):
            message_service.post_warning(
                "{%banner_name_input%} requires a call to {%banner_character_functions%} in the scripts block."
            )

        return " ".join(pieces)


class BannerTextNode(template.Node):
    """Generates an input that cleans a non-name content for entry into Banner"""

    def __init__(self, args):
        self.args = args

    def render(self, context):
        # Prepare attributes
        attrs = support.process_args(self.args, context)

        # Value needs special processing
        value, changed = validation_service.clean_special_characters(attrs.get("value"))
        attrs["value"] = value if value else ""

        # Onchange needs special processing
        _onchange = attrs.get("onchange")
        if _onchange:
            onchange = (
                "clean_banner_characters($(this), function(){" + _onchange + "});"
            )
        else:
            onchange = "clean_banner_characters($(this));"
        attrs["onchange"] = onchange

        pieces = ["<input"]
        for attr_key, attr_val in attrs.items():
            pieces.append(f'{attr_key}="{attr_val}"')
        pieces.append(" />")

        # This requires the clean_banner_characters() JS function. Warn in development if not loaded
        if utility_service.is_development() and not utility_service.get_session_var(
            "banner_character_functions"
        ):
            message_service.post_warning(
                "{%banner_text_input%} requires a call to {%banner_character_functions%} in the scripts block."
            )

        return " ".join(pieces)


class FaNode(template.Node):
    """Handles the FontAwesome icon-generating tag"""

    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)
        # The FontAwesome (fa) classes are expected to be given first, without key="val" formatting
        # Collect all assumed fa classes first
        fa_classes = {k: v for k, v in attrs.items() if k == v}

        # Everything else should have been in key="value" format
        other_attributes = {k: v for k, v in attrs.items() if k != v}
        title = other_attributes.get("title")

        # fa class may be contained in a variable, in which case it can be provided via "fa_class" attr
        fa_class = other_attributes.get("fa_class")
        if fa_class:
            fa_classes[fa_class] = fa_class

        # Determine screen reader text
        if other_attributes.get("aria-hidden", "false").lower() == "true":
            aria_text = ""
        elif other_attributes.get("aria-label"):
            aria_text = other_attributes.get("aria-label")
            del other_attributes["aria-label"]
        elif title:
            aria_text = title
        else:
            aria_text = ""
        # If screen reader text was found, put it in a sr-only span
        if aria_text:
            aria_text = f'<span class="sr-only">{aria_text}</span>'

        # Icon will be wrapped in a button if it has an onclick action
        onclick = other_attributes.get("onclick")
        classes = other_attributes.get("class")
        if onclick:
            del other_attributes["onclick"]
            if classes:
                del other_attributes["class"]
            else:
                classes = ""
            icon = [
                f'<button type="button" onclick="{onclick}" class="btn btn-icon {classes}"'
            ]
        else:
            icon = ["<span"]

        for kk, vv in other_attributes.items():
            if kk == "title":
                # Title will be on the icon and in the sr-only span
                continue
            icon.append(f' {kk}="{vv}"')
        icon.append(">")

        # Build a basic FA icon inside the div or button
        icon.append('<span class="fa')
        for fa_class in fa_classes:
            icon.append(f" {fa_class}")
        icon.append('"')
        if title:
            icon.append(f' title="{title}"')
        # Icon should always be aria-hidden, since title/label was printed in an sr-only span
        icon.append(' aria-hidden="true"')
        icon.append("></span>")

        # Append hidden screen reader text, if present
        icon.append(aria_text)

        # Close the button or span wrapper
        if onclick:
            icon.append("</button>")
        else:
            icon.append("</span>")

        return "".join(icon)


class ImageNode(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        # Prepare attributes
        attrs = {}
        for arg in self.args[1:]:
            key = val = None
            if "=" in arg:
                key, val = arg.split("=")
            else:
                log.warn(
                    f'Ignoring invalid argument for image tag: {arg}. Arguments must be in \'key="value" format'
                )
                continue

            if val.startswith('"'):
                val = val.strip('"')
            else:
                val_str = template.Variable(val)
                val = val_str.resolve(context)

            # Allow src attribute to be called other things in this case
            if key.lower() in ["src", "source", "image", "file", "path", "filename"]:
                key = "src"

            attrs[key.lower()] = val

        # Prepend the static content url to the src
        if "src" in attrs:
            attrs[
                "src"
            ] = f"{utility_service.get_static_content_url()}/images/{attrs['src']}"
        # If no src was given, log warning and use empty src (for broken image indicator)
        else:
            log.warn("No image file name was provided as 'src' in the 'image' taglib")
            attrs["src"] = ""

        pieces = [f"<img"]
        for attr_key, attr_val in attrs.items():
            pieces.append(f'{attr_key}="{attr_val}"')
        pieces.append("/>")

        return " ".join(pieces)


class PhotoNode(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)

        # A user object must be provided
        user_instance = attrs.get("user")
        if not user_instance:
            log.warn("No user attribute was provided. ID photo cannot be displayed")

        # Does the user have a photo?
        if user_instance and user_instance.id_photo:
            src = user_instance.id_photo
            default_alt = f"ID photo of {user_instance.display_name}"
            has_img = True
        else:
            src = f"{utility_service.get_static_content_url()}/images/no-id-photo.png"
            default_alt = "Missing ID photo"
            has_img = False
            if user_instance and user_instance.display_name:
                default_alt += f" for {user_instance.display_name}"

        # Prepare attributes
        attrs = {}
        nvl = False
        for arg in self.args[1:]:
            key = val = None
            if "=" in arg:
                key, val = arg.split("=")
            elif arg == "user_instance":
                continue
            else:
                log.warn(
                    f'Ignoring invalid argument for id_photo tag: {arg}. Arguments must be in \'key="value" format'
                )
                continue

            if key.lower() == "src":
                log.warn(
                    "Ignoring src attribute in id_photo tag. The src is determined automatically."
                )
            elif key.lower() == "nvl":
                # Any value means True, except false or no
                nvl = val.lower() not in ["false", "no", "n"]
            else:
                if val.startswith('"'):
                    val = val.strip('"')
                else:
                    val_str = template.Variable(val)
                    val = val_str.resolve(context)

                attrs[key.lower()] = val

        # If alt not provided, use default
        if "alt" not in attrs:
            attrs["alt"] = default_alt

        # If no classes provided, use default class
        if "class" not in attrs:
            attrs["class"] = "id_photo"

        # If a valid user has no image, and using nvl, render their initials instead of a picture
        if user_instance and user_instance.is_valid() and (not has_img) and nvl:
            pieces = [f"<span"]
            for attr_key, attr_val in attrs.items():
                pieces.append(f'{attr_key}="{attr_val}"')
            pieces.append(">")
            pieces.append(
                f'<div class="id_photo-nvl">{user_instance.first_name[:1]}{user_instance.last_name[:1]}</div>'
            )
            pieces.append("</span>")
        else:
            pieces = [f'<img src="{src}"']
            for attr_key, attr_val in attrs.items():
                pieces.append(f'{attr_key}="{attr_val}"')
            pieces.append("/>")

        return " ".join(pieces)


class HeaderNavTab(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)

        # A URL and label must be provided
        url = attrs.get("url")
        url_arg = attrs.get("url_arg")
        label = attrs.get("label")
        icon = attrs.get("icon")
        icon_only = icon and attrs.get("icon_only")
        optional = attrs.get("optional")
        active_only = attrs.get("active_only")

        # Item is allowed for everyone if no authorities are specified
        allowed = True

        # A list of required authorities may be provided
        authorities = attrs.get("authorities", None)
        if type(authorities) is str:
            authorities = utility_service.csv_to_list(authorities)
        elif authorities and type(authorities) is not list:
            allowed = False
            log.warn(
                f"Invalid authority list was provided. Menu item will not be displayed: {url}"
            )

        if authorities and allowed:
            allowed = auth_service.has_authority(authorities)

        # If feature is specified, then feature must be enabled (skip check if already not allowed)
        if allowed:
            feature_code = attrs.get("feature", None)
            # If feature was specified, and is not active
            if feature_code and not utility_service.feature_is_enabled(feature_code):
                allowed = False

        # If not allowed, do not print the link
        if not allowed:
            return ""

        path = None
        is_active = False

        # If no URL was given
        if not url:
            log.warn("No URL was provided. Menu item cannot be marked active")

        # If root path is given
        elif url == "/":
            path = util_context(context.request).get("home_url")
            is_active = path == context.request.path

        # If using current path
        elif url == "#":
            path = context.request.path
            is_active = True

        # Named URL was probably given
        elif "/" not in url:
            try:
                if url_arg:
                    path = reverse(url, args=[url_arg])
                else:
                    path = reverse(url)
                is_active = path == context.request.path
            except Exception as ee:
                log.debug(f"Path comparison error: {str(ee)}")

        # Otherwise, maybe an actual URL was given
        else:
            path = url
            is_active = path == context.request.path

        if is_active:
            classes = "nav-item header-nav-item header-nav-item-active"
        elif active_only:
            return ""
        elif optional:
            classes = "nav-item header-nav-item header-nav-item-optional"
        else:
            classes = "nav-item header-nav-item"

        pieces = [f"""<li class="{classes}">"""]
        pieces.append(f"""<a href="{path}">""")

        if icon_only:
            pieces.append(
                f"""<span class="fa {icon} fa-fw" aria-hidden="true" title="{label}"> </span>"""
            )
            pieces.append(f"""<span class="sr-only">{label}</span>""")
        elif icon:
            pieces.append(
                f"""<span class="fa {icon} fa-fw" aria-hidden="true"> </span>"""
            )
            pieces.append(label)
        else:
            pieces.append(label)

        pieces.append("</a></li>")
        return " ".join(pieces)


class HeaderNavMenuItem(template.Node):
    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)

        # A map of attributes may be accepted in place of individual attributes
        attributes = attrs.get("attributes")
        if attributes:
            attrs.update(attributes)

        # A URL and label must be provided
        url = attrs.get("url")
        label = attrs.get("label", url)
        icon = attrs.get("icon", "fa-link")

        # Item is allowed for all admins and developers if no authorities are specified
        allowed = auth_service.has_authority("~power_user")

        # A list of required authorities may be provided
        authorities = attrs.get("authorities")

        # Turn authorities into a list
        if authorities and type(authorities) is not list:
            authorities = utility_service.csv_to_list(authorities)

        # If authorities were given and a list could not be generated from it
        if authorities and type(authorities) is not list:
            allowed = False
            log.warn(
                f"Invalid authority list was provided. Menu item will not be displayed: {label}"
            )

        if authorities:
            allowed = auth_service.has_authority(authorities)

        # If feature is specified, then feature must be enabled (skip check if already not allowed)
        if allowed:
            feature_code = attrs.get("feature")
            # If feature was specified, and is not active
            if feature_code and not utility_service.feature_is_enabled(feature_code):
                allowed = False

        # If not allowed, do not print the link
        if not allowed:
            return ""

        # If marked as non-prod only, do not include in prod
        if attrs.get("nonprod_only", False) and utility_service.is_production():
            return ""

        path = None
        is_active = False

        # If no URL was given
        if not url:
            log.warn("No URL was provided. Menu item cannot be marked active")

        # If root path is given
        elif url == "/":
            path = util_context(context.request).get("home_url")
            is_active = path == context.request.path

        # Assume named URL was given
        else:
            try:
                path = reverse(url)
                is_active = path == context.request.path
            except Exception as ee:
                log.debug(f"Path comparison error: {str(ee)}")

        if is_active:
            classes = "header-menu-item header-menu-item-active"
        else:
            classes = "header-menu-item"

        pieces = [f"""<a class="{classes}" href="{path}">"""]

        if icon:
            pieces.append(f"""<span class="fa {icon}" aria-hidden="true"> </span>""")

        pieces.append(label)
        pieces.append("</a>")
        return " ".join(pieces)


def pagination(paginated_results):
    """Example: {%pagination polls%}"""
    if paginated_results:
        # Show three pages on either side of the current page
        current_page = paginated_results.number  # 10    2
        min_page = current_page - 3  # 7     -1
        max_page = current_page + 3  # 13    5

        # If starting before page 1, shift min and max to be higher
        while min_page < 1:
            min_page += 1
            max_page += 1

        # If Extending past the last page, shift min and max lower
        while max_page > paginated_results.paginator.num_pages:
            min_page -= 1
            max_page -= 1

        # If shifting resulted in page less than 1, set it to page 1
        if min_page < 1:
            min_page = 1
    else:
        current_page = 1
        min_page = 1
        max_page = 1

    # Show dots to indicate pages not displayed?
    if paginated_results:
        dots_before = bool(min_page > 1)
        dots_after = bool(max_page < paginated_results.paginator.num_pages)
    else:
        dots_before = dots_after = False

    if paginated_results:
        start_item = paginated_results.start_index
        end_item = paginated_results.end_index
        num_items = paginated_results.paginator.count
    else:
        start_item = end_item = num_items = 0

    return {
        "paginated_results": paginated_results,
        "min_page": min_page,
        "max_page": max_page,
        "dots_before": dots_before,
        "dots_after": dots_after,
        "start_item": start_item,
        "end_item": end_item,
        "num_items": num_items,
    }


class SortableThNode(template.Node):
    """Create a sortable <th> for server-side pagination"""

    def __init__(self, args):
        self.args = args

    def render(self, context):
        attrs = support.process_args(self.args, context)

        # The column and heading can be specified under various keywords for convenience
        column = None
        for cv in ["col", "column", "property", "attr", "sort", "sortby", "sort_by"]:
            if cv in attrs:
                column = attrs[cv]
                break

        heading = column.capitalize() if column else None
        for hv in ["heading", "label"]:
            if hv in attrs:
                heading = attrs[hv]
                break

        # Last-sorted column was saved in utility_service.pagination_sort_info()
        # This assumes only one sorted dataset is being displayed at a time
        sorted_col = utility_service.get_session_var("psu_last_sorted_column")
        sorted_secondary_col = utility_service.get_session_var(
            "psu_last_secondary_sorted_column"
        )
        sorted_dir = utility_service.get_session_var("psu_last_sorted_direction")

        fa = None
        if sorted_col and sorted_dir:
            if column == sorted_col:
                fa = f"fa-sort-amount-{sorted_dir} font-weight-bold"
                title = "Primary sort column"
            elif "," in column and column.startswith(sorted_col):
                fa = f"fa-sort-amount-{sorted_dir} font-weight-bold"
                title = "Primary sort column"
            elif column == sorted_secondary_col:
                fa = f"fa-angle-{'down' if sorted_dir == 'desc' else 'up'} text-muted"
                title = "Secondary sort column"
            elif "," in column and column.startswith(sorted_secondary_col):
                fa = f"fa-angle-{'down' if sorted_dir == 'desc' else 'up'} text-muted"
                title = "Secondary sort column"

        pieces = [
            """<th scope="col">""",
            f"""<a href="?sort={column}">{heading}</a>""",
            f"""&nbsp;<span class="fa {fa}" aria-hidden="true" title="{title}"></span>"""
            if fa
            else "",
            """</th>""",
        ]

        return "".join(pieces)
