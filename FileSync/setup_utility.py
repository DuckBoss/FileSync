from pathlib import Path
from os import getcwd


def ignore_dirs_setup():
    ignore_dirs_list = []
    ignore_dir_prompt = input('[Optional] Do you want to add directories to ignore? [Y/N]\n').lower()
    while ignore_dir_prompt != 'y' and ignore_dir_prompt != 'n':
        ignore_dir_prompt = input('[Optional] Do you want to add directories to ignore? [Y/N]\n').lower()
    if ignore_dir_prompt == 'y':
        ignore_dirs_input = ''
        while ignore_dirs_input.lower() != 'exit':
            ignore_dirs_input = input('Enter a directory to ignore, or "exit" to stop entering directories:\n')
            if len(ignore_dirs_input) == 0:
                continue
            ignore_dirs_list.append(ignore_dirs_input)
            print(f'Added ignore directory: {ignore_dirs_input}')
    else:
        print('No ignore directories have been added.')
    return ignore_dirs_list


def ignore_files_setup():
    ignore_files_list = []
    ignore_file_prompt = input('[Optional] Do you want to add files to ignore? [Y/N]\n').lower()
    while ignore_file_prompt != 'y' and ignore_file_prompt != 'n':
        ignore_file_prompt = input('[Optional] Do you want to add files to ignore? [Y/N]\n').lower()
    if ignore_file_prompt == 'y':
        ignore_dirs_input = ''
        while ignore_dirs_input.lower() != 'exit':
            ignore_dirs_input = input('Enter a file to ignore, or "exit" to stop entering files:\n')
            if len(ignore_dirs_input) == 0:
                continue
            ignore_files_list.append(ignore_dirs_input)
            print(f'Added ignore file: {ignore_dirs_input}')
    else:
        print('No ignore files have been added.')
    return ignore_files_list


def source_dir_setup():
    source_dir_prompt = input('Please enter your source directory path:\n')
    while len(source_dir_prompt) == 0:
        source_dir_prompt = input('Please enter your source directory path:\n')
    return source_dir_prompt


def destination_dirs_setup():
    destination_dirs_list = []
    destination_dirs_prompt = ''

    while destination_dirs_prompt.lower() != 'exit':
        destination_dirs_prompt = input('Please enter a destination directory path, or "exit" to stop entering directories:\n')
        if len(destination_dirs_prompt) == 0:
            continue
        if destination_dirs_prompt != 'exit':
            destination_dirs_list.append(destination_dirs_prompt)
            print(f'Added destination directory: {destination_dirs_prompt}')
    return destination_dirs_list


def batch_size_setup():
    try:
        batch_size_prompt = int(input('[Optional] Please enter a processing batch size, or "-1" to use the default: [Default - 100]\n'))
        if batch_size_prompt <= 0:
            print("Using default parameters for processing batch size: 100")
            return 100
        return batch_size_prompt
    except ValueError:
        print('The batch size can only be an integer value over 0.')
        return batch_size_setup()


def file_buffer_setup():
    try:
        buffer_size_prompt = int(input('[Optional] Please enter a file reading buffer size, or "-1" to use the default: [Default - 1024 bytes]\n'))
        if buffer_size_prompt <= 0:
            print("Using default parameters for processing batch size: 1024")
            return 1024
        return buffer_size_prompt
    except ValueError:
        print('The file reading buffer size can only be an integer value over 0.')
        return file_buffer_setup()


def use_sftp_setup():
    use_sftp_prompt = input('[Optional] Do you want to use SFTP for networked directories? [Y/N]\n').lower()
    while use_sftp_prompt != 'y' and use_sftp_prompt != 'n':
        use_sftp_prompt = input('[Optional] Do you want to use SFTP for networked directories? [Y/N]\n').lower()
    if use_sftp_prompt == 'y':
        return True
    return False


def sftp_ip_setup():
    sftp_ip_prompt = input('Please enter your server/host IP: [Default - 127.0.0.1]\n')
    while len(sftp_ip_prompt) == 0:
        sftp_ip_prompt = input('Please enter your server/host IP: [Default - 127.0.0.1]\n')
    return sftp_ip_prompt


def sftp_port_setup():
    try:
        sftp_port_prompt = int(input('Please enter your server/host Port, or "-1" for default: [Default - 22]\n'))
        if sftp_port_prompt <= 0:
            print("Using default parameters for SFTP server/host port: 22")
            return 22
        return sftp_port_prompt
    except ValueError:
        print("The port number must be a valid integer above 0.")
        return sftp_port_setup()


def setup_settings():
    print("Welcome to the FileSync Settings Setup Utility.\nThis utility will help you set up the settings.ini file.\n")
    ignore_directories = ignore_dirs_setup()
    ignore_files = ignore_files_setup()
    source_dir = source_dir_setup()
    destination_dirs = destination_dirs_setup()
    batch_proc_size = batch_size_setup()
    file_read_buffer_size = file_buffer_setup()

    use_sftp = use_sftp_setup()
    if use_sftp:
        sftp_ip = sftp_ip_setup()
        sftp_port = sftp_port_setup()
    else:
        sftp_ip = '127.0.0.1'
        sftp_port = 22
    with open(Path(getcwd(), 'settings.ini'), 'w') as settings:
        settings.write(
            "[Main_Settings]\n"
            "; Directories to ignore while copying from the source directory (can be left blank)\n"
            f"IgnoreDirectories = {','.join(ignore_directories)}\n"
            "; Files to ignore while copying from the source directory (can be left blank)\n"
            f"IgnoreFiles = {','.join(ignore_files)}\n"
            "; Source directory to copy files/folders from\n"
            f"SourceDirectory = {source_dir}\n"
            "; Destination directory to copy files/folders to\n"
            f"DestinationDirectories = {','.join(destination_dirs)}\n"
            "; Batch processing group number\n"
            f"BatchProcessingGroupSize = {batch_proc_size}\n"
            "; File reading buffer\n"
            f"FileReadBuffer = {file_read_buffer_size}\n"
            "; SFTP Server IP\n"
            f"SFTPServerIP = {sftp_ip}\n"
            "; SFTP Server Port\n"
            f"SFTPServerPort = {sftp_port}\n"
        )
        print("settings.ini file creation complete!")

