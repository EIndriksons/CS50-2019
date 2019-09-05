#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(int argc, string argv[])
{
    // Checks if input is not empty
    if (argc == 1)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    
    // Determines if argv[1] is actually integer
    int alpha = 0;
    for (int i = 0, j = strlen(argv[1]); i < j; i++)
    {
        char c = argv[1][i];
        if (isdigit(c) == 0)
        {
            alpha++;
        }
    }
         
    // Get key and check for validity if integer
    int key;
    if (argc == 2 && alpha == 0)
    {
        key = atoi(argv[1]);
    }
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    
    // Get plaintext
    string plaintext = get_string("plaintext: ");
    
    // Encipher and print plaintext
    char cc;
    string ciphertext[strlen(argv[1])];
    printf("ciphertext: ");
    for (int i = 0, j = strlen(plaintext); i < j; i++)
    {
        char c = plaintext[i];
        if (isupper(c) != 0) // If it is upper letter
        {
            cc = (c - 65 + key) % 26;
            cc = cc + 65;
            printf("%c", cc);
        }
        else if (islower(c) != 0) // If it is lower letter
        {
            cc = (c - 97 + key) % 26;
            cc = cc + 97;
            printf("%c", cc);
        }
        else
        {
            cc = c;
            printf("%c", cc);
        }
    }
    printf("\n");
}
