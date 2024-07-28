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

#ifndef SRSRAN_ENB_RRC_INTERFACE_MAC_H
#define SRSRAN_ENB_RRC_INTERFACE_MAC_H

#include "srsenb/hdr/stack/mac/sched_interface.h"

namespace srsenb {

/// RRC interface for MAC
class rrc_interface_mac
{
public:
  /* Radio Link failure */
  virtual int  add_user(uint16_t rnti, const sched_interface::ue_cfg_t& init_ue_cfg)      = 0;
  virtual void upd_user(uint16_t new_rnti, uint16_t old_rnti)                             = 0;
  virtual void set_activity_user(uint16_t rnti)                                           = 0;
  virtual void set_radiolink_dl_state(uint16_t rnti, bool crc_res)                        = 0;
  virtual void set_radiolink_ul_state(uint16_t rnti, bool crc_res)                        = 0;
  virtual bool is_paging_opportunity(uint32_t tti_tx_dl, uint32_t* payload_len)           = 0;
  virtual void read_pdu_pcch(uint32_t tti_tx_dl, uint8_t* payload, uint32_t payload_size) = 0;

  ///< Provide packed SIB to MAC (buffer is managed by RRC)
  virtual uint8_t* read_pdu_bcch_dlsch(const uint8_t enb_cc_idx, const uint32_t sib_index) = 0;
};

} // namespace srsenb

#endif // SRSRAN_ENB_RRC_INTERFACE_MAC_H
