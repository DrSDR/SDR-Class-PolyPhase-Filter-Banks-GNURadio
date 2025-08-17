#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: drsdr
# GNU Radio version: 3.10.11.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import threading



class s5(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "s5")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 96000
        self.lpf = lpf = firdes.low_pass(1.0, samp_rate, 7000,100, window.WIN_HAMMING, 6.76)

        ##################################################
        # Blocks
        ##################################################

        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(6, lpf, 32000, samp_rate)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/drsdr/sdrclass/IQSig_96KHz.wav', True)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.band_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                (samp_rate/6),
                100,
                5000,
                100,
                window.WIN_HAMMING,
                6.76))
        self.audio_sink_0 = audio.sink(16000, '', True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 1), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "s5")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_lpf(firdes.low_pass(1.0, self.samp_rate, 7000, 100, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, (self.samp_rate/6), 100, 5000, 100, window.WIN_HAMMING, 6.76))

    def get_lpf(self):
        return self.lpf

    def set_lpf(self, lpf):
        self.lpf = lpf
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.lpf)




def main(top_block_cls=s5, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
