#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: AM Receiver
# GNU Radio version: 3.7.13.5
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import sdrplay
import wx


class am_receiver(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="AM Receiver")
        _icon_path = "C:\Program Files\GNURadio-3.7\share\icons\hicolor\scalable/apps\gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.vol = vol = 50
        self.samp_rate = samp_rate = 2e6
        self.rf_gain = rf_gain = 70
        self.passband = passband = 6
        self.freq = freq = 990
        self.decimate = decimate = 10
        self.convert = convert = 125e6

        ##################################################
        # Blocks
        ##################################################
        _vol_sizer = wx.BoxSizer(wx.VERTICAL)
        self._vol_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_vol_sizer,
        	value=self.vol,
        	callback=self.set_vol,
        	label='Volume',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._vol_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_vol_sizer,
        	value=self.vol,
        	callback=self.set_vol,
        	minimum=0,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.GridAdd(_vol_sizer, 0, 8, 1, 3)
        _rf_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._rf_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_rf_gain_sizer,
        	value=self.rf_gain,
        	callback=self.set_rf_gain,
        	label='RF Gain',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._rf_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_rf_gain_sizer,
        	value=self.rf_gain,
        	callback=self.set_rf_gain,
        	minimum=10,
        	maximum=70,
        	num_steps=12,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.GridAdd(_rf_gain_sizer, 0, 1, 1, 3)
        _passband_sizer = wx.BoxSizer(wx.VERTICAL)
        self._passband_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_passband_sizer,
        	value=self.passband,
        	callback=self.set_passband,
        	label='Filter kHz',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._passband_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_passband_sizer,
        	value=self.passband,
        	callback=self.set_passband,
        	minimum=1,
        	maximum=10,
        	num_steps=10,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.GridAdd(_passband_sizer, 0, 4, 1, 3)
        self._freq_text_box = forms.text_box(
        	parent=self.GetWin(),
        	value=self.freq,
        	callback=self.set_freq,
        	label='Frequency in kHz',
        	converter=forms.int_converter(),
        )
        self.GridAdd(self._freq_text_box, 0, 12, 1, 12)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.GetWin(),
        	baseband_freq=freq*1000,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate/decimate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title='Decimated Sampling Bandpass',
        	peak_hold=False,
        	win=window.hamming,
        )
        self.Add(self.wxgui_fftsink2_0.win)
        self.sdrplay_rsp1a_source_0 = sdrplay.rsp1a_source(freq*1000, 200, True, 40, True, True,
                False, 0, 1, samp_rate, False, False, (70-rf_gain)/60*6, False,
                '0')

        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=6,
                decimation=25,
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=decimate,
                taps=None,
                fractional_bw=None,
        )
        self.low_pass_filter_0 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate/decimate, passband*1000, 200, firdes.WIN_HAMMING, 6.76))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((vol/100*1.2, ))
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_am_demod_cf_0 = analog.am_demod_cf(
        	channel_rate=samp_rate/decimate,
        	audio_decim=1,
        	audio_pass=10000,
        	audio_stop=11000,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_am_demod_cf_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_am_demod_cf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.wxgui_fftsink2_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.sdrplay_rsp1a_source_0, 0), (self.rational_resampler_xxx_0, 0))

    def get_vol(self):
        return self.vol

    def set_vol(self, vol):
        self.vol = vol
        self._vol_slider.set_value(self.vol)
        self._vol_text_box.set_value(self.vol)
        self.blocks_multiply_const_vxx_0.set_k((self.vol/100*1.2, ))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate/self.decimate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate/self.decimate, self.passband*1000, 200, firdes.WIN_HAMMING, 6.76))

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self._rf_gain_slider.set_value(self.rf_gain)
        self._rf_gain_text_box.set_value(self.rf_gain)
        self.sdrplay_rsp1a_source_0.set_lna_atten_step((70-self.rf_gain)/60*6)

    def get_passband(self):
        return self.passband

    def set_passband(self, passband):
        self.passband = passband
        self._passband_slider.set_value(self.passband)
        self._passband_text_box.set_value(self.passband)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate/self.decimate, self.passband*1000, 200, firdes.WIN_HAMMING, 6.76))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self._freq_text_box.set_value(self.freq)
        self.wxgui_fftsink2_0.set_baseband_freq(self.freq*1000)
        self.sdrplay_rsp1a_source_0.set_rf_freq(self.freq*1000)

    def get_decimate(self):
        return self.decimate

    def set_decimate(self, decimate):
        self.decimate = decimate
        self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate/self.decimate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate/self.decimate, self.passband*1000, 200, firdes.WIN_HAMMING, 6.76))

    def get_convert(self):
        return self.convert

    def set_convert(self, convert):
        self.convert = convert


def main(top_block_cls=am_receiver, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()
