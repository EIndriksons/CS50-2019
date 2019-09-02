#include <cs50.h>
#include <stdio.h>

int get_required_integer(string prompt);

int main(void)
{
    int i = get_required_integer("Height: ");
    
    // Right-aligned pyramid
    for (int n = 1; n <= i; n++)
    {
        for (int x = i - n; x > 0; x--)
        {
            printf(" ");
        }
        for (int j = 0; j < n; j++)
        {
            printf("#");
        }
        printf("\n");
    }
}

// Prompt user for integer between 1 and 8
int get_required_integer(string prompt)
{
    int i;
    do
    {
        i = get_int("%s", prompt);
    }
    while (i < 1 || i > 8);
    return i;
}
