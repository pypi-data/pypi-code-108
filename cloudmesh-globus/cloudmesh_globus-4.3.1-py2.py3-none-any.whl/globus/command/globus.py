from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
import os



class GlobusCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_globus(self, args, arguments):
        """::

        Usage:
        globus login FROM_EP TO_EP
        globus transfer FROM_EP TO_EP DIR FROM TO [--mkdir=no] [--tar] [--force] [--dryrun]
        globus transfer FROM_EP TO_EP DIR --file=FILE TO [--mkdir=no] [--run=1:100] [--tar] [--force] [--dryrun]

        Arguments:
        FROM_EP   the globus endpoint to transfer the file from
        TO_EP     the globus endpoint to transfer the file to
        DIR       the base directory from which to transfer. All transfers
        are done relative to this DIR and the new remote directory
        will not have the prefix DIR.
        FROM      a relative directory to transfer files from
        TO        the directory to transfer the relative directory FROM
        FILE      a file that contains files or directories to transfer

        Options:
        --file=FILE  specify the file that contains the transfers
        --tar        transfer the data in a tar file
        --mkdir=no   assume the remote directory to place the file in is
                     already created This can speed up the transfer in
                     case you have many transfers to execute.  So create
                     the file tree first. It also helps in case a transfer
                     failed and you need to redo it, but the directories
                     are already created.
        --force      in case force is not specified and the tar file already 
            exists on the remote, the transfer will be not conducted.
            With force the transfer will be done.
        --run=1:10   Only execute the transfers in the lines 1 to 10 
                    

        Description:

        globus transfer FROM_EP TO_EP DIR FROM TO [--mkdir=no] [--tar]

        This command is a convenience wrapper for the globus command
        allowing the transfer of relative directories towards a source
        directory. The program creates on the destination the same
        directory tree as on the source starting from the base directory
        specified with DIR. The FROM directory locates at DIR/FROM is
        then copied to TO without the prefix DIR.

        If you specify the --mkdir=no the destination directory is assumed to
        exist and is not explicitly created. If it does not exist the program
        will be terminated.

        bookmarks
        bookmarks can be stored in a file called
        ~/.cloudmesh/globus.yaml

        let us assume the file contains

        bookmark:
        uva: c4d80096-7612-11e7-8b5e-22000b9923ef
        laptoa: 1a1a1a1--7612-11e7-8b5e-22000b9923ef

        then you can use the keyword uva for an endpoint in the command

        Examples:

        Transfer via multiple globus tasks

        cd mydir
        ls -1 > file.txt
        cat -n file.txt

        cms globus transfer mars uva `pwd` --file=files.txt /remotedir --mkdir=no --run=13:18 --tar

        This command will from the file transfer the files in the lines 13 to 18 contained in files.txt.
        Each line will be handled as a separate transfer and the data will be placed in a tar file. that
        tar file will then be transferred. On the remote machine the tar file will not be untarred. This
        you do have to do by loggin into the machine such as with ssh abd untar the file. T

        """
        #TAR = "gtar"

        TAR = "tar"
        dryrun = arguments["--dryrun"] or False

        # arguments.FILE = arguments['--file'] or None

        map_parameters(arguments, "file")

        # VERBOSE(arguments)

        from cloudmesh.globus.globus import Globus


        if arguments.login or arguments.transfer:

            from_ep = arguments.FROM_EP
            to_ep = arguments.TO_EP

            globus = Globus(source_endpoint=from_ep,
            destination_endpoint=to_ep)
            globus.login(from_ep, to_ep)
            tar = arguments["--tar"] or False

        def transfer(from_ep, to_ep, label=None, tar=False):
            "globus transfer FROM_EP TO_EP DIR FROM TO"
            base_directory = arguments.DIR
            from_dir = arguments.FROM
            to_dir = arguments.TO

            # SETUP LABEL
            source = f"{from_ep}:{base_directory}/{from_dir}"
            destination = f"{to_ep}:{to_dir}/{from_dir}"

            char = "-"
            if label is None:

                label = f"{source}---{destination}"

            label = label\
            .replace("/", char) \
            .replace(":", char) \
            .replace(" ", char) \
            .replace("_", char) \
            .replace(".", char)


            # SETUP ENDPOINTS
            from_ep = globus.bookmark(from_ep)
            to_ep = globus.bookmark(to_ep)

            source = f"{from_ep}:{base_directory}/{from_dir}"
            destination = f"{to_ep}:~{to_dir}/{from_dir}"

            if arguments["--mkdir"] not in ["no", "NO", "0"]:
                r = globus.mkdir(to_ep, f"/~{to_dir}")
                if r == 1:
                    return ""

            recurseive="--recurseive"

            if tar:
                name= f"{from_dir}"
                tar_file = f"{name}.tgz"
                # BUG --exclude seems not to work
                command = f"cd {base_directory}; {TAR} -cvz --exclude='.DS_Store' -f {tar_file} {name}"

            if not os.path.exists("{base_directory}/{tar_file}") or arguments["--force"]:
                print(command)
                if not dryrun:
                    os.system(command)
                source = f"{from_ep}:{base_directory}/{tar_file}"
                destination = f"{to_ep}:~{to_dir}/{tar_file}"
                recursive = ""
            if not dryrun:
                globus.transfer(source, destination, label=label, recursive=recursive)

        if arguments.transfer and arguments["--file"]:
            "globus transfer FROM_EP TO_EP DIR --file=FROM TO [--mkdir=no]"
            filename = arguments["--file"]
            files = readfile(filename).strip().splitlines()

            if arguments["--run"] is not None:
                if ":" in arguments["--run"]:
                    i_start, i_end = arguments["--run"].split(":")
                    i_start = int(i_start) - 1
                    i_end = int(i_end) 
                else:
                    i_start = i_end = arguments["--run"]
                    i_start = int(i_start) - 1
                    i_end = min(int(i_end), len(files))
            else:
                i_start = 0
                i_end = len(files)

            if i_end - i_start > 100:
                Console.error("Only 100 pending jobs can be submitted. change the --run option\n"
                f"file contains {i_end} jobs")
                return ""


            for i in range(i_start, i_end):
                file = files[i]
                if file.startswith("#") or file is None:
                    pass
                else:
                    arguments.FROM = file
                    no = i + 1
                    transfer(from_ep, to_ep, label=f"{no}-{file}", tar=tar)

        elif arguments.transfer:
            "globus transfer FROM_EP TO_EP DIR FROM TO"

            transfer(from_ep, to_ep, tar=tar)


        return ""
