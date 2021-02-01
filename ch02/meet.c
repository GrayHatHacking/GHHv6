// meet.c
#include <stdio.h>         // needed for screen printing
#include <string.h>        // needed for strcpy
void greeting(char *temp1,char *temp2){  // greeting function to say hello
   char name[400];         // string variable to hold the name
   strcpy(name, temp2);    // copy argument to name with the infamous strcpy
   printf("Hello %s %s\n", temp1, name);  // print out the greeting
}
int main(int argc, char * argv[]){    // note the format for arguments
   greeting(argv[1], argv[2]);        // call function, pass title & name
   printf("Bye %s %s\n", argv[1], argv[2]);  // say "bye"
}                                     // exit program

