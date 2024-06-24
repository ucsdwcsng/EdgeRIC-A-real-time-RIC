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

#ifndef SRSRAN_OBJ_ID_CMP_UTILS_H
#define SRSRAN_OBJ_ID_CMP_UTILS_H

#include "srsran/common/common.h"
#include <algorithm>
#include <cassert>

namespace srsran {

using asn1_obj_id_t = uint8_t;

/// Template function to generically obtain id of asn1 object (e.g. srb_id of srbs, drb_id of drbs, etc.)
template <typename Asn1Obj>
uint8_t get_asn1_obj_id(const Asn1Obj& obj);

/// Template function to generically set id of asn1 object (e.g. srb_id of srbs, drb_id of drbs, etc.)
template <typename Asn1Obj>
void set_asn1_obj_id(Asn1Obj& obj, uint8_t id);

/// helper macro to help define get_asn1_obj_id and set_asn1_obj_id for specific asn1 objects
#define ASN1_OBJ_ID_DEFINE(Asn1ObjType, member)                                                                        \
  template <>                                                                                                          \
  uint8_t get_asn1_obj_id<Asn1ObjType>(const Asn1ObjType& obj)                                                         \
  {                                                                                                                    \
    return obj.member;                                                                                                 \
  }                                                                                                                    \
  template <>                                                                                                          \
  void set_asn1_obj_id<Asn1ObjType>(Asn1ObjType & obj, uint8_t id)                                                     \
  {                                                                                                                    \
    obj.member = id;                                                                                                   \
  }

//! Functor to compare RRC config elements (e.g. SRB/measObj/Rep) based on ID
struct rrc_obj_id_cmp {
  template <typename T, typename U>
  typename std::enable_if<not std::is_integral<T>::value and not std::is_integral<U>::value, bool>::type
  operator()(const T& lhs, const U& rhs) const
  {
    return get_asn1_obj_id(lhs) < get_asn1_obj_id(rhs);
  }
  template <typename T>
  bool operator()(const T& lhs, asn1_obj_id_t id) const
  {
    return get_asn1_obj_id(lhs) < id;
  }
  template <typename T>
  bool operator()(asn1_obj_id_t id, const T& rhs) const
  {
    return id < get_asn1_obj_id(rhs);
  }
};

template <typename Container>
struct unary_rrc_obj_id {
  asn1_obj_id_t id;
  template <typename T>
  explicit unary_rrc_obj_id(T id_) : id(id_)
  {}
  bool operator()(const typename Container::value_type& e) const { return get_asn1_obj_id(e) == id; }
};

/// Find rrc object in list based on ID
template <typename Container, typename IdType>
typename Container::iterator find_rrc_obj_id(Container& c, IdType id)
{
  return std::find_if(c.begin(), c.end(), unary_rrc_obj_id<Container>{id});
}
template <typename Container, typename IdType>
typename Container::const_iterator find_rrc_obj_id(const Container& c, IdType id)
{
  return std::find_if(c.begin(), c.end(), unary_rrc_obj_id<Container>{id});
}

/// Find rrc object in sorted list based on ID (binary search)
template <typename Container, typename IdType>
typename Container::iterator sorted_find_rrc_obj_id(Container& c, IdType id)
{
  auto it = std::lower_bound(c.begin(), c.end(), id, rrc_obj_id_cmp{});
  return (it == c.end() or get_asn1_obj_id(*it) != id) ? c.end() : it;
}
template <typename Container, typename IdType>
typename Container::const_iterator sorted_find_rrc_obj_id(const Container& c, IdType id)
{
  auto it = std::lower_bound(c.begin(), c.end(), id, rrc_obj_id_cmp{});
  return (it == c.end() or get_asn1_obj_id(*it) != id) ? c.end() : it;
}

template <typename Container, typename Container2>
bool equal_rrc_obj_ids(const Container& c, const Container2& c2)
{
  return std::equal(c.begin(),
                    c.end(),
                    c2.begin(),
                    c2.end(),
                    [](const typename Container::value_type& e, const typename Container2::value_type& e2) {
                      return get_asn1_obj_id(e) == get_asn1_obj_id(e2);
                    });
}

//! Add Id to List in a sorted manner
template <typename Container, typename IdType>
typename Container::iterator add_rrc_obj_id(Container& c, IdType id)
{
  auto it = sorted_find_rrc_obj_id(c, id);
  if (it == c.end()) {
    c.push_back({});
    it = c.end() - 1;
    set_asn1_obj_id(*it, id);
    std::sort(c.begin(), c.end(), rrc_obj_id_cmp{});
    it = sorted_find_rrc_obj_id(c, id);
  }
  return it;
}

template <typename Container>
typename Container::iterator add_rrc_obj(Container& c, const typename Container::value_type& v)
{
  auto it = sorted_find_rrc_obj_id(c, get_asn1_obj_id(v));
  if (it == c.end()) {
    c.push_back(v);
    std::sort(c.begin(), c.end(), rrc_obj_id_cmp{});
    it = sorted_find_rrc_obj_id(c, get_asn1_obj_id(v));
  } else {
    *it = v;
  }
  return it;
}

template <typename Container, typename IdType>
bool rem_rrc_obj_id(Container& c, IdType id)
{
  auto it = sorted_find_rrc_obj_id(c, id);
  if (it != c.end()) {
    c.erase(it);
    return true;
  }
  return false;
}

/**
 * Find rrc obj id gap in list of rrc objs (e.g. {1, 2, 4} -> 3)
 * Expects list to be sorted
 * @return id value
 */
template <typename Container>
auto find_rrc_obj_id_gap(const Container& c) -> decltype(get_asn1_obj_id(c[0]))
{
  auto id_cmp_op = rrc_obj_id_cmp{};
  assert(std::is_sorted(c.begin(), c.end(), id_cmp_op));

  auto prev_it = c.begin();
  if (prev_it != c.end() and get_asn1_obj_id(*prev_it) == 1) {
    auto it = prev_it;
    for (++it; it != c.end(); prev_it = it, ++it) {
      if (get_asn1_obj_id(*it) > get_asn1_obj_id(*prev_it) + 1) {
        break;
      }
    }
  }
  return (prev_it == c.end()) ? 1 : get_asn1_obj_id(*prev_it) + 1; // starts at 1.
}

/**
 * Apply toAddModList changes
 * @param src_list original list of rrc fields
 * @param add_diff_list added/modified elements
 * @param target_list resulting list. (Can be same as src_list)
 */
template <typename AddModList>
void apply_addmodlist_diff(const AddModList& src_list, const AddModList& add_diff_list, AddModList& target_list)
{
  // Shortcut for empty case
  if (add_diff_list.size() == 0) {
    if (&target_list != &src_list) {
      target_list = src_list;
    }
    return;
  }
  auto id_cmp_op = rrc_obj_id_cmp{};
  assert(std::is_sorted(src_list.begin(), src_list.end(), id_cmp_op));
  assert(std::is_sorted(add_diff_list.begin(), add_diff_list.end(), id_cmp_op));

  AddModList l;
  std::set_union(
      add_diff_list.begin(), add_diff_list.end(), src_list.begin(), src_list.end(), std::back_inserter(l), id_cmp_op);
  target_list = l;
}

/**
 * Apply toRemoveList changes
 * @param src_list original list of rrc fields
 * @param rm_diff_list removed elements
 * @param target_list resulting list. (Can be same as src_list)
 */
template <typename AddModList, typename RemoveList>
void apply_remlist_diff(const AddModList& src_list, const RemoveList& rm_diff_list, AddModList& target_list)
{
  if (rm_diff_list.size() == 0) {
    if (&target_list != &src_list) {
      target_list = src_list;
    }
    return;
  }
  auto id_cmp_op = rrc_obj_id_cmp{};
  assert(std::is_sorted(src_list.begin(), src_list.end(), id_cmp_op));
  assert(std::is_sorted(rm_diff_list.begin(), rm_diff_list.end()));

  AddModList tmp_lst;
  std::set_difference(src_list.begin(),
                      src_list.end(),
                      rm_diff_list.begin(),
                      rm_diff_list.end(),
                      std::back_inserter(tmp_lst),
                      id_cmp_op);
  target_list = tmp_lst;
}
/**
 * Apply toAddModList/toRemoveList changes
 * @param src_list original list of rrc fields
 * @param add_diff_list added/modified elements
 * @param rm_diff_list removed elements
 * @param target_list resulting list. (Can be same as src_list)
 */
template <typename AddModList, typename RemoveList>
void apply_addmodremlist_diff(const AddModList& src_list,
                              const AddModList& add_diff_list,
                              const RemoveList& rm_diff_list,
                              AddModList&       target_list)
{
  if (add_diff_list.size() == 0 and rm_diff_list.size() == 0) {
    if (&target_list != &src_list) {
      target_list = src_list;
    }
    return;
  }
  auto id_cmp_op = rrc_obj_id_cmp{};
  assert(std::is_sorted(src_list.begin(), src_list.end(), id_cmp_op));
  assert(std::is_sorted(add_diff_list.begin(), add_diff_list.end(), id_cmp_op));
  assert(std::is_sorted(rm_diff_list.begin(), rm_diff_list.end()));

  AddModList tmp_lst;
  // apply remove list
  std::set_difference(src_list.begin(),
                      src_list.end(),
                      rm_diff_list.begin(),
                      rm_diff_list.end(),
                      std::back_inserter(tmp_lst),
                      id_cmp_op);

  // apply toaddmodlist
  target_list.clear();
  std::set_union(add_diff_list.begin(),
                 add_diff_list.end(),
                 tmp_lst.begin(),
                 tmp_lst.end(),
                 std::back_inserter(target_list),
                 id_cmp_op);
}

//! Update RRC field toAddModList
template <typename List, typename RemFunctor, typename AddFunctor, typename ModFunctor>
void compute_cfg_diff(const List& src_list,
                      const List& target_list,
                      RemFunctor  rem_func,
                      AddFunctor  add_func,
                      ModFunctor  mod_func)
{
  auto id_cmp_op = rrc_obj_id_cmp{};
  assert(std::is_sorted(src_list.begin(), src_list.end(), id_cmp_op));
  assert(std::is_sorted(target_list.begin(), target_list.end(), id_cmp_op));

  auto src_it    = src_list.begin();
  auto target_it = target_list.begin();

  bool src_left    = src_it != src_list.end();
  bool target_left = target_it != target_list.end();
  while (src_left or target_left) {
    if (not target_left or (src_left and id_cmp_op(*src_it, *target_it))) {
      rem_func(src_it++);
    } else if (not src_left or (target_left and id_cmp_op(*target_it, *src_it))) {
      // a new object has been added to target
      add_func(target_it++);
    } else {
      mod_func(src_it++, target_it++);
    }
    src_left    = src_it != src_list.end();
    target_left = target_it != target_list.end();
  }
}

template <typename toAddModList, typename RemoveList>
void compute_cfg_diff(const toAddModList& src_list,
                      const toAddModList& target_list,
                      toAddModList&       add_diff_list,
                      RemoveList&         rem_diff_list)
{
  if (&src_list == &target_list) {
    // early exit
    return;
  }

  if (&src_list == &add_diff_list) {
    // use const src_list
    toAddModList src_list2 = src_list;
    compute_cfg_diff(src_list2, target_list, add_diff_list, rem_diff_list);
    return;
  }

  if (&target_list == &add_diff_list) {
    // use const target_list
    toAddModList target_list2 = target_list;
    compute_cfg_diff(src_list, target_list2, add_diff_list, rem_diff_list);
    return;
  }

  using it_t    = typename toAddModList::const_iterator;
  auto rem_func = [&rem_diff_list](it_t rem_it) { rem_diff_list.push_back(get_asn1_obj_id(*rem_it)); };
  auto add_func = [&add_diff_list](it_t add_it) { add_diff_list.push_back(*add_it); };
  auto mod_func = [&add_diff_list](it_t src_it, it_t target_it) {
    if (not(*src_it == *target_it)) {
      add_diff_list.push_back(*target_it);
    }
  };
  compute_cfg_diff(src_list, target_list, rem_func, add_func, mod_func);
}

} // namespace srsran

#endif // SRSRAN_OBJ_ID_CMP_UTILS_H
