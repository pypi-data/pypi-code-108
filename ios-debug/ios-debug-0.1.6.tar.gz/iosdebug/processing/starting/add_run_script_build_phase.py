from iosdebug.constants import RUN_SCRIPT_PHASE_ID, SYNC_RUN_SCRIPT_FILE
import os
import re


RUN_SCRIPT_PHASE = """
    BBF071DD2631DA3900DF13DA /* Sync debug mode */ = {
        isa = PBXShellScriptBuildPhase;
        buildActionMask = 2147483647;
        files = (
        );
        inputFileListPaths = (
        );
        inputPaths = (
        );
        name = "Sync debug mode";
        outputFileListPaths = (
        );
        outputPaths = (
        );
        runOnlyForDeploymentPostprocessing = 0;
        shellPath = /bin/sh;
        shellScript = "if [ -n \\"$CI\\" ]; then\\n    echo \\"Running on CI Skipping\\"\\n    exit 0\\nfi\\n\n/usr/bin/python3 ${PROJECT_DIR}/.ios-debug_sync.py";
    };"""
BUILD_PHASE = "				BBF071DD2631DA3900DF13DA /* Sync debug mode */,"


RUN_SCRIPT_BUILD_PHASE = """
import os
from iosdebug.stop import stop
from iosdebug.start import start

try:
    if os.environ['ENABLE_PREVIEWS'] == "YES":
        raise SystemExit
except KeyError:
    pass

stop(update_project=False)
start(update_project=False)
""".strip()


def add_run_script_build_phase(path):
    print("Adding run script build phase...")
    files = os.listdir(path)
    xcodeproj_file_name = [file for file in files if ".xcodeproj" in file][0]
    project_file = path + os.sep + xcodeproj_file_name + os.sep + "project.pbxproj"
    with open(project_file, "r") as file:
        content = file.read()
        if RUN_SCRIPT_PHASE_ID in content:
            return

        shell_scripts_part_end = "/* End PBXShellScriptBuildPhase section */"

        if shell_scripts_part_end in content:
            content = content.replace(
                shell_scripts_part_end, RUN_SCRIPT_PHASE + "\n" + shell_scripts_part_end
            )
        else:
            content += (
                shell_scripts_part_end.replace("End", "Start")
                + "\n"
                + RUN_SCRIPT_PHASE
                + "\n"
                + shell_scripts_part_end
            )

        native_target_section = re.findall(
            r"/\* Begin PBXNativeTarget section \*/([\s\S]+)/\* End PBXNativeTarget section \*/",
            content,
        )[0]
        targets = re.split(r"[A-Z0-9]{24} /\* .* \*/ =", native_target_section)[1:]
        app_flavours = [
            target
            for target in targets
            if 'productType = "com.apple.product-type.bundle.unit-test";' not in target
            and 'productType = "com.apple.product-type.bundle.ui-testing";'
            not in target
        ]
        build_phases_start = "buildPhases = ("
        for flavour in app_flavours:
            new_flavour = flavour.replace(
                build_phases_start, build_phases_start + "\n" + BUILD_PHASE
            )
            content = content.replace(flavour, new_flavour)

    with open(project_file, "w") as file:
        file.write(content)

    with open(SYNC_RUN_SCRIPT_FILE, "w") as file:
        file.write(RUN_SCRIPT_BUILD_PHASE)

    print("Run script build phase added.")