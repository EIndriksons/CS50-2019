#include <cs50.h>
#include <stdio.h>

long get_valid_input(string prompt);
int get_lenght(long number);
int get_creditcard(long number);

int main(void)
{
    // Obtaining value from function
    long number = get_valid_input("Number: ");
    
    // Obtaining credit card number lenght
    int lenght = get_lenght(number);
    
    // Performing first checksum:
    long div = 10;
    int sum = 0, num, mult;
    for (int x = 0; x < lenght / 2; x++)
    {
        // Gets every second number starting from the back
        num = (number / div) % 10;
        div = div * 100;
        
        // Multiplication by 2 as required by the algorithm
        mult = num * 2;
        
        // Then we check if the result is single or double digit number
        if (mult > 9)
        {
            // If it is double digit number we add both of its products to sum
            sum = sum + ((mult / 10) + (mult % 10));
        }
        else
        {
            // If it is single digit number we add it to sum
            sum = sum + mult;
        }
    }
    
    // Performing second checksum:
    div = 1;
    for (int x = 0; x < lenght - (lenght / 2); x++)
    {
        // Obtains rest of the numbers and adds them to sum
        num = (number / div) % 10;
        div = div * 100;
        sum = sum + num;
    }
    
    // Determining creditcard type & validity if checksum is correct
    if (sum % 10 == 0 && get_creditcard(number) == 1)
    {
        printf("VISA\n");
    }
    else if (sum % 10 == 0 && get_creditcard(number) == 2)
    {
        printf("AMEX\n");
    }
    else if (sum % 10 == 0 && get_creditcard(number) == 3)
    {
        printf("MASTERCARD\n");
    }
    else
    {
        printf("INVALID\n");
    }
}

// Prompt user for valid input
long get_valid_input(string prompt)
{
    long i;
    do
    {
        i = get_long("%s", prompt);
    }
    while (i <= 0);
    return i;
}

// Outputs lenght of input number
int get_lenght(long number)
{
    int lenght = 0;
    while (number > 0)
    {
        number = number / 10;
        lenght++;
    }
    return lenght;
}

// Outputs credit card company type if valid
int get_creditcard(long number)
{
    int lenght = get_lenght(number);
    int first_digit, second_digit, card_type;
    
    // Div preparation to obtain first & second digits
    long div1 = 1, div2 = 1;
    for (int i = 0; i < lenght - 1; i++)
    {
        // To get first digit
        div1 = div1 * 10;
    }
    for (int i = 0; i < lenght - 2; i++)
    {
        // To get second digit
        div2 = div2 * 10;
    }
    
    // Obtaining first & second digits
    first_digit = (number / div1) % 10;
    second_digit = (number / div2) % 10;
    
    // Final credit card check
    if (first_digit == 4 && (lenght == 13 || lenght == 16))
    {
        // VISA: 13 & 16 digit cards, starts with 4
        card_type = 1;
    }
    else if (first_digit == 3 && (second_digit == 4 || second_digit == 7) && lenght == 15)
    {
        // AMEX: 15 digit cards, starts with 34 & 37
        card_type = 2;
    }
    else if (first_digit == 5 && (second_digit == 1 || second_digit == 2 || second_digit == 3
                                  || second_digit == 4 || second_digit == 5) && lenght == 16)
    {
        // MASTERCARD: 16 digit cards, starts with 51, 52, 53, 54 or 55.
        card_type = 3;
    }
    else
    {
        // INVALID or OTHER COMPANY
        card_type = 0;
    }
    
    return card_type;
}
