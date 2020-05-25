import argparse
import configparser
import os
from sys import exit
from pathlib import Path
from resources.strings import *
from main import FileChecker


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synchronizes files from one directory to another by checking individual file checksums."
    )
    parser.add_argument('--debug', dest='debug_feature', action='store_true', default=False, help='Enables debug print messages')
    parser.add_argument('--benchmark', dest='bench_feature', action='store_true', default=False, help='Enables benchmarking file/directory processes')
    parser.add_argument('--multi', dest='multi_feature', action='store_true', default=False, help='Enables multi-core processing (not recommended for small directories)')
    parser.add_argument('--scan-interval', dest='scan_interval', default=5, help='Sets the time interval in seconds between directory scans (recommended - 2-5s)')
    parser.add_argument('--hash', dest='hash_algorithm', default='sha256',
                        help='Sets the hashing algorithm to use for checksums (recommended - sha256)\n'
                             'Supported hashing algorithms: [crc32, adler32, md5, sha1, sha224, sha256, sha384, sha512]')
    parser.add_argument('--batch-size', dest='batch_size', default=-1, help='Sets the batch size for multi-core processing, if enabled (recommended - 100+ for large quantities of data)')
    parser.add_argument('--no-live-scan', dest='live_scan', action='store_true', default=False, help='Disables live scanning for changes in the directories which makes the program only sync once')
    parser.add_argument('--quiet', dest='quiet_feature', action='store_true', default=False, help='Suppresses all standard output messages. This is preferable for a headless environment')

    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if config is None or not os.path.isfile(Path(os.getcwd(), 'settings.ini')):
        print("Encountered an error with the settings.ini file. Please make sure the file exists in the root directory of the program.")
        exit(-1)
    if not os.path.isdir(config[C_MAIN_SETTINGS][P_SRC_DIR]):
        print(f"Encountered a directory error in the settings.ini file. Please make sure the {P_SRC_DIR} is a valid directory.")
        exit(-1)
    target_paths = ([x.strip() for x in config[C_MAIN_SETTINGS][P_DEST_DIR].split(',')])
    for target in target_paths:
        if not os.path.isdir(target):
            print(f"Encountered a directory error in the settings.ini file. Please make sure the {P_DEST_DIR} is a valid directory.")
            exit(-1)
    checker = FileChecker(config=config, debug=args.debug_feature, quiet=args.quiet_feature, no_live_scan=args.live_scan, batch_size=args.batch_size, hash_algo=args.hash_algorithm, benchmark=args.bench_feature, multi=args.multi_feature, scan_interval=int(args.scan_interval))
