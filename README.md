# MVB-Kit

This repo hosts MVB-Kit, mean to serve as an ICPC team reference document. Consists of 25 pages of copy-pastable C++ code, for use in ICPC-style programming competitions

The PDF is built automatically by CI.
Download it from **Actions → latest successful run → Artifacts**.

Sources are in [`library/`](./library/).

---

## Cusomizing Kit

All code processing and display in documents is handled by [**`preprocessor.py`**](`./library/tex/preprocessor.py`).
Currently, it is designed for **C++**, but it can be extended to handle other languages.

### File Structure & Style

* Header files should use `.hpp` extensions with **header guards**.
* Prefer `std::` explicitly over `using namespace std;` for efficiency and clarity.
* Each file should start with a **C++ style comment block (`/** */`)** containing:
  * **Author** (required)
  * **Source** (optional)
  * **Description** (required)
  * **Time** (optional)
  * **Memory** (optional)
  * **Warning** (optional, formatted as **bold**)

#### Code Commands & Display Rules

* **`///`**: Marks multiple variations of code; these will be displayed without `///` and document alternative approaches.
* **`// keep-include`**: Displays the library header inline in the code instead of the global includes section.
* **`// exclude-line`**: Excludes a specific line from being displayed (e.g., typedefs like `using ll = long long;`).
* **`// exclude-function`**: Excludes entire functions or code blocks from display.


### Additional Features

* Both `.h` and `.hpp` are handled, but `.hpp` is preferred for style consistency.
* Code sections display their **dependencies** (header files) for clarity.
* Each code block has a **unique hashcode** for easy reference and integration.
* Commands are inspired by **KACTL**, ensuring organized, documented, and reusable algorithms.

### Example

```cpp
/** 
 * Author: Mihnea
 * Source: MyLibrary
 * Description: Example of command usage in documentation
 * Time: O(n)
 * Memory: O(1)
 * Warning: Demonstration only
 */

#include <bits/stdc++.h>

// Example of multiple variations
/// void printNumbers() { for(int i=0;i<5;i++) cout<<i<<" "; }
// Alternative approach
void printNumbers() { 
    std::vector <int> line;
    for(int i=0;i<5;i++) cout<<i<<" ",line.emplace_back(i); 
}

// Keep-include example: this header will show inline in the code display
#include <algorithm> // keep-include

// Exclude-line example: this line will not be displayed
using ll = long long; // exclude-line

// exclude-function (this function wil lbe excluded)
void hiddenFunction() { cout << "You won't see this"; }
// exclude-function (should have two instances)

int main() {
    printNumbers(); // Displays: 0 1 2 3 4
    return 0;
}
```

---
