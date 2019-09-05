#define _XOPEN_SOURCE
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <cs50.h>

int main(int argc, string argv[])
{
    // Check for valid input
    if (argc != 2)
    {
        printf("Usage: ./crack hash\n");
        return 1;
    }
    
    // Cracking character array, used http://letterfrequency.org/
    string characters = "etaoinsrhldcumfpgwybvkxjqzETAOINSRHLDCUMFPGWYBVKXJQZ\0";
    const int characters_count = strlen(characters) + 1; // + 1 to include \o
    
    // The first two letters of hash is salt
    // Salt is then added to plaintext password and encrypted
    // It is also important to declare where the string ends with \o
    string hash = argv[1];
    char salt[3];
    
    // Copying salt value
    for (int i = 0; i < 3; i++)
    {
        salt[i] = hash[i];
        if (i == 2)
        {
            salt[i] = '\0';
        }
    }
    
    // Defining password placeholder value
    char password[6] = "\0\0\0\0\0\0";
    
    // Cracking:
    // Algorithm will start from the end, or in other words:
    // The FOR loop below will be executed, however,
    // It will execute all FOR loops after it until the FOR loop for FIRST char
    // Then FIRST char will loop through, after which if password is not found
    // It will start to loop SECOND and FIRST character, and so on...
    for (int fifth = 0; fifth < characters_count; fifth++)
    {
        for (int fourth = 0; fourth < characters_count; fourth++)
        {
            for (int third = 0; third < characters_count; third++)
            {
                for (int second = 0; second < characters_count; second++)
                {
                    for (int first = 0; first < characters_count; first++)
                    {
                        // Inputting values from our character count
                        password[0] = characters[first];
                        password[1] = characters[second];
                        password[2] = characters[third];
                        password[3] = characters[fourth];
                        password[4] = characters[fifth];
                        
                        // printf("Maybe? %s\n", password);
                        
                        // Creating a hash and checking it against our password
                        if (strcmp(crypt(password, salt), hash) == 0)
                        {
                            printf("%s\n", password);
                            return 0;
                        }
                    }
                }
            }
        }
    }
    
    printf("Sir, we ain't got shit!\n");
    return 2;
}
