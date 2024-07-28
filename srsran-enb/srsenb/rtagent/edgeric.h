#ifndef EDGERIC_H
#define EDGERIC_H

#include <fstream>
#include <iostream>
#include <map>
#include <tuple>
#include <zmq.hpp>

#include "metrics.pb.h"
#include "scheduling_weights.pb.h"



class edgeric {
private:
    static int a;
    static int b;
    static std::map<uint16_t, float> weights_recved;

    static uint32_t tti_cnt;

    static std::map<uint16_t, uint32_t> pending_data_ues;
    static std::map<uint16_t, float> snr_ul_ues;
    static std::map<uint16_t, uint32_t> cqi_dl_ues;
    static std::map<uint16_t, float> rx_bytes_ues;
    static std::map<uint16_t, float> tx_bytes_ues;
    static std::map<uint16_t, uint32_t> backlogBufferDL;

    
    static bool initialized;

    static void ensure_initialized();
    

public:
    static bool enable_logging; // Logging flag

    static void init();
    //////////////////////////////////// Static setters - sets the metrics to be sent to EdgeRIC
    static void setVariable1(int v1) { a = v1; }
    static void setVariable2(int v2) { b = v2; }
    static void setTTI(uint32_t tti_count) {tti_cnt = tti_count;}

    //Setters
    static void setPendingDataUe(const std::map<uint16_t, uint32_t>& data) { pending_data_ues = data; }
    static void setULsnr(const std::map<uint16_t, float>& snr_ul) { snr_ul_ues = snr_ul; }
    static void setDLcqi(const std::map<uint16_t, uint32_t>& cqi_dl) { cqi_dl_ues = cqi_dl; }
    static void setRXbytes(const std::map<uint16_t, float>& rx_bytes) { rx_bytes_ues = rx_bytes; }
    static void setTXbytes(const std::map<uint16_t, float>& tx_bytes) { tx_bytes_ues = tx_bytes; }
    static void setbacklogDL(const std::map<uint16_t, uint32_t>& BL) { backlogBufferDL = BL; }

    //////////////////////////////////// ZMQ function to send RT-E2 Report 
    static void printmyvariables();
    static void send_to_er();
    static void send_to_er_protobuf();
    static void receive_from_er();
    static void receive_from_er_protobuf(); 
    //////////////////////////////////// ZMQ function to receive RT-E2 Policy - called at end of slot
    //static void get_from_er();

    //////////////////////////////////// Static getters - sets the control actions - called at slot beginning
    // static void getcontrol();
    static std::tuple<int, int> get_blanking();
    static std::map<uint16_t, float> get_weights();


};

#endif // EDGERIC_H

