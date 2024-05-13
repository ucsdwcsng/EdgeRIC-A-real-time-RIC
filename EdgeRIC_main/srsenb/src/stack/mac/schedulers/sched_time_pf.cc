/**
 * Copyright 2013-2022 Software Radio Systems Limited
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
#include <fstream>
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
      ul_queue.push(&it->second);
    }
  }
  /*
  uint16_t min_rnti_idx = 0 ; 
  for (int i = 0; i< num_ues ; i++){
    for (int j = 0 ; j < num_ues ; j++){
      if (i==j) continue; 
      min_rnti_idx =  (temp_ue_rntis[i] <= temp_ue_rntis[j] ) ? i : j ; 
    }
    ue_rntis[i]= temp_ue_rntis[min_rnti_idx] ; 
    temp_ue_rntis[min_rnti_idx] = 60000; 
  }
  printf("\n"); 
  for (int k  = 0 ; k < num_ues ; k++)
    printf(" %d ", ue_rntis[k] ); 
  printf("\n"); 
  */
}

/*****************************************************************
 *                         Dowlink
 *****************************************************************/

int cnt =0 ;
int wgt_cnt = 0;
std::map<uint16_t, uint16_t> rbg_alloc ; 

//void sched_time_pf::sched_dl_users(sched_ue_list& ue_db, sf_sched* tti_sched)
void sched_time_pf::sched_dl_users(sched_ue_list& ue_db, sf_sched* tti_sched, std::map<uint16_t, float>& weights_recved )
{
  //printf("pf.cc weights[0]: %f weights[1]: %f    size: %d \n", weights_recved[0], weights_recved[1], (int) weights_recved.size());    
  
  uint8_t num_ues = ue_db.size();
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
  

  //srand((unsigned)time(NULL)); 
  //srand(time(0)); 
  //printf("rnad: %f \n", (float) rand()/RAND_MAX); 
  
  /*
  // varying weights for 2 ue
  //weights[0] = 0.5 + (cnt%2 *0.1); 
  //weights[1] = 1- weights[0] ; 
  //int available_rbgs = 25 ; 


  rbgs[0] = floor(weights[0]*available_rbgs) ; 
  rbgs[1] =  available_rbgs  - rbgs[0] ; 

  rbg_alloc.clear(); 
  if(ue_rntis[0] <= ue_rntis[1]){
    rbg_alloc[ue_rntis[0]] = rbgs[0] ; 
    rbg_alloc[ue_rntis[1]] = rbgs[1] ; 
  }
  else{
    rbg_alloc[ue_rntis[1]] = rbgs[0] ; 
    rbg_alloc[ue_rntis[0]] = rbgs[1] ; 
  }
  //printf("rbg_alloc: rnti: %d rbgs: %d   ,  rnti: %d rbgs: %d \n", ue_rntis[0], rbg_alloc[ue_rntis[0]], ue_rntis[1], rbg_alloc[ue_rntis[1]]); 

  */

  //2//weights[num_ues-1] = 1 ; 
  //2//rbgs[num_ues-1] = available_rbgs ; 
  
  uint8_t total_rbgs = 0;
  //2//for (int j = 0 ; j < num_ues-1 ; j++){
  for (int j = 0 ; j < num_ues ; j++){
    
    //weights[j] = 1.0/num_ues + 0.05*(cnt%2); 
    if ((int) weights_recved.size()> 0){
      weights[j] = weights_recved[ue_rntis[j]]; 
      //weights[j] = weights_recved[j]; 
    }
    else{
      //weights[j] = 1.0/num_ues ;
      weights[j] = 1.0/num_ues ;  
    }
    rbgs[j] = floor(weights[j]*available_rbgs) ; 
    rbg_alloc[ue_rntis[j]] = rbgs[j] ; 

    //2//weights[num_ues-1] = weights[num_ues-1] - weights[j] ; 
    //2//rbgs[num_ues-1] = rbgs[num_ues-1] - rbgs[j] ; 
    
    //printf("rnti: %d rbgs: %d    , ", ue_rntis[j], rbgs[j]); 
    total_rbgs = total_rbgs + rbg_alloc[ue_rntis[j]];

    // if(wgt_cnt>=1000)
    // {
    //   printf("weights[%d] = %f rbg_alloc[%d] = %d available_rbgs %d\n",j,weights[j],ue_rntis[j],rbg_alloc[ue_rntis[j]],available_rbgs);
    // }
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
  //printf("ue_ctxt.rnti: %d \n", ue_ctxt.rnti); 

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

void sched_time_pf::sched_ul_users(sched_ue_list& ue_db, sf_sched* tti_sched, uint8_t& a, uint8_t& b, std::map<uint16_t, uint32_t>& pending_data_ul)
{
  // ushasi
  uint8_t num_ues = ue_db.size();
  float* weights = new float[num_ues];
  uint16_t* rbgs = new uint16_t[num_ues];

  int c = static_cast<int>(a);
  int d = static_cast<int>(b);
  
  //a = 20;
  //b = 20;
  //int c = static_cast<size_t>(a);
  //int d = static_cast<size_t>(b);

  //sf_sched* scheduler;
  prbmask_t modified_mask = ~(tti_sched->get_ul_mask()); // Assume this is the new mask you want to set
  
  size_t bit = c;
  for (int bit = c; bit <= d; ++bit) {
    modified_mask.reset(bit);
} 

  // Step 1: Create a mask with bits 10 through 17 set to 0
  // prbmask_t clear_mask = ~(((1UL << (17 - 10 + 1)) - 1) << 10);

  // Step 2: Apply the mask using bitwise AND
  // modified_mask &= clear_mask;

  tti_sched->set_ul_mask(~modified_mask);

  // rbgmask_t current_mask = ~(tti_sched->get_ul_mask());

  //auto ul_mask = tti_sched->get_ul_mask(); // Assume this returns a bounded_bitset<100>
  prbmask_t current_mask = ~(tti_sched->get_ul_mask()); // Assume this is a bounded_bitset<25>
  /***
  // Invert and copy bits manually. Be careful with sizes to avoid out-of-bounds access.
  for (size_t i = 0; i < current_mask.size(); ++i) {
      if (i < ul_mask.size()) {
          current_mask.set(i, !ul_mask.test(i));
      } else {
          // Handle cases where current_mask is larger than the size of ul_mask
          current_mask.set(i, true); // Or false, depending on your logic
      }
  }**/
  
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

  std::ofstream log_file("ue_allocations.log", std::ios::app);
    if (log_file.is_open()) {
  log_file << "time: " << cnt_ul
          << " cnt_ul: " << cnt_ul
          << " Available PRBs: " << avail
          << " masking is between: " << c << " " << d 
          << " Current Mask: " << mask_str << '\n';
       
  log_file.close(); // Close the file after writing to it
}



  if (cnt_ul > 2000){
    //printf("\n\n"); 
    cnt_ul = 0 ;
  }
  tti_count++;
  cnt_ul++;

  //





  srsran::tti_point tti_rx{tti_sched->get_tti_rx()};
  if (current_tti_rx != tti_rx) {
    new_tti(ue_db, tti_sched);
  }

  while (not ul_queue.empty()) {
    ue_ctxt& ue = *ul_queue.top();
    pending_data_ul[ue.rnti] = pending_data_ul_local[ue.rnti];
    ue.save_ul_alloc(try_ul_alloc(ue, *ue_db[ue.rnti], tti_sched), 0.01);
    ul_queue.pop();
  }
  
//   std::ofstream log_file_2("pending_data.log", std::ios::app);
//     if (log_file_2.is_open()) {
//   log_file_2 << "time: " << tti_count
//           << " cnt_ul: " << tti_count << '\n';
//       for (const auto& pair : pending_data_ul) {
//             log_file_2 << "RNTI: " << pair.first << ", Pending Data: " << pair.second << '\n';
//         }     
       
//   log_file_2.close(); // Close the file after writing to it
// }
   
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
    //prb_interval alloc      = find_contiguous_ul_prbs(pending_rb, current_mask);
    // if (alloc.empty()) {
    //   return 0;
    // }
    // code            = tti_sched->alloc_ul_user(&ue, alloc); // should chnage this

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
       log_file << "time: " << cur_utime << " rnti: " << ue_ctxt.rnti << " alloc_mask: " << s << std::endl;
       log_file.close(); // Close the file after writing to it
      } 

      if(cnt_ul>2000){
        printf("time: %ld rnti: %d alloc_mask: %s \n",cur_utime,  ue_ctxt.rnti,  s.c_str()); 
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
