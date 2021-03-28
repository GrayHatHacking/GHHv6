#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int func1(char* input)
{

	char string1[60];

	strcpy(string1, input);
	printf("You entered %s", string1);
	return 0;
}

int main(int argc, char* argv[])
{

        if(argc !=2){
                printf("Usage: Enter Something\n");
                exit(1);}

func1(argv[1]);
return 0;
}
