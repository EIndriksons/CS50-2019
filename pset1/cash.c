#include <cs50.h>
#include <stdio.h>
#include <math.h>

int get_valid_input(string prompt);

int main(void)
{
    // Return value in coins
    int coins = get_valid_input("Change owed: ");
    
    // Start performing checks
    int amount = 0;
    while (coins >= 25)
    {
        coins = coins - 25;
        amount++;
    }
    while (coins >= 10)
    {
        coins = coins - 10;
        amount++;
    }
    while (coins >= 5)
    {
        coins = coins - 5;
        amount++;
    }
    while (coins >= 1)
    {
        coins = coins - 1;
        amount++;
    }
    
    // Print coin amount
    printf("%d\n", amount);
}

// Prompt user for float input and check for validity
// Then convert to cents and integer value type
int get_valid_input(string prompt)
{
    float dollars;
    int coins;
    do
    {
        dollars = get_float("%s", prompt);
        coins = round(dollars * 100);
    }
    while (coins <= 0);
    return coins;
}
