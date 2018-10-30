/* -*- c++ -*- */
/*
 * Copyright 2018 Antonio Miraglia - ISISpace.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_ECSS_PLL_IMPL_H
#define INCLUDED_ECSS_PLL_IMPL_H

#include <ecss/pll.h>
#include <vector>

namespace gr {
  namespace ecss {

    class pll_impl : public pll
    {

      int d_N;
      float d_samp_rate;
      int d_order;
      int64_t d_integer_phase;
      double d_integer_phase_denormalized;                /*!< Integer value after to be denormalized */
      double precision;
      double branch_3_par, branch_2_3_par, branch_2_3;
      double d_freq_central, d_bw;
      double branch_2_3_max, branch_2_3_min;
      std::vector<double> d_coefficients;

      double mod_2pi(double in);                          /*! Keep the value between -2pi and 2pi */
      void reset();                                       /*! Reset all the registers */
      void NCO_denormalization();
      double phase_detector(gr_complexd sample);
      double magnitude(gr_complexd sample);

      public:
        pll_impl(float samp_rate, int order, int N, const std::vector<double> &coefficients, float freq_central, float bw);
        ~pll_impl();

        int work(int noutput_items,
                 gr_vector_const_void_star &input_items,
                 gr_vector_void_star &output_items);

        /*! \brief Integer phase converter
      *
      * converts the filter output into integer mathematics
      */
        int64_t integer_phase_converter(double step_phase);

        /*! \brief Integer accumulator
      *
      * integrates the filter output (already converted) using an integer mathematics
      */
        void accumulator(int64_t filter_out);

        /*! \brief Evaluate the Loop filter output.
      *
      * \details
      * This function evaluate the output of the PLL loop filter. This function can
      * evaluate the output for 2nd order or 3rd order loop filter. It uses the global
      * variable d_order to choose the order of the filter.
      *
      * This function uses the global variables d_Coeff3_3, d_Coeff2_3, d_Coeff1_3, d_Coeff4_2
      * d_Coeff2_2, d_Coeff1_2 to evaluate the output in according with the order of the filter.
      * \returns (double) output loop filter
      */
        double advance_loop(double error);

        /*! \brief Keep the phase in the range [-pi, pi).
      *
      * \details
      * This function keeps the phase between -pi and pi. If the
      * phase is greater than pi by d, it wraps around to be -pi+d;
      * similarly if it is less than -pi by d, it wraps around to
      * pi-d.
      * \returns (double) new phase limited
      */
        double phase_wrap(double phase);

        /*! \brief Keep the frequency between d_min_freq and d_max_freq.
      *
      * \details
      * Specifically, this function works with the phase steps. Thus,
      * keeps the steps of branch_2_3 (so, the integrated parts of the
      * loop filter) between branch_2_3_max and branch_2_3_min.
      * If the step is greater than branch_2_3_max, it
      * is set to branch_2_3_max.  If the frequency is less than
      * branch_2_3_min, it is set to branch_2_3_min.
      *
      * \param step (double) step
      * \returns (double) new step limited
      */
        double frequency_limit(double step);

        /*******************************************************************
      * SET FUNCTIONS
      *******************************************************************/

        /*!
       * \brief Set the precision of the PLL.
       *
       * \details
       * Sets the internal number of bits.
       * This value is set only at the start.
       *
       * \param N    (int) new number of bits
       */
        void set_N(int N);

        /*!
       * \brief Set the loop filter order.
       *
       * \details
       * Sets the loop filter's order.
       *
       * This value should really only be set by adjusting the loop
       * bandwidth and damping factor.
       *
       * \param order (int) new loop filer order
       */
        void set_order(int order);

        /*!
       * \brief Set the loop gain coefficients.
       *
       * \details
       * Sets the loop filter's coefficient gain parameters.
       *
       * This values should really only be set by adjusting the loop
       * bandwidth and damping factor.
       *
       * \param coefficients (double) new coefficients
       */
        void set_coefficients(const std::vector<double> &coefficients);

        /*!
       * \brief Set the control loop's frequency.
       *
       * \details
       * Sets the control loop's frequency. While this is normally
       * updated by the inner loop of the algorithm, it could be
       * useful to manually initialize, set, or reset this under
       * certain circumstances.
       *
       * \param freq    (float) new frequency
       */
        void set_frequency(float freq);

        /*!
      * \brief Set the control loop's phase.
      *
      * \details
      * Sets the control loop's phase. While this is normally
      * updated by the inner loop of the algorithm, it could be
      * useful to manually initialize, set, or reset this under
      * certain circumstances.
      *
      * \param phase (float) new phase
      */
        void set_phase(float phase);

        /*!
      * \brief Set the control loop's central frequency.
      *
      * \details
      * Set the central frequency the control loop can track.
      *
      * \param freq (float) new central frequency
      */
        void set_freq_central(float freq);

        /*!
      * \brief Set the control loop's bandwidth.
      *
      * \details
      * Set the bandwidth the control loop can track.
      *
      * \param bw (float) new bandwidth
      */
        void set_bw(float bw);

        /*******************************************************************
      * GET FUNCTIONS
      *******************************************************************/

        /*!
      * \brief Returns the loop gain order.
      */
        int get_order() const;

        /*!
      * \brief Returns the loop gain coefficients.
      */
        std::vector<double> get_coefficients() const;

        /*!
      * \brief Get the control loop's frequency estimated.
      */
        float get_frequency() const;

        /*!
      * \brief Get the control loop's phase estimate.
      */
        float get_phase() const;

        /*!
      * \brief Get the control loop's central frequency.
      */
        float get_freq_central() const;

        /*!
      * \brief Get the control loop's bandwidth.
      */
        float get_bw() const;
      };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_PLL_IMPL_H */
