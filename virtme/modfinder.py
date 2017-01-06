# -*- mode: python -*-
# modfinder: A simple tool to resolve required modules
# Copyright © 2014 Andy Lutomirski
# Licensed under the GPLv2, which is available in the virtme distribution
# as a file called LICENSE with SHA-256 hash:
# 8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643

"""
This is a poor man's module resolver and loader.  It does not support any
sort of hotplug.  Instead it generates a topological order and loads
everything.  The idea is to require very few modules.
"""

import re
import subprocess
import os, os.path
import itertools

_INSMOD_RE = re.compile('insmod (.*[^ ]) *$')

def resolve_dep(modalias, root=None, kver=None, moddir=None):
    if moddir is not None:
        moddir = os.path.abspath(moddir)
        modules = os.path.dirname(moddir)
        assert modules.endswith('/lib/modules'), 'moddir has to be <root>/lib/modules/<version>'
        root = modules[:-len('/lib/modules')] or None
        kver = os.path.basename(moddir)
    args = ['modprobe', '--show-depends']
    args += ['-C', '/var/empty']
    if root is not None:
        args += ['-d', root]
    if kver is not None and kver != os.uname().release:
        # If booting the loaded kernel, skip -S.  This helps certain
        # buggy modprobe versions that don't support -S.
        args += ['-S', kver]
    args += ['--', modalias]

    deps = []

    try:
        with open('/dev/null', 'r+b') as devnull:
            script = subprocess.check_output(args, stderr=devnull.fileno()).\
                     decode('utf-8', errors='replace')
        for line in script.split('\n'):
            m = _INSMOD_RE.match(line)
            if m:
                deps.append(m.group(1))
    except subprocess.CalledProcessError:
        pass  # This is most likely because the module is built in.

    return deps

def merge_mods(lists):
    found = set()
    mods = []
    for mod in itertools.chain(*lists):
        if mod not in found:
            found.add(mod)
            mods.append(mod)
    return mods

def find_modules_from_install(aliases, root=None, kver=None, moddir=None):
    return merge_mods(resolve_dep(a, root=root, kver=kver, moddir=moddir)
                      for a in aliases)
