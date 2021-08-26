#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
	char *ghh = malloc(30);
	strncpy(ghh, "Gray Hat Hacking", 16);
	printf("%s - ", ghh);
	free(ghh);
	puts("6th Edition");
	return 0;
}

