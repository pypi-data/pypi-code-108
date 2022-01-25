"""
Write text onto an SimpleSurface object.

This class allows for easier manipulation of text being written on a
Surface. Basic functionality is provided, such as specifying the font
(based on a local font file), font size, and location of text. More
advanced functionality is also provided, including:

- specifying the maximum width and height of the text box
- text alignment (right, center, left, justified)
- determining the location of the text box as a string, instead of a
  number (e.g., top, bottom, left, right, center)
- text box padding
- text outline with a desired outline width and color
- automatic resizing of the text to fill the text box if a font size is
  not specified
- support for newlines ('\n') within the text string, including
  successive newlines (e.g., '\n\n\n')
- automatic line breaks for long lines of text at a specified font size
  (newlines are still taken into account in this case)
"""
import ctypes as ct

import cairo


class TextSurface:
    """Write a block of text according to provided attributes."""

    def __init__(self, calling_surface):
        """
        Initialize the TextSurface object.

        Keyword arguments:
                calling_surface (SimpleSurface) -- the surface onto which
                        text will be written.

        Class attributes:
                alignment (str) -- the alignment of the text.
                break_lines (bool) -- whether to break text up into
                        multiple lines if it's too long.
                color (4-tuple) -- the color of the text as an RGB(A) tuple.
                exterior_extended_surface (SimpleSurface) -- the Surface
                        containing the text within the padding.
                font_size (int) -- the font size, in pts.
                full_line_height (float) -- the height of one line of text,
                        including ascent and descent.
                interior_extended_surface (SimpleSurface) -- the Surface
                        containing just the text.
                justify_last_line (bool) -- whether to justify the last line
                        of text , if the text is justified.
                line_spacing (float) -- the line spacing multiplier.
                max_height (int) -- the maximum vertical space the text and
                        padding will take up, in pixels.
                max_width (int) -- the maximum horizontal space the text and
                        padding will take up, in pixels.
                min_font_size (int) -- the minimum font size, in pts.
                outline_width (int) -- the text outline width, in pixels.
                outline_color (4-tuple) -- the color of the text outline as
                        an RGB(A) tuple.
                padding (dict) -- the padding around the text, in pixels.
                text_height (float) -- the height of the bounding box
                        containing the text.
                text_lines (list) -- the text once split up into separate lines.
                text_lines_metadata (dict) -- the metadata for each line of text
                        (width, line height, line ascent, line descent, x bearing,
                        and y bearing)
                text_width (float) -- the width of the bounding box
                        containing the text.
        """
        self.calling_surface = calling_surface

        self.exterior_extended_surface = None
        self.interior_extended_surface = None

        self.alignment = None
        self.break_lines = None
        self.color = None
        self.font = None
        self.font_face = None
        self.font_size = None
        self.justify_last_line = None
        self.line_spacing = None
        self.max_width = None
        self.max_height = None
        self.min_font_size = None
        self.outline_width = None
        self.outline_color = None
        self.padding = None

        self.full_line_height = None
        self.text_lines = []
        self.text_lines_metadata = {}
        self.text_width = None
        self.text_height = None

    def write(self, text, x, y, font, **kwargs):
        # Make sure the (x, y)-coordinates are sent in properly
        if isinstance(x, str):
            assert x in ["left", "center", "right"], (
                f"parameter 'x' cannot be '{x}', must be either a number "
                "or one of 'left', 'center', or 'right'"
            )
        if isinstance(y, str):
            assert y in ["top", "center", "bottom"], (
                f"parameter 'y' cannot be '{y}', must be either a number "
                "or one of 'top', 'center', or 'bottom'"
            )

        # Set the font path
        self.font = font

        # Import the SimpleSurface module
        from .SimpleSurface import SimpleSurface

        # Initialize the text attributes based on the keyword arguments
        self._init_attributes(**kwargs)

        # Convert the text sent in to a string
        text = str(text)

        # Take care of the case when an empty string is sent in
        if text == "":
            return None, None

        # Calculate the maximum width and height the text block can be,
        # based on desired location, surface size, and padding
        self._set_max_dimensions(x, y)

        # If font_size == "fill", calculate the largest font size the
        # text can be
        if self.font_size == "fill":
            self.font_size = self._calculate_max_font_size(text)

        # If we can't determine a font size, then exit out
        assert (
            self.font_size >= 0
        ), f"Cannot write text given these constraints: {text}, {x}, {y}, {font}, {kwargs}"

        # Now that we have a font size, split the text up into separate lines
        self.text_lines = self._split_text_into_lines(text)

        # Get the width, height, and metadata of each line of text
        self.text_width, self.text_height, self.text_lines_metadata = self._get_text_dimensions(
            self.text_lines
        )

        # Create the interior SimpleSurface to hold the text block
        self.interior_extended_surface = SimpleSurface(
            int(self.text_width + self.outline_width), int(self.text_height + self.outline_width)
        )

        # Write the text to the interior
        self._write_text_to_interior()

        # Create the exterior SimpleSurface to hold the text block within
        # the given padding
        self.exterior_extended_surface = SimpleSurface(
            int(
                self.padding["left"]
                + self.interior_extended_surface.get_width()
                + self.padding["right"]
            ),
            int(
                self.padding["top"]
                + self.interior_extended_surface.get_height()
                + self.padding["bottom"]
            ),
        )

        # Paste the interior surface to the exterior based on the padding
        self.exterior_extended_surface.paste(
            self.interior_extended_surface, self.padding["left"], self.padding["top"]
        )

        # Make sure the x and y coordinates are set to actual numbers
        x, y = self._calculate_final_coordinates(x, y)

        # Paste the exterior surface to the calling surface
        self.calling_surface.paste(self.exterior_extended_surface, x, y)

        # Grab the dimensions of the exterior surface to return
        exterior_dimensions = [
            self.exterior_extended_surface.get_width(),
            self.exterior_extended_surface.get_height(),
        ]

        # Delete the now-unnecessary objects to free up memory
        del self.interior_extended_surface
        del self.exterior_extended_surface
        del self.font_face

        # Return the dimensions of the box containing the text and padding
        return exterior_dimensions

    def _calculate_final_coordinates(self, x, y):
        """
        Return the final (x, y)-coordinates of the text on the calling surface.

        Keyword arguments:
                x (float/str) -- the x-coordinate of the text. It can either
                        be a number, or one of "left", "center", "right".
                y (float/str) -- the y-coordinate of the text. It can either
                        be a number, or one of "top", "center", "bottom".
        """
        # Grab the dimensions for easier code readability
        calling_width = self.calling_surface.get_width()
        calling_height = self.calling_surface.get_height()
        exterior_width = self.exterior_extended_surface.get_width()
        exterior_height = self.exterior_extended_surface.get_height()

        # Convert the x-coordinate if it was sent in as a string
        if x == "left":
            x = 0
        elif x == "center":
            x = (calling_width - exterior_width) / 2
        elif x == "right":
            x = calling_width - exterior_width

        # Convert the y-coordinate if it was sent in as a string
        if y == "top":
            y = 0
        elif y == "center":
            y = (calling_height - exterior_height) / 2
        elif y == "bottom":
            y = calling_height - exterior_height

        return x, y

    def _calculate_max_font_size(self, text):
        """
        Return the largest font size the text can be.

        Keyword arguments:
                text (str) -- the text to check the font size against.
        """
        # Set the minimum and maximum font size placeholders
        min_font_size = int(self.min_font_size)
        max_font_size = int(self.max_height * 3)

        # Make sure the minimum font size is not too big
        text_width, text_height = self._dims_at_font_size(text, self.min_font_size)

        assert (
            text_width <= self.max_width and text_height <= self.max_height
        ), f"keyword argument 'min_font_size' too big: {self.min_font_size}"

        # Make sure the min font size is smaller than the max font size
        assert (
            min_font_size <= max_font_size
        ), f"cannot reconcile font size: {min_font_size} > {max_font_size}"

        # Threshold for how far apart the max and min font sizes can be
        # before we break the binary search
        threshold = 10

        # Do a binary search for the font size
        while True:
            # Leave if the max and min font sizes are within the
            # threshold from one another
            if max_font_size - min_font_size <= threshold:
                break

            # Calculate the midpoint between the two font sizes
            mid_font_size = (max_font_size + min_font_size) // 2

            # Get the text dimensions at the mid font size
            text_width, text_height = self._dims_at_font_size(text, mid_font_size)

            # If the text is too big in either dimension, then scale it down.
            # Otherwise, scale it up.
            if text_width > self.max_width or text_height > self.max_height:
                max_font_size = mid_font_size
            else:
                min_font_size = mid_font_size

        # Now that our max and min font sizes are relatively close,
        # go through them and find the one that works best
        font_size = max_font_size - 1
        for font_size_inc in range(min_font_size, max_font_size):
            # Get the text dimensions at the attempted font size
            text_width, text_height = self._dims_at_font_size(text, font_size_inc)

            # As soon as one or both dimensions gets too big,
            # choose the font size just below it
            if text_width > self.max_width or text_height > self.max_height:
                font_size = font_size_inc - 1
                break

        # Return the font size
        return font_size

    def _create_font_face(self, face_index=0, load_options=0):
        """
        Return a PyCairo font face, given a font file.

        NOTE: I did not write this method, and I actually do not really know
        how it works. The original source code can be found at:
        https://www.cairographics.org/cookbook/freetypepython/

        Given the name of a font file, and optional face_index to pass to
        FT_New_Face and load_options to pass to
        cairo_ft_font_face_create_for_ft_face, creates a cairo.FontFace
        object that may be used to render text with that font.

        Keyword arguments:
                face_index (int) -- the face index? (default 0)
                load_options (int) -- the load options? (default 0)
        """
        cairo_status_success = 0
        ft_err_ok = 0

        # find shared objects
        _freetype_so = ct.CDLL("libfreetype.so.6")
        _cairo_so = ct.CDLL("libcairo.so.2")
        _cairo_so.cairo_ft_font_face_create_for_ft_face.restype = ct.c_void_p
        _cairo_so.cairo_ft_font_face_create_for_ft_face.argtypes = [ct.c_void_p, ct.c_int]
        _cairo_so.cairo_font_face_get_user_data.restype = ct.c_void_p
        _cairo_so.cairo_font_face_get_user_data.argtypes = (ct.c_void_p, ct.c_void_p)
        _cairo_so.cairo_font_face_set_user_data.argtypes = (
            ct.c_void_p,
            ct.c_void_p,
            ct.c_void_p,
            ct.c_void_p,
        )
        _cairo_so.cairo_set_font_face.argtypes = [ct.c_void_p, ct.c_void_p]
        _cairo_so.cairo_font_face_status.argtypes = [ct.c_void_p]
        _cairo_so.cairo_font_face_destroy.argtypes = (ct.c_void_p,)
        _cairo_so.cairo_status.argtypes = [ct.c_void_p]
        # initialize freetype
        _ft_lib = ct.c_void_p()
        status = _freetype_so.FT_Init_FreeType(ct.byref(_ft_lib))
        if status != ft_err_ok:
            raise RuntimeError(f"Error {status} initializing FreeType library.")

        class PycairoContext(ct.Structure):
            """PyCairo Context"""

            _fields_ = [
                ("PyObject_HEAD", ct.c_byte * object.__basicsize__),
                ("ctx", ct.c_void_p),
                ("base", ct.c_void_p),
            ]

        _surface = cairo.ImageSurface(cairo.FORMAT_A8, 0, 0)
        _ft_destroy_key = ct.c_int()  # dummy address

        ft_face = ct.c_void_p()
        cr_face = None
        try:
            # load FreeType face
            status = _freetype_so.FT_New_Face(
                _ft_lib, self.font.encode("utf-8"), face_index, ct.byref(ft_face)
            )
            if status != ft_err_ok:
                raise RuntimeError(f"Error {status} creating FreeType font face for {self.font}")

            # create Cairo font face for freetype face
            cr_face = _cairo_so.cairo_ft_font_face_create_for_ft_face(ft_face, load_options)
            status = _cairo_so.cairo_font_face_status(cr_face)
            if status != cairo_status_success:
                raise RuntimeError(f"Error {status} creating cairo font face for {self.font}")

            # Problem: Cairo doesn't know to call FT_Done_Face when its
            # font_face object is destroyed, so we have to do that for it, by
            # attaching a cleanup callback to the font_face. This only needs to
            # be done once for each font face, while
            # cairo_ft_font_face_create_for_ft_face will return the same
            # font_face if called twice with the same FT Face. The following
            # check for whether the cleanup has been attached or not is
            # actually unnecessary in our situation, because each call to
            # FT_New_Face will return a new FT Face, but we include it here to
            # show how to handle the general case.
            if _cairo_so.cairo_font_face_get_user_data(cr_face, ct.byref(_ft_destroy_key)) is None:
                status = _cairo_so.cairo_font_face_set_user_data(
                    cr_face, ct.byref(_ft_destroy_key), ft_face, _freetype_so.FT_Done_Face
                )
                if status != cairo_status_success:
                    raise RuntimeError(f"Error {status} doing user_data dance for {self.font}")
                ft_face = None  # Cairo has stolen my reference

            # set Cairo font face into Cairo context
            cairo_ctx = cairo.Context(_surface)
            cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx
            _cairo_so.cairo_set_font_face(cairo_t, cr_face)
            status = _cairo_so.cairo_font_face_status(cairo_t)
            if status != cairo_status_success:
                raise RuntimeError(f"Error {status} creating cairo font face for {self.font}")

        finally:
            _cairo_so.cairo_font_face_destroy(cr_face)
            _freetype_so.FT_Done_Face(ft_face)

        # get back Cairo font face as a Python object
        face = cairo_ctx.get_font_face()
        return face

    def _dims_at_font_size(self, text, font_size):
        """
        Return the width and height of text at a given font size.

        Keyword arguments:
                text (str) -- the text to check.
                font_size (int) -- the font size, in pts.
        """
        # Split the text up into lines based on the font size
        lines = self._split_text_into_lines(text, font_size)

        # Get the width and height of the text
        width, height = self._get_text_dimensions(lines, font_size)[0:2]

        # Return the text dimensions for the text based on the font size
        return width, height

    def _get_text_dimensions(self, lines, font_size=None):
        """
        Return the width and height of the bounding box that exactly
        contains the block of text, along with a dictionary of each
        line's metadata.

        Keyword arguments:
                lines (list) -- a list of lines of text.
                font_size (int) -- the font size (default self.font_size).
        """
        if font_size is None:
            font_size = self.font_size

        # Save the state of our Context so we can restore it when this is done
        self.calling_surface.context.save()

        # Set up the font for our Context
        self.calling_surface.context.set_font_face(self.font_face)
        self.calling_surface.context.set_font_size(font_size)

        # Calculate the maximum height of a line of text
        font_ascent, font_descent = self.calling_surface.context.font_extents()[0:2]
        self.full_line_height = font_ascent + font_descent

        # Initialize what we'll be returning
        text_height = 0
        text_width = 0
        line_dictionary = {}

        # The overall height of the text is the font height for each line
        # except the top and bottom: the top line only measures up to the top
        # of the tallest letter, and the bottom line only measures down to the
        # bottom of the lowest letter's descent.
        for index, line in enumerate(lines):
            # Grab the text extents of the line of text
            x_bearing, y_bearing, width, height = self.calling_surface.context.text_extents(line)[
                0:4
            ]

            # Set the line ascent and descent equal to those of the font
            line_ascent = font_ascent
            line_descent = font_descent

            # If this is the top line, change the line ascent to the
            # y-bearing of the line.
            # Note that the y-bearing is negative if the text is above
            # the origin (which means it's usually negative), so we have
            # to account for that.
            if index == 0:
                line_ascent = -y_bearing

            # If this is the bottom line, change the line descent to
            # the descent of this line's text.
            # Note that the y-bearing is negative if the text is above
            # the origin (which means it's usually negative), so we have
            # to account for that.
            if index == len(lines) - 1:
                line_descent = height - (-y_bearing)

            # Set the line height as the sum of the ascent and descent
            line_height = line_ascent + line_descent

            # Add the line height to the height of the block of text
            text_height += line_height

            # If this line is longer than any previous, record it
            text_width = max(text_width, width)

            # Add the metadata of the line to its entry in the dictionary
            line_dictionary[index] = [
                width,
                line_height,
                line_ascent,
                line_descent,
                x_bearing,
                y_bearing,
            ]

        # Calculate the height of the extra space between the lines.
        # Note that we aren't including space below the bottom line, and that
        # we need to remove the height of the text itself to just give us the
        # space between the lines.
        line_spacing_height = (len(lines) - 1) * (self.line_spacing - 1) * self.full_line_height

        # Add the line spacing height to the full height of the text block
        text_height += line_spacing_height

        # Restore our Context back to its original state
        self.calling_surface.context.restore()

        return text_width, text_height, line_dictionary

    def _init_attributes(self, **kwargs):
        """
        Initialize the class attributes based on the keyword arguments sent in.

        Keyword arguments:
                **kwargs (dict) -- the keyword arguments (see TextSurface.write()
                        documentation for list of all keyword arguments)
        """
        # Grab the text attributes from the keyword arguments
        self.alignment = kwargs.get("alignment", "left")
        self.break_lines = kwargs.get("break_lines", True)
        self.color = kwargs.get("color", (0, 0, 0))
        self.font_face = self._create_font_face()
        self.font_size = kwargs.get("font_size", "fill")
        self.justify_last_line = kwargs.get("justify_last_line", False)
        self.line_spacing = kwargs.get("line_spacing", 1.0)
        self.max_width = kwargs.get("max_width", "fill")
        self.max_height = kwargs.get("max_height", "fill")
        self.min_font_size = kwargs.get("min_font_size", 7)
        self.outline_width = kwargs.get("outline_width", 0)
        self.outline_color = kwargs.get("outline_color", (0, 0, 0))

        # Set the default padding and update it with whatever's sent in
        self.padding = {"top": 0, "right": 0, "bottom": 0, "left": 0}
        padding = kwargs.get("padding", {})
        for pad, amt in padding.items():
            self.padding[pad] = amt

        # Make sure the attributes sent in follow the desired format.
        # We're doing this after the fact because some attributes might not
        # have been sent in, so they wouldn't be in kwargs.
        assert self.alignment in ("left", "center", "right", "justified"), (
            f"parameter 'alignment' cannot be '{self.alignment}', must be "
            "one of: 'left', 'right', 'center', 'justified'"
        )
        padding_keys_good = all(pad in ("top", "right", "bottom", "left") for pad in padding)
        assert padding_keys_good, (
            "All keys in 'padding' must be one of: 'top', 'right', 'bottom', " "'left'"
        )
        if isinstance(self.font_size, str):
            assert self.font_size == "fill", (
                f"parameter 'font_size' cannot be '{self.font_size}', must "
                "be either a number or 'fill'"
            )

    def _outline_text(self, x, y, text):
        """
        Outline the given text.

        Keyword arguments:
                x (float) -- the x-coordinate.
                y (float) -- the y-coordinate.
                text (str) -- the string to outline.
        """
        # Outline the text by stroking along it
        self.interior_extended_surface.context.save()
        self.interior_extended_surface._set_color(self.outline_color)
        self.interior_extended_surface.context.move_to(x, y)
        self.interior_extended_surface.context.text_path(text)
        self.interior_extended_surface.context.set_line_width(self.outline_width)
        self.interior_extended_surface.context.stroke()
        self.interior_extended_surface.context.restore()

    def _set_max_dimensions(self, x, y):
        """
        Calculate the maximum width and height the text block can be.

        Keyword arguments:
                x (float) -- the x-coordinate where the text is being placed.
                y (float) -- the y-coordinate where the text is being placed.
        """
        # Check if the box width is set to "fill". If it is, then set it to the
        # width of the page, minus the x-placement
        if self.max_width == "fill":
            # The maximum possible width is the surface width minus the padding
            self.max_width = self.calling_surface.get_width() - (
                self.padding["left"] + self.padding["right"]
            )

            # If we specify a numerical x-position, take that into account
            if isinstance(x, (float, int)):
                self.max_width -= x

        # If a value was sent in, adjust it based on the padding
        else:
            self.max_width -= self.padding["left"] + self.padding["right"]

        # Check if the box height is set to "fill". If it is, then set it to
        # the height of the page, minus the y-placement
        if self.max_height == "fill":
            # The maximum possible height is the surface height minus the
            # padding
            self.max_height = self.calling_surface.get_height() - (
                self.padding["top"] + self.padding["bottom"]
            )

            # If we specify a numerical y-position, take that into account
            if isinstance(y, (float, int)):
                self.max_height -= y

        # If a value was sent in, adjust it based on the padding
        else:
            self.max_height -= self.padding["top"] + self.padding["bottom"]

        # Reduce the max dimensions by the outline width as well, since the
        # outline straddles the edge of the text on all sides
        self.max_width -= self.outline_width
        self.max_height -= self.outline_width

    def _split_text_into_lines(self, text, font_size=None):
        """
        Return a list of strings gotten by splitting up the text by
        newlines ('\n'). This method also breaks up long lines of text
        as needed.

        Keyword arguments:
                text (str) -- the text to split up, potentially containing
                        newlines.
                font_size (int) -- the size of the font (default self.font_size).
        """
        if font_size is None:
            font_size = self.font_size

        # The list of lines of text, where each entry is a string of
        # words separated by spaces
        lines = []

        # The list containing the words contained in the current line
        line = []

        # Split the text up into words
        words = text.split(" ")

        # Go through each word
        for word in words:
            # Split the word up by newlines (even if there aren't any)
            split_words = word.split("\n")

            # Get the width of the current line plus the first word from the
            # split. This will tell us if we can put this word at the end of
            # the current line or if we need to put it on its own line.
            line_width = self._get_text_dimensions([" ".join(line + [split_words[0]])], font_size)[
                0
            ]

            # If it doesn't fit, flush the current line to the list of lines.
            # Only do this if we already have at least one word in the line.
            # Also only do this if we want long lines broken up.
            if self.break_lines and line_width > self.max_width and len(line) > 0:
                lines.append(" ".join(line))
                line = []

            # Add the first word in the split list into the current line
            line.append(split_words[0])

            # If there was at least one newline
            if len(split_words) > 1:
                # Flush the current line
                lines.append(" ".join(line))
                line = []

                # Run through the middle of the split list and flush
                # each word to its own line
                for i in range(1, len(split_words) - 1):
                    lines.append(" ".join([split_words[i]]))

                # Add the last element to the current line
                line.append(split_words[-1])

        # If we've run through them all and there's still a line left,
        # add it to the list of lines
        if line:
            lines.append(" ".join(line))

        return lines

    def _write_text_to_interior(self):
        """
        Write the lines of text to the interior SimpleSurface.

        Go through the text line by line and write it. The placement of
        the text is calculated according to the alignment.

        If the text is justified, then the space between words is
        calculated and each word on the line is written, moving over by
        the custom space. The last word on that line is right-aligned to
        make sure the justification lines up along the right side.
        """
        # Set the text attributes to the interior's Context
        self.interior_extended_surface.context.set_font_face(self.font_face)
        self.interior_extended_surface.context.set_font_size(self.font_size)
        self.interior_extended_surface._set_color(self.color)

        # Our first y-coordinate is the height of the top line's ascent,
        # plus half of the outline width
        y = self.text_lines_metadata[0][2] + self.outline_width / 2

        for index, line in enumerate(self.text_lines):
            # Grab some needed attributes of the line
            line_width = self.text_lines_metadata[index][0]
            x_bearing = self.text_lines_metadata[index][4]

            # Set the initial x-position based on the text alignment.
            # If the text is justified, calculate the spacing between words.
            if self.alignment == "left":
                x = -x_bearing + self.outline_width / 2
            elif self.alignment == "center":
                x = (self.text_width - line_width) / 2 - x_bearing + self.outline_width / 2
            elif self.alignment == "right":
                x = (self.text_width - line_width) - x_bearing + self.outline_width / 2
            elif self.alignment == "justified":
                x = -x_bearing + self.outline_width / 2

                # Get the width of the text without spaces by summing up
                # the width of each word.
                # Note that we don't simply remove the spaces and measure the
                # result, because the kerning between words might affect it.
                no_spaces_width = 0
                for word in line.split():
                    no_spaces_width += self._get_text_dimensions([word])[0]

                # Set the line width to be the whole line, accounting for the
                # outline
                line_width = self.text_width - self.outline_width

                # If we're at the last line of our text, or at the last line
                # in a paragraph, and we don't want to justify it, set the line
                # width back to what it was
                if (
                    index == len(self.text_lines) - 1
                    or (index < len(self.text_lines) - 1 and len(self.text_lines[index + 1]) == 0)
                ) and not self.justify_last_line:
                    line_width = self.text_lines_metadata[index][0]

                # Divide the difference in widths by the number of spaces to
                # get the new space width. If there's only one word on the
                # line, then this doesn't matter
                space_width = ((line_width - no_spaces_width)) / max((len(line.split()) - 1), 1)

            # If the text is justified, write the line word by word,
            # using custom spacing
            if self.alignment == "justified":
                # Go through each word
                for word in line.split():
                    # Outline the word first
                    self._outline_text(x, y, word)

                    # Write the word
                    self.interior_extended_surface.context.move_to(x, y)
                    self.interior_extended_surface.context.show_text(word)

                    # Move forward the predetermined amount of space
                    word_width = self._get_text_dimensions([word])[0]
                    x += word_width + space_width

            # Otherwise, just write the line normally
            else:
                # Outline the line first
                self._outline_text(x, y, line)

                # Write the line
                self.interior_extended_surface.context.move_to(x, y)
                self.interior_extended_surface.context.show_text(line)

            # Move down to the next line
            y += self.line_spacing * self.full_line_height
