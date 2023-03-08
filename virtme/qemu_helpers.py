# -*- mode: python -*-
# qemu_helpers: Helpers to find QEMU and handle its quirks
# Copyright © 2014 Andy Lutomirski
# Licensed under the GPLv2, which is available in the virtme distribution
# as a file called LICENSE with SHA-256 hash:
# 8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643

import os
import re
import shutil
import subprocess
from typing import Optional

class Qemu(object):
    qemubin: str
    version: Optional[str]

    def __init__(self, arch) -> None:
        self.arch = arch

        qemubin = shutil.which('qemu-system-%s' % arch)
        if qemubin is None and arch == os.uname().machine:
            qemubin = shutil.which('qemu-kvm')
        if qemubin is None:
            raise ValueError('cannot find qemu for %s' % arch)

        self.qemubin = qemubin
        self.version = None

    def probe(self) -> None:
        if self.version is None:
            self.version = subprocess.check_output([self.qemubin, '--version'])\
                                     .decode('utf-8')

            # Parse version parts into a tuple of ints, default to (0,)
            m = re.search(r'version ((?:\d\.)*\d)', self.version)
            if m is None:
                version_parts = (0,)
            else:
                try:
                    version_parts = tuple(int(i) for i in m.group(1).split('.'))
                except ValueError:
                    version_parts = (0,)

            self.cannot_overmount_virtfs = version_parts <= (1, 5)

            # QEMU 4.2+ supports -fsdev multidevs=remap
            self.has_multidevs = version_parts >= (4, 2)

    def quote_optarg(self, a: str) -> str:
        """Quote an argument to an option."""
        return a.replace(',', ',,')

