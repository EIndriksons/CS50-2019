#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int shift(char k);

int main(int argc, string argv[])
{
    // Checks for valid input
    if (argc != 2)
    {
        // Input must be lenght of 2
        printf("Usage: ./vigenere keyword\n");
        return 1;
    }
    else
    {
        // Input must be alphabetical
        for (int i = 0, n = strlen(argv[1]); i < n; i++)
        {
            if (isalpha(argv[1][i]) == false)
            {
                printf("Usage: ./vigenere keyword\n");
                return 1;
            }
        }
    }
    
    // If all good - saves the key
    string keyword = argv[1];
    
    // Get plaintext
    string plaintext = get_string("plaintext: ");
    
    // Encipher
    printf("ciphertext: ");
    for (int i = 0, j = 0, ni = strlen(plaintext); i < ni; i++, j++)
    {
        // Resetting keyword counter if required
        int nj = strlen(keyword);
        if (j >= nj)
        {
            j = 0;
        }
        
        // Enciphering character
        char c = plaintext[i], cc;
        if (isupper(c) != 0) // If it is upper letter
        {
            cc = (c - 65 + shift(keyword[j])) % 26;
            cc = cc + 65;
            printf("%c", cc);
        }
        else if (islower(c) != 0) // If it is lower letter
        {
            cc = (c - 97 + shift(keyword[j])) % 26;
            cc = cc + 97;
            printf("%c", cc);
        }
        else
        {
            cc = c;
            printf("%c", cc);
            j--;
        }
    }
    printf("\n");
}

// Returns key shift required for that char of keyword
int shift(char c)
{
    int key;
    if (isupper(c) != 0) // If it is upper letter
    {
        key = (c - 65) % 26;
    }
    else if (islower(c) != 0) // If it is lower letter
    {
        key = (c - 97) % 26;
    }
    else // If it is some other char type
    {
        key = c;
    }
    
    return key;
}
