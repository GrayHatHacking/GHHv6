//smallbuff.c
#include <string.h>
int main(int argc, char * argv[]){
    char buff[10];  //small buffer
    strcpy(buff, argv[1]);  //vulnerable function call
    return 0;
}

