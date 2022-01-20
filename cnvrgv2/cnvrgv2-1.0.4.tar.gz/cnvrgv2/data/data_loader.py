import os
import time
import threading
from queue import Queue, Empty, Full

from cnvrgv2.errors import CnvrgRetryError, CnvrgArgumentsError
from cnvrgv2.data.clients.storage_client_factory import storage_client_factory


class DataLoader:
    def __init__(self, dataset, batch_size=1, num_workers=40, prefetch=3000, chunk_size=1000, force=False):
        """
        Python iterable over cnvrg datasets.
        Provides a file iterator that downloads files from dataset in real-time in order to parallelize data processing
        and dataset cloning. the data loader allows allows to batch files together and define number of files to
        prefetch
        @param dataset: Cnvrg dataset object
        @param batch_size: Iterator batch size - for values over 1 a list will be returned
        @param num_workers: Number of threads to download
        @param prefetch: Prefetch factor for files
        @param chunk_size: File meta chunk size to fetch from the server
        @param force: Force rewrite existing files
        """
        # Init the storage client
        self.dataset = dataset
        self.storage_meta = dataset.storage_meta
        self.storage_client = storage_client_factory(storage_meta=self.storage_meta)

        # Handle batch input
        if not isinstance(batch_size, int) or batch_size < 1:
            raise CnvrgArgumentsError("Batch sise must be an integer greater than 0")
        self.batch_size = batch_size

        # Init file stats
        self.total_files = dataset.num_files
        self.files_processed = 0

        # Init file queues
        if not isinstance(prefetch, int) or prefetch < 1:
            raise CnvrgArgumentsError("Prefetch factor must be an integer greater than 0")
        if not isinstance(chunk_size, int) or chunk_size < 1:
            raise CnvrgArgumentsError("Chunk size must be an integer greater than 0")
        if not isinstance(num_workers, int) or num_workers < 1:
            raise CnvrgArgumentsError("Number of workers must be an integer greater than 0")

        self.force = force
        self.prefetch = prefetch
        self.chunk_size = chunk_size
        self.file_queue = Queue(self.prefetch)
        self.download_queue = Queue(self.prefetch)

        # Create a thread event in order to exit download when needed
        self.download_active = threading.Event()
        self.download_active.set()

        # Create a thread-safe lock
        self.download_lock = threading.Lock()

        # Create collector thread which fetches file chunks from the server
        self.file_index = 1
        self.collector_thread = threading.Thread(target=self.file_collector)
        self.collector_thread.start()

        # Create downloader threads to parallelize s3 file download
        self.downloader_threads = []
        for i in range(num_workers):
            t = threading.Thread(target=self.file_downloader)
            t.start()
            self.downloader_threads.append(t)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Returns a single file meta object if batch_size is 1, otherwise returns a list of file meta objects
        @return: dict/list
        """
        file_batch = []

        # Attempt to batch files together
        while (len(file_batch) < self.batch_size) and (self.files_processed < self.total_files):
            file = self.file_queue.get()

            with self.download_lock:
                self.files_processed += 1

            self.file_queue.task_done()
            file_batch.append(file)

        if len(file_batch) > 0 and self.batch_size > 1:
            # We return list if the batch size is greater than 1
            return file_batch
        elif len(file_batch) > 0 and self.batch_size == 1:
            # We return a single object if the batch size is equal to 1
            return file_batch[0]
        else:
            # If the file batch is empty it means we processed all of the files and should clear download
            self.clear()
            raise StopIteration

    def __enter__(self):
        """
        Support context manager
        @return: self
        """
        return self

    def __exit__(self, *exc):
        """
        Ensure data loader threads will be cleaned in case of an error
        @param exc: The error that triggered exit
        @return:
        """
        # TODO: handle exception?
        self.clear()

    def clear(self):
        """
        Clear the threads used to download files
        @return: none
        """
        # Clear download threads
        self.download_active.clear()
        self.collector_thread.join()

        for t in self.downloader_threads:
            t.join()

    def file_collector(self):
        """
        The function that handles collecting files-to-download metadata from the server
        @return: None
        """
        while self.file_index < self.total_files and self.download_active.is_set():
            end_index = self.file_index + self.chunk_size

            # Attempt to retrieve file chunk from the server
            try:
                files_to_download = self.dataset.get_files_by_range(
                    start=self.file_index,
                    end=end_index
                )
            except Exception:
                files_to_download = []
                print("Could not download files {}-{}".format(self.file_index, end_index))
                # TODO: change exception handling? add retry?

                # If we could not get the chunk we still count it as processed
                with self.download_lock:
                    self.files_processed += self.chunk_size
            finally:
                self.file_index = end_index

            # Attempt to put the new files in the download queue, non-blocking in case we want to break iterator loop
            for file in files_to_download:
                while self.download_active.is_set():
                    try:
                        self.download_queue.put_nowait(file)
                        break
                    except Full:
                        time.sleep(0.5)

    def file_downloader(self):
        """
        Handles downloading files from the remote object storage.
        @return: None
        """
        # Run as long as we have files to download
        while self.download_active.is_set():
            try:
                # Get file non-blocking way, otherwise thread will hang forever
                file = self.download_queue.get_nowait()
                local_path = "{}/{}".format(self.dataset.working_dir, file["fullpath"])
                if self.force or not os.path.exists(local_path):
                    self.storage_client.download_single_file(local_path, file["object_path"])
                file["local_path"] = local_path
                self.download_queue.task_done()

                self.file_queue.put(file)
            except Empty:
                time.sleep(0.5)
            except CnvrgRetryError:
                # If we could not download the file we still count it as processed
                with self.download_lock:
                    self.files_processed += 1
            except Exception as e:
                # Should not be possible to enter here, safeguard against deadlock
                print("An unhandled exception in downloader thread has occurred:")
                print(e)
                with self.download_lock:
                    self.files_processed += 1
