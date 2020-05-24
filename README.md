# FileSync
A directory/file syncing program with multi-core support.

## Features
- Sync directories/files to other directories
- Sync to multiple directories (mirrors source files to multiple directories)
- Optional multi-core support
- Support for md5, sha1, sha224, sha256, sha384, sha512

## Usage
- As a module:
```
python FileSync/
```
- As a script:
```
python FileSync/__init__.py
```

## Optional Parameters
```
--h/--help: Displays all the available commands to the user.
--debug: Enables debug print messages.
--benchmark: Enables benchmarking file/directory processes.
--multi: Enables multi-core processing (not recommended for small directories).
--scan-interval: Sets the time interval between directory scans (recommended - 2-5s)
--hash: Sets the hashing algorithm to use for checksums (recommended - sha256).
        Supported hashing algorithms: [md5, sha1, sha224, sha256, sha384, sha512]
```

## TODO
- Add SFTP support to allow file syncing across a networked computer.
