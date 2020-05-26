# FileSync
A directory/file syncing program with multi-core support.

![GitHub release (latest by date)](https://img.shields.io/github/v/release/DuckBoss/FileSync)

## Features
- Sync directories/files to other local directories or networked directories with SFTP
- Live scans to detect changes in source files to automatically re-sync destination files
- Sync to multiple local or networked directories (mirrors source files to multiple directories)
- Optional batched multi-core support
- Optionally ignore specific directories/files during synchronization
- Support for crc32, adler32, md5, sha1, sha224, sha256, sha384, sha512 checksums

## Usage
---
### Step 1) Setup the settings.ini file
You can either manually create the settings.ini file based on the provided one, or generate one using the setup utility.<br>
1. **Running the setup utility for settings.ini:**<br>
Run the python module with the following launch parameter:  
`--setup`
2. **Manually setup settings.ini:**<br>
Open the settings.ini file provided in the repository and modify the data as needed.
---
### Step 2) After setting up the settings.ini file, run the program:
- As a module: 
`python FileSync/`
---

## Optional Parameters
```
--h/--help: Displays all the available commands to the user.
--setup: Initializes setup mode which provides an interactive settings.ini creation utility
--debug: Enables debug print messages.
--quiet: Suppresses all standard output messages. This is preferable for a headless environment.
--benchmark: Enables benchmarking file/directory processes.
--no-live-scan: Disables live scanning for changes in the directories which makes the program only sync once.
--multi: Enables multi-core processing (not recommended for small directories).
--batch-size <int>: Sets the batch size for multi-core processing, if enabled (recommended - 100+ for large quantities of data)
--scan-interval <int>: Sets the time interval in seconds between directory scans (recommended - 2-5s)
--hash <algorithm>: Sets the hashing algorithm to use for checksums (recommended - sha256).
        Supported hashing algorithms: [adler32, crc32, md5, sha1, sha224, sha256, sha384, sha512]
--use-sftp: Enables SFTP server connectivity (use with --username/--password command)
--username: Sets the username for sftp server communication
--password: Sets the password for sftp server communication
```

## Requirements
- Python 3.7+
- paramiko (only if SFTP is used)

### Installing Dependencies
```
pip install -r requirements.txt
```
