import os
import time
import threading
import mimetypes

from queue import Queue, Empty, Full
from cnvrgv2.cli.utils.progress_bar_utils import init_progress_bar_for_cli
from cnvrgv2.utils.converters import convert_bytes
from cnvrgv2.utils.storage_utils import chunk_list, get_file_sha1, total_files_size
from cnvrgv2.data.clients.storage_client_factory import storage_client_factory


class LocalFilesHandler:
    def __init__(
        self,
        data_owner,
        files,
        override=False,
        num_workers=40,
        chunk_size=1000,
        queue_size=5000,
        progress_bar_enabled=False
    ):
        """
        Multithreaded local file handler base class
        @param data_owner: Cnvrg dataset / project object
        @param files: List of files to handle
        @param override: Boolean stating whether or not we should re-upload even if the file already exists
        @param num_workers: Number of threads to use for concurrent file handling
        @param chunk_size: File meta chunk size to fetch from the server
        @param queue_size: Max number of file meta to put in queue
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        """
        # Init the storage client
        self.data_owner = data_owner
        self.storage_meta = data_owner.storage_meta
        self.storage_client = storage_client_factory(storage_meta=self.storage_meta)

        # Init helper vars
        self.override = override
        self.queue_size = queue_size
        self.chunk_size = chunk_size
        self.chunks = chunk_list(files, self.chunk_size)
        self.progress_bar_enabled = progress_bar_enabled
        self.errors = []
        self.progress_bar = None
        if progress_bar_enabled:
            self.progress_bar = init_progress_bar_for_cli("Uploading", total_files_size(files))

        # Init file queues
        self.progress_queue = Queue(self.queue_size)
        self.handle_queue = Queue(self.queue_size)

        # Create a thread event in order to exit handling when needed
        self.handling_active = threading.Event()
        self.handling_active.set()

        # Create a thread-safe lock
        self.progress_lock = threading.Lock()

        # Create collector thread which sends file chunks to the server
        self.collector_thread = threading.Thread(target=self.file_collector)
        self.collector_thread.start()

        # Create progress thread which tracks the upload progress
        self.total_files = len(files)
        self.handled_files = 0
        self.progress_thread = threading.Thread(target=self.task_progress)
        self.progress_thread.start()

        # Create downloader threads to parallelize file handling
        self.handler_threads = []
        for i in range(num_workers):
            t = threading.Thread(target=self.file_handler)
            t.start()
            self.handler_threads.append(t)

    def clear(self):
        """
        Clear the threads used to upload files
        @return: none
        """
        # Clear download threads
        self.handling_active.clear()
        self.collector_thread.join()

        try:
            for t in self.handler_threads:
                t.join()

            if self.progress_bar_enabled:
                self.progress_bar.finish()
        except Exception:
            pass

    @property
    def in_progress(self):
        """
        Property used to check if the upload is still in progress
        @return: Boolean
        """
        return self.handling_active.is_set()

    def file_collector(self):
        """
        The function that handles collecting files metadata from the server
        @return: None
        """
        for chunk in self.chunks:
            files_metadata = {}
            for fullpath in chunk:

                is_file = os.path.isfile(fullpath)
                is_directory = os.path.isdir(fullpath)

                if is_file:
                    content_type = mimetypes.guess_type(fullpath, strict=True)[0] or "plain/text"
                    files_metadata[fullpath] = {
                        "sha1": get_file_sha1(fullpath),
                        "file_name": os.path.basename(fullpath),
                        "file_size": os.path.getsize(fullpath),
                        "local_path": fullpath,
                        "content_type": content_type,
                        "relative_path": fullpath
                    }
                elif is_directory:
                    # For directories we don't need any metadata
                    files_metadata[fullpath] = None

            try:
                files_to_upload = self._file_collector_function(files_metadata)
            except Exception as e:
                self.errors.append(e)
                if self.progress_bar_enabled:
                    print("Could not process files {}".format(chunk))
                    print(e)

                self.handling_active.clear()
                return

            # Since we don't want to re-upload files the server might less files to upload than the chunks size
            # In that case we add the delta to the progress since those files already exist
            with self.progress_lock:
                self.handled_files += len(chunk) - len(files_to_upload)

                # Show progress for files already in server
                if self.progress_bar_enabled:
                    chunk_progress = 0
                    for file_name in chunk:
                        if not any(file for file in files_to_upload if file["fullpath"] == file_name):
                            file_size = files_metadata[file_name]["file_size"] if files_metadata[file_name] else 0
                            chunk_progress += file_size
                    converted_bytes, unit = convert_bytes(chunk_progress, self.progress_bar.unit)
                    self.progress_bar.next(converted_bytes)

            # Attempt to put the new files in the upload queue, non-blocking in case we want to stop the upload
            for file in files_to_upload:
                while self.handling_active.is_set():
                    try:
                        self.handle_queue.put_nowait(file)
                        break
                    except Full:
                        time.sleep(0.5)

    def file_handler(self):
        """
        Handles uploading files to the relevant object storage
        @return: None
        """
        # Run as long as we have files to upload
        file = None

        while self.handling_active.is_set():
            try:
                # Get file non-blocking way, otherwise thread will hang forever
                file = self.handle_queue.get_nowait()
                self._file_handler_function(file["local_path"], file.get("object_path"), progress_bar=self.progress_bar)
                self.handle_queue.task_done()

                self.progress_queue.put(file)
            except Empty:
                time.sleep(0.5)
            except Exception as e:
                self.errors.append(e)
                if self.progress_bar_enabled:
                    print("could not upload file {}".format(file["local_path"]))
                    print(e)
                with self.progress_lock:
                    self.handled_files += 1

    def task_progress(self):
        """
        Handles the upload progress and confirming file uploads to the server
        @return: None
        """
        uploaded_ids = []

        while self.handled_files < self.total_files and self.handling_active.is_set():
            try:
                file = self.progress_queue.get_nowait()

                with self.progress_lock:
                    self.handled_files += 1

                uploaded_ids.append(file["id"])

                if len(uploaded_ids) >= self.chunk_size or self.handled_files >= self.total_files:
                    try:
                        self._handle_file_progress_function(uploaded_ids)
                    finally:
                        uploaded_ids = []
            except Empty:
                time.sleep(0.5)

        self.clear()

    def _handle_file_progress_function(self, uploaded_ids):
        """
        Base function to progress the task
        @param uploaded_ids: Uploaded file ids
        @return: None
        """
        pass

    def _file_handler_function(self, local_path, object_path, progress_bar=None):
        """
        Base function to handle single file
        @param local_path: File location locally
        @param object_path: File location in bucket
        @return: None
        """
        pass

    def _file_collector_function(self, files_metadata):
        """
        Base function to collect files metadata from server
        @param files_metadata: Local files metadata to sent to the server for getting files to handle
        @return: Should return array of files metadata
        """
        pass
