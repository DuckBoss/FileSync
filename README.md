# FileSync
A directory/file syncing program with multi-core support.

## Features
- Sync directories/files to other directories
- Live scans to detect changes in files to automatically re-sync
- Sync to multiple directories (mirrors source files to multiple directories)
- Optional batched multi-core support
- Optionally ignore specific directories/files during synchronization
- Support for md5, sha1, sha224, sha256, sha384, sha512 checksums

## Usage
- *Please make sure to modify the settings.ini file in the program's root directory to adjust it to your specifications.*
- As a module:
```
python FileSync/
```
- As a script:
```
python FileSync/__main__.py
```

## Optional Parameters
```
--h/--help: Displays all the available commands to the user.
--debug: Enables debug print messages.
--quiet: Suppresses all standard output messages. This is preferable for a headless environment.
--benchmark: Enables benchmarking file/directory processes.
--no-live-scan: Disables live scanning for changes in the directories which makes the program only sync once.
--multi: Enables multi-core processing (not recommended for small directories).
--batch-size <int>: Sets the batch size for multi-core processing, if enabled (recommended - 100+ for large quantities of data)
--scan-interval <int>: Sets the time interval in seconds between directory scans (recommended - 2-5s)
--hash <algorithm>: Sets the hashing algorithm to use for checksums (recommended - sha256).
        Supported hashing algorithms: [md5, sha1, sha224, sha256, sha384, sha512]
```

## Requirements
- Python 3.7+

## TODO
- Add SFTP support to allow file syncing across a networked computer (or multiple computers in the network).
