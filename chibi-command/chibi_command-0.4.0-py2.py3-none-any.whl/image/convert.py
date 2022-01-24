from chibi_command import Command


class Convert( Command ):
    """
    NAME
        convert -  convert between image  formats as  well as resize  an image,
        blur, crop, despeckle, dither, draw on, flip, join, re-sample, and much
        more.

    SYNOPSIS
        convert [input-options] input-file [output-options] output-file

    OVERVIEW
        The convert program  is a member of the ImageMagick(1)  suite of tools.
        Use it  to convert between  image formats as  well as resize  an image,
        blur, crop, despeckle, dither, draw on, flip, join, re-sample, and much
        more.

        For   more  information   about   the  convert   command,  point   your
        browser   to  file:///usr/share/doc/ImageMagick-7/www/convert.html   or
        http://imagemagick.org/script/convert.php.
    """
    command = 'convert'
    captive = False

    @classmethod
    def stripe( cls, *args, **kw ):
        return cls()( '-stripe', *args, **kw  )
