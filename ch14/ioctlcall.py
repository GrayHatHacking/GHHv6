from ctypes import windll, POINTER, byref
from ctypes.wintypes import LPVOID, DWORD, LPCSTR, LPSTR, BOOL, HANDLE


gle = windll.kernel32.GetLastError


# ctypes errcheck functions
def errcheck_bool(res, func, args):
    if not res:
        print("{} failed. GLE: {}".format(func.__name__, gle()))
    return res


def errcheck_createfile(res, func, args):
    if res == HANDLE(-1).value:  # INVALID_HANDLE_VALUE
        raise Exception("Failed to open device {}. GLE: {}"
                        .format(args[0], gle()))
    return res


DeviceIoControl = windll.kernel32.DeviceIoControl
CreateFileA = windll.kernel32.CreateFileA
CloseHandle = windll.kernel32.CloseHandle

DeviceIoControl.restype = BOOL
# we won't use LPOVERLAPPED (arg 8) so just use LPVOID
DeviceIoControl.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID, DWORD,
                            POINTER(DWORD), LPVOID]
DeviceIoControl.errcheck = errcheck_bool
CreateFileA.restype = HANDLE
# we won't use LPSECURITY_ATTRIBUTES (arg 4) so just use LPVOID
CreateFileA.argtypes = [LPCSTR, DWORD, DWORD, LPVOID, DWORD, DWORD, HANDLE]
CreateFileA.errcheck = errcheck_createfile
CloseHandle.restype = BOOL
CloseHandle.argtypes = [HANDLE]


# constants
GENERIC_READ = (1 << 30)
GENERIC_WRITE = (1 << 31)
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80


def opendevice(dev):
    # open the device
    hdev = CreateFileA(dev, GENERIC_READ | GENERIC_WRITE,
                       FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING,
                       FILE_ATTRIBUTE_NORMAL, None)
    return hdev


def ioctl(hdev, ioctl, input, outbuf_len):
    outbuf = LPSTR(b"\x00" * outbuf_len) if outbuf_len else None

    outret = DWORD()
    DeviceIoControl(hdev, ioctl, input, len(input), outbuf, outbuf_len,
                    byref(outret), None)
    return outret.value, (outbuf.value if outbuf else b'')


if __name__ == '__main__':
    import argparse
    import sys

    def _buf_or_stdin(arg):
        if arg == "-":
            return sys.stdin.read().encode()
        return bytes.fromhex(arg)

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--device', required=True, help="Device to open",
                    type=lambda x: x.encode())
    ap.add_argument('-i', '--ioctl', required=True, help="IOCTL to invoke",
                    type=lambda x: int(x, 0))
    ap.add_argument('-b', '--buffer', type=_buf_or_stdin, default=b"",
                    help="Input buffer as hex (- for raw from stdin)")
    ap.add_argument('-o', '--output-buffer-length', default=0,
                    type=lambda x: int(x, 0), help="Output buffer length")
    ap.add_argument('-m', '--match-input-output', action='store_true',
                    help="Make output buffer size input buffer size")
    args = ap.parse_args()

    print("Device: {}\nIOCTL: 0x{:x}".format(args.device.decode(), args.ioctl))
    print("Input buffer: {}".format(args.buffer.hex()))

    if args.match_input_output:
        args.output_buffer_length = len(args.buffer)

    hdev = opendevice(args.device)
    ret, buf = ioctl(hdev, args.ioctl, args.buffer, args.output_buffer_length)
    CloseHandle(hdev)

    print("Return value: {}\nOutput Buffer length: {}\nOutput Buffer: {}"
          .format(ret, len(buf), buf.hex()))
