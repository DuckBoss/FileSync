import shutil
import errno
import multiprocessing
from hashlib import sha512, sha224, sha256, sha384, sha1, md5
from zlib import crc32, adler32
from os import makedirs, walk
from pathlib import Path
from time import sleep, time
from resources.strings import *


# Resolves hash algorithm provided by the end-user.
class HashResolver:
    def __init__(self, debug=False):
        self.debug = debug

    # Resolves the hash algorithm given by the end-user and returns the hash object.
    @staticmethod
    def hash_classify(given_hash: str):
        if given_hash.lower() == H_SHA_256:
            return sha256()
        if given_hash.lower() == H_SHA_224:
            return sha224()
        if given_hash.lower() == H_SHA_384:
            return sha384()
        if given_hash.lower() == H_SHA_512:
            return sha512()
        elif given_hash.lower() == H_MD5:
            return md5()
        elif given_hash.lower() == H_SHA_1:
            return sha1()
        else:
            return None


# Handles file copying and directory creation.
class FileBackup:
    def __init__(self, debug=False):
        self.debug = debug

    # Copies files from a source file path to a destination file path, maintaining sub-folder hierarchy.
    def copy_file(self, file_src, target_src, full_target_src):
        # Makes required sub-directories as required by the source path.
        try:
            makedirs(target_src)
        except FileExistsError:
            if self.debug:
                print(f"Directory already exists: {target_src}")
        # Copies the files with respect to the folder hierarchy.
        try:
            shutil.copytree(file_src, full_target_src)
        except OSError as e:
            # If the item being copied is not a directory, copy as a file.
            if e.errno == errno.ENOTDIR:
                shutil.copy(file_src, full_target_src)
            # Reports file read/write permission errors.
            elif e.errno == errno.EPERM:
                print(f"Encountered a file permission error while copying files/directories:\n{e}")
            else:
                print(f"Encountered an error while copying files/directories:\n{e}")


# Scans the source directory for changes (by checksum) and syncs files to destination directories.
class FileChecker:
    def __init__(self, config, multi, no_live_scan, batch_size, hash_algo, benchmark, scan_interval, debug=False, quiet=False):
        self.config = config
        self.debug = debug
        self.no_live_scan = no_live_scan
        self.quiet = quiet
        if batch_size == -1:
            self.batch_size = self.config[C_MAIN_SETTINGS][P_BATCH_SIZE]
        else:
            self.batch_size = batch_size
        self.multi = multi
        self.hash = hash_algo
        # Reports an error if an unsupported hash algorithm is used by the end-user.
        if self.hash != H_CRC_32 and self.hash != H_ADLER_32:
            if HashResolver.hash_classify(self.hash) is None:
                print(f"Encountered an error while resolving the hash algorithm type: {self.hash}\nPlease use a supported hash.")
                return
        self.benchmark = benchmark
        self.scan_interval = scan_interval
        self.hasher = None
        self.hash_resolver = HashResolver(debug=self.debug)
        self.copier = FileBackup(debug=self.debug)
        self.hash_dict = {}

        self.live_scan()

    def live_scan(self):
        if not self.quiet:
            print("Scanning initialized...")
        if self.multi:
            print("Initializing as a multi-core process...")
        while True:
            start_time = time()
            if not self.quiet:
                print("Starting directory scan...")
            if self.multi:
                if self.scan_directory_multi():
                    if self.debug:
                        print(f"File hash dictionary:\n{self.hash_dict}")
                else:
                    if self.debug:
                        print('...')
            else:
                if self.scan_directory_single():
                    if self.debug:
                        print(f"File hash dictionary:\n{self.hash_dict}")
                else:
                    if self.debug:
                        print('...')
            end_time = time() - start_time
            if self.benchmark:
                print(f"Directory Scan Benchmark: {end_time:.2f}s")
                print("...")
            if not self.quiet:
                print("Synchronization Complete.")
            if self.no_live_scan:
                return
            sleep(self.scan_interval)

    def check_file_multi(self, file, file_hashes, debug) -> bool:
        self.hasher = HashResolver.hash_classify(self.hash)
        use_crc32 = False
        use_adler32 = False
        if self.hash == H_CRC_32:
            use_crc32 = True
        if self.hash == H_ADLER_32:
            use_adler32 = True
        with open(file, 'rb') as cur_file:
            buffer = cur_file.read(int(self.config[C_MAIN_SETTINGS][P_FILE_BUFFER]))
            try:
                if self.hasher is not None:
                    if not use_crc32 and not use_adler32:
                        self.hasher.update(buffer)
                else:
                    if use_crc32:
                        self.hasher = crc32(buffer, 0)
                    elif use_adler32:
                        self.hasher = adler32(buffer, 0)
                    else:
                        return False
            except RuntimeError as e:
                print(f"Encountered error while hashing:\n{e}")
                return False

            while len(buffer) > 0:
                buffer = cur_file.read(int(self.config[C_MAIN_SETTINGS][P_FILE_BUFFER]))
                try:
                    if self.hasher is not None:
                        if not use_crc32 and not use_adler32:
                            self.hasher.update(buffer)
                    else:
                        if use_crc32:
                            self.hasher = crc32(buffer, self.hasher)
                        elif use_adler32:
                            self.hasher = adler32(buffer, 0)
                        else:
                            return False
                except RuntimeError as e:
                    print(f"Encountered error while hashing:\n{e}")
                    return False

        if not use_crc32 and not use_adler32:
            cur_hash = self.hasher.hexdigest()
        else:
            cur_hash = format(self.hasher & 0xFFFFFFF, '08x')
        try:
            if file_hashes[file.as_posix()] != cur_hash:
                file_hashes[file.as_posix()] = cur_hash
                if debug:
                    print(f"Changes detected - {file}")
                return True
        except KeyError:
            if debug:
                print(f"Key does not exist, creating now: [{file.as_posix()}]")
            file_hashes[file.as_posix()] = cur_hash
            return True
        del self.hasher
        return False

    def check_file_single(self, file) -> bool:
        self.hasher = HashResolver.hash_classify(self.hash)
        use_crc32 = False
        use_adler32 = False
        if self.hash == H_CRC_32:
            use_crc32 = True
        if self.hash == H_ADLER_32:
            use_adler32 = True
        with open(file, 'rb') as cur_file:
            buffer = cur_file.read(int(self.config[C_MAIN_SETTINGS][P_FILE_BUFFER]))
            try:
                if self.hasher is not None:
                    if not use_crc32 and not use_adler32:
                        self.hasher.update(buffer)
                else:
                    if use_crc32:
                        self.hasher = crc32(buffer, 0)
                    elif use_adler32:
                        self.hasher = adler32(buffer, 0)
                    else:
                        return False
            except RuntimeError as e:
                print(f"Encountered error while hashing:\n{e}")
                return False

            while len(buffer) > 0:
                buffer = cur_file.read(int(self.config[C_MAIN_SETTINGS][P_FILE_BUFFER]))
                try:
                    if self.hasher is not None:
                        if not use_crc32 and not use_adler32:
                            self.hasher.update(buffer)
                    else:
                        if use_crc32:
                            self.hasher = crc32(buffer, self.hasher)
                        elif use_adler32:
                            self.hasher = adler32(buffer, self.hasher)
                        else:
                            return False
                except RuntimeError as e:
                    print(f"Encountered error while hashing:\n{e}")
                    return False

        if not use_crc32 and not use_adler32:
            cur_hash = self.hasher.hexdigest()
        else:
            cur_hash = format(self.hasher & 0xFFFFFFF, '08x')
        try:
            if self.hash_dict[file.as_posix()] != cur_hash:
                self.hash_dict[file.as_posix()] = cur_hash
                if self.debug:
                    print(f"Changes detected - {file}")
                return True
        except KeyError:
            if self.debug:
                print(f"Key does not exist, creating now: [{file.as_posix()}]")
            self.hash_dict[file.as_posix()] = cur_hash
            return True
        del self.hasher
        return False

    def file_worker(self, dir_path, batch, ignore_file_list, proc_num, return_dict, file_hashes, debug):
        change_detected = False
        for i, file in enumerate(batch):
            if file in ignore_file_list:
                if self.debug:
                    print(f"Ignoring file: {file}")
                continue
            if self.check_file_multi(Path(dir_path, file), file_hashes, debug):
                change_detected = True
                parent_dir = dir_path.rsplit('/', 1)
                if len(parent_dir) == 0:
                    parent_dir = dir_path.rsplit('\\', 1)
                parent_dir = parent_dir[1]
                target_paths = ([x.strip() for x in self.config[C_MAIN_SETTINGS][P_DEST_DIR].split(',')])
                for target in target_paths:
                    target_path = Path(target, parent_dir)
                    full_target = Path(target, Path(parent_dir, file))
                    self.copier.copy_file(Path(dir_path, file), target_path, full_target)
        return_dict[proc_num] = change_detected

    def scan_directory_multi(self) -> bool:
        change_detected = False
        jobs = []
        batch_groups = []
        batch = []
        batch_counter = 0
        job_manager = multiprocessing.Manager()
        return_dict = job_manager.dict()
        file_hashes = job_manager.dict()
        ignore_dir_list = ([x.strip() for x in self.config[C_MAIN_SETTINGS][P_DIR_IGNORE].split(',')])
        ignore_file_list = ([x.strip() for x in self.config[C_MAIN_SETTINGS][P_FILE_IGNORE].split(',')])
        src_dir = self.config[C_MAIN_SETTINGS][P_SRC_DIR]
        for file_hash in self.hash_dict.keys():
            file_hashes[file_hash] = self.hash_dict[file_hash]
        for (dir_path, dir_names, file_names) in walk(src_dir):
            if dir_path.split('\\')[-1] in ignore_dir_list:
                if self.debug:
                    print(f"Ignoring directory: {dir_path}")
                continue
            elif dir_path.split('/')[-1] in ignore_dir_list:
                if self.debug:
                    print(f"Ignoring directory: {dir_path}")
                continue

            for i, file in enumerate(file_names):
                if i % int(self.batch_size) == 0 and i != 0:
                    print(f"Batch {batch_counter} created.")
                    batch_groups.append(batch)
                    batch = []
                    batch_counter += 1
                else:
                    batch.append(file)
            if len(batch_groups) == 0:
                batch_groups.append(batch)

            if self.debug:
                print(batch_groups)
            start_time = time()
            for batch_item in batch_groups:
                process = multiprocessing.Process(
                    target=self.file_worker,
                    args=(dir_path, batch_item, ignore_file_list, len(jobs) + 1, return_dict, file_hashes, self.debug)
                )
                jobs.append(process)
                process.start()
            end_time = time() - start_time
            print(f"Batch processes complete.")
            if self.benchmark:
                print(f"Batch Scan Benchmark: {end_time:.2f}s")
        for job in jobs:
            job.join()
        del jobs, job_manager
        self.hash_dict = file_hashes

        if True in return_dict.values():
            change_detected = True
        return change_detected

    def scan_directory_single(self) -> bool:
        change_detected = False
        ignore_dir_list = ([x.strip() for x in self.config[C_MAIN_SETTINGS][P_DIR_IGNORE].split(',')])
        ignore_file_list = ([x.strip() for x in self.config[C_MAIN_SETTINGS][P_FILE_IGNORE].split(',')])
        src_dir = self.config[C_MAIN_SETTINGS][P_SRC_DIR]
        for (dir_path, dir_names, file_names) in walk(src_dir):
            if dir_path.split('\\')[-1] in ignore_dir_list:
                if self.debug:
                    print(f"Ignoring directory: {dir_path}")
                continue
            elif dir_path.split('/')[-1] in ignore_dir_list:
                if self.debug:
                    print(f"Ignoring directory: {dir_path}")
                continue
            for i, file in enumerate(file_names):
                start_time = time()
                if file in ignore_file_list:
                    if self.debug:
                        print(f"Ignoring file: {file}")
                    continue
                if self.check_file_single(Path(dir_path, file)):
                    change_detected = True
                    parent_dir = dir_path.rsplit('/', 1)
                    if len(parent_dir) == 0:
                        parent_dir = dir_path.rsplit('\\', 1)
                    parent_dir = parent_dir[1]
                    target_paths = ([x.strip() for x in self.config[C_MAIN_SETTINGS][P_DEST_DIR].split(',')])
                    for target in target_paths:
                        target_path = Path(target, parent_dir)
                        full_target = Path(target, Path(parent_dir, file))
                        self.copier.copy_file(Path(dir_path, file), target_path, full_target)
                end_time = time() - start_time
                if self.benchmark:
                    print(f"File Scan Benchmark: {end_time:.2f}s")
        return change_detected
