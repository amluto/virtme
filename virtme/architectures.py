#!/usr/bin/python3
# -*- mode: python -*-
# qemu_helpers: Helpers to find QEMU and handle its quirks
# Copyright © 2014 Andy Lutomirski
# Licensed under the GPLv2, which is available in the virtme distribution
# as a file called LICENSE with SHA-256 hash:
# 8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643

import os

class Arch(object):
    @staticmethod
    def serial_dev_name(index):
        return 'ttyS%d' % index

    @staticmethod
    def qemuargs(is_native):
        return []

    @staticmethod
    def virtio_dev_type(virtiotype):
        # Return a full name for a virtio device.  It would be
        # nice if QEMU abstracted this away, but it doesn't.
        return 'virtio-%s-pci' % virtiotype

    @staticmethod
    def earlyconsole_args():
        return []

    @staticmethod
    def serial_console_args():
        return []

class Arch_unknown(Arch):
    @staticmethod
    def qemuargs(is_native):
        return Arch.qemuargs(is_native)

class Arch_x86(Arch):
    @staticmethod
    def qemuargs(is_native):
        ret = Arch.qemuargs(is_native)

        # Add a watchdog.  This is useful for testing.
        ret.extend(['-watchdog', 'i6300esb'])

        if is_native and os.access('/dev/kvm', os.R_OK):
            # If we're likely to use KVM, request a full-featured CPU.
            # (NB: if KVM fails, this will cause problems.  We should probe.)
            ret.extend(['-cpu', 'host'])  # We can't migrate regardless.

        return ret

    @staticmethod
    def earlyconsole_args():
        return ['earlyprintk=serial,ttyS0,115200']

    @staticmethod
    def serial_console_args():
        return ['console=ttyS0']

class Arch_arm(Arch):
    def qemuargs(is_native):
        ret = Arch.qemuargs(is_native)

        # Emulate a versatilepb.
        ret.extend(['-M', 'versatilepb'])

        # Add a watchdog.  This is useful for testing.  Oddly, this works
        # fine on ARM even though it's an Intel chipset device.
        ret.extend(['-watchdog', 'i6300esb'])

        return ret

    @staticmethod
    def virtio_dev_type(virtiotype):
        return 'virtio-%s-pci' % virtiotype

    @staticmethod
    def earlyconsole_args():
        return ['earlyprintk=serial,ttyAMA0,115200']

    @staticmethod
    def serial_console_args():
        return ['console=ttyAMA0']

class Arch_aarch64(Arch):
    def qemuargs(is_native):
        ret = Arch.qemuargs(is_native)

        # Emulate a fully virtual system.
        ret.extend(['-M', 'virt'])

        # Despite being called qemu-system-aarch64, QEMU defaults to
        # emulating a 32-bit CPU.  Override it.
        ret.extend(['-cpu', 'cortex-a57'])

        return ret

    @staticmethod
    def virtio_dev_type(virtiotype):
        return 'virtio-%s-device' % virtiotype

    @staticmethod
    def earlyconsole_args():
        return ['earlyprintk=serial,ttyAMA0,115200']

    @staticmethod
    def serial_console_args():
        return ['console=ttyAMA0']

ARCHES = {
    'x86_64': Arch_x86,
    'i386': Arch_x86,
    'arm': Arch_arm,
    'aarch64': Arch_aarch64,
}

def get(arch):
    return ARCHES.get(arch, Arch_unknown)
