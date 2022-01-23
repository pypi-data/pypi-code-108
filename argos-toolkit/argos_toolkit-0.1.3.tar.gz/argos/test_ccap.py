import argparse
import cv2

from argos.ccapture import vcapture, get_roi


def make_parser():
    parser = argparse.ArgumentParser('Record video based on motion detection.'
                                     ' It can create an output video file with'
                                     ' only the frames between which some'
                                     ' motion was detected.'
                                     ' It also dumps a csv file with the'
                                     ' input frame no., output frame no., and'
                                     ' the time stamp for the output frame in'
                                     ' the input file.')
    parser.add_argument('-i', '--input', type=str, default='0',
                        help='Input source, '
                        'if unspecified or 0 use first available camera;'
                        'if string, extract motion from video file;'
                        'if an integer, that camera number.')
    parser.add_argument('-o', '--output', type=str, default='',
                        help='output file path')
    motion_group = parser.add_argument_group(
        title='Motion based',
        description='Capture video based on motion')
    motion_group.add_argument('-m', '--motion_based', action='store_true',
                              help='Whether to use motion detection')
    motion_group.add_argument('-k', '--kernel_width', type=int, default=21,
                              help='Width of the Gaussian kernel for smoothing'
                              ' the frame before comparison with previous'
                              'frame. Small changes are better detected '
                              ' With a smaller value (21 works well for about'
                              ' 40x10 pixel insects)')
    motion_group.add_argument('--threshold', type=int, default=10,
                              help='Grayscale threshold value for detecting'
                              ' change in pixel value between frames')
    motion_group.add_argument('-a', '--min_area', type=int, default=100,
                              help='Area in pixels that must change in'
                              ' order to consider it actual movement as'
                              'opposed to noise.'
                              ' Works with --motion_based option')
    motion_group.add_argument('--show_contours', action='store_true',
                              help='Draw the contours exceeding `min_area`.'
                              ' Useful for debugging')
    motion_group.add_argument('--show_diff', action='store_true',
                              help='Show the absolute difference between'
                              ' successive frames and the thresholded '
                              ' difference in two additional windows.'
                              ' Useful for debugging and choosing parameters'
                              ' for motion detection.'
                              'NOTE: the diff values are displayed using'
                              ' the infamous jet colormap, which turns out'
                              ' to be good at highlighting small differences')
    timestamp_group = parser.add_argument_group(
        title='Timestamp parameters',
        description='Parameters to display timestamp in recorded frame')
    timestamp_group.add_argument('-t', '--timestamp', action='store_true',
                                 help='Put a timestamp each recorded frame')
    timestamp_group.add_argument('--tx', type=int, default=15,
                                 help='X position of timestamp text')
    timestamp_group.add_argument('--ty', type=int, default=15,
                                 help='Y position of timestamp text')
    timestamp_group.add_argument('--tc', type=str, default='#ff0000',
                                 help='Color of timestamp text in web format'
                                 ' (#RRGGBB)')
    timestamp_group.add_argument('--tb', type=str, default='',
                                 help='Background color for timestamp text')
    timestamp_group.add_argument('--fs', type=float, default=1.0,
                                 help='Font scale for timestamp text '
                                 '(this is not font size).')
    parser.add_argument('--interval', type=float, default=-1,  #
                        help='Interval in seconds between acquiring frames.')
    parser.add_argument('--duration', type=str, default='',
                        help='Duration of recordings in HH:MM:SS format.'
                        ' If unspecified or empty string, we will record'
                        'indefinitely.')
    parser.add_argument('--interactive', type=int, default=1,
                        help='Whether to display video as it gets captured. '
                             'Setting it to 0 may speed up things a bit.')
    parser.add_argument('--roi', type=int, default=1,
                        help='Whether to select ROI.')
    parser.add_argument('--max_frames', type=int, default=-1,
                        help='After these many frames, save in a '
                        'new video file')
    parser.add_argument('--format', type=str, default='MJPG',
                        help='Output video codec, see '
                        'http://www.fourcc.org/codecs.php for description'
                        ' of available codecs on different platforms.'
                        ' default X264 produces the smallest videos')
    camera_group = parser.add_argument_group(
        title='Camera settings',
        description='Parameters to set camera properties')
    camera_group.add_argument('--fps', type=float, default=30,
                              help='frames per second, if recording from a'
                              ' camera, and left unspecified (or -1), we '
                              'record 120 frames first to estimate frame'
                              ' rate of camera.')
    camera_group.add_argument('--width', type=int, default=-1,
                              help='Frame width')
    camera_group.add_argument('--height', type=int, default=-1,
                              help='Frame height')
    # parser.add_argument('--logbuf', action='store_true',
    #                     help='Buffer the log messages to improve speed')
    return parser


    
def parse_interval(tstr):
    h = 0
    m = 0
    s = 0
    values = tstr.split(':')
    if len(values) < 1:
        raise ValueError('At least the number of seconds must be specified')
    elif len(values) == 1:
        s = int(values[0])
    elif len(values) == 2:
        m, s = [int(v) for v in values]
    elif len(values) == 3:
        h, m, s = [int(v) for v in values]
    else:
        raise ValueError('Expected duration in hours:minutes:seconds format')
    t = timedelta(hours=h, minutes=m, seconds=s)
    return t



if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    
    # setup_logger(f'{params["output"]}.log', params['logbuf'])
    if len(args.duration) > 0:
        duration = parse_interval(args.duration).total_seconds()
    else:
        duration = -1
    roi = get_roi(args.input, args.width, args.height)
    if roi is not None:
        roi_x, roi_y, roi_w, roi_h, width, height = roi
    else:
        roi_x, roi_y, roi_w, roi_h = 0, 0, args.width, args.height
        width = args.width,
        height = args.height
    
    vcapture(args.input, args.output, args.format, args.fps, args.interactive,
            width, height, roi_x, roi_y, roi_w, roi_h,
            args.interval,
            duration,
            args.max_frames,
            args.motion_based,
            args.threshold,
            args.min_area,
            args.kernel_width
            )
