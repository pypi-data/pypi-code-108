from upyog.imports import *
from upyog.os.read_files import PathLike


__all__ = ["load_json", "check_pil_simd_usage", "sanitise_filename"]


def load_json(path: PathLike):
    "Load a JSON file"
    return json.loads(Path(path).read_bytes())


def check_pil_simd_usage():
    pil_version = PIL.__version__

    if not "post" in pil_version:
        msg = f"Pillow-SIMD not installed. Using PIL {pil_version} instead"
        warnings.warn(msg)

    else:
        if not PILFeatures.check_feature("libjpeg_turbo"):
            warnings.warn(
                f"Pillow-SIMD is installed, but Libjpeg Turbo is not being used. "
                f"Unlikely to see any speedups"
            )


# fmt: off
def sanitise_filename(
    f: str, lowercase=False, prefix=None, truncate: Optional[int] = 240
):
    # see https://stackoverflow.com/questions/49460802/regex-match-all-vular-fractions
    fractions = "\u00BC-\u00BE\u2150-\u215E"  # not-exhaustive..?
    supscripts = "\u00B1-\u00B9"

    fn = re.sub(f'[\W{supscripts}{fractions}]', '_', f) # captures (?) subscripts, fractions, other non-alphanumerics
    fn = re.sub(f'[^A-Za-z0-9_+]', '_', fn)             # captures alphabets in foreign languages
    fn = re.sub('^[\W_]*'     , '' , fn)                # replace leading spl characters or '_'

    assert re.match("^[A-Za-z0-9_]*$", fn), f'{fn} contains non-alphanumeric/underscore characters'
    assert re.match("^[A-Za-z0-9]",    fn), f'{fn} OR {f} starts with a non-alphanumeric character'

    if prefix: fn = f"{prefix}{fn}"
    if truncate: fn = fn[:truncate]
    if lowercase: fn = fn.lower()

    return fn
# fmt: on
