#include <stdio.h>

int main(void){
  int x = 0;
  while(1){
    if (x == 0) {
      printf("x = %d\n", x);
      x++;
      continue;
    }
    else {
      printf("x != 0\n");
      break;
    }
    return 0;
  }
}

