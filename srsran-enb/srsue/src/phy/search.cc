/**
 * Copyright 2013-2023 Software Radio Systems Limited
 *
 * This file is part of srsRAN.
 *
 * srsRAN is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * srsRAN is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * A copy of the GNU Affero General Public License can be found in
 * the LICENSE file in the top-level directory of this distribution
 * and at http://www.gnu.org/licenses/.
 *
 */

#include "srsue/hdr/phy/search.h"
#include "srsran/common/standard_streams.h"

#define Error(fmt, ...)                                                                                                \
  if (SRSRAN_DEBUG_ENABLED)                                                                                            \
  logger.error(fmt, ##__VA_ARGS__)
#define Warning(fmt, ...)                                                                                              \
  if (SRSRAN_DEBUG_ENABLED)                                                                                            \
  logger.warning(fmt, ##__VA_ARGS__)
#define Info(fmt, ...)                                                                                                 \
  if (SRSRAN_DEBUG_ENABLED)                                                                                            \
  logger.info(fmt, ##__VA_ARGS__)
#define Debug(fmt, ...)                                                                                                \
  if (SRSRAN_DEBUG_ENABLED)                                                                                            \
  logger.debug(fmt, ##__VA_ARGS__)

namespace srsue {

static int
radio_recv_callback(void* obj, cf_t* data[SRSRAN_MAX_CHANNELS], uint32_t nsamples, srsran_timestamp_t* rx_time)
{
  srsran::rf_buffer_t x(data, nsamples);
  return ((search_callback*)obj)->radio_recv_fnc(x, rx_time);
}

static SRSRAN_AGC_CALLBACK(callback_set_rx_gain)
{
  ((search_callback*)h)->set_rx_gain(gain_db);
}

search::~search()
{
  srsran_ue_mib_sync_free(&ue_mib_sync);
  srsran_ue_cellsearch_free(&cs);
}

void search::init(srsran::rf_buffer_t& buffer_, uint32_t nof_rx_channels, search_callback* parent, int force_N_id_2_, int force_N_id_1_)
{
  p = parent;

  buffer = buffer_;

  if (srsran_ue_cellsearch_init_multi(&cs, 8, radio_recv_callback, nof_rx_channels, parent)) {
    Error("SYNC:  Initiating UE cell search");
  }
  srsran_ue_cellsearch_set_nof_valid_frames(&cs, 4);

  if (srsran_ue_mib_sync_init_multi(&ue_mib_sync, radio_recv_callback, nof_rx_channels, parent)) {
    Error("SYNC:  Initiating UE MIB synchronization");
  }

  // Set options defined in expert section
  p->set_ue_sync_opts(&cs.ue_sync, 0);

  force_N_id_2 = force_N_id_2_;
  force_N_id_1 = force_N_id_1_;
}

void search::set_cp_en(bool enable)
{
  srsran_set_detect_cp(&cs, enable);
}

void search::reset()
{
  srsran_ue_sync_reset(&ue_mib_sync.ue_sync);
}

float search::get_last_cfo()
{
  return srsran_ue_sync_get_cfo(&ue_mib_sync.ue_sync);
}

void search::set_agc_enable(bool enable)
{
  if (enable) {
    srsran_rf_info_t* rf_info = p->get_radio()->get_info();
    srsran_ue_sync_start_agc(&ue_mib_sync.ue_sync,
                             callback_set_rx_gain,
                             rf_info->min_rx_gain,
                             rf_info->max_rx_gain,
                             p->get_radio()->get_rx_gain());
  } else {
    ERROR("Error stop AGC not implemented");
  }
}

search::ret_code search::run(srsran_cell_t* cell_, std::array<uint8_t, SRSRAN_BCH_PAYLOAD_LEN>& bch_payload)
{
  srsran_cell_t new_cell = {};

  srsran_ue_cellsearch_result_t found_cells[3];

  bzero(found_cells, 3 * sizeof(srsran_ue_cellsearch_result_t));

  /* Find a cell in the given N_id_2 or go through the 3 of them to find the strongest */
  uint32_t max_peak_cell = 0;
  int      ret           = SRSRAN_ERROR;

  Info("SYNC:  Searching for cell...");
  srsran::console(".");

  if (force_N_id_2 >= 0 && force_N_id_2 < SRSRAN_NOF_NID_2) {
    ret           = srsran_ue_cellsearch_scan_N_id_2(&cs, force_N_id_2, &found_cells[force_N_id_2]);
    max_peak_cell = force_N_id_2;
  } else {
    ret = srsran_ue_cellsearch_scan(&cs, found_cells, &max_peak_cell);
  }

  if (ret < 0) {
    Error("SYNC:  Error decoding MIB: Error searching PSS");
    return ERROR;
  } else if (ret == 0) {
    Info("SYNC:  Could not find any cell in this frequency");
    return CELL_NOT_FOUND;
  }

  // In case of forced N_id_1 discard any results with different values
  if (force_N_id_1 >= 0 && force_N_id_1 < SRSRAN_NOF_NID_1) {
    /* Note that srsran_ue_cellsearch_scan_N_id_2 only finds the strongest cell for a given N_id_2/PSS within the search
     * window. A cell with the desired SSS can be occluded by other cells with the same PSS, if their PSS is stronger and
     * within the same search window.
     */
    bool N_id_1_found = false;
    if (force_N_id_2 >= 0 && force_N_id_2 < SRSRAN_NOF_NID_2) {
      // N_id_2 (PSS) was forced, so there is only one search result to check
      if (found_cells[max_peak_cell].cell_id / SRSRAN_NOF_NID_2 == (uint32_t)force_N_id_1) {
        N_id_1_found = true;
      }
    } else {
      // Go through the results for all N_id_2 (PSS); pick strongest with matching N_id_1 (SSS)
      float max_peak_value = -1.0;
      for (uint32_t N_id_2 = 0; N_id_2 < SRSRAN_NOF_NID_2; N_id_2++) {
        if (found_cells[N_id_2].cell_id / SRSRAN_NOF_NID_2 == (uint32_t)force_N_id_1) {
          if (found_cells[N_id_2].peak > max_peak_value) {
            N_id_1_found   = true;
            max_peak_value = found_cells[N_id_2].peak;
            max_peak_cell  = N_id_2;
          }
        }
      }
    }
    if (!N_id_1_found) {
      Info("SYNC:  Could not find any cell with preselected SSS (force_N_id_1=%d)", force_N_id_1);
      return CELL_NOT_FOUND;
    }
  }

  // Save result
  new_cell.id         = found_cells[max_peak_cell].cell_id;
  new_cell.cp         = found_cells[max_peak_cell].cp;
  new_cell.frame_type = found_cells[max_peak_cell].frame_type;
  float cfo           = found_cells[max_peak_cell].cfo;

  srsran::console("\n");
  Info("SYNC:  PSS/SSS detected: Mode=%s, PCI=%d, CFO=%.1f KHz, CP=%s",
       new_cell.frame_type ? "TDD" : "FDD",
       new_cell.id,
       cfo / 1000,
       srsran_cp_string(new_cell.cp));

  if (srsran_ue_mib_sync_set_cell(&ue_mib_sync, new_cell)) {
    Error("SYNC:  Setting UE MIB cell");
    return ERROR;
  }

  // Set options defined in expert section
  p->set_ue_sync_opts(&ue_mib_sync.ue_sync, cfo);

  srsran_ue_sync_reset(&ue_mib_sync.ue_sync);

  /* Find and decode MIB */
  int sfn_offset;
  ret = srsran_ue_mib_sync_decode(&ue_mib_sync, 40, bch_payload.data(), &new_cell.nof_ports, &sfn_offset);
  if (ret == 1) {
    srsran_pbch_mib_unpack(bch_payload.data(), &new_cell, NULL);
    // pack MIB and store inplace for PCAP dump
    std::array<uint8_t, SRSRAN_BCH_PAYLOAD_LEN / 8> mib_packed;
    srsran_bit_pack_vector(bch_payload.data(), mib_packed.data(), SRSRAN_BCH_PAYLOAD_LEN);
    std::copy(std::begin(mib_packed), std::end(mib_packed), std::begin(bch_payload));

    fprintf(stdout,
            "Found Cell:  Mode=%s, PCI=%d, PRB=%d, Ports=%d, CP=%s, CFO=%.1f KHz\n",
            new_cell.frame_type ? "TDD" : "FDD",
            new_cell.id,
            new_cell.nof_prb,
            new_cell.nof_ports,
            new_cell.cp ? "Extended" : "Normal",
            cfo / 1000);

    Info("SYNC:  MIB Decoded: Mode=%s, PCI=%d, PRB=%d, Ports=%d, CFO=%.1f KHz",
         new_cell.frame_type ? "TDD" : "FDD",
         new_cell.id,
         new_cell.nof_prb,
         new_cell.nof_ports,
         cfo / 1000);

    if (!srsran_cell_isvalid(&new_cell)) {
      Error("SYNC:  Detected invalid cell.");
      return CELL_NOT_FOUND;
    }

    // Save cell pointer
    if (cell_) {
      *cell_ = new_cell;
    }

    return CELL_FOUND;
  } else if (ret == 0) {
    Warning("SYNC:  Found PSS but could not decode PBCH");
    return CELL_NOT_FOUND;
  } else {
    Error("SYNC:  Receiving MIB");
    return ERROR;
  }
}

}; // namespace srsue
