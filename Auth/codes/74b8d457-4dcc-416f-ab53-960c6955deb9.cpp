#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    string str;
    getline(cin, str);  // Take input with spaces
    reverse(str.begin(), str.end());  // Built-in reverse
    cout << str << endl;
    return 0;
}
