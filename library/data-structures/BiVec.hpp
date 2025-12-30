/**
 * Author: Lucian Bicsi
 * Date: 2020-12-26
 * License: CC0
 * Description: Bi-directional std::vector. \\
 * Indices in $[-n..n)$.
 */

#ifndef BIVEC_HPP
#define BIVEC_HPP

#include <vector> // exclude-line

template <class T>
struct BiVec { 
    std::vector <T> v;
    BiVec(int n, T x = {}): v(2 * n, x) {}
    T& operator[](int i) { return v[2 * std::max(i, ~i) + (i < 0)]; }
    void resize(int n) { v.resize(2 * n); }
};

#endif // BIVEC_HPP

