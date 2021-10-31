#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <errno.h>
#include <sys/wait.h>

#define BUFLEN 64
#define BIND_ADDRESS "127.0.0.1"
#define PORT 4446

const char secret_pass[] = "Ultr4S3cr3tP4ssw0rd!";

int auth(int connfd) {

    char msg[] = "User Access Verification\n\nPassword: ";
    write(connfd, msg, strlen(msg)); 

    char buf[BUFLEN];
    read(connfd, buf, 512);

    return (strncmp(buf, secret_pass, strlen(secret_pass)) == 0);
}

int main(void) {

  int sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {
      perror("socket() error...\n");
      return -1;
  }
  
  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) == -1) {
    perror("setsockopt() error...\n");
    return -1;
  }
  
  struct sockaddr_in sa;
  memset(&sa, 0, sizeof(sa));
  sa.sin_family = AF_INET;
  sa.sin_port = htons(PORT);
  sa.sin_addr.s_addr = htonl(INADDR_ANY);
  if (inet_aton(BIND_ADDRESS, &sa.sin_addr) == 0) {
    perror("Invalid address\n");
    close(sockfd);
    return -1;
  }
  
  if (bind(sockfd, (struct sockaddr*) &sa, sizeof(sa)) == -1) {
    printf("Can't bind on %s:%d.\n", BIND_ADDRESS, PORT);
    close(sockfd);
    return -1;
  }

  if (listen(sockfd, 1) == -1) {
    printf("error: %s\n", strerror(errno));
    close(sockfd);
    return -1;
  }

  printf("Listening on %s:%d\n", BIND_ADDRESS, PORT);

  struct sockaddr_in peer_addr;
  socklen_t addr_len = sizeof(peer_addr);
  int connfd;
  while(1) {

    if ((connfd = accept(sockfd, (struct sockaddr*) &peer_addr, &addr_len)) < 0)
        exit(-1);

    pid_t pid = fork();
    if (pid == -1) {
      perror("fork");
      exit(0);
    }
    
    if (pid == 0) { //Child
        close(sockfd);

        if (auth(connfd) == 1) {
            char success[] = "Login Successful!";
            write(connfd, success, strlen(success));

        } else {
            char invalid[] = "Invalid Pasword!";
            write(connfd, invalid, strlen(invalid));
        }

    } else if (pid > 0) { //parent
      close(connfd);
    }
  }
  
  return 0;
}

