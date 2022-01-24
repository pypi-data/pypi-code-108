from videoprops import get_video_properties
import datetime, glob, os, subprocess
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
exe_path = os.path.join(SCRIPT_DIR,'exiftool.exe')


def combine_videos(path=None):
    if(path is None):
        print('Please provide path for folder with .MP4 files')
        return

    if not(os.path.exists(path)):
        print(path + ' does not exist.')
        return

    filePath = os.path.join(path, '*.MP4')
    df = pd.DataFrame(columns=['fname', 'start', 'stop','duration(s)'])
    i = 0
    for file in sorted(glob.glob(filePath)):
        fname = os.path.basename(file)
        props = get_video_properties(file)
        dur_s = int(props['duration'].split('.')[0])
        num_frame = int(props['nb_frames'])
        frame_rate = int(num_frame / dur_s)
        frame_height = props['coded_height']
        frame_width = props['coded_width']

        time_created_str = props['tags']['creation_time']

        time_created = datetime.datetime.strptime(time_created_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        stop_time = time_created - datetime.timedelta(0, 1)
        start_time = stop_time - datetime.timedelta(0, dur_s)
        df.loc[i] = [fname, start_time, stop_time,dur_s]
        i = i + 1

    df['ref'] = df['start'].shift(periods=-1)
    df['gap'] = df['ref'] - df['stop']

    tmp_fold = os.path.join(os.path.dirname(file), 'tmp')
    if not os.path.exists(tmp_fold):
        os.makedirs(tmp_fold)
    file_list_txt = open(os.path.join(tmp_fold, 'file_list.txt'), 'w')

    num = len(df.index)
    for i in range(num):
        this_fname = df.loc[i, 'fname']

        file_to_add = os.path.join(os.path.dirname(file), this_fname)
        file_list_txt.write("file '%s'\n" % file_to_add)

        this_gap = df.loc[i, 'gap']
        if (i != num - 1):
            this_gap_s = int(this_gap.total_seconds())
            if (this_gap_s > 0):
                this_blankvideo_fname = os.path.join(tmp_fold, str(this_gap_s) + '_seconds_blank.MP4')

                if not os.path.exists(this_blankvideo_fname):
                    cmd = 'ffmpeg -f lavfi -i color=c=black:s=' + str(frame_width) + 'x' + str(
                        frame_height) + ':r=' + str(frame_rate) + ':d=' + str(this_gap_s) + ' ' + this_blankvideo_fname
                    print('CREATING BLANK VIDEO ' + this_blankvideo_fname)
                    p = subprocess.run(cmd, capture_output=True, shell=True)
                    if p.returncode != 0:
                        raise subprocess.CalledProcessError(p.returncode, cmd)
                    print('DONE CREATING BLANK VIDEO.')
                file_list_txt.write("file '%s'\n" % this_blankvideo_fname)

    file_list_txt.close()
    video_files = os.path.join(tmp_fold, 'file_list.txt')
    start_datetime = (df.loc[0, 'start']- datetime.timedelta(0, 1)).to_pydatetime().strftime("%Y-%m-%d_%H-%M-%S")
    stop_datetime = (df.loc[num - 1, 'stop']- datetime.timedelta(0, 1)).to_pydatetime().strftime("%Y-%m-%d_%H-%M-%S")

    metadata_file = os.path.join(tmp_fold, start_datetime + '_TO_' + stop_datetime + '.csv')
    metadata_df = df[['fname', 'start', 'stop','duration(s)']]
    metadata_df.to_csv(metadata_file,index=False)

    concatenated_file = os.path.join(tmp_fold, start_datetime + '_TO_' + stop_datetime + '.MP4')

    st_time_str = (df.loc[0, 'start']- datetime.timedelta(0, 1)).to_pydatetime().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    cmd = 'ffmpeg -f concat -safe 0 -i ' + video_files + ' -metadata creation_time="' + st_time_str +'" -c copy ' + concatenated_file

    print('COMBINING VIDEOS...')
    p = subprocess.run(cmd, capture_output=True, shell=True)

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)

    print("DONE COMBINING VIDEOS.")

    print("MANIPULATING FILE MODIFIED TIME METADATA TO FIX ISSUE WITH THE ANNOTATION TOOL")

    # st_time_str = (df.loc[0, 'start'] - datetime.timedelta(0, 1)).to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
    cmd = exe_path+' "-FileModifyDate=' + st_time_str +'" ' + concatenated_file
    p = subprocess.run(cmd, capture_output=True, shell=False)

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    print("DONE MANIPULATING COMBINED FILE METADATA.")

# combine_videos('C:/Users\BINOD\Documents/tmp/mp4')