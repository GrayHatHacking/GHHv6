// memory.c
#include <stdlib.h>
#include <string.h>
/* memory.c */        // this comment simply holds the program name
  int _index = 5;     // integer stored in data (initialized)
  char * str;         // string stored in bss (uninitialized)
  int nothing;        // integer stored in bss (uninitialized)
void funct1(int c){ // bracket starts function1 block with argument (c)
  int i=c;                                   // stored in the stack region
  str = (char*) malloc (10 * sizeof (char)); // Reserves 10 characters in
                                              // the heap region
  strncpy(str, "abcde", 5);  // copies 5 characters "abcde" into str
}                            // end of function1
void main (){                // the required main function
  funct1(1);                 // main calls function1 with an argument
}                            // end of the main function

