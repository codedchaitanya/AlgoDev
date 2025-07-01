#include <iostream>
#include <string>
#include <algorithm> // for reverse()

int main() {
    std::string str;

    std::cout << "Enter a string: ";
    std::getline(std::cin, str);

    // Method 1: Using built-in reverse function
    std::reverse(str.begin(), str.end());

    std::cout << "Reversed string: " << str << std::endl;

    return 0;
}
