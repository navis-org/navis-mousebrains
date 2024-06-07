#    This script is part of mousebrains (http://www.github.com/schlegelp/navis-mousebrains).
#    Copyright (C) 2024 Philipp Schlegel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import os
import requests

from tqdm.auto import tqdm

from typing import Optional

__all__ = []


def download_from_url(url, dst, resume=False):
    """Download file with progress bar.

    Parameters
    ----------
    url :       str
                URL to download from.
    dst :       str
                Destination filepath.
    resume :    bool
                If True, will attempt to resume download if file exists. If
                False, will overwrite existing files!

    Returns
    -------
    filesize
                Filesize in bytes.

    """
    try:
        file_size = int(requests.head(url, allow_redirects=True).headers["Content-Length"])
    except KeyError:
        file_size = None

    if file_size and os.path.exists(dst) and resume:
        first_byte = os.path.getsize(dst)
        mode = 'ab'
    else:
        first_byte = 0
        mode = 'wb'

    if file_size and first_byte >= file_size:
        return file_size

    header = {"Range": f"bytes={first_byte}-{file_size}"}
    with tqdm(total=file_size, initial=first_byte,
              unit='B', unit_scale=True, desc=os.path.basename(dst)) as pbar:
        req = requests.get(url, headers=header, stream=True, allow_redirects=True)
        with open(dst, mode) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)

    return file_size


def get_data_home(data_home: Optional[str] = None, create=False) -> str:
    """Return a path to the cache directory for transforms.

    If the ``data_home`` argument is not specified, it tries to read from the
    ``MOUSEBRAINS_DATA`` environment variable and defaults to ``~/mousebrains-data``.
    """
    if data_home is None:
        data_home = os.environ.get('MOUSEBRAINS_DATA',
                                   os.path.join('~', 'mousebrains-data'))

    data_home = os.path.expanduser(data_home)
    if not os.path.exists(data_home) and create:
        os.makedirs(data_home)

    return data_home
