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


#include <pthread.h>
#include <string.h>

#include "srsenb/hdr/stack/mac/mac.h"
#include "srsran/adt/pool/obj_pool.h"
#include "srsran/common/rwlock_guard.h"
#include "srsran/common/standard_streams.h"
#include "srsran/common/time_prof.h"
#include "srsran/interfaces/enb_phy_interfaces.h"
#include "srsran/interfaces/enb_rlc_interfaces.h"
#include "srsran/interfaces/enb_rrc_interface_mac.h"
#include "srsran/srslog/event_trace.h"


#include <sys/time.h>
#include "zmq.hpp"
#include <fstream>

// #define zmq_rtt_eval


// #define WRITE_SIB_PCAP
using namespace asn1::rrc;

zmq::context_t context(1); 
zmq::socket_t publisher(context, ZMQ_PUB) ; 
zmq::socket_t subscriber(context, ZMQ_SUB);



struct timeval __time ; 

long __utime, __seconds, __useconds;
long __utime_init ; 
int zmq_count = 0;

std::ofstream outfile ;
std::ofstream outfile_seq ;
bool __outfile_flag = false ;
bool __outfile_seq_flag = false ; 
std::string __outfile_buf; 
std::string __outfile_seq_buf; 
long __fileout_period  = 120000000; 

namespace srsenb {

mac::mac(srsran::ext_task_sched_handle task_sched_, srslog::basic_logger& logger) :
  logger(logger), rar_payload(), common_buffers(SRSRAN_MAX_CARRIERS), task_sched(task_sched_)
{
  pthread_rwlock_init(&rwlock, nullptr);
  stack_task_queue = task_sched.make_task_queue();
}

mac::~mac()
{
  stop();
  pthread_rwlock_destroy(&rwlock);
}
FILE *fp,*fp1;
uint8_t num_ues = 2;
// Algo 1: Max Throughput
// Algo 2: Max Weight
// Algo 3: PF
// Algo 4: RL
uint8_t algoflag = 2;
// scenario 1: No delay no CQI evolution same load
// scenario 2: No delay no CQI evolution different load
// scenario 3: No delay CQI evolution same load
// scenario 4: No delay CQI evolution different load
// scenario 5: State/Action delay no CQI evolution same load
// scenario 6: State/Action delay no CQI evolution different load
// scenario 7: State/Action delay CQI evolution same load
// scenario 8: State/Action delay CQI evolution different load
uint8_t scenarioflag = 3;
float load = 7.5;
uint8_t cqi_change_period = 100;
uint8_t cqi_step_size = 4;
uint8_t cqi_range_size = 2;
bool cqi_change_flag = 0;
uint8_t delay = 100;
bool firstwrite = 0;
bool bufsaveflag = 0;

bool mac::init(const mac_args_t&        args_,
               const cell_list_t&       cells_,
               phy_interface_stack_lte* phy,
               rlc_interface_mac*       rlc,
               rrc_interface_mac*       rrc)
{

  struct timeval ctime ; 
   gettimeofday(&ctime, NULL); 
  
  long seconds = ctime.tv_sec ; 
  long useconds = ctime.tv_usec; 
  __utime_init = (1000000*seconds + useconds);   

  
  
  
  char algo[10];
  switch(algoflag)
  {
    case 1: strncpy(algo,"max_tpt",sizeof(algo)); break;
    case 2: strncpy(algo,"max_wgt",sizeof(algo)); break;
    case 3: strncpy(algo,"pf",sizeof(algo)); break;
    case 4: strncpy(algo,"rl",sizeof(algo)); break;
    default: strncpy(algo,"max_tpt",sizeof(algo));
  }
  char scenario[15];
  switch(scenarioflag)
  {
    case 1: strncpy(scenario,"nd_nc_sl",sizeof(scenario)); break;
    case 2: strncpy(scenario,"nd_nc_dl",sizeof(scenario)); break;
    case 3: strncpy(scenario,"nd_wc_sl",sizeof(scenario)); break;
    case 4: strncpy(scenario,"nd_wc_dl",sizeof(scenario)); break;
    case 5: sprintf(scenario,"wd%d_nc_sl",delay); break;
    case 6: sprintf(scenario,"wd%d_nc_dl",delay); break;
    case 7: sprintf(scenario,"wd%d_wc_sl",delay); break;
    case 8: sprintf(scenario,"wd%d_wc_dl",delay); break;
    default: strncpy(scenario,"nd_nc_sl",sizeof(scenario));
  }
  // char filename[120];
  // sprintf(filename,"/home/santosh/Harish/MobiCom_Results/%dUEs/%s/SL_%0.1fM_CQI_CHANGE_1IN%d_STEP%d/bb_%s.txt",num_ues,algo,load,cqi_change_period,cqi_step_size,scenario);
  // fp = fopen(filename,"w+");
  // printf("Backlog Buffer saving file %s is opened %p\n",filename,fp);

  // char filename1[120];
  // sprintf(filename1,"/home/santosh/Harish/MobiCom_Results/%dUEs/%s/SL_%0.1fM_CQI_CHANGE_1IN%d_STEP%d/tpt_%s.txt",num_ues,algo,load,cqi_change_period,cqi_step_size,scenario);
  // fp1 = fopen(filename1,"w+");
  // printf("Throughput saving file %s is opened %p\n",filename1,fp1);

  char filename[440];
  if(cqi_change_flag)
    sprintf(filename,"/home/wcsng-24/Ushasi/EdgeRIC_main/MobiCom_Results/%dUEs/%s/CQI_CHANGE/SL_%0.1fM_CQI_CHANGE_1IN%d_RSTEP%d/bb_%s.txt",num_ues,algo,load,cqi_change_period,cqi_range_size,scenario);
  else
    sprintf(filename,"/home/wcsng-24/Ushasi/EdgeRIC_main/MobiCom_Results/%dUEs/%s/NO_CQI_CHANGE/SL_%0.1fM_NO_CQI_CHANGE/bb_%s.txt",num_ues,algo,load,scenario);
  fp = fopen(filename,"w+");
  printf("Backlog Buffer saving file %s is opened %p\n",filename,fp);

  char filename1[440];
  if(cqi_change_flag)
    sprintf(filename1,"/home/wcsng-24/Ushasi/EdgeRIC_main/MobiCom_Results/%dUEs/%s/CQI_CHANGE/SL_%0.1fM_CQI_CHANGE_1IN%d_RSTEP%d/tpt_%s.txt",num_ues,algo,load,cqi_change_period,cqi_range_size,scenario);
  else
    sprintf(filename1,"/home/wcsng-24/Ushasi/EdgeRIC_main/MobiCom_Results/%dUEs/%s/NO_CQI_CHANGE/SL_%0.1fM_NO_CQI_CHANGE/tpt_%s.txt",num_ues,algo,load,scenario);
  fp1 = fopen(filename1,"w+");
  printf("Throughput saving file %s is opened %p\n",filename1,fp1);

  /// ipc
  publisher.bind("ipc:///tmp/socket_metrics"); 
  subscriber.connect("ipc:///tmp/socket_weights");
  
  //subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
  //subscriber.setsockopt(zmq::sockopt::subscribe, "");


  outfile.open("out_mac.txt"); 
  outfile_seq.open("out_mac_seq.txt"); 

  /////////
  
  

  started = false;
  phy_h   = phy;
  rlc_h   = rlc;
  rrc_h   = rrc;

  args  = args_;
  cells = cells_;

  scheduler.init(rrc, args.sched);

  // Init softbuffer for SI messages
  common_buffers.resize(cells.size());
  for (auto& cc : common_buffers) {
    for (int i = 0; i < NOF_BCCH_DLSCH_MSG; i++) {
      srsran_softbuffer_tx_init(&cc.bcch_softbuffer_tx[i], args.nof_prb);
    }
    // Init softbuffer for PCCH
    srsran_softbuffer_tx_init(&cc.pcch_softbuffer_tx, args.nof_prb);

    // Init softbuffer for RAR
    srsran_softbuffer_tx_init(&cc.rar_softbuffer_tx, args.nof_prb);
  }

  // Initiate common pool of softbuffers
  uint32_t nof_prb          = args.nof_prb;
  auto     init_softbuffers = [nof_prb](void* ptr) {
    new (ptr) ue_cc_softbuffers(nof_prb, SRSRAN_FDD_NOF_HARQ, SRSRAN_FDD_NOF_HARQ);
  };
  auto recycle_softbuffers = [](ue_cc_softbuffers& softbuffers) { softbuffers.clear(); };
  softbuffer_pool.reset(new srsran::background_obj_pool<ue_cc_softbuffers>(
      8, 8, args.nof_prealloc_ues, init_softbuffers, recycle_softbuffers));

  detected_rachs.resize(cells.size());

  started = true;
  return true;
}

void mac::stop()
{
  srsran::rwlock_write_guard lock(rwlock);
  if (started) {
    started = false;

    ue_db.clear();
    for (auto& cc : common_buffers) {
      for (int i = 0; i < NOF_BCCH_DLSCH_MSG; i++) {
        srsran_softbuffer_tx_free(&cc.bcch_softbuffer_tx[i]);
      }
      srsran_softbuffer_tx_free(&cc.pcch_softbuffer_tx);
      srsran_softbuffer_tx_free(&cc.rar_softbuffer_tx);
    }
  }
}

void mac::start_pcap(srsran::mac_pcap* pcap_)
{
  srsran::rwlock_read_guard lock(rwlock);
  pcap = pcap_;
  // Set pcap in all UEs for UL messages
  for (auto& u : ue_db) {
    u.second->start_pcap(pcap);
  }
}

void mac::start_pcap_net(srsran::mac_pcap_net* pcap_net_)
{
  srsran::rwlock_read_guard lock(rwlock);
  pcap_net = pcap_net_;
  // Set pcap in all UEs for UL messages
  for (auto& u : ue_db) {
    u.second->start_pcap_net(pcap_net);
  }
}

/********************************************************
 *
 * RLC interface
 *
 *******************************************************/

std::map<uint16_t, uint32_t> backlogBuffer; 

int mac::rlc_buffer_state(uint16_t rnti, uint32_t lc_id, uint32_t tx_queue, uint32_t retx_queue)
{
  srsran::rwlock_read_guard lock(rwlock);
  int                       ret = -1;
  if (check_ue_active(rnti)) {
    if (rnti != SRSRAN_MRNTI) {
      ret = scheduler.dl_rlc_buffer_state(rnti, lc_id, tx_queue, retx_queue);
      // whko 08122022
      backlogBuffer[rnti] = tx_queue + retx_queue ;
      // fprintf(fp,"%d\t%d\n",rnti,backlogBuffer[rnti]);
      bufsaveflag = 1;
    } else {
      for (uint32_t i = 0; i < mch.num_mtch_sched; i++) {
        if (lc_id == mch.mtch_sched[i].lcid) {
          mch.mtch_sched[i].lcid_buffer_size = tx_queue;
        }
      }
      ret = 0;
    }
  }
  return ret;
}

int mac::bearer_ue_cfg(uint16_t rnti, uint32_t lc_id, mac_lc_ch_cfg_t* cfg)
{
  srsran::rwlock_read_guard lock(rwlock);
  return check_ue_active(rnti) ? scheduler.bearer_ue_cfg(rnti, lc_id, *cfg) : -1;
}

int mac::bearer_ue_rem(uint16_t rnti, uint32_t lc_id)
{
  srsran::rwlock_read_guard lock(rwlock);
  return check_ue_active(rnti) ? scheduler.bearer_ue_rem(rnti, lc_id) : -1;
}

void mac::phy_config_enabled(uint16_t rnti, bool enabled)
{
  scheduler.phy_config_enabled(rnti, enabled);
}

// Update UE configuration
int mac::ue_cfg(uint16_t rnti, const sched_interface::ue_cfg_t* cfg)
{
  srsran::rwlock_read_guard lock(rwlock);
  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }
  ue* ue_ptr = ue_db[rnti].get();

  // Start TA FSM in UE entity
  ue_ptr->start_ta();

  // Update Scheduler configuration
  if (cfg) {
    if (scheduler.ue_cfg(rnti, *cfg) == SRSRAN_ERROR) {
      logger.error("Registering UE rnti=0x%x to SCHED", rnti);
      return SRSRAN_ERROR;
    }
    ue_ptr->ue_cfg(*cfg);
  }

  return SRSRAN_SUCCESS;
}

// Removes UE from DB
int mac::ue_rem(uint16_t rnti)
{
  // Remove UE from the perspective of L2/L3
  {
    srsran::rwlock_read_guard lock(rwlock);
    if (check_ue_active(rnti)) {
      ue_db[rnti]->set_active(false);
    } else {
      logger.error("User rnti=0x%x not found", rnti);
      return SRSRAN_ERROR;
    }
  }
  scheduler.ue_rem(rnti);

  // Remove UE from the perspective of L1
  // Note: Let any pending retx ACK to arrive, so that PHY recognizes rnti
  task_sched.defer_callback(FDD_HARQ_DELAY_DL_MS + FDD_HARQ_DELAY_UL_MS, [this, rnti]() {
    phy_h->rem_rnti(rnti);
    srsran::rwlock_write_guard lock(rwlock);
    ue_db.erase(rnti);
    logger.info("User rnti=0x%x removed from MAC/PHY", rnti);
  });
  return SRSRAN_SUCCESS;
}

// Called after Msg3
int mac::ue_set_crnti(uint16_t temp_crnti, uint16_t crnti, const sched_interface::ue_cfg_t& cfg)
{
  srsran::rwlock_read_guard lock(rwlock);
  if (temp_crnti == crnti) {
    // Schedule ConRes Msg4
    scheduler.dl_mac_buffer_state(crnti, (uint32_t)srsran::dl_sch_lcid::CON_RES_ID);
  }
  return ue_cfg(crnti, &cfg);
}

int mac::cell_cfg(const std::vector<sched_interface::cell_cfg_t>& cell_cfg_)
{
  srsran::rwlock_write_guard lock(rwlock);
  cell_config = cell_cfg_;
  return scheduler.cell_cfg(cell_config);
}

void mac::get_metrics(mac_metrics_t& metrics)
{
  srsran::rwlock_read_guard lock(rwlock);
  metrics.ues.reserve(ue_db.size());
  for (auto& u : ue_db) {
    if (not scheduler.ue_exists(u.first)) {
      continue;
    }
    metrics.ues.emplace_back();
    auto& ue_metrics = metrics.ues.back();

    u.second->metrics_read(&ue_metrics);
    scheduler.metrics_read(u.first, ue_metrics);
    ue_metrics.pci = (ue_metrics.cc_idx < cell_config.size()) ? cell_config[ue_metrics.cc_idx].cell.id : 0;
  }
  metrics.cc_info.resize(detected_rachs.size());
  for (unsigned cc = 0, e = detected_rachs.size(); cc != e; ++cc) {
    metrics.cc_info[cc].cc_rach_counter = detected_rachs[cc];
    metrics.cc_info[cc].pci             = (cc < cell_config.size()) ? cell_config[cc].cell.id : 0;
  }
}

void mac::toggle_padding()
{
  do_padding = !do_padding;
}

void mac::add_padding()
{
  srsran::rwlock_read_guard lock(rwlock);
  for (auto it = ue_db.begin(); it != ue_db.end(); ++it) {
    uint16_t cur_rnti = it->first;
    auto     ue       = it;
    scheduler.dl_rlc_buffer_state(ue->first, args.lcid_padding, 20e6, 0);
    ue->second->trigger_padding(args.lcid_padding);
  }
}

/********************************************************
 *
 * PHY interface
 *
 *******************************************************/

int mac::ack_info(uint32_t tti_rx, uint16_t rnti, uint32_t enb_cc_idx, uint32_t tb_idx, bool ack)
{
  logger.set_context(tti_rx);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  int nof_bytes = scheduler.dl_ack_info(tti_rx, rnti, enb_cc_idx, tb_idx, ack);
  ue_db[rnti]->metrics_tx(ack, nof_bytes);

  rrc_h->set_radiolink_dl_state(rnti, ack);

  return SRSRAN_SUCCESS;
}

int mac::crc_info(uint32_t tti_rx, uint16_t rnti, uint32_t enb_cc_idx, uint32_t nof_bytes, bool crc)
{
  logger.set_context(tti_rx);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  ue_db[rnti]->set_tti(tti_rx);
  ue_db[rnti]->metrics_rx(crc, nof_bytes);

  rrc_h->set_radiolink_ul_state(rnti, crc);

  // Scheduler uses eNB's CC mapping
  return scheduler.ul_crc_info(tti_rx, rnti, enb_cc_idx, crc);
}

int mac::push_pdu(uint32_t tti_rx,
                  uint16_t rnti,
                  uint32_t enb_cc_idx,
                  uint32_t nof_bytes,
                  bool     crc,
                  uint32_t ul_nof_prbs)
{
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  srsran::unique_byte_buffer_t pdu = ue_db[rnti]->release_pdu(tti_rx, enb_cc_idx);
  if (pdu == nullptr) {
    logger.warning("Could not find MAC UL PDU for rnti=0x%x, cc=%d, tti=%d", rnti, enb_cc_idx, tti_rx);
    return SRSRAN_ERROR;
  }

  // push the pdu through the queue if received correctly
  if (crc) {
    logger.info("Pushing PDU rnti=0x%x, tti_rx=%d, nof_bytes=%d", rnti, tti_rx, nof_bytes);
    srsran_expect(nof_bytes == pdu->size(),
                  "Inconsistent PDU length for rnti=0x%x, tti_rx=%d (%d!=%d)",
                  rnti,
                  tti_rx,
                  nof_bytes,
                  (int)pdu->size());
    auto process_pdu_task = [this, rnti, enb_cc_idx, ul_nof_prbs](srsran::unique_byte_buffer_t& pdu) {
      srsran::rwlock_read_guard lock(rwlock);
      if (check_ue_active(rnti)) {
        ue_db[rnti]->process_pdu(std::move(pdu), enb_cc_idx, ul_nof_prbs);
      } else {
        logger.debug("Discarding PDU rnti=0x%x", rnti);
      }
    };
    stack_task_queue.try_push(std::bind(process_pdu_task, std::move(pdu)));
  } else {
    logger.debug("Discarding PDU rnti=0x%x, tti_rx=%d, nof_bytes=%d", rnti, tti_rx, nof_bytes);
  }
  return SRSRAN_SUCCESS;
}

int mac::ri_info(uint32_t tti, uint16_t rnti, uint32_t enb_cc_idx, uint32_t ri_value)
{
  logger.set_context(tti);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  scheduler.dl_ri_info(tti, rnti, enb_cc_idx, ri_value);
  ue_db[rnti]->metrics_dl_ri(ri_value);

  return SRSRAN_SUCCESS;
}

int mac::pmi_info(uint32_t tti, uint16_t rnti, uint32_t enb_cc_idx, uint32_t pmi_value)
{
  logger.set_context(tti);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  scheduler.dl_pmi_info(tti, rnti, enb_cc_idx, pmi_value);
  ue_db[rnti]->metrics_dl_pmi(pmi_value);

  return SRSRAN_SUCCESS;
}

int mac::cqi_info(uint32_t tti, uint16_t rnti, uint32_t enb_cc_idx, uint32_t cqi_value)
{
  logger.set_context(tti);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  scheduler.dl_cqi_info(tti, rnti, enb_cc_idx, cqi_value);
  ue_db[rnti]->metrics_dl_cqi(cqi_value);

  return SRSRAN_SUCCESS;
}

int mac::sb_cqi_info(uint32_t tti, uint16_t rnti, uint32_t enb_cc_idx, uint32_t sb_idx, uint32_t cqi_value)
{
  logger.set_context(tti);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  scheduler.dl_sb_cqi_info(tti, rnti, enb_cc_idx, sb_idx, cqi_value);
  return SRSRAN_SUCCESS;
}

int mac::snr_info(uint32_t tti_rx, uint16_t rnti, uint32_t enb_cc_idx, float snr, ul_channel_t ch)
{
  logger.set_context(tti_rx);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  rrc_h->set_radiolink_ul_state(rnti, snr >= args.rlf_min_ul_snr_estim);

  return scheduler.ul_snr_info(tti_rx, rnti, enb_cc_idx, snr, (uint32_t)ch);
}

int mac::ta_info(uint32_t tti, uint16_t rnti, float ta_us)
{
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  uint32_t nof_ta_count = ue_db[rnti]->set_ta_us(ta_us);
  if (nof_ta_count > 0) {
    return scheduler.dl_mac_buffer_state(rnti, (uint32_t)srsran::dl_sch_lcid::TA_CMD, nof_ta_count);
  }
  return SRSRAN_SUCCESS;
}

int mac::sr_detected(uint32_t tti, uint16_t rnti)
{
  logger.set_context(tti);
  srsran::rwlock_read_guard lock(rwlock);

  if (not check_ue_active(rnti)) {
    return SRSRAN_ERROR;
  }

  return scheduler.ul_sr_info(tti, rnti);
}

bool mac::is_valid_rnti_unprotected(uint16_t rnti)
{
  if (not started) {
    logger.info("RACH ignored as eNB is being shutdown");
    return false;
  }
  if (not ue_db.has_space(rnti)) {
    logger.info("Failed to allocate rnti=0x%x. Attempting a different rnti.", rnti);
    return false;
  }
  return true;
}

uint16_t mac::allocate_ue(uint32_t enb_cc_idx)
{
  ue*      inserted_ue = nullptr;
  uint16_t rnti        = SRSRAN_INVALID_RNTI;

  do {
    // Assign new RNTI
    rnti = FIRST_RNTI + (ue_counter.fetch_add(1, std::memory_order_relaxed) % 60000);

    // Pre-check if rnti is valid
    {
      srsran::rwlock_read_guard read_lock(rwlock);
      if (ue_db.full()) {
        logger.warning("Maximum number of connected UEs %zd connected to the eNB. Ignoring PRACH", SRSENB_MAX_UES);
        return SRSRAN_INVALID_RNTI;
      }
      if (not is_valid_rnti_unprotected(rnti)) {
        continue;
      }
    }

    // Allocate and initialize UE object
    unique_rnti_ptr<ue> ue_ptr = make_rnti_obj<ue>(
        rnti, rnti, enb_cc_idx, &scheduler, rrc_h, rlc_h, phy_h, logger, cells.size(), softbuffer_pool.get());

    // Add UE to rnti map
    srsran::rwlock_write_guard rw_lock(rwlock);
    if (not is_valid_rnti_unprotected(rnti)) {
      continue;
    }
    auto ret = ue_db.insert(rnti, std::move(ue_ptr));
    if (ret.has_value()) {
      inserted_ue = ret.value()->second.get();
    } else {
      logger.info("Failed to allocate rnti=0x%x. Attempting a different rnti.", rnti);
    }
  } while (inserted_ue == nullptr);

  // Set PCAP if available
  if (pcap != nullptr) {
    inserted_ue->start_pcap(pcap);
  }

  if (pcap_net != nullptr) {
    inserted_ue->start_pcap_net(pcap_net);
  }

  return rnti;
}

bool mac::is_pending_pdcch_order_prach(const uint32_t preamble_idx, uint16_t& rnti)
{
  for (auto it = pending_po_prachs.begin(); it != pending_po_prachs.end();) {
    auto& pending_po_prach = *it;
    if (pending_po_prach.preamble_idx == preamble_idx) {
      rnti = pending_po_prach.crnti;
      // delete pending PDCCH PRACH from vector
      it = pending_po_prachs.erase(it);
      return true;
    }
    ++it;
  }
  return false;
}

uint16_t mac::reserve_new_crnti(const sched_interface::ue_cfg_t& uecfg)
{
  uint16_t rnti = allocate_ue(uecfg.supported_cc_list[0].enb_cc_idx);
  if (rnti == SRSRAN_INVALID_RNTI) {
    return rnti;
  }

  // Add new user to the scheduler so that it can RX/TX SRB0
  if (ue_cfg(rnti, &uecfg) != SRSRAN_SUCCESS) {
    return SRSRAN_INVALID_RNTI;
  }
  return rnti;
}

void mac::rach_detected(uint32_t tti, uint32_t enb_cc_idx, uint32_t preamble_idx, uint32_t time_adv)
{
  static srsran::mutexed_tprof<srsran::avg_time_stats> rach_tprof("rach_tprof", "MAC", 1);
  logger.set_context(tti);
  auto rach_tprof_meas = rach_tprof.start();

  stack_task_queue.push([this, tti, enb_cc_idx, preamble_idx, time_adv, rach_tprof_meas]() mutable {
    uint16_t rnti = 0;
    // check if this is a PRACH from a PDCCH order
    bool is_po_prach = is_pending_pdcch_order_prach(preamble_idx, rnti);
    if (!is_po_prach) {
      rnti = allocate_ue(enb_cc_idx);
      if (rnti == SRSRAN_INVALID_RNTI) {
        return;
      }
    }

    rach_tprof_meas.defer_stop();
    // Generate RAR data
    sched_interface::dl_sched_rar_info_t rar_info = {};
    rar_info.preamble_idx                         = preamble_idx;
    rar_info.ta_cmd                               = time_adv;
    rar_info.temp_crnti                           = rnti;
    rar_info.msg3_size                            = 7;
    rar_info.prach_tti                            = tti;

    // Log this event.
    ++detected_rachs[enb_cc_idx];

    // If this is a PRACH from a PDCCH order, the user already exists
    if (not is_po_prach) {
      // Add new user to the scheduler so that it can RX/TX SRB0
      sched_interface::ue_cfg_t uecfg = {};
      uecfg.supported_cc_list.emplace_back();
      uecfg.supported_cc_list.back().active     = true;
      uecfg.supported_cc_list.back().enb_cc_idx = enb_cc_idx;
      uecfg.ue_bearers[0].direction             = mac_lc_ch_cfg_t::BOTH;
      uecfg.supported_cc_list[0].dl_cfg.tm      = SRSRAN_TM1;
      if (ue_cfg(rnti, &uecfg) != SRSRAN_SUCCESS) {
        return;
      }

      // Register new user in RRC
      if (rrc_h->add_user(rnti, uecfg) == SRSRAN_ERROR) {
        ue_rem(rnti);
        return;
      }
    }

    // Trigger scheduler RACH
    scheduler.dl_rach_info(enb_cc_idx, rar_info);

    auto get_pci = [this, enb_cc_idx]() {
      srsran::rwlock_read_guard lock(rwlock);
      return (enb_cc_idx < cell_config.size()) ? cell_config[enb_cc_idx].cell.id : 0;
    };
    uint32_t pci = get_pci();
    logger.info("%sRACH:  tti=%d, cc=%d, pci=%d, preamble=%d, offset=%d, temp_crnti=0x%x",
                (is_po_prach) ? "PDCCH order " : "",
                tti,
                enb_cc_idx,
                pci,
                preamble_idx,
                time_adv,
                rnti);
    srsran::console("%sRACH:  tti=%d, cc=%d, pci=%d, preamble=%d, offset=%d, temp_crnti=0x%x\n",
                    (is_po_prach) ? "PDCCH order " : "",
                    tti,
                    enb_cc_idx,
                    pci,
                    preamble_idx,
                    time_adv,
                    rnti);
  });
}


int tti_cnt = 0;
struct timeval __start, __end; 
long __utime, __seconds, __useconds; 
long __total_dt = 0; 

std::map<uint16_t, uint8_t> __cqis; 
////


#ifdef zmq_rtt_eval

void mac::ric_comm(std::map<uint16_t, float>& weights)
{
  //static mac_metrics_t ue_metrics;
  static mac_ue_metrics_t ue_metrics;

  // to be blocked
  /*
  float *fixed_weights = new float[2]; 
  fixed_weights[0] = 0.5 ; 
  fixed_weights[1] = 0.5 ; 
  
  uint16_t idx = 0; 
  for (auto& ue_pair : ue_db) {
    weights[ue_pair.first] = fixed_weights[idx++]; 
    //printf(" rnti: %d weight:  %f \n" , ue_pair.first, weights[ue_pair.first]); 
  }
  */
  
  
  //printf("ric_comm\n"); 
  std::string send_message_to_rl("");
  
  
  struct timeval ctime ; 
  
  gettimeofday(&ctime, NULL); 
  
  long seconds = ctime.tv_sec - __time.tv_sec ; 
  long useconds = ctime.tv_usec - __time.tv_usec ; 
  long  utime= (1000000*seconds + useconds);   
  
 
  
  __time = ctime; 
  
  long clock_get_time =clock_gettime(); 
  
  printf(" %lf \n", clock_get_time); 

  zmq::message_t recv_message;
  //subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
  zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "", 0); 
  // true or false
  
  weights.clear(); 
  //auto size = subscriber.recv(&recv_message, ZMQ_DONTWAIT);
  gettimeofday(&__start, NULL);
  auto size = subscriber.recv(recv_message, zmq::recv_flags::dontwait);
  
  uint8_t num_ues_rtt = 20;
  if (size) {
    std::string text((const char*)recv_message.data()); 

    if(text.size() >num_ues_rtt*3 ){
      printf("mac: %li,  %s\n",text.size(), text.c_str()); 
    
      std::string space_delimiter = " ";
      size_t len_delimiter = space_delimiter.length(); 
      size_t pos_rnti = 0; 
      size_t pos_weight = 0 ; 
      //printf("string: %s \n", text.c_str()); 
      float sum_weight = 0; 
      uint16_t *rntis = new uint16_t[num_ues_rtt]; 
      uint16_t idx = 0;
      //while((pos_rnti = text.find(space_delimiter)) != std::string::npos){
      for( uint16_t i = 0 ; i< num_ues_rtt ; i++)
      {
        pos_rnti = text.find(space_delimiter) ;

        if (text.substr(0,pos_rnti).size() > 0)
        {
          printf("stoi: -%s-  size: %ld  \n",  text.substr(0,pos_rnti).c_str(),text.substr(0,pos_rnti).size()  ); 
          uint16_t rnti = std::stoi(text.substr(0,pos_rnti));
          rntis[idx++] = rnti ; 
          text.erase(0, pos_rnti + len_delimiter); 
        
          pos_weight = text.find(space_delimiter);
          float weight = std::stof(text.substr(0,pos_weight));
          text.erase(0, pos_weight + len_delimiter); 
            
          weights[rnti] = weight;
          sum_weight += weight;
          //printf("received: rnti: %i  , weight : %f \n", rnti, weight) ; 
        }
      }

      for (uint16_t k = 0 ; k < weights.size(); k++){
        weights[rntis[k]] = weights[rntis[k]]/sum_weight; 
        //printf("normalized: rnti: %i  , weight : %f \n", rntis[k], weights[rntis[k]]) ; 
      }
      //printf("\n"); 
      //std::map<uint16_t, float> temp = std::stof(std::to_string(*static_cast<char*>(recv_message.data())));
      //printf("mac: %i,  %s\n",size, (const char*)recv_message.data()); 
    }
  }

  for (auto& ue_pair : ue_db) {
    int backlog = backlogBuffer[ue_pair.first]; 
    ue_pair.second->metrics_read(&ue_metrics);
    send_message_to_rl += std::to_string(ue_pair.first) + " " + std::to_string((int)ue_metrics.dl_cqi) + " " + std::to_string(backlog) + " "; 
    //if ((int) ue_metrics.dl_cqi >= 0 ) printf("rnti: %i cqi: %i\n ", ue_pair.first , (int)ue_metrics.dl_cqi); 
  }

  if(ue_db.size()>0)
  {
    for(uint8_t i=0;i<num_ues_rtt-(uint8_t)ue_db.size();i++)
    {
      uint16_t rnti = (rand()%65535)+1;
      int cqi = (rand()%15)+1;
      int backlog = rand()%320000;
      send_message_to_rl += std::to_string(rnti) + " " + std::to_string((int)cqi) + " " + std::to_string(backlog) + " ";
    }
  }

  send_message_to_rl +=" "; 
  int m_size = send_message_to_rl.size(); 
  zmq::message_t message(m_size); 
  snprintf((char *)message.data(), m_size, send_message_to_rl.c_str(), NULL ); 
  publisher.send(message, zmq::send_flags::none ); 
  //publisher.send(send_message_to_rl.c_str(), send_message_to_rl.size());
  
  // if(ue_db.size()>0)
  // {
  //   printf("mac: %s \n", send_message_to_rl.c_str());
  // }
}
#else


std::map<uint16_t, float> tx_bytes_ues;
std::map<uint16_t, float> prev_weights;
std::map<uint16_t, float> cur_weights;
long prev_weight_time= 0; 
long cur_weight_time= 0; 
  

void mac::ric_comm(std::map<uint16_t, float>& weights)
{

  struct timespec curtime ; 
  int cur_ret =clock_gettime(CLOCK_REALTIME, &curtime); 
  long utime_cur = (curtime.tv_sec*1000000000 + curtime.tv_nsec )/1000.0; 

  if (utime_cur- __utime_init > __fileout_period){
      printf("\n\n   %ld \n\n\n", utime_cur- __utime_init ); 
      printf("\n\n   %s \n\n\n", __outfile_seq_buf.c_str() ); 
      if (__outfile_seq_flag) outfile_seq << __outfile_seq_buf;
      exit(0); 
  }
  //static mac_metrics_t ue_metrics;
  static mac_ue_metrics_t ue_metrics;

  // to be blocked
  /*
  float *fixed_weights = new float[2]; 
  fixed_weights[0] = 0.5 ; 
  fixed_weights[1] = 0.5 ; 
  
  uint16_t idx = 0; 
  for (auto& ue_pair : ue_db) {
    weights[ue_pair.first] = fixed_weights[idx++]; 
    //printf(" rnti: %d weight:  %f \n" , ue_pair.first, weights[ue_pair.first]); 
  }
  */
  
  
  //printf("ric_comm\n"); 
  std::string send_message_to_rl("");
  
  
  /*struct timeval ctime ; 
  
  gettimeofday(&ctime, NULL); 
  
  long seconds = ctime.tv_sec - __time.tv_sec ; 
  long useconds = ctime.tv_usec - __time.tv_usec ; 
  long  utime= (1000000*seconds + useconds);   
  
  
  __time = ctime; 
  */
  
  zmq::message_t recv_message;
  //subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
  zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "", 0); 
  // true or false
  
  weights.clear(); 
  //auto size = subscriber.recv(&recv_message, ZMQ_DONTWAIT);

  
  
  auto size = subscriber.recv(recv_message, zmq::recv_flags::dontwait);
  
  //printf("after receiving  \n\n\n"); 
  zmq_count++;
  bool pflag = 0;

  if (size) {
    
    std::string text((const char*)recv_message.data()); 
    

    // flag to log all stats by whko 09072022
    __outfile_flag = true ; //true; 
    __outfile_seq_flag = true ; //true; 
    ///struct timeval ctime ; 
    ///gettimeofday(&ctime, NULL); 
  
    ///long seconds = ctime.tv_sec ; 
    ///long useconds = ctime.tv_usec; 
    ///long utime_cur= (1000000*seconds + useconds) - __utime_init;   

    struct timespec ctime ; 
    int ret =clock_gettime(CLOCK_REALTIME, &ctime); 
  
    //printf(" %ld \n", start.tv_sec*1000000000 + start.tv_nsec ); 
    long utime_cur_system = ctime.tv_sec*1000000000 + ctime.tv_nsec ; 

    if (__outfile_flag) outfile << std::to_string(utime_cur_system) + ", "; 

    
   
    
    ///  5. RAN received weights from RC
    
    //if (__outfile_seq_flag) outfile_seq << std::to_string(utime_cur_system) + ",\t" +  "5\n"; 
    if (__outfile_seq_flag) __outfile_seq_buf.append(std::to_string(utime_cur_system) + ",\t" +  "5\n"); 
    

    ///

    if(text.size() >ue_db.size()*3 ){
      //printf("mac: %li,  %s\n",text.size(), text.c_str()); 
    
      std::string space_delimiter = " ";
      size_t len_delimiter = space_delimiter.length(); 
      size_t pos_rnti = 0; 
      size_t pos_weight = 0 ; 
      //printf("string: %s \n", text.c_str()); 
      float sum_weight = 0; 
      uint16_t *rntis = new uint16_t[ue_db.size()]; 
      uint16_t idx = 0;
      //while((pos_rnti = text.find(space_delimiter)) != std::string::npos){
      for( uint16_t i = 0 ; i< ue_db.size() ; i++) {
        pos_rnti = text.find(space_delimiter) ;
        if (text.substr(0,pos_rnti).size() > 0){
          int rnti ;
          try{
            rnti = std::stoi(text.substr(0,pos_rnti));
            if(rnti < 0) throw 1;
          }
          catch(...){
            printf("rnti is not correct.\n");
            break;
          }
          rntis[idx++] = (uint16_t) rnti ;
          text.erase(0, pos_rnti + len_delimiter);
          pos_weight = text.find(space_delimiter);
          float weight = std::stof(text.substr(0,pos_weight));
          text.erase(0, pos_weight + len_delimiter);
          weights[rnti] = weight;
          sum_weight += weight;

          prev_weights[rnti] = cur_weights[rnti]; 
          cur_weights[rnti] = weight ; 
          //printf("received: rnti: %i  , weight : %f \n", rnti, weight) ;
        }
      }
      
      // to be deleted by whko 09252022
      //pos_rnti = text.find(space_delimiter) ;
      //if (text.substr(0,pos_rnti).size() > 0){
        //long weight_time ;
        //try{
          //weight_time = std::stol(text.substr(0,pos_rnti));
          //prev_weight_time = cur_weight_time ; 
          //cur_weight_time = weight_time ; 
          ///printf("prev_weight_time %ld \n", prev_weight_time); 
         // if(weight_time < 0) throw 1;
       // }
        //catch(...){
          //printf("rnti is not correct.\n");
          //break;
        //}
      
      //}


      for (uint16_t k = 0 ; k < weights.size(); k++){
        weights[rntis[k]] = weights[rntis[k]]/sum_weight ; 

        if (__outfile_flag) outfile <<  std::to_string(rntis[k]) + ", " + std::to_string(weights[rntis[k]]) + ", " ;
        //printf("normalized: rnti: %i  , weight : %f \n", rntis[k], weights[rntis[k]]) ; 
      }

      //printf("\n"); 
      //std::map<uint16_t, float> temp = std::stof(std::to_string(*static_cast<char*>(recv_message.data())));
      //printf("mac: %i,  %s\n",size, (const char*)recv_message.data()); 
    }


 
  }
  else
    //__outfile_flag = false; 
    __outfile_flag = true;  // only for logging with usrp 


  
  for (auto& ue_pair : ue_db) {
    int backlog = backlogBuffer[ue_pair.first]; 
    int tx_bytes = tx_bytes_ues[ue_pair.first] ; 

    ue_pair.second->metrics_read(&ue_metrics);
    

    uint8_t rnti = ue_pair.first; 
    uint8_t cqi = (uint8_t) ue_metrics.dl_cqi; 

    __cqis[rnti] = cqi ? cqi : __cqis[rnti]; 
    cqi = __cqis[rnti]; 

    send_message_to_rl += std::to_string(rnti) + " " + std::to_string(cqi) + " " + std::to_string(backlog) + " ";
    //send_message_to_rl += std::to_string(rnti) + " " + std::to_string(cqi) + " " + std::to_string(tx_bytes) + " ";
    
    if (__outfile_flag) outfile << std::to_string(rnti) + ", " + std::to_string(cqi) + ", " + std::to_string(backlog) + ", ";
    // if(ue_db.size() == num_ues){
    //   fprintf(fp,"%d\t%d\t",ue_pair.first,backlog);
    // }
    // if ((int) ue_metrics.dl_cqi >= 0 && zmq_count>=1000){
    //   printf("rnti: %i cqi: %i zmq_count: %d\n ", ue_pair.first , (int)ue_metrics.dl_cqi, zmq_count);
    //   // bool pflag = 1;
    //   zmq_count = 0;
    // }
  }
  // 7. RAN measures state change
  struct timespec ctime ; 
  int ret =clock_gettime(CLOCK_REALTIME, &ctime); 
  long utime_cur_system = ctime.tv_sec*1000000000 + ctime.tv_nsec ;
  //if (__outfile_seq_flag) outfile_seq << std::to_string(utime_cur_system) + ",\t" +  "7\n"; 
  if (__outfile_seq_flag) __outfile_seq_buf.append(std::to_string(utime_cur_system) + ",\t" +  "7\n"); 
  
  // to be deleted by whko 09252022
  for (auto& ue_pair : ue_db) {
    uint8_t rnti = ue_pair.first; 
    send_message_to_rl += std::to_string(prev_weights[rnti]) + " "; 
  }
  send_message_to_rl += std::to_string(prev_weight_time) + " "; 


  ///////


  // if(ue_db.size() == num_ues)
  //   fprintf(fp,"\n");
  // if(zmq_count>=1000 && pflag){
    
  //   pflag = 0;
  // }
  send_message_to_rl +=" "; 
  int m_size = send_message_to_rl.size(); 
  zmq::message_t message(m_size); 
  snprintf((char *)message.data(), m_size, send_message_to_rl.c_str(), NULL ); 
  publisher.send(message, zmq::send_flags::none ); 
  // 1. RAN transmits state information to RIC
  struct timespec ctime_1 ; 
  int ret_1 =clock_gettime(CLOCK_REALTIME, &ctime_1); 
  long utime_cur_system_1 = ctime_1.tv_sec*1000000000 + ctime_1.tv_nsec ; 
  if (__outfile_seq_flag) outfile_seq << std::to_string(utime_cur_system_1) + ",\t" +  "1\n"; 
  if (__outfile_seq_flag) __outfile_seq_buf.append(std::to_string(utime_cur_system_1) + ",\t" +  "1\n"); 

  //publisher.send(send_message_to_rl.c_str(), send_message_to_rl.size());

}
#endif

double avg_tx_bytes = 0 ; 
std::map<uint16_t, float> avg_tx_bytes_ues;
std::map<uint16_t, float> ue_throughput;
bool tpt_log_flag = 0;


#define new_cal
#ifdef new_cal
void mac::calFairness(sched_interface::dl_sched_res_t sched_result){

  tti_cnt++; 

  

  // calculating backlog buffer fairness
  double sq_of_sum_yi = 0 ;
  double sum_of_yi_sq = 0 ;

  int sum_backlog = 0; 
  for (auto& ue_pair : ue_db) {
    sum_backlog += backlogBuffer[ue_pair.first]; 

    double yi =backlogBuffer[ue_pair.first]; 
    sq_of_sum_yi += yi; 
    sum_of_yi_sq += yi*yi; 
  }
  sq_of_sum_yi = sq_of_sum_yi*sq_of_sum_yi; 

  double backlogFairness = sq_of_sum_yi / (ue_db.size()*sum_of_yi_sq);
  
  if(__outfile_flag) outfile << std::to_string(sum_backlog) + ", " + std::to_string(backlogFairness) + ", " ;


  ///
  uint32_t tx_bytes = 0;
  uint8_t sz = sched_result.data.size();
  //std::map<uint16_t, float> tx_bytes_ues;
  
  for (uint32_t k = 0 ; k < sz; k++ )
  {
    uint16_t rnti = sched_result.data[k].dci.rnti;
    tx_bytes_ues[rnti] = 0;

    for (uint32_t tb_ = 0; tb_ < SRSRAN_MAX_TB; tb_++)
    {
        // printf("%i %i transmitted bytes %i \n", k, tb_, sched_result.data[k].tbs[tb_]); 
        tx_bytes += sched_result.data[k].tbs[tb_] ;
        tx_bytes_ues[rnti] += sched_result.data[k].tbs[tb_] ;
    }
    
  }

  
  for (auto& u : ue_db)
  {
    uint16_t rnti= u.first;

    if (__outfile_flag) outfile << std::to_string(rnti) + ", " + std::to_string(tx_bytes_ues[rnti]*8.0/1000.0) + ", "; 

    avg_tx_bytes_ues[rnti] = (avg_tx_bytes_ues[rnti]*(tti_cnt-1) + tx_bytes_ues[rnti])*1.0/tti_cnt;
    //tx_bytes_ues[rnti] = 0;
    if(bufsaveflag)
      fprintf(fp,"%d\t%d\n",rnti,backlogBuffer[rnti]);
  }
  if (__outfile_flag) outfile << std::to_string(tx_bytes*8.0/1000.0) + ", "; 

  

  // printf("avg_tx_bytes_ues[%d] = %f\n",rnti,avg_tx_bytes_ues[rnti]);

  // avg_tx_bytes =  (avg_tx_bytes != 0) ? (uint32_t) (tx_bytes*0.5+ avg_tx_bytes*0.5) : tx_bytes ; 
  avg_tx_bytes =  (avg_tx_bytes*(tti_cnt-1) + tx_bytes)*1.0/tti_cnt;


  if(avg_tx_bytes>10)
    tpt_log_flag = 1;


  // calculating thourghput fairness
  double _thrptFairness = 0; 
  double _sumthroughput = 0; 
  if (avg_tx_bytes > 0){
    _sumthroughput = avg_tx_bytes*8.0/1000.0 ; 

    double _sq_of_sum_xi = 0 ;
    double _sum_of_xi_sq = 0 ;


    for (auto& u : ue_db) {
      uint16_t rnti= u.first;
      double xi = (double)avg_tx_bytes_ues[rnti]/avg_tx_bytes;
      ue_throughput[rnti] = avg_tx_bytes_ues[rnti]*8.0/1000.0;
      _sq_of_sum_xi += xi;
      _sum_of_xi_sq += xi*xi;
      avg_tx_bytes_ues[rnti] = 0;

      //if (__outfile_flag) outfile << std::to_string(rnti) + "\t" + std::to_string(ue_throughput[rnti]) + "\t"; 
    }
    _sq_of_sum_xi = _sq_of_sum_xi*_sq_of_sum_xi;

    _thrptFairness = 1.0*_sq_of_sum_xi / ((int)ue_db.size()*_sum_of_xi_sq);

  }

  if (__outfile_flag) outfile << std::to_string(_sumthroughput) + ", " + std::to_string(_thrptFairness) + ", " + std::to_string((int)round(avg_tx_bytes))+ ", " + std::to_string((int)round(tx_bytes)) + "\r"; 

  ///



  if(tti_cnt>=1000)
  {
    //printf("avg_tx_bytes: %i\n", avg_tx_bytes ); 
    double sumthroughput = avg_tx_bytes*8.0/1000.0 ; 
    double sq_of_sum_xi = 0 ;
    double sum_of_xi_sq = 0 ;

    char algo[10];
    switch(algoflag)
    {
      case 1: strncpy(algo,"max_tpt",sizeof(algo)); break;
      case 2: strncpy(algo,"max_wgt",sizeof(algo)); break;
      case 3: strncpy(algo,"pf",sizeof(algo)); break;
      case 4: strncpy(algo,"rl",sizeof(algo)); break;
      default: strncpy(algo,"max_tpt",sizeof(algo));
    }
    char scenario[15];
    switch(scenarioflag)
    {
      case 1: strncpy(scenario,"nd_nc_sl",sizeof(scenario)); break;
      case 2: strncpy(scenario,"nd_nc_dl",sizeof(scenario)); break;
      case 3: strncpy(scenario,"nd_wc_sl",sizeof(scenario)); break;
      case 4: strncpy(scenario,"nd_wc_dl",sizeof(scenario)); break;
      case 5: sprintf(scenario,"wd%d_nc_sl",delay); break;
      case 6: sprintf(scenario,"wd%d_nc_dl",delay); break;
      case 7: sprintf(scenario,"wd%d_wc_sl",delay); break;
      case 8: sprintf(scenario,"wd%d_wc_dl",delay); break;
      default: strncpy(scenario,"nd_nc_sl",sizeof(scenario));
    }

    // printf("%f %f %f\n",avg_tx_bytes_ues[0],avg_tx_bytes_ues[1],avg_tx_bytes); 
    char filename1[440];
    // sprintf(filename1,"/home/afc/git/5G_EdgeRIC_Updated/MobiCom_Results/%dUEs/%s/SL_%0.1fM_CQI_CHANGE_1IN%d_STEP%d/tpt_%s.txt",num_ues,algo,load,cqi_change_period,cqi_step_size,scenario);
    if(cqi_change_flag)
      sprintf(filename1,"/home/wcsng-24/Ushasi/EdgeRIC_main/MobiCom_Results/%dUEs/%s/CQI_CHANGE/SL_%0.1fM_CQI_CHANGE_1IN%d_RSTEP%d/tpt_%s.txt",num_ues,algo,load,cqi_change_period,cqi_range_size,scenario);
    else
      sprintf(filename1,"/home/wcsng-24/Ushasi/EdgeRIC_main/MobiCom_Results/%dUEs/%s/NO_CQI_CHANGE/SL_%0.1fM_NO_CQI_CHANGE/tpt_%s.txt",num_ues,algo,load,scenario);

    for (auto& u : ue_db)
    {
      uint16_t rnti= u.first;
      double xi = (double)avg_tx_bytes_ues[rnti]/avg_tx_bytes;
      ue_throughput[rnti] = avg_tx_bytes_ues[rnti]*8.0/1000.0;
      sq_of_sum_xi += xi;
      sum_of_xi_sq += xi*xi;
      avg_tx_bytes_ues[rnti] = 0;
    }
    sq_of_sum_xi = sq_of_sum_xi*sq_of_sum_xi;

    double thrptFairness = 1.0*sq_of_sum_xi / ((int)ue_db.size()*sum_of_xi_sq);
    
    printf("Thrpt.[Mbps]: %lf Thrpt.Fairness: %lf  avg_tx_bytes: %i\n",sumthroughput, thrptFairness, (int)round(avg_tx_bytes));

    // if(!(thrptFairness!=thrptFairness) || tpt_log_flag)
    if(tpt_log_flag)
    {
      if(ue_db.size()==num_ues)
      {
        fp1 = fopen(filename1,"a+");
        for (auto& u : ue_db){
          fprintf(fp1,"%d\t%lf\t", u.first, ue_throughput[u.first]);
          
        }
          
        if((thrptFairness!=thrptFairness))
          thrptFairness = 0.0;
        fprintf(fp1,"%lf\t%lf\t%i\n", sumthroughput, thrptFairness, (int)round(avg_tx_bytes));
        fclose(fp1);

        

      }
    }



    tti_cnt = 0;

    avg_tx_bytes = 0;
  }
}
#else
void mac::calFairness(sched_interface::dl_sched_res_t sched_result){

  uint32_t tx_bytes = 0; 
  uint8_t sz = sched_result.data.size(); 
  uint32_t *tx_bytes_ues = new uint32_t[sz]; 

  for (uint32_t k = 0 ; k < sz; k++ ){
    for (uint32_t tb_ = 0; tb_ < SRSRAN_MAX_TB; tb_++) {
        //printf("%i %i transmitted bytes %i \n", k, tb_, sched_result.data[k].tbs[tb_]); 
        tx_bytes += sched_result.data[k].tbs[tb_] ; 
        tx_bytes_ues[k] += sched_result.data[k].tbs[tb_] ; 
    }
    avg_tx_bytes_ues[k] = (avg_tx_bytes_ues[k] != 0) ? (uint32_t) (tx_bytes_ues[k]*0.0003+ avg_tx_bytes_ues[sched_result.data[k].dci.rnti]*0.9997) : tx_bytes_ues[k] ; 
    
  }
  
  avg_tx_bytes =  (avg_tx_bytes != 0) ? (uint32_t) (tx_bytes*0.0003+ avg_tx_bytes*0.9997) : tx_bytes ; 

  tti_cnt++; 
  if(tti_cnt>1000){
    //printf("avg_tx_bytes: %i\n", avg_tx_bytes ); 
    double throughput = avg_tx_bytes*8.0/1000.0 ; 
    double sq_of_sum_xi = 0 ;
    double sum_of_xi_sq = 0 ; 
    
    
    for (int i = 0; i < sz ; i++){
      double xi = avg_tx_bytes_ues[i]; 
      sq_of_sum_xi += xi; 
      sum_of_xi_sq += xi*xi; 
    }
    sq_of_sum_xi = sq_of_sum_xi*sq_of_sum_xi; 

    double thrptFairness = sq_of_sum_xi / (sz*sum_of_xi_sq);
    
    printf("Thrpt.[Mbps]: %lf Thrpt.Fairness: %lf  avg_tx_bytes: %i\n",throughput, thrptFairness, avg_tx_bytes ); 

    tti_cnt = 0;
  }
}
#endif

int mac::get_dl_sched(uint32_t tti_tx_dl, dl_sched_list_t& dl_sched_res_list)
{
  ric_comm(scheduler.weights);
 
  if (!started) {
    return 0;
  }

  trace_threshold_complete_event("mac::get_dl_sched", "total_time", std::chrono::microseconds(100));
  logger.set_context(TTI_SUB(tti_tx_dl, FDD_HARQ_DELAY_UL_MS));
  if (do_padding) {
    add_padding();
  }

  srsran::rwlock_read_guard lock(rwlock);

  for (uint32_t enb_cc_idx = 0; enb_cc_idx < cell_config.size(); enb_cc_idx++) {
    // Run scheduler with current info
    sched_interface::dl_sched_res_t sched_result = {};
    if (scheduler.dl_sched(tti_tx_dl, enb_cc_idx, sched_result) < 0) {
      logger.error("Running scheduler");
      return SRSRAN_ERROR;
    }

    // To check transmitted bytes: whko 08112022 
    calFairness(sched_result); 
    ///    

    int         n            = 0;
    dl_sched_t* dl_sched_res = &dl_sched_res_list[enb_cc_idx];
    
  

    // Copy data grants
    for (uint32_t i = 0; i < sched_result.data.size(); i++) {
      uint32_t tb_count = 0;

      // Get UE
      uint16_t rnti = sched_result.data[i].dci.rnti;

      if (ue_db.contains(rnti)) {
        // Copy dci info
        dl_sched_res->pdsch[n].dci = sched_result.data[i].dci;

        for (uint32_t tb = 0; tb < SRSRAN_MAX_TB; tb++) {
          dl_sched_res->pdsch[n].softbuffer_tx[tb] =
              ue_db[rnti]->get_tx_softbuffer(enb_cc_idx, sched_result.data[i].dci.pid, tb);

          // If the Rx soft-buffer is not given, abort transmission
          if (dl_sched_res->pdsch[n].softbuffer_tx[tb] == nullptr) {
            continue;
          }

          if (sched_result.data[i].nof_pdu_elems[tb] > 0) {
            /* Get PDU if it's a new transmission */
            dl_sched_res->pdsch[n].data[tb] = ue_db[rnti]->generate_pdu(enb_cc_idx,
                                                                        sched_result.data[i].dci.pid,
                                                                        tb,
                                                                        sched_result.data[i].pdu[tb],
                                                                        sched_result.data[i].nof_pdu_elems[tb],
                                                                        sched_result.data[i].tbs[tb]);

            if (!dl_sched_res->pdsch[n].data[tb]) {
              logger.error("Error! PDU was not generated (rnti=0x%04x, tb=%d)", rnti, tb);
            }

            if (pcap) {
              pcap->write_dl_crnti(
                  dl_sched_res->pdsch[n].data[tb], sched_result.data[i].tbs[tb], rnti, true, tti_tx_dl, enb_cc_idx);
            }
            if (pcap_net) {
              pcap_net->write_dl_crnti(
                  dl_sched_res->pdsch[n].data[tb], sched_result.data[i].tbs[tb], rnti, true, tti_tx_dl, enb_cc_idx);
            }
          } else {
            /* TB not enabled OR no data to send: set pointers to NULL  */
            dl_sched_res->pdsch[n].data[tb] = nullptr;
          }

          tb_count++;
        }

        // Count transmission if at least one TB has successfully added
        if (tb_count > 0) {
          n++;
        }
      } else {
        logger.warning("Invalid DL scheduling result. User 0x%x does not exist", rnti);
      }
    }

    // Copy RAR grants
    for (uint32_t i = 0; i < sched_result.rar.size(); i++) {
      // Copy dci info
      dl_sched_res->pdsch[n].dci = sched_result.rar[i].dci;

      // Set softbuffer (there are no retx in RAR but a softbuffer is required)
      dl_sched_res->pdsch[n].softbuffer_tx[0] = &common_buffers[enb_cc_idx].rar_softbuffer_tx;

      // Assemble PDU
      dl_sched_res->pdsch[n].data[0] = assemble_rar(sched_result.rar[i].msg3_grant.data(),
                                                    enb_cc_idx,
                                                    sched_result.rar[i].msg3_grant.size(),
                                                    i,
                                                    sched_result.rar[i].tbs,
                                                    tti_tx_dl);

      if (pcap) {
        pcap->write_dl_ranti(dl_sched_res->pdsch[n].data[0],
                             sched_result.rar[i].tbs,
                             dl_sched_res->pdsch[n].dci.rnti,
                             true,
                             tti_tx_dl,
                             enb_cc_idx);
      }
      if (pcap_net) {
        pcap_net->write_dl_ranti(dl_sched_res->pdsch[n].data[0],
                                 sched_result.rar[i].tbs,
                                 dl_sched_res->pdsch[n].dci.rnti,
                                 true,
                                 tti_tx_dl,
                                 enb_cc_idx);
      }
      n++;
    }

    // Copy SI and Paging grants
    for (uint32_t i = 0; i < sched_result.bc.size(); i++) {
      // Copy dci info
      dl_sched_res->pdsch[n].dci = sched_result.bc[i].dci;

      // Set softbuffer
      if (sched_result.bc[i].type == sched_interface::dl_sched_bc_t::BCCH) {
        dl_sched_res->pdsch[n].softbuffer_tx[0] =
            &common_buffers[enb_cc_idx].bcch_softbuffer_tx[sched_result.bc[i].index];
        dl_sched_res->pdsch[n].data[0] = rrc_h->read_pdu_bcch_dlsch(enb_cc_idx, sched_result.bc[i].index);
#ifdef WRITE_SIB_PCAP
        if (pcap) {
          pcap->write_dl_sirnti(dl_sched_res->pdsch[n].data[0], sched_result.bc[i].tbs, true, tti_tx_dl, enb_cc_idx);
        }
        if (pcap_net) {
          pcap_net->write_dl_sirnti(
              dl_sched_res->pdsch[n].data[0], sched_result.bc[i].tbs, true, tti_tx_dl, enb_cc_idx);
        }
#endif
      } else {
        dl_sched_res->pdsch[n].softbuffer_tx[0] = &common_buffers[enb_cc_idx].pcch_softbuffer_tx;
        dl_sched_res->pdsch[n].data[0]          = common_buffers[enb_cc_idx].pcch_payload_buffer;
        rrc_h->read_pdu_pcch(tti_tx_dl, common_buffers[enb_cc_idx].pcch_payload_buffer, pcch_payload_buffer_len);

        if (pcap) {
          pcap->write_dl_pch(dl_sched_res->pdsch[n].data[0], sched_result.bc[i].tbs, true, tti_tx_dl, enb_cc_idx);
        }
        if (pcap_net) {
          pcap_net->write_dl_pch(dl_sched_res->pdsch[n].data[0], sched_result.bc[i].tbs, true, tti_tx_dl, enb_cc_idx);
        }
      }

      n++;
    }

    // Copy PDCCH order grants
    for (uint32_t i = 0; i < sched_result.po.size(); i++) {
      uint16_t rnti = sched_result.po[i].dci.rnti;
      if (ue_db.contains(rnti)) {
        // Copy dci info
        dl_sched_res->pdsch[n].dci = sched_result.po[i].dci;
        if (pcap) {
          pcap->write_dl_pch(dl_sched_res->pdsch[n].data[0], sched_result.po[i].tbs, true, tti_tx_dl, enb_cc_idx);
        }
        if (pcap_net) {
          pcap_net->write_dl_pch(dl_sched_res->pdsch[n].data[0], sched_result.po[i].tbs, true, tti_tx_dl, enb_cc_idx);
        }
        n++;
      } else {
        logger.warning("Invalid PDCCH order scheduling result. User 0x%x does not exist", rnti);
      }
    }

    dl_sched_res->nof_grants = n;

    // Number of CCH symbols
    dl_sched_res->cfi = sched_result.cfi;
  }

  // Count number of TTIs for all active users
  for (auto& u : ue_db) {
    u.second->metrics_cnt();
  }

  return SRSRAN_SUCCESS;
}

void mac::build_mch_sched(uint32_t tbs)
{
  int sfs_per_sched_period = mcch.pmch_info_list[0].sf_alloc_end;
  int bytes_per_sf         = tbs / 8 - 6; // leave 6 bytes for header

  int total_space_avail_bytes = sfs_per_sched_period * bytes_per_sf;

  int total_bytes_to_tx = 0;

  // calculate total bytes to be scheduled
  for (uint32_t i = 0; i < mch.num_mtch_sched; i++) {
    total_bytes_to_tx += mch.mtch_sched[i].lcid_buffer_size;
    mch.mtch_sched[i].stop = 0;
  }

  int last_mtch_stop = 0;

  if (total_bytes_to_tx > 0 && total_bytes_to_tx >= total_space_avail_bytes) {
    for (uint32_t i = 0; i < mch.num_mtch_sched; i++) {
      double ratio           = mch.mtch_sched[i].lcid_buffer_size / total_bytes_to_tx;
      float  assigned_sfs    = floor(sfs_per_sched_period * ratio);
      mch.mtch_sched[i].stop = last_mtch_stop + (uint32_t)assigned_sfs;
      last_mtch_stop         = mch.mtch_sched[i].stop;
    }
  } else {
    for (uint32_t i = 0; i < mch.num_mtch_sched; i++) {
      float assigned_sfs     = ceil(((float)mch.mtch_sched[i].lcid_buffer_size) / ((float)bytes_per_sf));
      mch.mtch_sched[i].stop = last_mtch_stop + (uint32_t)assigned_sfs;
      last_mtch_stop         = mch.mtch_sched[i].stop;
    }
  }
}

int mac::get_mch_sched(uint32_t tti, bool is_mcch, dl_sched_list_t& dl_sched_res_list)
{
  srsran::rwlock_read_guard lock(rwlock);
  dl_sched_t*               dl_sched_res = &dl_sched_res_list[0];
  logger.set_context(tti);
  srsran_ra_tb_t mcs      = {};
  srsran_ra_tb_t mcs_data = {};
  mcs.mcs_idx             = enum_to_number(this->sib13.mbsfn_area_info_list[0].mcch_cfg.sig_mcs);
  mcs_data.mcs_idx        = this->mcch.pmch_info_list[0].data_mcs;
  srsran_dl_fill_ra_mcs(&mcs, 0, cell_config[0].cell.nof_prb, false);
  srsran_dl_fill_ra_mcs(&mcs_data, 0, cell_config[0].cell.nof_prb, false);
  if (is_mcch) {
    build_mch_sched(mcs_data.tbs);
    mch.mcch_payload              = mcch_payload_buffer;
    mch.current_sf_allocation_num = 1;
    logger.info("MCH Sched Info: LCID: %d, Stop: %d, tti is %d ",
                mch.mtch_sched[0].lcid,
                mch.mtch_sched[mch.num_mtch_sched - 1].stop,
                tti);
    phy_h->set_mch_period_stop(mch.mtch_sched[mch.num_mtch_sched - 1].stop);
    for (uint32_t i = 0; i < mch.num_mtch_sched; i++) {
      mch.pdu[i].lcid = (uint32_t)srsran::mch_lcid::MCH_SCHED_INFO;
      // m1u.mtch_sched[i].lcid = 1+i;
    }

    mch.pdu[mch.num_mtch_sched].lcid   = 0;
    mch.pdu[mch.num_mtch_sched].nbytes = current_mcch_length;
    dl_sched_res->pdsch[0].dci.rnti    = SRSRAN_MRNTI;

    // we use TTI % HARQ to make sure we use different buffers for consecutive TTIs to avoid races between PHY workers
    ue_db[SRSRAN_MRNTI]->metrics_tx(true, mcs.tbs);
    dl_sched_res->pdsch[0].data[0] =
        ue_db[SRSRAN_MRNTI]->generate_mch_pdu(tti % SRSRAN_FDD_NOF_HARQ, mch, mch.num_mtch_sched + 1, mcs.tbs / 8);
  } else {
    uint32_t current_lcid = 1;
    uint32_t mtch_index   = 0;
    uint32_t mtch_stop    = mch.mtch_sched[mch.num_mtch_sched - 1].stop;

    for (uint32_t i = 0; i < mch.num_mtch_sched; i++) {
      if (mch.current_sf_allocation_num <= mch.mtch_sched[i].stop) {
        current_lcid = mch.mtch_sched[i].lcid;
        mtch_index   = i;
        break;
      }
    }
    if (mch.current_sf_allocation_num <= mtch_stop) {
      int requested_bytes = (mcs_data.tbs / 8 > (int)mch.mtch_sched[mtch_index].lcid_buffer_size)
                                ? (mch.mtch_sched[mtch_index].lcid_buffer_size)
                                : ((mcs_data.tbs / 8) - 2);
      int bytes_received = ue_db[SRSRAN_MRNTI]->read_pdu(current_lcid, mtch_payload_buffer, requested_bytes);
      mch.pdu[0].lcid    = current_lcid;
      mch.pdu[0].nbytes  = bytes_received;
      mch.mtch_sched[0].mtch_payload  = mtch_payload_buffer;
      dl_sched_res->pdsch[0].dci.rnti = SRSRAN_MRNTI;
      if (bytes_received) {
        ue_db[SRSRAN_MRNTI]->metrics_tx(true, mcs.tbs);
        dl_sched_res->pdsch[0].data[0] =
            ue_db[SRSRAN_MRNTI]->generate_mch_pdu(tti % SRSRAN_FDD_NOF_HARQ, mch, 1, mcs_data.tbs / 8);
      }
    } else {
      dl_sched_res->pdsch[0].dci.rnti = 0;
      dl_sched_res->pdsch[0].data[0]  = nullptr;
    }
    mch.current_sf_allocation_num++;
  }

  // Count number of TTIs for all active users
  for (auto& u : ue_db) {
    u.second->metrics_cnt();
  }
  return SRSRAN_SUCCESS;
}

uint8_t* mac::assemble_rar(sched_interface::dl_sched_rar_grant_t* grants,
                           uint32_t                               enb_cc_idx,
                           uint32_t                               nof_grants,
                           uint32_t                               rar_idx,
                           uint32_t                               pdu_len,
                           uint32_t                               tti)
{
  uint8_t grant_buffer[64] = {};
  if (pdu_len < rar_payload_len && rar_idx < rar_pdu_msg.size()) {
    srsran::rar_pdu* pdu = &rar_pdu_msg[rar_idx];
    rar_payload[enb_cc_idx][rar_idx].clear();
    pdu->init_tx(&rar_payload[enb_cc_idx][rar_idx], pdu_len);
    for (uint32_t i = 0; i < nof_grants; i++) {
      srsran_dci_rar_pack(&grants[i].grant, grant_buffer);
      if (pdu->new_subh()) {
        pdu->get()->set_rapid(grants[i].data.preamble_idx);
        pdu->get()->set_ta_cmd(grants[i].data.ta_cmd);
        pdu->get()->set_temp_crnti(grants[i].data.temp_crnti);
        pdu->get()->set_sched_grant(grant_buffer);
      }
    }
    if (pdu->write_packet(rar_payload[enb_cc_idx][rar_idx].msg)) {
      return rar_payload[enb_cc_idx][rar_idx].msg;
    }
  }

  logger.error("Assembling RAR: rar_idx=%d, pdu_len=%d, rar_payload_len=%d, nof_grants=%d",
               rar_idx,
               pdu_len,
               int(rar_payload_len),
               nof_grants);
  return nullptr;
}

int mac::get_ul_sched(uint32_t tti_tx_ul, ul_sched_list_t& ul_sched_res_list)
{
  if (!started) {
    return SRSRAN_SUCCESS;
  }

  logger.set_context(TTI_SUB(tti_tx_ul, FDD_HARQ_DELAY_UL_MS + FDD_HARQ_DELAY_DL_MS));

  srsran::rwlock_read_guard lock(rwlock);

  // Execute UE FSMs (e.g. TA)
  for (auto& ue : ue_db) {
    ue.second->tic();
  }

  for (uint32_t enb_cc_idx = 0; enb_cc_idx < cell_config.size(); enb_cc_idx++) {
    ul_sched_t* phy_ul_sched_res = &ul_sched_res_list[enb_cc_idx];

    // Run scheduler with current info
    sched_interface::ul_sched_res_t sched_result = {};
    if (scheduler.ul_sched(tti_tx_ul, enb_cc_idx, sched_result) < 0) {
      logger.error("Running scheduler");
      return SRSRAN_ERROR;
    }

    // Copy DCI grants
    phy_ul_sched_res->nof_grants = 0;
    int n                        = 0;
    for (uint32_t i = 0; i < sched_result.pusch.size(); i++) {
      if (sched_result.pusch[i].tbs > 0) {
        // Get UE
        uint16_t rnti = sched_result.pusch[i].dci.rnti;

        if (ue_db.contains(rnti)) {
          // Copy grant info
          phy_ul_sched_res->pusch[n].current_tx_nb = sched_result.pusch[i].current_tx_nb;
          phy_ul_sched_res->pusch[n].pid           = TTI_RX(tti_tx_ul) % SRSRAN_FDD_NOF_HARQ;
          phy_ul_sched_res->pusch[n].needs_pdcch   = sched_result.pusch[i].needs_pdcch;
          phy_ul_sched_res->pusch[n].dci           = sched_result.pusch[i].dci;
          phy_ul_sched_res->pusch[n].softbuffer_rx = ue_db[rnti]->get_rx_softbuffer(enb_cc_idx, tti_tx_ul);

          // If the Rx soft-buffer is not given, abort reception
          if (phy_ul_sched_res->pusch[n].softbuffer_rx == nullptr) {
            logger.warning("Failed to retrieve UL softbuffer for tti=%d, cc=%d", tti_tx_ul, enb_cc_idx);
            continue;
          }

          if (sched_result.pusch[n].current_tx_nb == 0) {
            srsran_softbuffer_rx_reset_tbs(phy_ul_sched_res->pusch[n].softbuffer_rx, sched_result.pusch[i].tbs * 8);
          }
          phy_ul_sched_res->pusch[n].data =
              ue_db[rnti]->request_buffer(tti_tx_ul, enb_cc_idx, sched_result.pusch[i].tbs);
          if (phy_ul_sched_res->pusch[n].data) {
            phy_ul_sched_res->nof_grants++;
          } else {
            logger.error("Grant for rnti=0x%x could not be allocated due to lack of buffers", rnti);
          }
          n++;
        } else {
          logger.warning("Invalid UL scheduling result. User 0x%x does not exist", rnti);
        }
      } else {
        logger.warning("Grant %d for rnti=0x%x has zero TBS", i, sched_result.pusch[i].dci.rnti);
      }
    }

    // Copy PHICH actions
    for (uint32_t i = 0; i < sched_result.phich.size(); i++) {
      phy_ul_sched_res->phich[i].ack  = sched_result.phich[i].phich == sched_interface::ul_sched_phich_t::ACK;
      phy_ul_sched_res->phich[i].rnti = sched_result.phich[i].rnti;
    }
    phy_ul_sched_res->nof_phich = sched_result.phich.size();
  }
  // clear old buffers from all users
  for (auto& u : ue_db) {
    u.second->clear_old_buffers(tti_tx_ul);
  }
  return SRSRAN_SUCCESS;
}

void mac::write_mcch(const srsran::sib2_mbms_t* sib2_,
                     const srsran::sib13_t*     sib13_,
                     const srsran::mcch_msg_t*  mcch_,
                     const uint8_t*             mcch_payload,
                     const uint8_t              mcch_payload_length)
{
  srsran::rwlock_write_guard lock(rwlock);
  mcch               = *mcch_;
  mch.num_mtch_sched = this->mcch.pmch_info_list[0].nof_mbms_session_info;
  for (uint32_t i = 0; i < mch.num_mtch_sched; ++i) {
    mch.mtch_sched[i].lcid = this->mcch.pmch_info_list[0].mbms_session_info_list[i].lc_ch_id;
  }
  sib2  = *sib2_;
  sib13 = *sib13_;
  memcpy(mcch_payload_buffer, mcch_payload, mcch_payload_length * sizeof(uint8_t));
  current_mcch_length = mcch_payload_length;

  unique_rnti_ptr<ue> ue_ptr = make_rnti_obj<ue>(
      SRSRAN_MRNTI, SRSRAN_MRNTI, 0, &scheduler, rrc_h, rlc_h, phy_h, logger, cells.size(), softbuffer_pool.get());

  auto ret = ue_db.insert(SRSRAN_MRNTI, std::move(ue_ptr));
  if (!ret) {
    logger.info("Failed to allocate rnti=0x%x.for eMBMS", SRSRAN_MRNTI);
  }
  rrc_h->add_user(SRSRAN_MRNTI, {});
}

// Internal helper function, caller must hold UE DB rwlock
bool mac::check_ue_active(uint16_t rnti)
{
  if (not ue_db.contains(rnti)) {
    logger.error("User rnti=0x%x not found", rnti);
    return false;
  }
  return ue_db[rnti]->is_active();
}


} // namespace srsenb
