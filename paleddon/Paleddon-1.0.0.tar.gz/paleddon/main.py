import click
from .f_installrdf import install_rdf
from .f_manifest import chrome_manifest
from .f_overlay_xul import overlay_xul
from .f_overlay_css import overlay_css
from .libs import generate_id, do_secure_name, check_locale_code, validate_id, build_addon


@click.group(help="Paleddon CLI")
def cli():
    pass


@click.command(help="Create addon manually")
@click.option('--id', default=generate_id(), help='Addon ID', callback=validate_id, prompt=True)
@click.option('--version', default="1.0.0", help='Initial version', prompt=True)
@click.option('--name', default="My Extension", help='Name of extension', prompt=True)
@click.option('--description', default="My addon description", help='Addon description', prompt=True)
@click.option('--creator', default="Jhon Doe", help='Creator of the addon', prompt=True)
@click.option('--homepage', default="http://www.example.com", help='Repository/Addon Support Page', prompt=True)
@click.option('--minVersion', default="28.*", help='Minimun supported browser version', prompt=True)
@click.option('--maxVersion', default="29.*", help='Maximum supported browser version', prompt=True)
@click.option('--existing/--not-existing', help="Replace addon folder if this already exist", default=False)
def custom(id, version, name, description, creator, homepage, minversion, maxversion, existing):
    contributors = []
    secure_name = do_secure_name(name)

    if click.confirm('Add contributors?'):
        ncont = click.prompt('Contributors number', default=1, type=int)

        for x in range(ncont):
            cont = click.prompt('Contributor name', default="Jhon Doe")
            contributors.append(cont)

    toolBtnData = {'type': False,
                   'tooltip': False,
                   'menu_options': False}

    localesData = []

    locales = click.confirm('Add locales? Must exist almost one: so default is en-US')
    if locales:
        nlocales = click.prompt('Locales number', default=1, type=int)
        for x in range(nlocales):
            locale_code = click.prompt('Locale code. Please use following format: en-US, es_ES...etc', default=f"en-US")
            if check_locale_code(locale_code):
                localesData.append(locale_code)
            else:
                raise excepts.LocaleCodeError("Error with locale code")
    else:
        localesData = ["en-US"]

    toolbarbutton = click.confirm('Have toolbar button?')
    if toolbarbutton:
        tooltip = click.prompt('Button tooltip', default="Pretty tooltip")

        button_type = click.prompt(
            "Button type",
            default="button",
            show_default=True,
            type=click.Choice(["button", "menu", "menu-button", "checkbox", "radio"],
                              case_sensitive=False))

        # GET TOOLTIP TEXT
        toolBtnData['type'] = button_type
        toolBtnData['tooltip'] = tooltip

        if button_type == 'menu' or button_type == 'menu-button':
            opts = []
            nopts = click.prompt('Options number', default=1, type=int)

            for x in range(nopts):
                option = click.prompt('Option text', default=f"Option {x + 1}")
                opts.append(option)

            toolBtnData['menu_options'] = opts

    file_installrdf = install_rdf(id, version, name, secure_name, description, creator, contributors, homepage, minversion, maxversion)
    file_installrdf = file_installrdf.build()

    file_manifest = chrome_manifest(secure_name, localesData, toolBtnData)
    file_manifest = file_manifest.build()

    file_overlay_xul = overlay_xul(name, secure_name, toolBtnData)
    file_overlay_xul = file_overlay_xul.build()

    file_overlay_css = overlay_css(secure_name, toolBtnData)
    file_overlay_css = file_overlay_css.build()

    build_addon(name, file_installrdf, file_manifest, file_overlay_xul, file_overlay_css, localesData, existing)


@click.command(help="Create fast addon with default values")
@click.option('--existing/--not-existing', help="Replace addon folder if this already exist", default=False)
def fast(existing):
    toolBtnData = {'type': 'button',
                   'tooltip': 'Amazing addon',
                   'menu_options': False}

    name = 'Amazing addon'
    secure_name = 'amazing_addon'

    file_installrdf = install_rdf(generate_id(),
                                  "1.0.0",
                                  "Amazing addon",
                                  "amazing_addon",
                                  "This is the best addon of the world",
                                  "Jhon Doe",
                                  [],
                                  "www.example.com",
                                  "28.*",
                                  "29.*")

    file_installrdf = file_installrdf.build()

    file_manifest = chrome_manifest(secure_name, ['en-US'], toolBtnData)
    file_manifest = file_manifest.build()

    file_overlay_xul = overlay_xul(name, secure_name, toolBtnData)
    file_overlay_xul = file_overlay_xul.build()

    file_overlay_css = overlay_css(secure_name, toolBtnData)
    file_overlay_css = file_overlay_css.build()

    build_addon(name, file_installrdf, file_manifest, file_overlay_xul, file_overlay_css, ['en-US'], existing)


cli.add_command(custom)
cli.add_command(fast)


def main():
    cli()


if __name__ == "__main__":
    cli()
