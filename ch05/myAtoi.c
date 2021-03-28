#include <stdio.h>
#include <stdlib.h>

int myAtoi(char *str){
    int res = 0;
    for (int i = 0; str[i] != '\0'; ++i)
        res = res*10 + str[i] - '0';
    return res;
}

int main(){
    char str[] = "1234";
    int val = myAtoi(str);
    printf("Value is: %d\n", val);
    return 0;
}

