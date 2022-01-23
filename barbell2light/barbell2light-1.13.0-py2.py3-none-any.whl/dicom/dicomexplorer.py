import os
import cmd2
import pydicom

from barbell2light.dicom import is_dicom_file, get_dicom_tag_for_name, get_dictionary_items


class DicomExplorer:

    def __init__(self):
        self.files = []

    # LOAD

    def load_file(self, f, verbose=True):
        if not os.path.isfile(f):
            if verbose:
                print('Cannot find file {}'.format(f))
            return
        if is_dicom_file(f):
            self.files.append(f)
            if verbose:
                print(f)

    def load_dir(self, d, verbose=True):
        if not os.path.isdir(d):
            if verbose:
                print('Cannot find directory {}'.format(d))
            return
        for root, dirs, files in os.walk(d):
            for f in files:
                f = os.path.join(root, f)
                self.load_file(f, verbose)
        if verbose:
            print('Loaded {} files'.format(len(self.files)))

    # CONVERT

    def to_raw(self, d_out, verbose=True):
        result = os.system('which gdcmconv>/dev/null')
        if result > 0:
            raise RuntimeError('Tool "gdcmconv" is not installed')
        os.makedirs(d_out, exist_ok=False)
        for f in self.files:
            f_target = os.path.join(d_out, os.path.split(f)[1])
            command = 'gdcmconv --raw {} {}'.format(f, f_target)
            os.system(command)
            if verbose:
                print('Converted {}'.format(f))

    # INSPECTION

    @staticmethod
    def get_header(f, verbose=True):
        if os.path.isfile(f) and is_dicom_file(f):
            p = pydicom.read_file(f, stop_before_pixels=True)
            if verbose:
                print(p)
            return p
        return None

    @staticmethod
    def get_pixel_data(f):
        if os.path.isfile(f) and is_dicom_file(f):
            p = pydicom.read_file(f, stop_before_pixels=False)
            return p.pixel_array
        return None


    @staticmethod
    def get_tags(key_word='', verbose=True):
        outputs = []
        for key, value in get_dictionary_items():
            output = '{}: {}'.format(key, value)
            if key_word == '':
                outputs.append(output)
                if verbose:
                    print(output)
            else:
                for item in value:
                    if key_word in item:
                        outputs.append(output)
                        if verbose:
                            print(output)
        return outputs

    def get_tag_values(self, tag_name, verbose=True):
        tag = get_dicom_tag_for_name(tag_name)
        if verbose:
            print(tag)
        values = {}
        for f in self.files:
            p = pydicom.read_file(f)
            if tag in list(p.keys()):
                values[f] = p[tag].value
                if verbose:
                    print('{}: {}'.format(f, values[f]))
        return values

    def check_pixels(self, verbose=True):
        bad_files = []
        for f in self.files:
            p = pydicom.read_file(f)
            try:
                p.convert_pixel_data()
            except NotImplementedError:
                bad_files.append(f)
                if verbose:
                    print('ERROR: {}'.format(f))
        return bad_files


class DicomExplorerShell(cmd2.Cmd):

    def __init__(self):
        super(DicomExplorerShell, self).__init__()
        self.intro = 'Welcome to the DICOM Explorer Shell!'
        self.prompt = '(dicom) '
        self.debug = True
        self.explorer = DicomExplorer()

    def do_load_file(self, f):
        """ Usage: load_file <file>
        Loads single DICOM file <file>
        """
        self.explorer.load_file(f)
        self.poutput('Done')

    def do_load_dir(self, d):
        """ Usage: load_dir <directory>
        Loads all DICOM files (recursively) in given <directory>"""
        self.explorer.load_dir(d)
        self.poutput('Done')

    def do_to_raw(self, d_out='.'):
        """ Usage: to_raw
        Converts all loaded DICOM files to RAW format using GDCM"""
        self.explorer.to_raw(d_out)
        self.poutput('Done')

    def do_show_header(self, f):
        """ Usage: show_header <file>
        Show header information for DICOM file <file>"""
        self.explorer.get_header(f)
        self.poutput('Done')

    def do_show_tags(self, key_word):
        """ Usage: show_tags <key_word>
        Show all tags containing <key_word>"""
        self.explorer.get_tags(key_word)
        self.poutput('Done')

    def do_show_tag_values(self, tag_name):
        """ Usage: show_tag_values <tag_name>
        For all loaded DICOM files, show value of tag <tag_name>"""
        tag_values = self.explorer.get_tag_values(tag_name)
        with open('tag_values.txt', 'w') as f:
            for k in tag_values.keys():
                f.write('{}: {}\n'.format(k, tag_values[k]))
        self.poutput('Done (written string output to tag_values.txt)')

    def do_check_pixels(self, _):
        """ Usage: check_pixels
        For all loaded DICOM files, check whether the pixels can be loaded into a NumPy array. If not,
        the pixel values probably need to be converted to RAW format. Use the to_raw() function for that"""
        self.explorer.check_pixels()
        self.poutput('Done')


def main():
    import sys
    shell = DicomExplorerShell()
    sys.exit(shell.cmdloop())


if __name__ == '__main__':
    main()
