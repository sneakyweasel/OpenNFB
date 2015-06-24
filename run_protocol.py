from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import scipy.signal

from PySide import QtCore
from bdf import BDFReader, BDFWriter
from acquisition import BDFThread, OpenBCIThread

import sys, imp

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.setWindowTitle("OpenNFB")
#mw.resize(800,800)

#win = pg.GraphicsWindow(title="OpenNFB")

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

protocol_filename = './alpha-theta.py'
#protocol_filename = 'ekg-drum.py'

widget = None


def handle_reload(path):
    global protocol, widget
    protocol = imp.load_module('foo', file(protocol_filename), protocol_filename, ('.py', 'U', 1))
    widget = protocol.widget()
    win.setCentralWidget(widget)
    #win.show()
    print path

watcher = QtCore.QFileSystemWatcher()
watcher.addPath(protocol_filename)
watcher.fileChanged.connect(handle_reload)

handle_reload(protocol_filename)
win.show()


replay = sys.argv[1] == 'replay'
if replay:
    sourceThread = BDFThread(sys.argv[2])
else:
    sourceThread = OpenBCIThread(sys.argv[1])

try:
    if not replay:
        write_file = file(sys.argv[2], 'wb')
        import bdf
        writer = bdf.BDFWriter(8)
        sourceThread.newPacket.connect(writer.append_sample)
        QtGui.QApplication.instance().aboutToQuit.connect(lambda: writer.write_file(write_file))
except IndexError:
  print "No log file specified"

def handlePacket(packet):
    protocol.update(packet)

sourceThread.newPacket.connect(handlePacket)
sourceThread.start()

def updateGUI():
    for child in widget.children():
        if hasattr(child, 'updateGUI'):
            child.updateGUI()


guiTimer = QtCore.QTimer()
guiTimer.timeout.connect(updateGUI)
guiTimer.start(0)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
       QtGui.QApplication.instance().exec_()
