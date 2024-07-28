// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: metrics.proto

#ifndef PROTOBUF_INCLUDED_metrics_2eproto
#define PROTOBUF_INCLUDED_metrics_2eproto

#include <string>

#include <google/protobuf/stubs/common.h>

#if GOOGLE_PROTOBUF_VERSION < 3006001
#error This file was generated by a newer version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please update
#error your headers.
#endif
#if 3006001 < GOOGLE_PROTOBUF_MIN_PROTOC_VERSION
#error This file was generated by an older version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please
#error regenerate this file with a newer version of protoc.
#endif

#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/arena.h>
#include <google/protobuf/arenastring.h>
#include <google/protobuf/generated_message_table_driven.h>
#include <google/protobuf/generated_message_util.h>
#include <google/protobuf/inlined_string_field.h>
#include <google/protobuf/metadata.h>
#include <google/protobuf/message.h>
#include <google/protobuf/repeated_field.h>  // IWYU pragma: export
#include <google/protobuf/extension_set.h>  // IWYU pragma: export
#include <google/protobuf/unknown_field_set.h>
// @@protoc_insertion_point(includes)
#define PROTOBUF_INTERNAL_EXPORT_protobuf_metrics_2eproto 

namespace protobuf_metrics_2eproto {
// Internal implementation detail -- do not use these members.
struct TableStruct {
  static const ::google::protobuf::internal::ParseTableField entries[];
  static const ::google::protobuf::internal::AuxillaryParseTableField aux[];
  static const ::google::protobuf::internal::ParseTable schema[2];
  static const ::google::protobuf::internal::FieldMetadata field_metadata[];
  static const ::google::protobuf::internal::SerializationTable serialization_table[];
  static const ::google::protobuf::uint32 offsets[];
};
void AddDescriptors();
}  // namespace protobuf_metrics_2eproto
class Metrics;
class MetricsDefaultTypeInternal;
extern MetricsDefaultTypeInternal _Metrics_default_instance_;
class UeMetrics;
class UeMetricsDefaultTypeInternal;
extern UeMetricsDefaultTypeInternal _UeMetrics_default_instance_;
namespace google {
namespace protobuf {
template<> ::Metrics* Arena::CreateMaybeMessage<::Metrics>(Arena*);
template<> ::UeMetrics* Arena::CreateMaybeMessage<::UeMetrics>(Arena*);
}  // namespace protobuf
}  // namespace google

// ===================================================================

class UeMetrics : public ::google::protobuf::Message /* @@protoc_insertion_point(class_definition:UeMetrics) */ {
 public:
  UeMetrics();
  virtual ~UeMetrics();

  UeMetrics(const UeMetrics& from);

  inline UeMetrics& operator=(const UeMetrics& from) {
    CopyFrom(from);
    return *this;
  }
  #if LANG_CXX11
  UeMetrics(UeMetrics&& from) noexcept
    : UeMetrics() {
    *this = ::std::move(from);
  }

  inline UeMetrics& operator=(UeMetrics&& from) noexcept {
    if (GetArenaNoVirtual() == from.GetArenaNoVirtual()) {
      if (this != &from) InternalSwap(&from);
    } else {
      CopyFrom(from);
    }
    return *this;
  }
  #endif
  static const ::google::protobuf::Descriptor* descriptor();
  static const UeMetrics& default_instance();

  static void InitAsDefaultInstance();  // FOR INTERNAL USE ONLY
  static inline const UeMetrics* internal_default_instance() {
    return reinterpret_cast<const UeMetrics*>(
               &_UeMetrics_default_instance_);
  }
  static constexpr int kIndexInFileMessages =
    0;

  void Swap(UeMetrics* other);
  friend void swap(UeMetrics& a, UeMetrics& b) {
    a.Swap(&b);
  }

  // implements Message ----------------------------------------------

  inline UeMetrics* New() const final {
    return CreateMaybeMessage<UeMetrics>(NULL);
  }

  UeMetrics* New(::google::protobuf::Arena* arena) const final {
    return CreateMaybeMessage<UeMetrics>(arena);
  }
  void CopyFrom(const ::google::protobuf::Message& from) final;
  void MergeFrom(const ::google::protobuf::Message& from) final;
  void CopyFrom(const UeMetrics& from);
  void MergeFrom(const UeMetrics& from);
  void Clear() final;
  bool IsInitialized() const final;

  size_t ByteSizeLong() const final;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input) final;
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const final;
  ::google::protobuf::uint8* InternalSerializeWithCachedSizesToArray(
      bool deterministic, ::google::protobuf::uint8* target) const final;
  int GetCachedSize() const final { return _cached_size_.Get(); }

  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const final;
  void InternalSwap(UeMetrics* other);
  private:
  inline ::google::protobuf::Arena* GetArenaNoVirtual() const {
    return NULL;
  }
  inline void* MaybeArenaPtr() const {
    return NULL;
  }
  public:

  ::google::protobuf::Metadata GetMetadata() const final;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // uint32 rnti = 1;
  void clear_rnti();
  static const int kRntiFieldNumber = 1;
  ::google::protobuf::uint32 rnti() const;
  void set_rnti(::google::protobuf::uint32 value);

  // uint32 cqi = 2;
  void clear_cqi();
  static const int kCqiFieldNumber = 2;
  ::google::protobuf::uint32 cqi() const;
  void set_cqi(::google::protobuf::uint32 value);

  // uint32 backlog = 3;
  void clear_backlog();
  static const int kBacklogFieldNumber = 3;
  ::google::protobuf::uint32 backlog() const;
  void set_backlog(::google::protobuf::uint32 value);

  // float snr = 4;
  void clear_snr();
  static const int kSnrFieldNumber = 4;
  float snr() const;
  void set_snr(float value);

  // uint32 pending_data = 5;
  void clear_pending_data();
  static const int kPendingDataFieldNumber = 5;
  ::google::protobuf::uint32 pending_data() const;
  void set_pending_data(::google::protobuf::uint32 value);

  // float tx_bytes = 6;
  void clear_tx_bytes();
  static const int kTxBytesFieldNumber = 6;
  float tx_bytes() const;
  void set_tx_bytes(float value);

  // float rx_bytes = 7;
  void clear_rx_bytes();
  static const int kRxBytesFieldNumber = 7;
  float rx_bytes() const;
  void set_rx_bytes(float value);

  // @@protoc_insertion_point(class_scope:UeMetrics)
 private:

  ::google::protobuf::internal::InternalMetadataWithArena _internal_metadata_;
  ::google::protobuf::uint32 rnti_;
  ::google::protobuf::uint32 cqi_;
  ::google::protobuf::uint32 backlog_;
  float snr_;
  ::google::protobuf::uint32 pending_data_;
  float tx_bytes_;
  float rx_bytes_;
  mutable ::google::protobuf::internal::CachedSize _cached_size_;
  friend struct ::protobuf_metrics_2eproto::TableStruct;
};
// -------------------------------------------------------------------

class Metrics : public ::google::protobuf::Message /* @@protoc_insertion_point(class_definition:Metrics) */ {
 public:
  Metrics();
  virtual ~Metrics();

  Metrics(const Metrics& from);

  inline Metrics& operator=(const Metrics& from) {
    CopyFrom(from);
    return *this;
  }
  #if LANG_CXX11
  Metrics(Metrics&& from) noexcept
    : Metrics() {
    *this = ::std::move(from);
  }

  inline Metrics& operator=(Metrics&& from) noexcept {
    if (GetArenaNoVirtual() == from.GetArenaNoVirtual()) {
      if (this != &from) InternalSwap(&from);
    } else {
      CopyFrom(from);
    }
    return *this;
  }
  #endif
  static const ::google::protobuf::Descriptor* descriptor();
  static const Metrics& default_instance();

  static void InitAsDefaultInstance();  // FOR INTERNAL USE ONLY
  static inline const Metrics* internal_default_instance() {
    return reinterpret_cast<const Metrics*>(
               &_Metrics_default_instance_);
  }
  static constexpr int kIndexInFileMessages =
    1;

  void Swap(Metrics* other);
  friend void swap(Metrics& a, Metrics& b) {
    a.Swap(&b);
  }

  // implements Message ----------------------------------------------

  inline Metrics* New() const final {
    return CreateMaybeMessage<Metrics>(NULL);
  }

  Metrics* New(::google::protobuf::Arena* arena) const final {
    return CreateMaybeMessage<Metrics>(arena);
  }
  void CopyFrom(const ::google::protobuf::Message& from) final;
  void MergeFrom(const ::google::protobuf::Message& from) final;
  void CopyFrom(const Metrics& from);
  void MergeFrom(const Metrics& from);
  void Clear() final;
  bool IsInitialized() const final;

  size_t ByteSizeLong() const final;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input) final;
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const final;
  ::google::protobuf::uint8* InternalSerializeWithCachedSizesToArray(
      bool deterministic, ::google::protobuf::uint8* target) const final;
  int GetCachedSize() const final { return _cached_size_.Get(); }

  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const final;
  void InternalSwap(Metrics* other);
  private:
  inline ::google::protobuf::Arena* GetArenaNoVirtual() const {
    return NULL;
  }
  inline void* MaybeArenaPtr() const {
    return NULL;
  }
  public:

  ::google::protobuf::Metadata GetMetadata() const final;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // repeated .UeMetrics ue_metrics = 2;
  int ue_metrics_size() const;
  void clear_ue_metrics();
  static const int kUeMetricsFieldNumber = 2;
  ::UeMetrics* mutable_ue_metrics(int index);
  ::google::protobuf::RepeatedPtrField< ::UeMetrics >*
      mutable_ue_metrics();
  const ::UeMetrics& ue_metrics(int index) const;
  ::UeMetrics* add_ue_metrics();
  const ::google::protobuf::RepeatedPtrField< ::UeMetrics >&
      ue_metrics() const;

  // uint32 tti_cnt = 1;
  void clear_tti_cnt();
  static const int kTtiCntFieldNumber = 1;
  ::google::protobuf::uint32 tti_cnt() const;
  void set_tti_cnt(::google::protobuf::uint32 value);

  // uint32 ric_cnt = 3;
  void clear_ric_cnt();
  static const int kRicCntFieldNumber = 3;
  ::google::protobuf::uint32 ric_cnt() const;
  void set_ric_cnt(::google::protobuf::uint32 value);

  // @@protoc_insertion_point(class_scope:Metrics)
 private:

  ::google::protobuf::internal::InternalMetadataWithArena _internal_metadata_;
  ::google::protobuf::RepeatedPtrField< ::UeMetrics > ue_metrics_;
  ::google::protobuf::uint32 tti_cnt_;
  ::google::protobuf::uint32 ric_cnt_;
  mutable ::google::protobuf::internal::CachedSize _cached_size_;
  friend struct ::protobuf_metrics_2eproto::TableStruct;
};
// ===================================================================


// ===================================================================

#ifdef __GNUC__
  #pragma GCC diagnostic push
  #pragma GCC diagnostic ignored "-Wstrict-aliasing"
#endif  // __GNUC__
// UeMetrics

// uint32 rnti = 1;
inline void UeMetrics::clear_rnti() {
  rnti_ = 0u;
}
inline ::google::protobuf::uint32 UeMetrics::rnti() const {
  // @@protoc_insertion_point(field_get:UeMetrics.rnti)
  return rnti_;
}
inline void UeMetrics::set_rnti(::google::protobuf::uint32 value) {
  
  rnti_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.rnti)
}

// uint32 cqi = 2;
inline void UeMetrics::clear_cqi() {
  cqi_ = 0u;
}
inline ::google::protobuf::uint32 UeMetrics::cqi() const {
  // @@protoc_insertion_point(field_get:UeMetrics.cqi)
  return cqi_;
}
inline void UeMetrics::set_cqi(::google::protobuf::uint32 value) {
  
  cqi_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.cqi)
}

// uint32 backlog = 3;
inline void UeMetrics::clear_backlog() {
  backlog_ = 0u;
}
inline ::google::protobuf::uint32 UeMetrics::backlog() const {
  // @@protoc_insertion_point(field_get:UeMetrics.backlog)
  return backlog_;
}
inline void UeMetrics::set_backlog(::google::protobuf::uint32 value) {
  
  backlog_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.backlog)
}

// float snr = 4;
inline void UeMetrics::clear_snr() {
  snr_ = 0;
}
inline float UeMetrics::snr() const {
  // @@protoc_insertion_point(field_get:UeMetrics.snr)
  return snr_;
}
inline void UeMetrics::set_snr(float value) {
  
  snr_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.snr)
}

// uint32 pending_data = 5;
inline void UeMetrics::clear_pending_data() {
  pending_data_ = 0u;
}
inline ::google::protobuf::uint32 UeMetrics::pending_data() const {
  // @@protoc_insertion_point(field_get:UeMetrics.pending_data)
  return pending_data_;
}
inline void UeMetrics::set_pending_data(::google::protobuf::uint32 value) {
  
  pending_data_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.pending_data)
}

// float tx_bytes = 6;
inline void UeMetrics::clear_tx_bytes() {
  tx_bytes_ = 0;
}
inline float UeMetrics::tx_bytes() const {
  // @@protoc_insertion_point(field_get:UeMetrics.tx_bytes)
  return tx_bytes_;
}
inline void UeMetrics::set_tx_bytes(float value) {
  
  tx_bytes_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.tx_bytes)
}

// float rx_bytes = 7;
inline void UeMetrics::clear_rx_bytes() {
  rx_bytes_ = 0;
}
inline float UeMetrics::rx_bytes() const {
  // @@protoc_insertion_point(field_get:UeMetrics.rx_bytes)
  return rx_bytes_;
}
inline void UeMetrics::set_rx_bytes(float value) {
  
  rx_bytes_ = value;
  // @@protoc_insertion_point(field_set:UeMetrics.rx_bytes)
}

// -------------------------------------------------------------------

// Metrics

// uint32 tti_cnt = 1;
inline void Metrics::clear_tti_cnt() {
  tti_cnt_ = 0u;
}
inline ::google::protobuf::uint32 Metrics::tti_cnt() const {
  // @@protoc_insertion_point(field_get:Metrics.tti_cnt)
  return tti_cnt_;
}
inline void Metrics::set_tti_cnt(::google::protobuf::uint32 value) {
  
  tti_cnt_ = value;
  // @@protoc_insertion_point(field_set:Metrics.tti_cnt)
}

// repeated .UeMetrics ue_metrics = 2;
inline int Metrics::ue_metrics_size() const {
  return ue_metrics_.size();
}
inline void Metrics::clear_ue_metrics() {
  ue_metrics_.Clear();
}
inline ::UeMetrics* Metrics::mutable_ue_metrics(int index) {
  // @@protoc_insertion_point(field_mutable:Metrics.ue_metrics)
  return ue_metrics_.Mutable(index);
}
inline ::google::protobuf::RepeatedPtrField< ::UeMetrics >*
Metrics::mutable_ue_metrics() {
  // @@protoc_insertion_point(field_mutable_list:Metrics.ue_metrics)
  return &ue_metrics_;
}
inline const ::UeMetrics& Metrics::ue_metrics(int index) const {
  // @@protoc_insertion_point(field_get:Metrics.ue_metrics)
  return ue_metrics_.Get(index);
}
inline ::UeMetrics* Metrics::add_ue_metrics() {
  // @@protoc_insertion_point(field_add:Metrics.ue_metrics)
  return ue_metrics_.Add();
}
inline const ::google::protobuf::RepeatedPtrField< ::UeMetrics >&
Metrics::ue_metrics() const {
  // @@protoc_insertion_point(field_list:Metrics.ue_metrics)
  return ue_metrics_;
}

// uint32 ric_cnt = 3;
inline void Metrics::clear_ric_cnt() {
  ric_cnt_ = 0u;
}
inline ::google::protobuf::uint32 Metrics::ric_cnt() const {
  // @@protoc_insertion_point(field_get:Metrics.ric_cnt)
  return ric_cnt_;
}
inline void Metrics::set_ric_cnt(::google::protobuf::uint32 value) {
  
  ric_cnt_ = value;
  // @@protoc_insertion_point(field_set:Metrics.ric_cnt)
}

#ifdef __GNUC__
  #pragma GCC diagnostic pop
#endif  // __GNUC__
// -------------------------------------------------------------------


// @@protoc_insertion_point(namespace_scope)


// @@protoc_insertion_point(global_scope)

#endif  // PROTOBUF_INCLUDED_metrics_2eproto
