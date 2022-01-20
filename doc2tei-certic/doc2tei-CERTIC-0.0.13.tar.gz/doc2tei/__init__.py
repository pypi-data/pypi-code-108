import logging
import re
import fnmatch
from typing import List, Tuple
import os
import os.path
import sys
from subprocess import Popen, PIPE
import shutil
from xml.etree import ElementTree as ET
import glob
import base64

SOFFICE_PATH = shutil.which("soffice")
JAVA_PATH = shutil.which("java")
RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/resources/"
SAXON_PATH = os.getenv("SAXON_PATH") or (RESOURCES_PATH + "saxon9.jar")
XMLLINT_PATH = shutil.which("xmllint")

if not SOFFICE_PATH:
    sys.exit("Could not find soffice. Is it in your PATH ?")
if not JAVA_PATH:
    sys.exit("Could not find java. Is it in your PATH ?")
if not SAXON_PATH:
    sys.exit(
        "Could not find the Saxon jar. Please set SAXON_PATH environment variable."
    )
if not os.path.isfile(SAXON_PATH):
    sys.exit(
        "Could not find the Saxon jar. Please check your SAXON_PATH environment variable."
    )
if not XMLLINT_PATH:
    sys.exit("Could not find xmllint. Is it in your PATH ?")


def _silent_remove(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def _union_java_output(std_out: bytes, std_err: bytes) -> str:
    """
    Java outputs errors to STDOUT ???
    """
    if std_err:
        out = std_err.decode("utf-8")
        out = out.strip()
        if out:
            return out
    if std_out:
        out = std_out.decode("utf-8")
        out = out.strip()
        if out:
            return out
    return "subprocess provided no error output"


def _find_files(what: str, where: str = ".") -> List[str]:
    rule = re.compile(fnmatch.translate(what), re.IGNORECASE)
    return [
        "{}{}{}".format(where, os.path.sep, name)
        for name in os.listdir(where)
        if rule.match(name)
    ]


def _process_doc(
    doc_file,
    working_dir: str,
    logger: logging.Logger,
    keep_transient_files: bool = False,
) -> Tuple[bool, str]:
    doc_file_no_extension = os.path.splitext(doc_file)[0]
    transient_files = []
    #
    # STEP 1, convert to XML
    #
    cli_args = [
        SOFFICE_PATH,
        "--invisible",
        "--convert-to",
        "xml:OpenDocument Text Flat XML",
        "--outdir",
        working_dir,
        doc_file,
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        logger.info("Wrote {}".format(os.path.basename(doc_file_no_extension + ".xml")))
        transient_files.append(doc_file_no_extension + ".xml")
    p.terminate()

    #
    # STEP 2 : TRANSFORMATIONS XSL
    # 2a, cleanup
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + ".xml",
        RESOURCES_PATH + "cleanup/cleanup.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_01_clean.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_01_clean.xml")
                )
            )
            transient_files.append(doc_file_no_extension + "_01_clean.xml")

    #
    # STEP 2 : TRANSFORMATIONS XSL
    # 2b, control styles
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + "_01_clean.xml",
        RESOURCES_PATH + "control/control.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_02_control.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_02_control.xml")
                )
            )
            transient_files.append(doc_file_no_extension + "_02_control.xml")

    control_xml = ET.fromstring(out.decode("utf-8"))
    for error_node in control_xml.findall(".//FATAL"):
        logger.fatal(error_node.text)
        return False, "Not OK"

    #
    # STEP 2 : TRANSFORMATIONS XSL
    # 2c, floatingText
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + "_02_control.xml",
        RESOURCES_PATH + "floatingText/floatingText.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_03_floatingText.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_03_floatingText.xml")
                )
            )
            transient_files.append(doc_file_no_extension + "_03_floatingText.xml")

    control_xml = ET.fromstring(out.decode("utf-8"))
    for error_node in control_xml.findall(".//FATAL"):
        logger.fatal(error_node.text)
        return False, "Not OK"

    #
    # STEP 2d, hierarchy
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + "_03_floatingText.xml",
        RESOURCES_PATH + "hierarchize/hierarchize.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_04_hierarchize.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_04_hierarchize.xml")
                )
            )
            transient_files.append(doc_file_no_extension + "_04_hierarchize.xml")

    #
    # STEP 2e, normalisation
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + "_04_hierarchize.xml",
        RESOURCES_PATH + "normalisation/normalize.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_05_normalize.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_05_normalize.xml")
                )
            )
            transient_files.append(doc_file_no_extension + "_05_normalize.xml")

    #
    # STEP 2f, modules to TEI
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + "_05_normalize.xml",
        RESOURCES_PATH + "totei-modules/totei.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_06_tei.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_06_tei.xml")
                )
            )
            transient_files.append(doc_file_no_extension + "_06_tei.xml")

    #
    # STEP 2f, modules to TEI
    #
    cli_args = [
        JAVA_PATH,
        "-jar",
        SAXON_PATH,
        doc_file_no_extension + "_06_tei.xml",
        RESOURCES_PATH + "toOpenedition/toOpenedition.xsl",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        return False, _union_java_output(out, err)
    else:
        with open(doc_file_no_extension + "_07_tei_openedition.xml", "wb") as f:
            f.write(out)
            logger.info(
                "Wrote {}".format(
                    os.path.basename(doc_file_no_extension + "_07_tei_openedition.xml")
                )
            )

    p.terminate()

    #
    # STEP 3 : VALIDATION
    #
    cli_args = [
        XMLLINT_PATH,
        "--schema",
        RESOURCES_PATH + "schema/metopes.xsd",
        doc_file_no_extension + "_06_tei.xml",
        "--noout",
    ]
    logger.debug(" ".join(cli_args))
    p = Popen(
        cli_args,
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        logger.error(
            "Validate {} {}".format(
                os.path.basename(doc_file_no_extension + "_06_tei.xml"),
                _union_java_output(out, err),
            )
        )
    else:
        logger.info(
            "Validate {}".format(
                os.path.basename(doc_file_no_extension + "_06_tei.xml validates")
            )
        )

    #
    # STEP 4: write images
    #
    for b64_path in glob.glob(working_dir + "/images/*.base64"):
        destination_path, _ = os.path.splitext(b64_path)
        with open(destination_path, "wb") as destination_file:
            with open(b64_path, "rb") as b64_file:
                destination_file.write(base64.decodebytes(b64_file.read()))
        _silent_remove(b64_path)

    if not keep_transient_files:
        for transient_file_path in transient_files:
            _silent_remove(transient_file_path)
        _silent_remove(doc_file)

    return True, "All OK"


def doc2tei(working_dir: str, logger: logging.Logger, options: dict = None):
    options = options or {}
    keep_transient_files = False
    if options.get("keep_transient_files", False) == "oui":
        keep_transient_files = True
    success_counter = 0
    failure_counter = 0
    doc_files = _find_files("*.docx", working_dir) + _find_files("*.odt", working_dir)
    logger.info("{} file(s) to convert.".format(len(doc_files)))
    for doc_file in doc_files:
        logger.info("converting {}".format(os.path.basename(doc_file)))
        success, output = _process_doc(
            doc_file, working_dir, logger, keep_transient_files
        )
        if not success:
            logger.error(
                "could not convert {}. Process output: {}".format(
                    os.path.basename(doc_file), output
                )
            )
            failure_counter = failure_counter + 1
        else:
            success_counter = success_counter + 1
            logger.info("{}: success".format(os.path.basename(doc_file)))
    logger.info("Job done, {} files converted".format(success_counter))


doc2tei.description = {
    "label": "Docx vers TEI",
    "help": "Convertir les fichiers *.docx et *.odt en fichiers *.xml (vocabulaire TEI)",
    "options": [
        {
            "id": "keep_transient_files",
            "label": "garder les fichiers intermédiaires",
            "values": {"oui": "oui", "non": "non"},
            "default": "non",
            "free_input": False,
        }
    ],
}
