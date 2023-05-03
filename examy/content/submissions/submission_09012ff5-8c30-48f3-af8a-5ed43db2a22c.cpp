#include <iostream>  
using namespace std;  
int main()  
{  
int a=10;  
int &value=a;  
value+=10;
std::cout << value << std::endl;  
std::cout << a << std::endl; 
return 0;  
}  