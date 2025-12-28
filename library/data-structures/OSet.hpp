/**
 * Author: @MVB
 * Date: 2025-12-18
 * License: CC0
 * Source: https://codeforces.com/blog/entry/11080
 * Description: Ordered Set. 
 * Supports fiding k-th element (0-indexed) and count of elements < x.
 * Time: $O(\log N)$
 */

#ifndef OSET_HPP
#define OSET_HPP

#include <bits/extc++.h> /// keep-include

template <class T>
using ordered_set = __gnu_pbds::tree <
    T,
    __gnu_pbds::null_type, // or type to get map functionality
    std::less <>, // less_equal <> is buggy
    __gnu_pbds::rb_tree_tag,
    __gnu_pbds::tree_order_statistics_node_update
>;
// *find_by_order() k-th element (0-indexed)
//  order_of_key(x) # of items that are < x
// For multiset use std::pair <T, int> with unique IDs.

#endif // OSET_HPP

