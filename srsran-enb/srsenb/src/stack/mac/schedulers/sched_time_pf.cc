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

#include "srsenb/hdr/stack/mac/schedulers/sched_time_pf.h"
#include "srsenb/hdr/stack/mac/sched_grid.h"
#include <vector>
#include <sys/time.h>
#include "zmq.hpp"
#include <fstream>
#include <sstream>

#include "srsenb/rtagent/edgeric.h"

#include <iostream>
#include <fstream>  // For file I/O
#include <string> 
#include <map>  // For std::to_string

// zmq::context_t context(1); 
// zmq::socket_t subscriber(context, ZMQ_SUB);
// zmq::socket_t subscriber2(context, ZMQ_SUB);
// zmq::socket_t publisher(context, ZMQ_PUB); // Add a publisher socket

// Declare global variables
int c = 0; // default value for c
int d = 0; // default value for d
std::map<uint16_t, uint32_t> pending_data_ul_local; 

namespace srsenb {

using srsran::tti_point;

uint16_t* ue_rntis = new uint16_t[10];

sched_time_pf::sched_time_pf(const sched_cell_params_t& cell_params_, const sched_interface::sched_args_t& sched_args)

{
  cc_cfg = &cell_params_;
  if (not sched_args.sched_policy_args.empty()) {
    fairness_coeff = std::stof(sched_args.sched_policy_args);
  }

  std::vector<ue_ctxt*> dl_storage;
  dl_storage.reserve(SRSENB_MAX_UES);
  dl_queue = ue_dl_queue_t(ue_dl_prio_compare{}, std::move(dl_storage));

  std::vector<ue_ctxt*> ul_storage;
  ul_storage.reserve(SRSENB_MAX_UES);
  ul_queue = ue_ul_queue_t(ue_ul_prio_compare{}, std::move(ul_storage));
  
  // // Connect ZMQ subscriber and subscribe to messages
  // subscriber.connect("ipc:///tmp/socket_blanking"); // Change this to your ZMQ server address
  // subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);

  // // Set the socket to conflate mode
  // int conflate = 1;
  // subscriber.setsockopt(ZMQ_CONFLATE, &conflate, sizeof(conflate));

  // // Connect ZMQ subscriber and subscribe to messages
  // subscriber2.connect("ipc:///tmp/socket_dlscheduling"); // Change this to your ZMQ server address
  // subscriber2.setsockopt(ZMQ_SUBSCRIBE, "", 0);

  // // Set the socket to conflate mode
  // int conflate2 = 1;
  // subscriber2.setsockopt(ZMQ_CONFLATE, &conflate2, sizeof(conflate2));


  // // Connect the publisher to an IPC address
  // publisher.bind("ipc:///tmp/socket_ul_pending_data"); // Bind publisher to an IPC address


  // //subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
  
}



void sched_time_pf::new_tti(sched_ue_list& ue_db, sf_sched* tti_sched)
{
  while (not dl_queue.empty()) {
    dl_queue.pop();
  }
  while (not ul_queue.empty()) {
    ul_queue.pop();
  }
  current_tti_rx = tti_point{tti_sched->get_tti_rx()};
  // remove deleted users from history
  for (auto it = ue_history_db.begin(); it != ue_history_db.end();) {
    if (not ue_db.contains(it->first)) {
      it = ue_history_db.erase(it);
    } else {
      ++it;
    }
  }
  // add new users to history db, and update priority queues
  
  uint16_t idx = 0; 
  uint16_t* temp_ue_rntis = new uint16_t[ue_db.size()];

  for (auto& u : ue_db) {
    auto it = ue_history_db.find(u.first);
    if (it == ue_history_db.end()) {
      it = ue_history_db.insert(u.first, ue_ctxt{u.first, fairness_coeff}).value();
    }
    it->second.new_tti(*cc_cfg, *u.second, tti_sched);
    if (it->second.dl_newtx_h != nullptr or it->second.dl_retx_h != nullptr) {
      dl_queue.push(&it->second);

      // added by whko 08082022
      if (idx < ue_db.size()){
        ue_rntis[idx]= it->second.rnti; 
        temp_ue_rntis[idx]= it->second.rnti; 
        idx++ ; 
      }
      ///
    }
    if (it->second.ul_h != nullptr) {
      // Allocate only if UL carrier is enabled
      for (auto& i : u.second->get_ue_cfg().supported_cc_list) {
        if (i.enb_cc_idx == cc_cfg->enb_cc_idx and not i.ul_disabled) {
          ul_queue.push(&it->second);
          break;
        }
      }
    }
  }
}

/*****************************************************************
 *                         Dowlink
 *****************************************************************/

int cnt =0 ;
int wgt_cnt = 0;
std::map<uint16_t, uint16_t> rbg_alloc ; 
void sched_time_pf::sched_dl_users(sched_ue_list& ue_db, sf_sched* tti_sched)

{ uint8_t num_ues = ue_db.size();
  float* weights = new float[num_ues];  
  uint16_t* rbgs = new uint16_t[num_ues]; 

  rbgmask_t current_mask = ~(tti_sched->get_dl_mask());
  uint8_t available_rbgs = 0;
    wgt_cnt++;
  for (size_t i = 0; i < current_mask.size(); i++)
  {
    if(current_mask.test(i))
    {
      available_rbgs++;
    }
  }
  
  uint8_t total_rbgs = 0;
  // Declare and initialize weights_recved with equal weights
  // Get weights from edgeric
  std::map<uint16_t, float> weights_recved;
  weights_recved = edgeric::get_weights();

  if(weights_recved.empty()){
    for (int j = 0 ; j < num_ues ; j++){
      // struct timeval ctime;
      // gettimeofday(&ctime, NULL);
      // long seconds = ctime.tv_sec;
      // long useconds = ctime.tv_usec;
      // double time_in_seconds = seconds + useconds / 1000000.0;
      weights_recved[ue_rntis[j]] = 1.0/num_ues;
    //   std::ofstream log_file("ue_allocations.log", std::ios::app);
    //   if (log_file.is_open()) {
    //   log_file << "time: " << std::fixed << std::setprecision(5) << time_in_seconds << "s" << " "
    //             << "RNTI" << ue_rntis[j] << " Default Weight " << weights_recved[ue_rntis[j]] << '\n';
          
    //   log_file.close(); // Close the file after writing to it
    // }
      
    }
    //printf("Parsed weights when not received:\n");
    int j = 0;
    for (const auto& pair : weights_recved) {
        //printf("weights_recved[%u] = %.4f\n", pair.first, pair.second);
        weights[j] = pair.second;
        j = j+1;
    }
  } else {
    int j = 0;
    //printf("Parsed weights when received:\n");
    for (const auto& pair : weights_recved) {
        //printf("weights_recved[%u] = %.4f\n", pair.first, pair.second);
        weights[j] = pair.second;
        j = j+1;
    }
  }

  for (int j = 0 ; j < num_ues ; j++){ 
    //weights[j] = weights_recved[ue_rntis[j]]; 
      
    rbgs[j] = floor(weights[j]*available_rbgs) ; 
    rbg_alloc[ue_rntis[j]] = rbgs[j] ; 
      std::ofstream log_file("ue_allocations.log", std::ios::app);
    
    //printf("Weight for %u is %f and %f\n", ue_rntis[j], weights[j], weights_recved[ue_rntis[j]]);
 
    total_rbgs = total_rbgs + rbg_alloc[ue_rntis[j]];
  }

    
  uint8_t remain_rbgs = available_rbgs - total_rbgs;
  for (int j=0 ; j < remain_rbgs ; j++)
    rbg_alloc[ue_rntis[j]]++;

  if(wgt_cnt>=1000)
  {
    // printf("\n");
    wgt_cnt = 0;
  }
  // allocate the last ue
  ///2//rbg_alloc[ue_rntis[num_ues-1]] = rbgs[num_ues-1] ;  
  
  //printf("rnti: %d rbgs: %d    , ", ue_rntis[num_ues-1], rbg_alloc[ue_rntis[num_ues-1]] ); 
  //printf("\n"); 

  srsran::tti_point tti_rx{tti_sched->get_tti_rx()};
  if (current_tti_rx != tti_rx) {
    new_tti(ue_db, tti_sched);
  }

  while (not dl_queue.empty()) {
    ue_ctxt& ue = *dl_queue.top();
    ue.save_dl_alloc(try_dl_alloc(ue, *ue_db[ue.rnti], tti_sched), 0.01);
    dl_queue.pop();
  }

   if (cnt > 2000){
    //printf("\n\n"); 
    cnt = 0 ;
  }
  
  cnt++ ; 
}

uint32_t sched_time_pf::try_dl_alloc(ue_ctxt& ue_ctxt, sched_ue& ue, sf_sched* tti_sched)
{
  alloc_result code = alloc_result::other_cause;
  if (ue_ctxt.dl_retx_h != nullptr) {
    code = try_dl_retx_alloc(*tti_sched, ue, *ue_ctxt.dl_retx_h);
    if (code == alloc_result::success) {
      return ue_ctxt.dl_retx_h->get_tbs(0) + ue_ctxt.dl_retx_h->get_tbs(1);
    }
  }

  // There is space in PDCCH and an available DL HARQ
  if (code != alloc_result::no_cch_space and ue_ctxt.dl_newtx_h != nullptr) {
    rbgmask_t alloc_mask;
    //code = try_dl_newtx_alloc_greedy(*tti_sched, ue, *ue_ctxt.dl_newtx_h, &alloc_mask);
    code = try_dl_newtx_alloc_greedy(*tti_sched, ue, *ue_ctxt.dl_newtx_h, &alloc_mask, rbg_alloc[ue_ctxt.rnti]);

    //if (cnt > 1000){
    if (cnt >= 0){
      std::string s;
      for (size_t i = 0; i < alloc_mask.size(); i++) {
        s.append(alloc_mask.test(i) ? "1" : "0");
      }

      struct timeval ctime ; 
      gettimeofday(&ctime, NULL);
      long cur_utime = ctime.tv_sec*1000000+ctime.tv_usec;
      if(cnt>2000){
        printf("time: %ld rnti: %d alloc_mask: %s \n",cur_utime,  ue_ctxt.rnti,  s.c_str()); 
      }       
    }

    if (code == alloc_result::success) {
      return ue.get_expected_dl_bitrate(cc_cfg->enb_cc_idx, alloc_mask.count()) * tti_duration_ms / 8;
    }
  }
  return 0;
}

/*****************************************************************
 *                         Uplink
 *****************************************************************/
int cnt_ul =0 ;
int wgt_cnt_ul = 0;
int tti_count = 0;

std::map<uint16_t, uint16_t> rbg_alloc_ul ;
void sched_time_pf::sched_ul_users(sched_ue_list& ue_db, sf_sched* tti_sched)
{

  // ushasi
  uint8_t num_ues = ue_db.size();
  float* weights = new float[num_ues];
  uint16_t* rbgs = new uint16_t[num_ues];
  // pending_data_ul_local.clear();

  // Publish UL pending data
  std::ostringstream oss;
  for (const auto& ue : ue_db) {
      uint16_t rnti = ue.first;
      uint32_t pending_data = ue.second->get_pending_ul_new_data(tti_sched->get_tti_tx_ul(), cc_cfg->enb_cc_idx);
      pending_data_ul_local[rnti] = pending_data;
  }
  edgeric::setPendingDataUe(pending_data_ul_local);

  std::tie(c, d) = edgeric::get_blanking();


  prbmask_t modified_mask = ~(tti_sched->get_ul_mask()); // Assume this is the new mask you want to set
  
  size_t bit = c;
  for (int bit = c; bit <= d; ++bit) {
    modified_mask.reset(bit);
  }
  
  tti_sched->set_ul_mask(~modified_mask);
  prbmask_t current_mask = ~(tti_sched->get_ul_mask());

  uint8_t available_rbgs = 0;
  int avail = 0;
  wgt_cnt_ul++;
  std::string mask_str;
  for (size_t i = 0; i < current_mask.size(); i++)
  {
    if(current_mask.test(i))
    {
      available_rbgs++;
      avail = avail + 1;
      mask_str.append("1");
    }
    else
    {
      mask_str.append("0");
    }
  }

  if (cnt_ul > 2000){
    //printf("\n\n"); 
    cnt_ul = 0 ;
  }
  tti_count++;
  cnt_ul++;

  //

//   std::ofstream log_file("ue_allocations.log", std::ios::app);
//     if (log_file.is_open()) {
//   log_file << "time: " << cnt_ul
//           << " cnt_ul: " << cnt_ul
//           << " Available PRBs: " << avail
//           << " masking is between: " << c << " " << d 
//           << " Current Mask: " << mask_str << '\n';
       
//   log_file.close(); // Close the file after writing to it
// }

  srsran::tti_point tti_rx{tti_sched->get_tti_rx()};
  if (current_tti_rx != tti_rx) {
    new_tti(ue_db, tti_sched);
  }

  while (not ul_queue.empty()) {
    ue_ctxt& ue = *ul_queue.top();
    ue.save_ul_alloc(try_ul_alloc(ue, *ue_db[ue.rnti], tti_sched), 0.01);
    ul_queue.pop();
  }
}

uint32_t sched_time_pf::try_ul_alloc(ue_ctxt& ue_ctxt, sched_ue& ue, sf_sched* tti_sched)
{
  if (ue_ctxt.ul_h == nullptr) {
    // In case the UL HARQ could not be allocated (e.g. meas gap occurrence)
    return 0;
  }
  if (tti_sched->is_ul_alloc(ue_ctxt.rnti)) {
    // NOTE: An UL grant could have been previously allocated for UCI
    return ue_ctxt.ul_h->get_pending_data();
  }

  alloc_result code;
  uint32_t     estim_tbs_bytes = 0;
  if (ue_ctxt.ul_h->has_pending_retx()) {
    code            = try_ul_retx_alloc(*tti_sched, ue, *ue_ctxt.ul_h);
    estim_tbs_bytes = code == alloc_result::success ? ue_ctxt.ul_h->get_pending_data() : 0;
  } else {
    // Note: h->is_empty check is required, in case CA allocated a small UL grant for UCI
    uint32_t pending_data = ue.get_pending_ul_new_data(tti_sched->get_tti_tx_ul(), cc_cfg->enb_cc_idx);
    // Check if there is a empty harq, and data to transmit
    uint16_t rnti = ue_ctxt.rnti;
    pending_data_ul_local[rnti] = pending_data;

    if (pending_data == 0) {
      return 0;
    }
    std::string mask_str;
    uint8_t available_rbgs = 0;
    int avail = 0;

    uint32_t     pending_rb = ue.get_required_prb_ul(cc_cfg->enb_cc_idx, pending_data);
    // usahsi
    //uint32_t pending_rb = 10;
    prbmask_t current_mask = ~(tti_sched->get_ul_mask()); 
    for (size_t i = 0; i < current_mask.size(); i++)
    {
      if(current_mask.test(i))
      {
        available_rbgs++;
        avail = avail + 1;
        mask_str.append("1");
      }
      else
      {
        mask_str.append("0");
      }
    }

    prb_interval alloc      = find_contiguous_ul_prbs(pending_rb, tti_sched->get_ul_mask());
    // Ushasi 
    if (cnt_ul >= 0) {
      std::string s;
      // Calculate the size of the interval. Assuming stop is exclusive, add 1 to include the start in the count.
      size_t size = alloc.stop() - alloc.start();
      for (size_t i = 0; i < size; i++) {
        // As prb_interval doesn't directly support 'test', we assume all positions within start and stop are '1'.
        s.append("1");
      }
      // Use s as needed...

      struct timeval ctime ; 
      gettimeofday(&ctime, NULL);
      long cur_utime = ctime.tv_sec*1000000+ctime.tv_usec;

      // Open a file in append mode to add the new entries
      std::ofstream log_file("per_ue_allocations.log", std::ios::app);
      if (log_file.is_open()) {
      log_file << "time: " << cur_utime 
              << " cnt_ul: " << cnt_ul
              << " rnti: " << ue_ctxt.rnti 
              << " pending_data: " << pending_data 
              << " pending_rb: " << pending_rb 
              << "available mask: " << mask_str
              << " alloc_mask: " << s << std::endl;
      log_file.close(); // Close the file after writing to it
    }
      if (log_file.is_open()) {
       log_file << "time: " << cur_utime << " rnti: " << ue_ctxt.rnti << " UL alloc_mask: " << s << std::endl;
       log_file.close(); // Close the file after writing to it
      } 

      if(cnt_ul>2000){
        printf("time: %ld rnti: %d UL alloc_mask: %s \n",cur_utime,  ue_ctxt.rnti,  s.c_str()); 
      }       
    }
    //
    if (alloc.empty()) {
      return 0;
    }
    code            = tti_sched->alloc_ul_user(&ue, alloc);
    estim_tbs_bytes = code == alloc_result::success
                          ? ue.get_expected_ul_bitrate(cc_cfg->enb_cc_idx, alloc.length()) * tti_duration_ms / 8
                          : 0;
  }
  return estim_tbs_bytes;
}

/*****************************************************************
 *                          UE history
 *****************************************************************/

void sched_time_pf::ue_ctxt::new_tti(const sched_cell_params_t& cell, sched_ue& ue, sf_sched* tti_sched)
{
  dl_retx_h  = nullptr;
  dl_newtx_h = nullptr;
  ul_h       = nullptr;
  dl_prio    = 0;
  ue_cc_idx  = ue.enb_to_ue_cc_idx(cell.enb_cc_idx);
  if (ue_cc_idx < 0) {
    // not active
    return;
  }

  // Calculate DL priority
  dl_retx_h  = get_dl_retx_harq(ue, tti_sched);
  dl_newtx_h = get_dl_newtx_harq(ue, tti_sched);
  if (dl_retx_h != nullptr or dl_newtx_h != nullptr) {
    // calculate DL PF priority
    float r = ue.get_expected_dl_bitrate(cell.enb_cc_idx) / 8;
    float R = dl_avg_rate();
    dl_prio = (R != 0) ? r / pow(R, fairness_coeff) : (r == 0 ? 0 : std::numeric_limits<float>::max());
  }

  // Calculate UL priority
  ul_h = get_ul_retx_harq(ue, tti_sched);
  if (ul_h == nullptr) {
    ul_h = get_ul_newtx_harq(ue, tti_sched);
  }
  if (ul_h != nullptr) {
    float r = ue.get_expected_ul_bitrate(cell.enb_cc_idx) / 8;
    float R = ul_avg_rate();
    ul_prio = (R != 0) ? r / pow(R, fairness_coeff) : (r == 0 ? 0 : std::numeric_limits<float>::max());
  }
}

void sched_time_pf::ue_ctxt::save_dl_alloc(uint32_t alloc_bytes, float exp_avg_alpha)
{
  if (dl_nof_samples < 1 / exp_avg_alpha) {
    // fast start
    dl_avg_rate_ = dl_avg_rate_ + (alloc_bytes - dl_avg_rate_) / (dl_nof_samples + 1);
  } else {
    dl_avg_rate_ = (1 - exp_avg_alpha) * dl_avg_rate_ + (exp_avg_alpha)*alloc_bytes;
  }
  dl_nof_samples++;
}

void sched_time_pf::ue_ctxt::save_ul_alloc(uint32_t alloc_bytes, float exp_avg_alpha)
{
  if (ul_nof_samples < 1 / exp_avg_alpha) {
    // fast start
    ul_avg_rate_ = ul_avg_rate_ + (alloc_bytes - ul_avg_rate_) / (ul_nof_samples + 1);
  } else {
    ul_avg_rate_ = (1 - exp_avg_alpha) * ul_avg_rate_ + (exp_avg_alpha)*alloc_bytes;
  }
  ul_nof_samples++;
}

bool sched_time_pf::ue_dl_prio_compare::operator()(const sched_time_pf::ue_ctxt* lhs,
                                                   const sched_time_pf::ue_ctxt* rhs) const
{
  bool is_retx1 = lhs->dl_retx_h != nullptr, is_retx2 = rhs->dl_retx_h != nullptr;
  return (not is_retx1 and is_retx2) or (is_retx1 == is_retx2 and lhs->dl_prio < rhs->dl_prio);
}

bool sched_time_pf::ue_ul_prio_compare::operator()(const sched_time_pf::ue_ctxt* lhs,
                                                   const sched_time_pf::ue_ctxt* rhs) const
{
  bool is_retx1 = lhs->ul_h->has_pending_retx(), is_retx2 = rhs->ul_h->has_pending_retx();
  return (not is_retx1 and is_retx2) or (is_retx1 == is_retx2 and lhs->ul_prio < rhs->ul_prio);
}

} // namespace srsenb
