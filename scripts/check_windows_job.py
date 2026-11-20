"""Check the original Watcher's file-readiness requirements on Windows."""
import argparse
import ctypes
from ctypes import wintypes
from pathlib import Path
from stat import FILE_ATTRIBUTE_REPARSE_POINT, S_ISREG
import sys
import time


def snapshot(folder):
    files = {}
    for path in sorted(folder.rglob("*")):
        stat = path.lstat()
        if stat.st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f"Linked path in job: {path.relative_to(folder)}")
        if S_ISREG(stat.st_mode):
            files[path] = (stat.st_size, stat.st_mtime_ns)
    if folder / "event.txt" not in files or len(files) < 2:
        raise ValueError("The job needs event.txt and a source file")
    return files


def check_writers(files):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    open_file = kernel.CreateFileW
    open_file.argtypes = (
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    )
    open_file.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = (wintypes.HANDLE,)
    close.restype = wintypes.BOOL
    invalid = ctypes.c_void_p(-1).value
    handles = []
    try:
        for path in files:
            # Request read access and share reads only, so Windows rejects existing writers.
            handle = open_file(str(path), 0x80000000, 0x1, None, 3, 0, None)
            if handle == invalid:
                raise OSError(f"{path.name}: Windows error {ctypes.get_last_error()}")
            handles.append(handle)
    finally:
        for handle in handles:
            close(handle)


def check(folder, pause=time.sleep):
    original = snapshot(folder)
    for sample in range(1, 4):
        if sample > 1:
            pause(30)
            if snapshot(folder) != original:
                raise ValueError("Files changed during the stability samples")
        print(f"Sample {sample}: {len(original)} files, "
              f"{sum(size for size, _ in original.values())} bytes", flush=True)
    check_writers(original)
    pause(60)
    if snapshot(folder) != original:
        raise ValueError("Files changed during the safety buffer")
    check_writers(original)
    print("READY: file checks passed. Human approval is still required.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("This check is for Windows")
    try:
        check(args.project.resolve(strict=True))
    except (OSError, ValueError) as exc:
        print(f"NOT READY: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
