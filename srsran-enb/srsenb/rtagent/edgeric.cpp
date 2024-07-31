#include "edgeric.h"

// Definition of static member variables
int edgeric::a = 0;
int edgeric::b = 0;
uint32_t edgeric::tti_cnt = 0;
std::map<uint16_t, uint32_t> edgeric::pending_data_ues = {};
std::map<uint16_t, float> edgeric::weights_recved = {};
std::map<uint16_t, float> edgeric::snr_ul_ues = {};
std::map<uint16_t, uint32_t> edgeric::cqi_dl_ues = {};
std::map<uint16_t, float> edgeric::rx_bytes_ues = {};
std::map<uint16_t, float> edgeric::tx_bytes_ues = {};
std::map<uint16_t, uint32_t> edgeric::backlogBufferDL = {};

bool edgeric::enable_logging = false; // Initialize logging flag to false

zmq::context_t context;
zmq::socket_t publisher(context, ZMQ_PUB);
zmq::socket_t subscriber_weights(context, ZMQ_SUB);
zmq::socket_t subscriber_blanking(context, ZMQ_SUB);

bool edgeric::initialized = false;
int stale_flag = 0;
int er_index = 0;
int recv_cnt = 0;


void edgeric::init() {
    publisher.bind("ipc:///tmp/socket_snr_cqi");

    subscriber_weights.connect("ipc:///tmp/control_weights_actions");
    zmq_setsockopt(subscriber_weights, ZMQ_SUBSCRIBE, "", 0);
    // subscriber_weights.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    int conflate = 1;
    // subscriber_weights.setsockopt(ZMQ_CONFLATE, &conflate, sizeof(conflate));
    zmq_setsockopt(subscriber_weights, ZMQ_CONFLATE, &conflate, sizeof(conflate));


    // subscriber_blanking.connect("ipc:///tmp/control_blanking_actions");
    // subscriber_blanking.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    // // int conflate = 1;
    // subscriber_blanking.setsockopt(ZMQ_CONFLATE, &conflate, sizeof(conflate));

    initialized = true;
}

void edgeric::ensure_initialized() {
    if (!initialized) {
        init();
    }
}

void edgeric::printmyvariables() {
    if (enable_logging) { // Check if logging is enabled
        std::ofstream logfile("log.txt", std::ios_base::app); // Open log file in append mode
        if (logfile.is_open()) {
            logfile << "TTI: " << tti_cnt << " ER index: " << er_index << " Receive from edgeric count: " << recv_cnt << std::endl;
            logfile << "Stale Flag " << stale_flag << std::endl;
            logfile << "Variable a: " << a << std::endl;
            logfile << "Variable b: " << b << std::endl;

            logfile << "Pending Data UEs:" << std::endl;
            for (const auto& pair : pending_data_ues) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile << "Weights Received:" << std::endl;
            for (const auto& pair : weights_recved) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile << "UL SNR:" << std::endl;
            for (const auto& pair : snr_ul_ues) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile << "DL CQI:" << std::endl;
            for (const auto& pair : cqi_dl_ues) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile << "RX Bytes:" << std::endl;
            for (const auto& pair : rx_bytes_ues) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile << "TX Bytes:" << std::endl;
            for (const auto& pair : tx_bytes_ues) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile << "Backlog Buffer DL:" << std::endl;
            for (const auto& pair : backlogBufferDL) {
                logfile << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
            }

            logfile.close();
        } else {
            std::cerr << "Unable to open log file" << std::endl;
        }
    }
}

// void edgeric::send_to_er() {
//     std::string message;
//     ensure_initialized();

//     message += std::to_string(tti_cnt) + " ";

//     for (const auto& pair : cqi_dl_ues) {
//         uint16_t rnti = pair.first;

//         uint32_t cqi = cqi_dl_ues[rnti];
//         uint32_t bl = backlogBufferDL[rnti];
//         float snr = snr_ul_ues[rnti];
//         uint32_t pending_data = pending_data_ues[rnti];
//         float tx_bytes = tx_bytes_ues[rnti];
//         float rx_bytes = rx_bytes_ues[rnti];

//         message += std::to_string(rnti) + " " + std::to_string(cqi) + " " + 
//         std::to_string(bl) + " " + std::to_string(tx_bytes) + " " + std::to_string(rx_bytes) + 
//         " " + std::to_string(pending_data) + " " + std::to_string(snr) + " ";
//     }
//     int m_size = message.size();
//     zmq::message_t zmq_message(m_size);
//     snprintf((char*)zmq_message.data(), m_size + 1, "%s", message.c_str());
//     publisher.send(zmq_message, zmq::send_flags::none);
// }


void edgeric::send_to_er() {
    ensure_initialized();

    std::ostringstream message_stream;
    message_stream << tti_cnt << " ";

    for (const auto& pair : cqi_dl_ues) {
        uint16_t rnti = pair.first;
        uint32_t cqi = cqi_dl_ues[rnti];
        uint32_t bl = backlogBufferDL[rnti];
        float snr = snr_ul_ues[rnti];
        uint32_t pending_data = pending_data_ues[rnti];
        float tx_bytes = tx_bytes_ues[rnti];
        float rx_bytes = rx_bytes_ues[rnti];

        message_stream << rnti << " " << cqi << " " << bl << " "
                       << tx_bytes << " " << rx_bytes << " "
                       << pending_data << " " << snr << " ";
    }

    std::string message = message_stream.str();
    zmq::message_t zmq_message(message.size());
    memcpy(zmq_message.data(), message.c_str(), message.size());
    publisher.send(zmq_message, zmq::send_flags::none);
}

void edgeric::send_to_er_protobuf() {
    ensure_initialized();

    Metrics metrics_msg;
    metrics_msg.set_tti_cnt(tti_cnt);
    metrics_msg.set_ric_cnt(er_index);

    for (const auto& pair : cqi_dl_ues) {
        uint16_t rnti = pair.first;
        uint32_t cqi = cqi_dl_ues[rnti];
        uint32_t bl = backlogBufferDL[rnti];
        float snr = snr_ul_ues[rnti];
        uint32_t pending_data = pending_data_ues[rnti];
        float tx_bytes = tx_bytes_ues[rnti];
        float rx_bytes = rx_bytes_ues[rnti];

        UeMetrics* ue_metrics = metrics_msg.add_ue_metrics();
        ue_metrics->set_rnti(rnti);
        ue_metrics->set_cqi(cqi);
        ue_metrics->set_backlog(bl);
        ue_metrics->set_snr(snr);
        ue_metrics->set_pending_data(pending_data);
        ue_metrics->set_tx_bytes(tx_bytes);
        ue_metrics->set_rx_bytes(rx_bytes);
    }

    std::string serialized_msg;
    metrics_msg.SerializeToString(&serialized_msg);

    zmq::message_t zmq_message(serialized_msg.size());
    memcpy(zmq_message.data(), serialized_msg.data(), serialized_msg.size());

    publisher.send(zmq_message, zmq::send_flags::none);
}

// Get blanking function
std::tuple<int, int> edgeric::get_blanking() {
    return std::make_tuple(a, b);
}

// Get weights function
std::map<uint16_t, float> edgeric::get_weights() {
    return weights_recved;
}

void edgeric::receive_from_er() {
    ensure_initialized();

    zmq::message_t recv_message_er;
    auto size = subscriber_weights.recv(recv_message_er, zmq::recv_flags::dontwait);

    if (size) {
        std::string received_str(static_cast<char*>(recv_message_er.data()), recv_message_er.size());

        // Split the string into components
        std::istringstream iss(received_str);
        std::vector<std::string> tokens;
        std::string token;
        while (iss >> token) {
            tokens.push_back(token);
        }

        if (tokens.size() > 1) {
            uint32_t er_ran_index = std::stoi(tokens[0]);
            er_index = er_ran_index;
            if (er_ran_index==tti_cnt-1){
                stale_flag = 0;

            for (size_t i = 1; i < tokens.size() - 2; i += 2) {
                uint16_t rnti = std::stoi(tokens[i]);
                float weight = std::stof(tokens[i + 1]);
                weights_recved[rnti] = weight;
            }

            a = std::stoi(tokens[tokens.size() - 2]);
            b = std::stoi(tokens[tokens.size() - 1]);
        } else{
            stale_flag = 1;
            weights_recved = {};
            a = 0;
            b = 0;
        }
    }
    }else{
        stale_flag = 0;
        weights_recved = {};
        a = 0;
        b = 0;
    }
}

void edgeric::receive_from_er_protobuf() {
    ensure_initialized();

    // zmq::message_t recv_message_er;
    // auto size = subscriber_edgeric.recv(recv_message_er, zmq::recv_flags::dontwait);

    // if (size) {
    //     std::string received_str(static_cast<char*>(recv_message_er.data()), recv_message_er.size());

    //     // Parse the received string into a SchedulingWeights message
    //     SchedulingWeights msg;
    //     if (msg.ParseFromString(received_str)) {
    //         uint32_t er_ran_index = msg.ran_index();

    //         for (int i = 0; i < msg.weights_size(); ++i) {
    //             float weight = msg.weights(i);
    //             weights_recved[i] = weight;
    //         }

    //         a = msg.a();
    //         b = msg.b();
    //     } else {
    //         // Handle parse error
    //         std::cerr << "Failed to parse SchedulingWeights message." << std::endl;
    //     }
    // } else {
    //     weights_recved = {};
    //     a = 0;
    //     b = 0;
    // }

    zmq::message_t recv_message_er;
    auto size = subscriber_weights.recv(recv_message_er, zmq::recv_flags::dontwait);

    if (size) {
        std::string received_str(static_cast<char*>(recv_message_er.data()), recv_message_er.size());
        recv_cnt = recv_cnt+1;

        // Parse the received string into a SchedulingWeights message
        SchedulingWeights msg;
        if (msg.ParseFromString(received_str)) {
            uint32_t er_ran_index = msg.ran_index();
            er_index = er_ran_index;
            if(er_ran_index==tti_cnt-1 || er_ran_index==tti_cnt){
                stale_flag = 0;

            for (int i = 0; i < msg.weights_size(); ++i) {
                float weight = msg.weights(i);
                weights_recved[i] = weight;
            }
        } else{
            stale_flag = 1;
            // weights_recved = {};
        } 
        }else {
            // Handle parse error
            std::cerr << "Failed to parse SchedulingWeights message." << std::endl;
        }
        
    } else {
        stale_flag = 0;
        weights_recved = {};
    }

    // zmq::message_t recv_message_er_2;
    // auto size2 = subscriber_blanking.recv(recv_message_er_2, zmq::recv_flags::dontwait);

    // if (size2) {
    //     std::string received_str(static_cast<char*>(recv_message_er_2.data()), recv_message_er_2.size());

    //     // Parse the received string into a Blanking message
    //     Blanking msg;
    //     if (msg.ParseFromString(received_str)) {
    //         uint32_t er_ran_index = msg.ran_index();
    //         a = msg.a();
    //         b = msg.b();
    //     } else {
    //         // Handle parse error
    //         std::cerr << "Failed to parse Blanking message." << std::endl;
    //     }
    // } else {
    //     a = 0;
    //     b = 0;
    // }
}