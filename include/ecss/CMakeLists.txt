# Copyright 2011,2012 Free Software Foundation, Inc.
#
# This file was generated by gr_modtool, a tool from the GNU Radio framework
# This file is a part of gr-ecss
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Install public header files
########################################################################
install(FILES
    api.h
    agc.h
    pll.h
    coherent_phase_modulator.h
    phase_converter.h
    loop_filter.h
    gain_phase_accumulator.h
    signal_search_goertzel.h
    signal_search_fft_v.h
    spl_encoder.h
    spl_decoder.h
    nrzl_encoder.h
    nrzl_encoder_subcarrier.h
    threshold_to_message.h DESTINATION include/ecss
)
