/**
 * Author: Simon Lindholm, chilli
 * Date: 2018-07-23
 * License: CC0
 * Source: http://codeforces.com/blog/entry/60737
 * Description: Hash-Map. \\
 * std::unordered\_map-like API. \asciitilde3x faster, 1.5x more memory.
 */

#ifndef HMAP_HPP
#define HMAP_HPP

#include <chrono> /// keep-include
#include <bits/extc++.h> /// keep-include

using ll = long long; // exclude-line
namespace ch = std::chrono;

static // exclude-line
auto RNG = ch::steady_clock::now().time_since_epoch().count();
struct chash {
    const uint64_t C = ll(4e18 * acos(0)) | 71; // large odd
    ll operator()(ll x) const { return __builtin_bswap64((x ^ RNG) * C); }
};
template <class T, class H>
using fast_map = __gnu_pbds::gp_hash_table <T, H, chash>;

#endif // HMAP_HPP

