import sys
import time
import threading

from queue import Queue, Empty, Full
from cnvrgv2.cli.utils.progress_bar_utils import init_progress_bar_for_cli
from cnvrgv2.errors import CnvrgRetryError
from cnvrgv2.data.clients.storage_client_factory import storage_client_factory


class RemoteFilesHandler:
    def __init__(
            self,
            data_owner,
            num_workers=40,
            chunk_size=1000,
            force=False,
            queue_size=5000,
            base_commit_sha1=None,
            commit_sha1=None,
            progress_bar_enabled=False):
        """
        Multithreaded remote file handler base class
        @param data_owner: Cnvrg dataset / project object
        @param num_workers: Number of threads to handle files
        @param chunk_size: File meta chunk size to fetch from the server
        @param force: Force rewrite existing files
        @param queue_size: Max number of file meta to put in queue
        """
        # Init data
        self.base_commit_sha1 = base_commit_sha1
        self.commit_sha1 = commit_sha1
        self.progress_bar_enabled = progress_bar_enabled
        self.progress_bar = None

        # Init the storage client
        self.data_owner = data_owner
        self.storage_meta = data_owner.storage_meta
        self.storage_client = storage_client_factory(storage_meta=self.storage_meta)

        self.force = force
        self.chunk_size = chunk_size
        self.queue_size = queue_size
        self.progress_queue = Queue(self.queue_size)  # Files deleted / downloaded
        self.handle_queue = Queue(self.queue_size)  # Files need to be deleted / downloaded

        # Create a thread event in order to exit download when needed
        self.task_active = threading.Event()
        self.task_active.set()

        # Create a thread-safe lock
        self.progress_lock = threading.Lock()

        # Create progress thread which tracks the upload progress
        self.total_files = sys.maxsize
        self.handled_files = 0
        self.progress_thread = threading.Thread(target=self.task_progress)
        self.progress_thread.start()

        # Create collector thread which fetches file chunks from the server
        self.file_index = 0
        self.collector_thread = threading.Thread(target=self.file_collector)
        self.collector_thread.start()

        # Create downloader threads to parallelize s3 file download
        self.handle_threads = []
        for i in range(num_workers):
            t = threading.Thread(target=self.file_handler)
            t.start()
            self.handle_threads.append(t)

    @property
    def in_progress(self):
        """
        Property used to check if the upload is still in progress
        @return: Boolean
        """
        return self.task_active.is_set()

    def task_progress(self):
        """
        Handles the upload progress and confirming file uploads to the server
        @return: None
        """

        while self.handled_files < self.total_files and self.task_active.is_set():

            try:
                self.progress_queue.get_nowait()

                with self.progress_lock:
                    self.handled_files += 1

            except Empty:
                time.sleep(0.5)

        self.clear()

    def clear(self):
        """
        Clear the threads used to download files
        @return: none
        """
        # Clear download threads
        self.task_active.clear()
        self.collector_thread.join()
        for t in self.handle_threads:
            t.join()

        if self.progress_bar_enabled:
            self.progress_bar.finish()

    def file_collector(self):
        """
        The function that handles collecting files metadata from the server
        @return: None
        """
        next_page = 0
        while (
            self.total_files > 0 and
            isinstance(self.file_index, int) and
            self.file_index < self.total_files and
            self.task_active.is_set()
        ):
            # Attempt to retrieve file chunk from the server
            try:
                resp = self._collector_function(page_after=next_page)
                files_to_process = resp["file_dict"]

                # Initialize total_files and progress bar only once
                if self.total_files == sys.maxsize:
                    self.total_files = resp["total_files"]

                if self.progress_bar_enabled and not self.progress_bar:
                    total_files_size = float(resp["total_files_size"])
                    self.progress_bar = init_progress_bar_for_cli("Downloading", total_files_size)

                self.file_index = self.file_index + len(files_to_process)

                # We want to prevent unnecessary loops
                if not resp["next"] or resp["next"] == next_page:
                    return
                else:
                    next_page = resp["next"]

            except Exception as e:
                if self.progress_bar_enabled:
                    print("Could not process files {}".format(self.file_index))
                    print(e)
                self.task_active.clear()
                return

            # Attempt to put the new files in the download queue, non-blocking in case we want to break iterator loop
            for file in files_to_process:
                while self.task_active.is_set():
                    try:
                        self.handle_queue.put_nowait(file)
                        break
                    except Full:
                        time.sleep(0.5)

    def file_handler(self):
        """
        Function to handle single file
        @return: None
        """
        # Run as long as we have files to download
        while self.task_active.is_set():
            try:
                # Get file non-blocking way, otherwise thread will hang forever
                file = self.handle_queue.get_nowait()
                local_path = "{}/{}".format(self.data_owner.working_dir, file["fullpath"])
                file["local_path"] = local_path

                self._handle_file_function(
                    local_path,
                    object_path=file["object_path"],
                    fullpath=file["fullpath"],
                    type=file.get("type", "files"),
                    progress_bar=self.progress_bar
                )

            except Empty:
                time.sleep(0.5)
            except CnvrgRetryError:
                # If we could not download the file we still count it as processed
                with self.progress_lock:
                    self.handled_files += 1
            except Exception as e:
                # Should not be possible to enter here, safeguard against deadlock
                print("An unhandled exception in downloader thread has occurred:")
                print(e)
                with self.progress_lock:
                    self.handled_files += 1

    def _collector_function(self, page_after=None):
        """
        Base function to collect files metadata from server
        @param page_after: The id of the next file that the iteration of the pagination should start from
        @return: Should return array of files metadata
        """
        pass

    def _handle_file_function(self, local_path, progress_bar=None, **kwargs):
        """
        Base function to handle single file
        @param local_path: File location locally
        @param kwargs: Needs to be fullpath / object_path depends on the class using this base
        @return: None
        """
        pass
