#define PROBLEM "https://judge.yosupo.jp/problem/associative_array"

//
// @MVB
//

#include <iostream>
#include "library/data-structures/HMap.hpp"

void solve() {
    int q; std::cin >> q;
    fast_map <ll, ll> H;
    for (int _{}; _ < q; ++_) {
        int task; ll k; std::cin >> task >> k;
        if (task == 0) {
            ll v; std::cin >> v;
            H[k] = v; continue;
        }
        std::cout << H[k] << '\n';
    }
}

int main() {
    std::cin.tie(nullptr)->sync_with_stdio(false);
    int test_cases = 1;
    while (test_cases--) { solve(); }
    return 0;
}
