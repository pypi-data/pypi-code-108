#   Copyright (c) 2021, Zenqi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from typing import Any, Optional


def convert_string(
    value: Any, 
    encoding: str='utf-8'
) -> str:

    """
    Convert the given value of bytes to string.
    """

    if isinstance(value, bytes):
        value = value.decode(
            encoding=encoding
        )

    else:
        value = str(value)

    return value

def convert_bytes(
    value: Any, 
    encoding: str='utf-8'
) -> bytes:

    """
    Convert the given value of bytes to string.
    """
    if isinstance(value, str):
        value = value.encode(
            encoding=encoding
        )

    else:
        value = bytes(
            value,
            encoding=encoding
        )

    return value

def password_with_asterisk(
    password: str, 
    percentage: Optional[float] = 40
):
    
    if len(password) <= 2:
        return "*" * len(password)
  
    percent = int(
        (percentage * len(password)) / 100.0
    )
        
    _ = "*" * (len(password) - percent)
    return "%s%s" % (_, password[-percent:])
    
