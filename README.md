# FileSync
A directory/file syncing program with multi-core support


## Usage
```
python FileSync/
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
