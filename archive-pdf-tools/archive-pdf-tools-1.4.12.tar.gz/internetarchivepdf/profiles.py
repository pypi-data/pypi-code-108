# archive-pdf-tools
# Copyright (C) 2020-2021, Internet Archive
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Merlijn Boris Wolf Wajer <merlijn@archive.org>


soorten profiles:

- profile voor mrc image *generatie*: dpi, downsample, denoise

- profile voor compressie (jpeg,jpeg2000,compression params, jbig2,ccitt), hq
  pages, image_mode


# TODO: Use argparse groups for these

image_args = [
    args.denoise_mask,
    args.downsample
    args.bg_downsample
    args.fg_downsample,
    args.dpi,
]

compression_args = [
    args.image_mode,
    args.mask_compression == COMPRESSOR_JBIG2,
    args.jpeg2000_implementation,
    args.bg_compression_flags.split(' '),
    args.fg_compression_flags.split(' '),
    args.mrc_image_format,
    args.hq_pages,
    args.hq_bg_compression_flags.split(' '),
    args.hq_fg_compression_flags.split(' '),
]

metadata_args = [
    args.metadata_url, args.metadata_title, args.metadata_author,
    args.metadata_creator, args.metadata_language,
    args.metadata_subject, args.metadata_creatortool,
]

input_args = [
    args.from_pdf, args.from_imagestack,
    args.hocr_file, args.scandata_file,
    args.out_pdf,
    args.out_dir,
]

misc_args = [
    args.reporter,
    args.verbose,
    args.report_every,
    args.stop_after,
    args.render_text_lines,
    args.tmp_dir,

    args.grayscale_pdf,
    args.bw_pdf,
]


