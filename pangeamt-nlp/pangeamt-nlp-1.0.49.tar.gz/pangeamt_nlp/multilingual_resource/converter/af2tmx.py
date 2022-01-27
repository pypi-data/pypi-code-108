from pangeamt_nlp.multilingual_resource.tmx.tmx_writter import TmxWriter
from typing import Union, Optional
from pangeamt_nlp.multilingual_resource.af.af import Af


def af2tmx(file: Union["Af", str],
           name: Optional[str] = None,
           jump_error: Optional[bool] = False):

    af = Af(file) if type(file) is str else file
    new_file = name if name is not None else af.file[:-3] + '.tmx'

    src_lang = af.header.left.lang
    tgt_lang = af.header.right.lang

    tmx_writer = TmxWriter(new_file, src_lang=src_lang)

    with tmx_writer:
        try:
            for src, tgt in af.read():
                with tmx_writer.create_tu() as tu:
                    tu.write(src, src_lang)
                    tu.write(tgt, tgt_lang)
        except Exception as e:
            if jump_error:
                pass
            else:
                print(e)
                exit()
