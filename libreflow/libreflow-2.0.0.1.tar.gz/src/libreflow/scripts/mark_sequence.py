#!/usr/bin/env python3

# Mark sequence, copyright (C) 2020 Les Fées Spéciales
# voeu@les-fees-speciales.coop
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import os
import platform
import subprocess
import json
import argparse
import fileseq
import textwrap
from tempfile import mkdtemp
from math import inf
from concurrent.futures import ThreadPoolExecutor


__all__ = ['default_template', 'SequenceMarker']

# Paths of installed binaries, depending on environment
# It would be better to let the OS handle the path, but for now let's not
bins = {'Linux':
        {'ffmpeg': 'ffmpeg',
         'convert': 'convert'},
        'Windows':
        {'ffmpeg': 'ffmpeg',
         'convert': 'convert'},
        'Darwin':
        {'ffmpeg': 'ffmpeg',
         'convert': 'convert'}
}


default_template = {
    "settings": {
        "font_size": 24,
        "color": "white"
        # "color": "chartreuse"
    },
    "fields": [
        {
            "name": "project",
            "direction": "NorthWest",
            "string": " %s "
        },
        {
            "name": "sequence",
            "direction": "NorthWest",
            "string": "%s "
        },
        {
            "name": "scene",
            "direction": "NorthWest",
            "string": "%s "
        },
        {
            "name": "frame_number",
            "direction": "NorthWest",
            "string": "%s"
        },
        {
            "name": "normalized_frame_number",
            "direction": "North",
            "string": "%04i / "
        },
        {
            "name": "total_images",
            "direction": "North",
            "string": "%s"
        },
        {
            "name": "file_name",
            "direction": "NorthEast",
            "string": " %s "
        },
        {
            "name": "version",
            "direction": "NorthEast",
            "string": " %s "
        },
        {
            "name": "resolution",
            "direction": "NorthEast",
            "string": " %s "
        },
        {
            "name": "copyright",
            "direction": "SouthWest",
            "string": " %s "
        },
        {
            "name": "simplify",
            "direction": "SouthWest",
            "string": " %s "
        },
        {
            "name": "focal_length",
            "direction": "SouthWest",
            "string": " Focal length: %d mm "
        },
        {
            "name": "studio",
            "direction": "SouthEast",
            "string": " %s "
        },
        {
            "name": "user",
            "direction": "SouthEast",
            "string": " %s "
        },
        {
            "name": "hostname",
            "direction": "SouthEast",
            "string": " %s "
        },
        {
            "name": "date",
            "direction": "SouthEast",
            "string": " %s "
        }
    ],
    "image_fields": [
        # {
        #     "name": "circle",
        #     "direction": "SouthWest",
        #     "geometry": "10x10+20+4"
        # }
    ]
}

class SequenceMarker():
    def __init__(self, image_filepath, data, template=default_template):
        self.data = data
        self.template = template
        self.create_temp_dir()

        self.file_sequence = fileseq.findSequenceOnDisk(image_filepath)
        self.frame_set = self.file_sequence.frameSet()

    def create_temp_dir(self):
        """Create temporary directory for images"""
        if 'mark_dir' in self.data and self.data['mark_dir']:
            self.mark_dir = self.data['mark_dir']
            os.makedirs(self.mark_dir, exist_ok=True)
        else:
            self.mark_dir = mkdtemp()

    def delete_temp_dir(self):
        """Delete temporary directory"""
        if not ('mark_dir' in self.data and self.data['mark_dir']):
            print("Deleting temp dir...")
            from shutil import rmtree
            rmtree(self.mark_dir)

    def mark_sequence(self):
        last_image_marked = self.mark_images()

        marked_sequence = fileseq.findSequenceOnDisk(last_image_marked)
        if self.data['video_output']:
            self.render_video(self.get_sequence_path(marked_sequence),
                              os.path.abspath(self.data['video_output']),
                              audio_file=self.data["audio_file"],
                              frame_rate=self.data["frame_rate"])

        self.delete_temp_dir()

    def mark_images(self):
        """Batch mark images"""
        image_data = self.data.copy()

        # Special fields: for each special field, give a default if it is
        # specified in the template but not passed as data
        for field in self.template['fields']:
            if field['name'] == 'date':
                import datetime
                image_data['date'] = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
            if field['name'] == 'user':
                import getpass
                image_data['user'] = getpass.getuser()
            if field['name'] == 'hostname':
                import platform
                image_data['hostname'] = platform.node()
            if field['name'] == 'total_images':
                image_data['total_images'] = len(self.frame_set)

        with ThreadPoolExecutor() as executor:
            for i, image_number in enumerate(self.frame_set):
                if (image_number < self.data['start_frame']
                    or image_number > self.data['end_frame']):
                    continue
                image_source = self.file_sequence.frame(image_number)
                image_marked = os.path.join(self.mark_dir,
                                            "marked.%04i.tif" % (i - self.data['offset'] + 1))

                # Special fields evaluated at each frame
                for field in self.template['fields']:
                    if field['name'] == 'frame_number':
                        image_data['frame_number'] = image_number
                    if field['name'] == 'normalized_frame_number':
                        image_data['normalized_frame_number'] = i - self.data['offset'] + 1
                    if field['name'] in self.data and type(self.data[field['name']]) is dict:
                        image_data[field['name']] = self.data[field['name']][image_number]

                executor.submit(self.mark_image, image_source, image_marked, image_data.copy())

        # Return last image path
        return image_marked

    def mark_image(self, path, output_path, image_data):
        '''Use ImageMagick's convert command line utility to overlay metadata on
        specified image'''
        print("Marking image %s..." % image_data['frame_number'])

        convert_bin = bins[platform.system()]['convert']
        convert_args = [convert_bin]
        convert_args += ['%s' % path]

        settings = self.template['settings']

        # Add gray band overlay
        convert_args.extend(['-fill', 'rgba(0,0,0,0.5)'])
        convert_args.extend(['-draw', 'rectangle 0,0 %s,%s' % (image_data['resolution_x'],
                                                               settings['font_size'])])
        convert_args.extend(['-draw', 'rectangle 0,%s %s,%s' % (image_data['resolution_y'] -
                                                                settings['font_size'] - 2,
                                                                image_data['resolution_x'],
                                                                image_data['resolution_y'])])

        directions = {}

        # Add annotations for each field to the list of directions
        # This has the effect of concatenating various fields for a given direction
        for field in self.template['fields']:
            direction = field['direction']
            value = field['string']
            # Try formatting the string with the value from the passed data
            try:
                value %= image_data[field['name']]
            except BaseException as e:
                print(f"Could not evaluate field {field['name']}: {e}")
                continue
            if not direction in directions:
                directions[direction] = ''
            directions[direction] += (value)

        # Set text color and size for outside stroke
        convert_args.extend(['-fill', 'black', '-strokewidth', '3',
                             '-stroke', 'black', '-weight', 'bold',
                             '-pointsize', str(settings['font_size'])])

        # Add annotations for each field, for outside stroke
        for direction, value in directions.items():
            convert_args.extend(['-gravity', direction, '-annotate', '0', value])

        # Set text color and size for fill
        convert_args.extend(['-fill', settings['color'],
                             '-stroke', 'none', '-weight', 'bold',
                             '-pointsize', str(settings['font_size'])])

        # Add annotations for each field, with only inside fill
        for direction, value in directions.items():
            convert_args.extend(['-gravity', direction, '-annotate', '0', value])

        # Add image annotations
        for image in self.template['image_fields']:
            convert_args.append('(')

            # File path, either from template or from command line
            if image['field'] and image_data[image['field']]:
                convert_args.append(os.path.abspath(image_data[image['field']]))
            else:
                convert_args.append(image['path'])
            convert_args.extend([
                '-gravity', image['direction'],
                '-geometry', image['geometry'],
                ')',
                '-composite'])

        # Debug alpha channel
        convert_args.extend(['-alpha', 'remove'])
        convert_args.extend(['-compress', 'Piz'])  # TODO : remettre DWAA quand ffmpeg le permettra

        # Output
        convert_args.append('%s' % output_path)
        # Windows needs to use shell=True, see https://stackoverflow.com/a/41860823
        proc = subprocess.run(convert_args, check=True, shell=platform.system() == 'Windows')

    def render_video(self, img_sources, destination, audio_file=None, frame_rate=25):
        print("Generating video...")
        ffmpeg_bin = bins[platform.system()]['ffmpeg']
        ffmpeg_args = [ffmpeg_bin, '-y', '-loglevel', 'error']
        ffmpeg_args.extend(['-r', str(frame_rate)])
        ffmpeg_args.extend(['-i', img_sources])

        if audio_file is not None:
            ffmpeg_args.extend(['-i', audio_file])
            ffmpeg_args.extend(['-c:a', 'aac', "-b:a", "160k"])
            ffmpeg_args.extend(["-map", "0:0", "-map", "1:0"])

        ffmpeg_args.extend(['-c:v', 'mjpeg', '-q:v', '3'])
        # ffmpeg_args.extend(['-c:v', 'h264', '-crf', '25', '-preset', 'slow', '-pix_fmt', 'yuv420p'])

        os.makedirs(os.path.dirname(destination), exist_ok=True)
        ffmpeg_args.extend(['%s' % (destination)])

        proc = subprocess.run(ffmpeg_args)

    @staticmethod
    def get_sequence_path(sequence):
        padding = sequence.getPaddingNum(sequence.padding())
        return sequence.format('{dirname}{basename}%0' + str(padding) + 'd{extension}')


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.indent(
            textwrap.dedent('''\

            Make an annotated movie output from a list of images. A JSON
            template may be specified, which will contain fields such as:

            {
                "name": "scene",
                "direction": "NorthWest",
                "string": ' sc%s '
            },

            You can then specify the option --scene on the command line, and
            the text will appear in the top left. Warning: underscores are
            replaced by dashes, so "my_field" becomes "my-field", to respect
            the customary option format.

            The direction uses ImageMagick’s convention: Center, North,
            NorthEast, East, SouthEast, South, SouthWest, West, NorthWest. If a
            direction is specified multiple times, the corresponding fields
            will be concatenated.

            '''
            ), '  '
        )
    )

    group = parser.add_argument_group('file options')
    group.add_argument('-t', '--template', type=str,
                        help='template file containing field descriptions')

    group.add_argument('image_sequence', type=str,
                        help='input image sequence, typically a frame in the sequence')
    group.add_argument('-d', '--mark-dir', type=str,
                        help='intermediate directory, leave blank for tmp dir')
    group.add_argument('-o', '--video-output', type=str,
                        help='render video to this destination')
    group.add_argument('-a', '--audio-file', type=str,
                        help='if rendering video, use this file as audio track')

    group.add_argument('-r', '--frame_rate', type=float, default=25.0,
                        help='playback speed')

    group = parser.add_argument_group('frame options')
    group.add_argument('-O', '--offset', type=int, default=0,
                        help='offset for renaming frames')
    group.add_argument('-s', '--start-frame', type=int, default=-inf,
                        help="don't mark images lower than this number")
    group.add_argument('-e', '--end-frame', type=int, default=inf,
                        help="don't mark images higher than this number")

    args = parser.parse_known_args()[0]

    # Load in template from supplied json file. If none given, use default one.
    if args.template is None:
        template = default_template
    else:
        with open(os.path.abspath(args.template), 'r') as f:
            template = json.load(f)

    # Add text fields to argument parser
    group = parser.add_argument_group('Template text field arguments')
    for field in template['fields']:
        field = field['name'].replace('_', '-')
        group.add_argument('--' + field, type=str, default='')

    # Add image fields to argument parser
    group = parser.add_argument_group('Template image field arguments')
    for image in template['image_fields']:
        image = image['name'].replace('_', '-')
        group.add_argument('--' + image, type=str, default='')

    args = parser.parse_args()

    sequence_marker = SequenceMarker(os.path.abspath(args.image_sequence), vars(args), template=template)

    # Get resolution from first image
    res = subprocess.check_output(['identify', '-format', '%wx%h',
                                   sequence_marker.file_sequence.frame(sequence_marker.frame_set[0])])
    res_x, res_y = res.decode('ascii').split("x")
    sequence_marker.data['resolution_x'] = int(res_x)
    sequence_marker.data['resolution_y'] = int(res_y)
    
    # If not specified, update sequence resolution with that of the first frame
    if not 'resolution' in sequence_marker.data:
        sequence_marker.data['resolution'] = res.decode('ascii')

    sequence_marker.mark_sequence()
