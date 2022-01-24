"""The scripts manager is used to manage the scripts in customization
packages as well as the Extender Scripts config."""
from accpac import showMessageBox, Continue

from extools.view import exgen
from extools.vi import import_script, remove_script
from extools.package import get_package_file_content

def screen_handler_on_after_insert(
        screen, package, template_path, module_id, config_view):

    if not screen.startswith("VI") and registrations(screen, config_view) == 1:
        name = template_path.name
        script_name = get_script_name(module_id, screen, name)
        script_content = get_package_file_content(package, template_path)
        script_content = script_content.replace("{PROGRAM}", screen)
        import_script(script_name, script_content)
        showMessageBox("Registered new screen handler. "
                       "Restart the desktop to finish the registration.")
    return Continue

def screen_handler_on_after_delete(
        screen, template_path, module_id, config_view):
    if not screen.startswith("VI") and registrations(screen, config_view) == 1:
        # We are the last.
        name = template_path.name
        remove_script(get_script_name(module_id, screen, name))
        showMessageBox(("Removed script handler for screen {}. "
                        "Restart the desktop to clean up.").format(
                            screen))
    return Continue

def get_script_name(module, screen, name):
    return "{}.{}.{}".format(module, screen, name)

def registrations(screen, config_view):
    count = 0
    for config in exgen(config_view):
        if config.get("SCREEN") == screen:
            count += 1
    return count
