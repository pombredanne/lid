# Copyright (c) 2017, The Linux Foundation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of The Linux Foundation nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import chardet
import codecs
import datetime
import getpass
import os
import os.path
import string


def detect_file_encoding(file_name):
    """
    Detect encoding by reading entire file in binary mode.

    Note: If the files are too large, we may want to consider using
          chardet.universaldetector to process it in smaller pieces.
    """
    with open(file_name, 'rb') as f:
        contents = f.read()
        encoding = chardet.detect(contents)["encoding"]

    return encoding

def read_lines_offsets(filename):
    encoding = detect_file_encoding(filename)

    try:
        return read_with_detected_encoding(filename, encoding)
    except:
        return read_with_default_encoder(filename)


def read_with_detected_encoding(filename, encoding):
    with codecs.open(filename, 'r', encoding=encoding, errors='replace') as fp:
        lines, line_offsets = get_lines_and_line_offsets(iter(fp))
    return lines, line_offsets


def read_with_default_encoder(filename):
    with codecs.open(filename, 'r', encoding='utf-8', errors='replace') as fp:
        lines, line_offsets = get_lines_and_line_offsets(iter(fp))
    return lines, line_offsets


def get_lines_and_line_offsets(lines):
    lines_stripped = []
    line_offsets = [0]

    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line))
        lines_stripped.append(line.rstrip('\r\n'))

    return lines_stripped, line_offsets


def is_punctuation(input_value):
    return not any(c not in string.punctuation for c in input_value)


def get_user_date_time_str():
    # add username and datetime
    username = getpass.getuser()
    start_datetime = datetime.datetime.now()

    return '{user}_{year}_{month}_{day}_{hour}_{min_}'.format(
        user=username,
        year=start_datetime.year,
        month=start_datetime.month,
        day=start_datetime.day,
        hour=start_datetime.hour,
        min_=start_datetime.minute
    )


def files_from_path(path):
    if os.path.isfile(path):
        filepaths = [path]
    elif os.path.isdir(path):
        filepaths = _files_from_dir(path)
    else:  # pragma: no cover
        raise Exception("Not a file or a directory: {}".format(path))

    return filepaths


def _files_from_dir(path):
    """
    Recursive helper function for extracting a list of files within
    a directory, in a platform-independent order.
    """
    assert os.path.isdir(path), "Not a directory: {}".format(path)

    filepaths = []

    # Explicitly sort contents to get a platform-independent order
    contents = sorted(os.listdir(path))

    # First, add files in the given directory
    for filename in contents:
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            filepaths.append(filepath)

    # Next, add subdirectories recursively
    for filename in contents:
        subdir = os.path.join(path, filename)
        if os.path.isdir(subdir):
            subdir_filepaths = _files_from_dir(subdir)
            filepaths.extend(subdir_filepaths)

    return filepaths
