#    This script is part of mousebrains (http://www.github.com/schlegelp/navis-mousebrains).
#    Copyright (C) 2020 Philipp Schlegel

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
import pathlib
import warnings

from navis import transforms

import numpy as np
import pandas as pd

from .download import get_data_home

__all__ = [
    "register_transforms",
]

# Read in meta data
fp = os.path.dirname(__file__)

data_filepath = os.path.join(fp, "data")


def inject_paths():
    """Register mousebrains paths with navis."""
    # Navis scans paths in order and if the same transform is found again
    # it will be ignored. Hence order matters in some circumstances!
    # First add the data home path
    transforms.registry.register_path(get_data_home(), trigger_scan=False)

    # Next add default path
    default_path = os.path.expanduser("~/mousebrains-data")
    if default_path not in transforms.registry.transpaths:
        transforms.registry.register_path(default_path, trigger_scan=False)

    transforms.registry.scan_paths()


def ccf_coronal_sagital(points):
    """Transform CCF points from coronal to sagital orientation.

    Points are expected to be in um space.

    """
    # Swap x and z axes = rotate 90 degrees clock-wise
    points = points[:, [2, 1, 0]]
    # Flip along (new) x-axis to make it a counter-clockwise rotation
    # Note that 528 * 28 is the width of the orignal CCF in um
    points[:, 0] = points[:, 0] * -1 + (528 * 25)
    return points


def ccf_sagital_coronal(points):
    """Transform CCF points from sagital to coronal orientation.

    Points are expected to be in um space.

    """
    # Flip along (new) x-axis to make it a counter-clockwise rotation
    # Note that 528 * 28 is the width of the orignal CCF in um
    points[:, 0] = (points[:, 0] - (528 * 25)) * -1
    # Swap x and z axes = rotate 90 degrees counter-clock-wise
    points = points[:, [2, 1, 0]]
    return points


def search_register_path(path, verbose=False):
    """Search a single path for transforms and register them."""
    path = pathlib.Path(path).expanduser()

    if verbose:
        print(f"Searching {path}")

    # Skip if this isn't an actual path
    if not path.is_dir():
        return

    # Find transform files/directories
    for ext, tr in zip(
        [".h5", ".list"], [transforms.h5reg.H5transform, transforms.cmtk.CMTKtransform]
    ):
        for hit in path.rglob(f"*{ext}"):
            if hit.is_dir() or hit.is_file():
                # These files are inside the CMTK folders and show as
                # symlinks in OSX/Linux but as files (?) in Windows
                # Hence we need to manually exclude them.
                if hit.name in ("orig.list", "original.list"):
                    continue

                # Register this transform
                try:
                    if "mirror" in hit.name or "imgflip" in hit.name:
                        transform_type = "mirror"
                        source = hit.name.split("_")[0]
                        target = None
                    else:
                        transform_type = "bridging"
                        source = hit.name.split("_")[0]
                        target = hit.name.split("_")[1].split(".")[0]

                    # "FAFB" refers to FAFB14 and requires microns
                    # we will change its label to make this explicit
                    # and later add a bridging transform
                    if target == "FAFB":
                        target = "FAFB14um"

                    if source == "FAFB":
                        source = "FAFB14um"

                    # "JRCFIB2018F" likewise requires microns
                    if target == "JRCFIB2018F":
                        target = "JRCFIB2018Fum"

                    if source == "JRCFIB2018F":
                        source = "JRCFIB2018Fum"

                    # "JRCFIB2022M" likewise requires microns
                    if target == "JRCFIB2022M":
                        target = "JRCFIB2022Mum"

                    if source == "JRCFIB2022M":
                        source = "JRCFIB2022Mum"

                    # "MANC" likewise requires microns
                    if target == "MANC":
                        target = "MANCum"

                    if source == "MANC":
                        source = "MANCum"

                    # Initialize the transform
                    transform = tr(hit)

                    if verbose:
                        print(
                            f"Registering {hit} ({tr.__name__}) "
                            f'as "{source}" -> "{target}"'
                        )

                    transforms.registry.register_transform(
                        transform=transform,
                        source=source,
                        target=target,
                        transform_type=transform_type,
                    )
                except BaseException as e:
                    warnings.warn(f"Error registering {hit} as transform: {str(e)}")


def register_transforms():
    """Register transforms with navis."""
    # These are the paths we need to scan
    data_home = pathlib.Path(get_data_home()).expanduser()
    default_path = pathlib.Path("~/mousebrains-data").expanduser()

    # Combine while retaining order
    search_paths = [data_home]
    if default_path not in search_paths:
        search_paths.append(default_path)

    # Go over all paths and add transforms
    for path in search_paths:
        # Do not (re-)move this line! Otherwise is_dir() might fail
        path = pathlib.Path(path).expanduser()

        # Skip if path does not exist
        if not path.is_dir():
            continue

        search_register_path(path)

    # Add transforms to go between CCF voxel and micron space
    transforms.registry.register_transform(
        transform=transforms.AffineTransform(np.diag([10, 10, 10, 1])),
        source="AllenCCF10",
        target="AllenCCF",
        transform_type="bridging",
        weight=0.1,
    )
    transforms.registry.register_transform(
        transform=transforms.AffineTransform(np.diag([25, 25, 25, 1])),
        source="AllenCCF25",
        target="AllenCCF",
        transform_type="bridging",
        weight=0.1,
    )
    transforms.registry.register_transform(
        transform=transforms.AffineTransform(np.diag([50, 50, 50, 1])),
        source="AllenCCF50",
        target="AllenCCF",
        transform_type="bridging",
        weight=0.1,
    )
    transforms.registry.register_transform(
        transform=transforms.AffineTransform(np.diag([100, 100, 100, 1])),
        source="AllenCCF100",
        target="AllenCCF",
        transform_type="bridging",
        weight=0.1,
    )

    # Add alias transform between AllenCCF and AllenCCFum (they are synonymous)
    tr = transforms.AliasTransform()
    transforms.registry.register_transform(
        transform=tr,
        source="AllenCCF",
        target="AllenCCFum",
        transform_type="bridging",
        weight=0,  # low weight = prefered in case of multiple possible paths
    )

    # Transform to go from coronal to sagital CCF orientation
    transforms.registry.register_transform(
        transform=transforms.FunctionTransform(ccf_coronal_sagital),
        source="AllenCCF_coronal",
        target="AllenCCF",
        transform_type="bridging",
    )
    transforms.registry.register_transform(
        transform=transforms.FunctionTransform(ccf_sagital_coronal),
        source="AllenCCF",
        target="AllenCCF_coronal",
        transform_type="bridging",
    )

    # Add the transform to go from AllenCCF (coronal) to the test uCT space
    fp = os.path.join(data_filepath, 'uct-to-ccf_landmarks.csv')
    lm = pd.read_csv(fp)
    tr = transforms.TPStransform(lm[['x_ccf', 'y_ccf', 'z_ccf']].values,
                                 lm[['x_uct', 'y_uct', 'z_uct']].values)
    transforms.registry.register_transform(transform=tr,
                                           source='AllenCCF_coronal',
                                           target='uCT_test',
                                           transform_type='bridging')
