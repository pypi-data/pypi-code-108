import logging
from asyncio import gather
from typing import Dict, Iterable, NamedTuple, Optional
from uuid import uuid4

from . import protocol
from .misc import str_exception

logger = logging.getLogger(__name__)


class ScanResult(NamedTuple):
    definition: protocol.Directory
    child_scan_results: Optional[Dict[str, "ScanResult"]]


class BackupController:

    def __init__(self, file_system_explorer: protocol.FileSystemExplorer, backup_session: protocol.BackupSession):
        self.all_files = {}
        self.backup_session = backup_session
        self.file_system_explorer = file_system_explorer
        self.read_last_backup = True
        self.match_meta_only = True
        self.full_prescan = False

    async def backup_all(self):
        """
        Scan all directories.
        """
        backup_roots = self.backup_session.server_session.client_config.backup_directories

        # Scans are internally parallelized.  Let's not gather() this one so we have some opportunity to understand
        # what it was doing if it failed.
        if self.read_last_backup:
            last_backup = await self.backup_session.server_session.get_backup()
            if last_backup is None:
                logger.warning("No previous backup found. This scan will slow-safe not fast-unsafe")
            else:
                logger.info("Comparing meta data to last backup, will not check content for existing files.")
            for name, scan_spec in backup_roots.items():
                await self.backup_root(root_name=name, scan_spec=scan_spec, last_backup=last_backup)
        else:
            logger.info("Ignoring last backup, will hash every file")
            for name, scan_spec in backup_roots.items():
                await self.backup_root(root_name=name, scan_spec=scan_spec)

    async def backup_root(self, root_name: str, scan_spec: protocol.ClientConfiguredBackupDirectory,
                          last_backup: Optional[protocol.Backup] = None):

        logger.info(f"Backing up '{root_name}' ({scan_spec.base_path})")
        if last_backup is not None:
            last_backup_root = last_backup.roots.get(root_name) if last_backup is not None else None
            if last_backup_root is None:
                logger.warning(f"Root '{root_name}' not in last backup")
        else:
            last_backup_root = None

        explorer = self.file_system_explorer(scan_spec)
        root_hash = await self._backup_directory(explorer, last_backup_root)
        root_inode = await explorer.inode()
        root_inode.hash = root_hash
        await self.backup_session.add_root_dir(root_name, root_inode)
        logger.info(f"Done backing up '{root_name}'")

    async def _backup_directory(self, explorer: protocol.DirectoryExplorer,
                                last_backup: Optional[protocol.Inode]) -> str:
        """
        Backup a directory, returning the ref-hash
        :param explorer: A DirectoryExplorer attached to the directory to backup.
        :param last_backup: The last backup definition if available.
        """
        directory_definition = await self._scan_directory(explorer, last_backup)
        if last_backup is None or last_backup.hash != directory_definition.definition.hash():
            return await self._upload_directory(explorer, directory_definition)
        else:
            logger.debug(f"Skipping %s directory not changed", explorer.get_path(None))
            return last_backup.hash


    async def _scan_directory(self, explorer: protocol.DirectoryExplorer,
                              last_backup: Optional[protocol.Inode]) -> ScanResult:

        if self.read_last_backup and last_backup is not None:
            last_backup_children = (await self.backup_session.server_session.get_directory(last_backup)).children
        else:
            last_backup_children = {}

        children = {}
        child_directories = {} if self.full_prescan else None
        async for child_name, child_inode in explorer.iter_children():
            if child_inode.type is protocol.FileType.DIRECTORY:
                # Two major modes of operation which change the pattern of how this code recurses through directories.
                if self.full_prescan:
                    # ... Either we scan the entire tree and then try to upload that scan in a separate step
                    # To do this _scan_directory calls _scan_directory to build a tree of ScanResult objects.
                    child_scan = await self._scan_directory(
                        explorer.get_child(child_name),
                        last_backup_children.get(child_name),
                    )
                    child_inode.hash, _ = child_scan.definition.hash()
                    child_directories[child_name] = child_scan
                else:
                    # ... Or we backup one directory at a time.  Scanning and uploading as we go.
                    # To do this, _scan_directory calls _backup_directory to ensure children are fully backed up
                    # before backing up the parent... There is no need to store a tree of ScanResult objects.
                    child_inode.hash = await self._backup_directory(
                        explorer.get_child(child_name),
                        last_backup_children.get(child_name),
                    )

            else:
                if (child_inode.hash is None and self.match_meta_only and last_backup is not None
                        and child_name in last_backup_children):
                    # Try to match on meta only from the last backup
                    child_last_backup = last_backup_children[child_name]
                    child_inode.hash = child_last_backup.hash
                    # After copying the hash across, the inodes will match [only] if the meta matches.
                    if child_inode != child_last_backup:
                        # It didn't match, remove the hash because it's most likely wrong.
                        child_inode.hash = None

                if child_inode.hash is None:
                    # The explorer will correctly handle reading the content of links etc.
                    # Opening a symlink will return a reader to read the link itself, NOT the file it links to.
                    with await explorer.open_child(child_name) as file:
                        child_inode.hash = await protocol.async_hash_content(file)

            children[child_name] = child_inode

        return ScanResult(
            definition=protocol.Directory(__root__=children),
            child_scan_results=child_directories,
        )


    async def _upload_directory(self, explorer: protocol.DirectoryExplorer, directory: ScanResult) -> str:
        """
        Uploads a directory to the server.

        First it uploads the filenames and inode information including hashes for all children.  The server can then
        reject this if any or all children are missing from the server.  If that happens the server will respond
        with a list of missing children...  we then upload all missing children and try again.
        """
        logger.debug(f"Uploading directory {explorer}")
        # The directory has changed.  We send the contents over to the server. It will tell us what else it needs.
        server_response = await self.backup_session.directory_def(directory.definition)

        if not server_response.success:
            upload_tasks = []

            logger.debug(f"{len(server_response.missing_files)} missing files in {explorer}")
            for missing_file in server_response.missing_files:
                if directory.definition.children[missing_file].type is protocol.FileType.DIRECTORY:
                    if not self.full_prescan:
                        # We should only need to recurse through directories if we are in full_prescan mode
                        # Otherwise _backup_directory should already have uploaded the children.
                        raise RuntimeError(f"Somehow the server does not have a copy of directory "
                                           f"{explorer.get_path(missing_file)}.  It should have been uploaded already!")
                    await self._upload_directory(
                        explorer=explorer.get_child(missing_file),
                        directory=directory.child_scan_results[missing_file],
                    )
                else:
                    upload_tasks.append(self._upload_file(explorer, directory.definition, missing_file))

            await gather(*upload_tasks)
            # Retry the directory now that all files have been uploaded.
            # We let the server know this replaces the previous request.  Some servers may place a marker on the session
            # preventing us from completing until unsuccessful requests have been replaced.
            server_response = await self.backup_session.directory_def(directory.definition, server_response.missing_ref)
            if not server_response.success:
                raise protocol.ProtocolError(
                    "Files disappeared server-side while backup is in progress.  "
                    "This must not happen or the backup will be corrupted. "
                    f"{ {name: directory.definition.children.get(name) for name in server_response.missing_files} }",
                )

        logger.debug(f"Server accepted directory {explorer.get_path(None)} as {server_response.ref_hash}")
        return server_response.ref_hash

    async def _upload_file(self, explorer: protocol.DirectoryExplorer, directory: protocol.Directory, child_name: str):
        """
        Upload a file after the server has stated it does not already have a copy.
        """
        file_path = explorer.get_path(child_name)
        logger.info(f"Uploading {file_path}")
        try:
            with await explorer.open_child(child_name) as missing_file_content:
                resume_id = uuid4()
                new_hash = await self.backup_session.upload_file_content(
                    file_content=missing_file_content,
                    resume_id=resume_id,
                )
                if new_hash != directory.children[child_name].hash:
                    logger.warning(f"Calculated hash for {file_path} ({resume_id}) was "
                                   f"{directory.children[child_name].hash} but server thinks it's {new_hash}.  "
                                   f"Did the file content change?")
                    directory.children[child_name].hash = new_hash
                logger.debug(f"Uploaded {file_path} - {new_hash}")
        except FileNotFoundError:
            logger.error(f"File disappeared before it could be uploaded: {file_path}")
            del directory.children[child_name]
        except OSError as exc:
            logger.error(f"Cannot read file to upload: {file_path} - {str_exception(exc)}")
            del directory.children[child_name]


class RestoreController:
    restore_meta_toggles: Dict[str, bool]

    def __init__(self, server_session: protocol.ServerSession, file_system_explorer: protocol.FileSystemExplorer):
        self._server_session = server_session
        self._file_system_explorer = file_system_explorer

        # Various toggles.
        self.clobber_existing = True
        self.delete_new = False
        self.check_meta_before_overwrite = False
        self.restore_meta = True
        self.restore_meta_toggles  = {}

    async def full_restore(self, backup: protocol.Backup):
        """
        Restores an entire backup to the client's configured locations.  This will log warnings if the backup
        does not contain all roots in the configuration.  It will raise a ValueError a root has no configuration.
        :param backup:  The backup to restore.
        """

        client_config = self._server_session.client_config
        logger.info(f"Restoring backup {client_config.date_string(backup.backup_date)}: {backup.description}")
        target_configuration = client_config.backup_directories

        missing = [root for root in backup.roots.keys() if root not in target_configuration]
        if missing:
            raise ValueError(f"Cannot restore root(s).  The target path is not configured: {missing}")

        missing = [root for root in target_configuration.keys() if root not in backup.roots]
        if missing:
            logger.warning(f"Configured backup directories not in this backup {missing}")

        for root, source_dir in backup.roots.items():
            target_dir = self._file_system_explorer(target_configuration[root].base_path)
            logger.info(f"Restoring root {root} to {target_dir}")
            await self.restore_directory(source_dir, target_dir)

    async def partial_restore(self, backup_root: protocol.Inode, source_path: Optional[str], target_path: str):
        """
        Partially restores a backup.  This can restore at most one root and it must be told where to restore it to.
        The caller takes responsibility for fetching the backup root and matching it to a client configuration.
        :param backup_root: The root inode of the backup
        :param source_path: An optional child path in the root.  Child paths are always seperated with "/" irrespective
            of the current or original operating system.
        :param target_path: A target path string to be interpreted by the file system explorer.
            Confusingly enough this might use backslashes eg: a local filesystem on MS Windows.
        """

        target_dir = self._file_system_explorer(directory_root=target_path)

        if source_path is not None:
            # Backups use / for separator regardless of operating system.  Anything else would get very messy when
            # restoring backups from one OS to another.
            try:
                for source_child in source_path.split("/"):
                    source_dir = await self._server_session.get_directory(backup_root)
                    backup_root = source_dir.children[source_child]

            except KeyError as ex:
                raise FileNotFoundError(f"path '{source_path}' does not exist in") from ex

            # source_child WILL have been set.
            # split() never returns the empty set so the above for loop must have executed at least once
            await self.restore_file(backup_root, target_dir, source_child)

        else:
            # For a bunch of implementation reasons. Backup roots are always directories.
            # Not least, there would be no filename here if the backup root was a file.
            await self.restore_directory(backup_root, target_dir)

    async def restore_directory(self, source_dir: protocol.Inode, target_dir: protocol.DirectoryExplorer):
        """
        Low level restore function.  Will ensure all files in the backup for source_dir are restored to the target_dir.
        It does NOT update any meta on target_dir.
        :param source_dir: Source directory inode to read the backup from
        :param target_dir: Target directory file exporer to write the directory contents to.
        """
        assert source_dir.type is protocol.FileType.DIRECTORY

        directory = await self._server_session.get_directory(source_dir)

        if self.delete_new:
            await self._delete_new(directory, target_dir)

        for child_name, inode in directory.children.items():
            await self.restore_file(inode, target_dir, child_name)

    async def restore_file(self, inode: protocol.Inode, target_dir: protocol.DirectoryExplorer, child_name: str):
        """
        Low level restore function.  Will restore a file or directory as the child of target_dir.
        :param inode: The backup inode to restore
        :param target_dir: The target dir to restore the file or directory into.
        :param child_name: The name to give the file or directory inside target_dir.
        """
        if self.check_meta_before_overwrite:
            # TODO
            raise NotImplementedError("Checking meta has not been implemented yet")

        if inode.type is protocol.FileType.DIRECTORY:
            await target_dir.restore_child(child_name, inode.type, None, self.clobber_existing)
            await self.restore_directory(inode, target_dir.get_child(child_name))
        else:
            with await self._server_session.get_file(inode) as content:
                await target_dir.restore_child(child_name, inode.type, content, self.clobber_existing)

        if self.restore_meta:
            await target_dir.restore_meta(child_name, inode, self.restore_meta_toggles)

    async def _delete_new(self, directory: Iterable[str], target_dir: protocol.DirectoryExplorer):
        # TODO
        raise NotImplementedError(f"Deleting files has not been added to the DirectoryExplorer protocol")
