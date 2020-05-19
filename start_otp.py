import socket
import subprocess

import win32api
import win32con


def port_is_free(port):
    s = socket.socket()
    result = False
    try:
        s.bind(("0.0.0.0", port))
        result = True
    except:
        print("Port {} is in use".format(port))
    s.close()
    return result

if port_is_free(8080):
    print('port is free')
    subprocess.Popen('''powershell.exe 
                        cd otp;
                        java -Xmx4096m -jar otp-1.4.0-shaded.jar --router houston --graphs graphs --server''')
else:
    win32api.GenerateConsoleCtrlEvent(win32con.CTRL_C_EVENT, 0)
    print('Server stopped')
