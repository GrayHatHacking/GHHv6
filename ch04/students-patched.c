// students.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[24];
    int id;
    int grades;
} Student;

char admin_password[32] = "Ultr4S3cr3tP4ssw0rd!";
Student students[32];
int count = 0;

void LoadStudents() {
    memset(&students, 0, sizeof(Student)*32);
    FILE *f = fopen("students.csv", "r");
    if (!f) {
        printf("ERROR: 'students.csv' database file missing!\n");
        exit(0);
    }
    char line[128];
    for (count=0; count < 32 && !feof(f); count++) {
        fscanf(f, "%128s\n", &line);
        char *coma = strchr(line, ',');
        coma[0] = 0;
        students[count].id = count;
        strncpy(students[count].name, line, 24);
        students[count].grades = atoi(&coma[1]);
    }
    fclose(f);
}

void ListStudents() {
    printf("\nNum Name         Grades\n");
    for (int i = 0; i < count; i++) {
        printf("%d - %s\t%6d\n", i, students[i].name, students[i].grades);
    }
}

int ViewStudentGrades() {
    int i;
    printf("Enter student number: ");
    scanf("%d", &i);
    if (i < 0 || i > count) {
        printf("Invalid student number!\n");
        return -1;
    }
    printf("\nNum Name         Grades\n");
    printf("%d - %s\t%6d\n", i, students[i].name, students[i].grades);
    return i;
}

void ChangeStudentGrades() {
    char pass[32];
    printf("Enter admin password: ");
    scanf("%32s", &pass);

    if (strcmp(pass, admin_password)) {
        printf("Incorrect password!\n\n");
        return;
    }

    int idx, grades;
    if ((idx = ViewStudentGrades()) == -1) {
        return;
    }
    printf("Enter new grades: ");
    scanf("%d", &grades);
    students[idx].grades = grades;
    printf("\n%s's new grade is %d\n", students[idx].name, grades);
}

void main(void) {
    int opt;
    LoadStudents();
    for (;;) {
        printf(
            "\n=========================\n"
            " Grades Management       \n"
            "=========================\n"
            " 1) List students\n"
            " 2) View grades\n"
            " 3) Change grades\n"
            " 4) Exit\n"
            "=========================\n"
            "Enter option: ");
        scanf("%i", &opt);
        switch (opt) {
            case 1: ListStudents(); break;
            case 2: ViewStudentGrades(); break;
            case 3: ChangeStudentGrades(); break;
            case 4: return;
            default: printf("Invalid Option!\n");
    }
  }
}
