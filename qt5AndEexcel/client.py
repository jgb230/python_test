
#!/usr/bin/env python3
# coding=utf-8

import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import myWind
import PyQt5.sip
def main():
    app = QApplication(sys.argv)
    w = myWind()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
