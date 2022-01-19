from django import template
from django.utils.html import format_html, mark_safe
from psu_base.services import utility_service
from psu_base.classes.Log import Log
from django.urls import reverse

log = Log()


def wdt_url(version=None):
    return utility_service.get_static_content_url() + "/wdt/v{}".format(
        str(version) if version else "1"
    )


def jquery(*args, **kwargs):
    url = utility_service.get_static_content_url() + "/wdt/jquery/"

    if "version" in kwargs and kwargs["version"] is not None:
        file_name = "jquery-{}.min.js".format(kwargs["version"].strip())
    else:
        file_name = "jquery.min.js"

    return format_html(
        f"""<script src="{url}{file_name}?v={utility_service.get_setting('PSU_BASE_VERSION')}"></script>"""
    )


def bootstrap(*args, **kwargs):
    url = utility_service.get_static_content_url() + "/wdt/bootstrap/"
    if "version" in kwargs and kwargs["version"] is not None:
        url += "{}/".format(kwargs["version"])

    return format_html(
        f"""
        <script src="{url}js/bootstrap.js"></script>
        <link rel="stylesheet" href="{url}css/bootstrap.css" />
        """
    )


def datatables(*args, **kwargs):
    url = utility_service.get_static_content_url() + "/wdt/datatables/"
    if "version" in kwargs and kwargs["version"] is not None:
        url += "{}/".format(kwargs["version"])

    return format_html(
        f"""
        <link rel="stylesheet" href="{url}datatables.min.css" />
        <script src="{url}datatables.min.js"></script>
        """
    )


def jquery_confirm(*args, **kwargs):
    log.trace()
    url = utility_service.get_static_content_url() + "/wdt/jquery_confirm/"
    if "version" in kwargs and kwargs["version"] is not None:
        url += "{}/".format(kwargs["version"])

    defaults = """
        <script type="text/javascript">
            jconfirm.defaults = {
                title: false,
                content: 'Are you sure?',
                contentLoaded: function(){},
                icon: '',
                confirmButton: 'Okay',
                cancelButton: 'Cancel',
                confirmButtonClass: 'btn-default',
                cancelButtonClass: 'btn-default',
                theme: 'modern',
                animation: 'Rotate',
                closeAnimation: 'scale',
                animationSpeed: 500,
                animationBounce: 1.2,
                keyboardEnabled: true,
                rtl: false,
                confirmKeys: [13], // ENTER key
                cancelKeys: [27], // ESC key
                container: 'body',
                confirm: function () {},
                cancel: function () {},
                backgroundDismiss: false,
                autoClose: false,
                closeIcon: null,
                columnClass: 'col-md-4 col-md-offset-4 col-sm-6 col-sm-offset-3 col-xs-10 col-xs-offset-1',
                onOpen: function(){},
                onClose: function(){},
                onAction: function(){}
            };
        </script>
        <style>
            .jconfirm.jconfirm-modern .jconfirm-box div.jconfirm-content{
                color: black;
            }
        </style>
    """
    return f"""
        <link rel="stylesheet" href="{url}jquery-confirm.min.css">
        <script src="{url}jquery-confirm.min.js"></script>
        {defaults}
    """


def chosen(*args, **kwargs):
    url = utility_service.get_static_content_url()
    wdt = wdt_url(kwargs["version"] if "version" in kwargs else None)
    return format_html(
        f"""
        <link rel="stylesheet" href="{url}/css/chosen.min.css" />
        <script src="{url}/javascript/chosen.jquery.min.js"></script>
        <script src="{wdt}/javascript/chosen-apply.js"></script>
        """
    )


def banner_character_functions(*args, **kwargs):
    utility_service.set_session_var("banner_character_functions", True)
    name_url = reverse("psu:clean_banner_name")
    chars_url = reverse("psu:clean_banner_chars")
    return mark_safe(
        """
        <script type="text/javascript">
        function clean_banner_name(el, callback){
            $.ajax({
                type:   "GET",
                url:    "##NAME-URL##",
                data:   {name: el.val()},
                dataType: "json",
                success:function(json_data){
                    console.log(json_data);
                    el.val(json_data.clean_name);
                    if(json_data.name_changed){
                        el.addClass('ajax-error');
                        el.attr('title', 'Disallowed characters have been removed or replaced');
                    }
                    else{
                        el.removeClass('ajax-error');
                        el.attr('title', '');
                    }
                },
                complete:function(){
                    if(typeof callback !== 'undefined'){
                        callback();
                    }
                }
            });
        }
        function clean_banner_characters(el, callback){
            $.ajax({
                type:   "GET",
                url:    "##CHARS-URL##",
                data:   {content: el.val()},
                dataType: "json",
                success:function(json_data){
                    console.log(json_data);
                    el.val(json_data.clean_content);
                    if(json_data.content_changed){
                        el.addClass('ajax-error');
                        el.attr('title', 'Disallowed characters have been removed or replaced');
                    }
                    else{
                        el.removeClass('ajax-error');
                        el.attr('title', '');
                    }
                },
                complete:function(){
                    if(typeof callback !== 'undefined'){
                        callback();
                    }
                }
            });
        }
        </script>
        """.replace(
            "##NAME-URL##", name_url
        ).replace(
            "##CHARS-URL##", chars_url
        )
    )


def font_awesome(*args, **kwargs):
    url = utility_service.get_static_content_url() + "/wdt/fontawesome/"
    if "version" in kwargs and kwargs["version"] is not None:

        # FontAwesome 4 is CSS rather than SVG
        if kwargs["version"] == "4":
            return format_html(
                f"""<link rel="stylesheet" href="{url}4/css/font-awesome.min.css" />"""
            )

        else:
            url += "{}/js/all.js".format(kwargs["version"])
    else:
        url += "recent/js/all.js"

    return format_html(f"""<script defer src="{url}"></script>""")


def wdt_stylesheet(css_file, version=None):
    url = wdt_url(version)
    return format_html(
        f'<link rel="stylesheet" href="{url}/styles/{css_file}?v={utility_service.get_app_version()}" />'
    )


def wdt_javascript(js_file, version=None):
    url = wdt_url(version)
    return format_html(
        f"""
        <script src="{url}/javascript/{js_file}"></script>
        """
    )
