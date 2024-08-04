#!/usr/bin/env python3

# -*- coding: utf-8 -*-



#

# SPDX-License-Identifier: GPL-3.0

#

# GNU Radio Python Flow Graph

# Title: Top Block

# GNU Radio version: 3.9.5.0



from gnuradio import blocks

from gnuradio import gr

from gnuradio.filter import firdes

from gnuradio.fft import window

import sys

import signal

from argparse import ArgumentParser

from gnuradio.eng_arg import eng_float, intx

from gnuradio import eng_notation

from gnuradio import zeromq









class top_block(gr.top_block):



    def __init__(self):

        gr.top_block.__init__(self, "Top Block")



        ##################################################

        # Variables

        ##################################################

        self.samp_rate = samp_rate = 23.04e6



        ##################################################

        # Blocks

        ##################################################

        self.zeromq_req_source_3 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://localhost:2101', 100, False, -1)

        self.zeromq_req_source_1 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://localhost:2001', 100, False, -1)

        self.zeromq_req_source_0 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://localhost:2011', 100, False, -1)

        self.zeromq_rep_sink_2 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://*:2000', 100, False, -1)

        self.zeromq_rep_sink_1 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://*:2010', 100, False, -1)

        self.zeromq_rep_sink_0 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://*:2100', 100, False, -1)

        self.blocks_throttle_0_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)

        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)

        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)

        self.blocks_add_xx_0 = blocks.add_vcc(1)





        ##################################################

        # Connections

        ##################################################

        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))

        self.connect((self.blocks_throttle_0, 0), (self.zeromq_rep_sink_0, 0))

        self.connect((self.blocks_throttle_0_0, 0), (self.zeromq_rep_sink_2, 0))

        self.connect((self.blocks_throttle_0_0_0, 0), (self.zeromq_rep_sink_1, 0))

        self.connect((self.zeromq_req_source_0, 0), (self.blocks_add_xx_0, 1))

        self.connect((self.zeromq_req_source_1, 0), (self.blocks_add_xx_0, 0))

        self.connect((self.zeromq_req_source_3, 0), (self.blocks_throttle_0_0, 0))

        self.connect((self.zeromq_req_source_3, 0), (self.blocks_throttle_0_0_0, 0))





    def get_samp_rate(self):

        return self.samp_rate



    def set_samp_rate(self, samp_rate):

        self.samp_rate = samp_rate

        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)

        self.blocks_throttle_0_0_0.set_sample_rate(self.samp_rate)









def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()



    def sig_handler(sig=None, frame=None):

        tb.stop()

        tb.wait()



        sys.exit(0)



    signal.signal(signal.SIGINT, sig_handler)

    signal.signal(signal.SIGTERM, sig_handler)



    tb.start()



    try:

        input('Press Enter to quit: ')

    except EOFError:

        pass

    tb.stop()

    tb.wait()





if __name__ == '__main__':

    main()