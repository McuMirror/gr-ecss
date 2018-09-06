#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from collections import namedtuple
from gnuradio.fft import window
import ecss_swig as ecss
import flaress
import math, time, datetime, os, abc, sys
import runner, threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class Pdf_class(object):
    """this class can print a single pdf for all the tests"""

    graphs_list = []

    def __init__(self, name_test='test'):
        current_dir = os.getcwd()
        dir_to = os.path.join(current_dir, 'Graphs')

        if not os.path.exists(dir_to):
            os.makedirs(dir_to)
        self.name_test = name_test.split('.')[0]
        self.name_complete = dir_to + '/' + name_test.split('.')[0] + "_graphs.pdf"

    def add_to_pdf(self, fig):
        """this function can add a new element/page to the list of pages"""

        fig_size = [21 / 2.54, 29.7 / 2.54] # width in inches & height in inches
        fig.set_size_inches(fig_size)
        Pdf_class.graphs_list.append(fig)

    def finalize_pdf(self):
        """this function print the final version of the pdf with all the pages"""

        with PdfPages(self.name_complete) as pdf:
            for graph in Pdf_class.graphs_list:
                pdf.savefig(graph)   #write the figures for that list

            d = pdf.infodict()
            d['Title'] = self.name_test
            d['Author'] = 'Antonio Miraglia - ISISpace'
            d['Subject'] = 'self generated graphs from the qa test'
            d['Keywords'] = self.name_test
            d['CreationDate'] = datetime.datetime(2018, 8, 21)
            d['ModDate'] = datetime.datetime.today()

def print_parameters(data):
    to_print = "\p Sample rate = %d Hz; Number of Bits = %d; Minimum Value = %.3f rad; Maximum Value = %.3f rad \p" \
        %(data.samp_rate, data.N, data.min_value, data.max_value)
    print to_print

def check_integer_phase(data_out, items):
    """this function checks the integer phase accumulator output from the pll. evaluates the minimum step and the slope"""

    minimum_step = sys.maxint
    slope = 0
    for i in reversed(xrange (len(data_out))):
        if i > 0:
            if (abs(data_out[i] - data_out[i - 1]) < abs(minimum_step)):
                minimum_step = abs(data_out[i] - data_out[i - 1])
            if (i < (len(data_out) - items - 1)):       #this is only the average on n items
                slope = ((data_out[i] - data_out[i - 1]) / items) + slope
    return minimum_step, slope

def plot(self, data_pe):
    """this function create a defined graph for the pll with the data input and output"""

    plt.rcParams['text.usetex'] = True

    data_in = np.asarray(data_pe.src)
    data_out = np.asarray(data_pe.out)
    time = np.asarray(data_pe.time)

    fig, (ax1, ax2) = plt.subplots(2)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Phase [rad]', color='r')
    ax1.set_title("Input",  fontsize=20)
    ax1.plot(time, data_in, color='r', scalex=True, scaley=True)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel ('Integer Phase', color='r')
    ax2.set_title("Output", fontsize=20)
    ax2.plot(time, data_out, color='r', scalex=True, scaley=True)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)

    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_ramp(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_pc = namedtuple('data_pc', 'src out time')

    src_ramp = analog.sig_source_f(param.samp_rate, analog.GR_SAW_WAVE, (param.samp_rate * 0.5 / param.items), 2.0 * (param.max_value - param.min_value), (2.0 * param.min_value - param.max_value))

    throttle = blocks.throttle(gr.sizeof_float*1, param.samp_rate,True)
    head = blocks.head(gr.sizeof_float, int (param.items))

    dst_source = blocks.vector_sink_f()
    dst_pc_out = flaress.vector_sink_int64()

    pc = ecss.phase_converter(param.N)

    tb.connect(src_ramp, throttle)
    tb.connect(throttle, head)
    tb.connect(head, dst_source)
    tb.connect(head, pc)
    tb.connect(pc, dst_pc_out)

    self.tb.run()

    data_pc.src = dst_source.data()
    data_pc.out = dst_pc_out.data()
    data_pc.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

    return data_pc

class qa_phase_converter (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: wrapping test"""
        param = namedtuple('param', 'samp_rate items N min_value max_value')
        param.N = 38
        param.samp_rate = 4096
        param.items = 4096 * 2
        param.max_value = 2 * math.pi
        param.min_value = -2 * math.pi

        print_parameters(param)

        data_pc = test_ramp(self, param)
        plot(self,data_pc)

        pc_min_step , pc_slope = check_integer_phase(data_pc.out, 100)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        pc_min_step_rad = (pc_min_step >> (64 - param.N)) * precision
        pc_slope_rad = (pc_slope >> (64 - param.N)) * precision
        self.assertGreaterEqual(pe_min_step_rad, precision)
        print "-Output Slope : %f rad/s;" % pc_slope_rad       # WARNING: this is only a mean
        print "-Output Min step : %f rad." % pc_min_step_rad

    def test_002_t (self):
        """test_002_t: precision test"""
        param = namedtuple('param', 'samp_rate items N min_value max_value')
        param.N = 4
        param.samp_rate = 4096
        param.items = 4096 * 2
        param.max_value = 2 * math.pi
        param.min_value = -2 * math.pi

        print_parameters(param)

        data_pc = test_ramp(self, param)
        plot(self,data_pc)

        pc_min_step , pc_slope = check_integer_phase(data_pc.out, 100)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        pc_min_step_rad = (pc_min_step >> (64 - param.N)) * precision
        pc_slope_rad = (pc_slope >> (64 - param.N)) * precision
        self.assertGreaterEqual(pc_min_step_rad, precision)
        print "-Output Slope : %f rad/s;" % pc_slope_rad       # WARNING: this is only a mean
        print "-Output Min step : %f rad." % pc_min_step_rad

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_phase_converter)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()