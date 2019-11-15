// implements a dictionary's functionality
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// global variable to keep track of words in dictionary
unsigned int words = 0;

// global variable to keep track if loaded function has been called
bool loaded = false;

// ====================
// HASH TABLE
// ====================

// Represents number of buckets in a hash table
// one for each letter of english alphabet
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// globally initialize hashtable
node *hashtable[N];

// hash function
// hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}


// ====================
// FUNCTIONS
// ====================

// loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // buffer for a word
    char word[LENGTH + 1];

    // insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {
        // get hashtable index
        unsigned int index = hash(word);

        // create temporary node for storage
        node *temp = malloc(sizeof(node));

        // initialize the temporary node
        memset(temp, 0, sizeof(node));

        // checking if malloc succeeded and we did not run out of memory
        if (temp == NULL)
        {
            unload();
            return false;
        }

        // copy dictionary word to temp node location
        strcpy(temp->word, word);

        // if hashtable bucket is empty - start filling it up
        if (hashtable[index] == NULL)
        {
            hashtable[index] = temp;
        }
        // else add it to an already existing linked list
        else
        {
            // save pointer to the previous first element of the list
            temp->next = hashtable[index];

            // assign hashtable pointer to start at the new node
            hashtable[index] = temp;
        }

        // global word counter
        words++;
    }

    // close dictionary
    fclose(file);

    // indicate success
    loaded = true;
    return true;
}

// returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    if (loaded == true)
    {
        return words;
    }
    else
    {
        return 0;
    }
}

// returns true if word is in dictionary else false
bool check(const char *word)
{
    // recreate hash index
    unsigned int index = hash(word);

    // create pointer cursor for location loop
    node *cursor = hashtable[index];

    // loop for finding the word
    while (cursor != NULL)
    {
        if (strcasecmp(cursor->word, word) == 0)
        {
            // word found
            return true;
        }

        // word not found - go to next link
        cursor = cursor->next;
    }

    // no matches found
    return false;
}

// unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    // for all hash indexes in hash table
    for (int i = 0; i < N; i++)
    {
        // create pointer cursor for location loop
        node *cursor = hashtable[i];

        while (cursor != NULL)
        {
            node *temp = cursor;
            cursor = cursor->next;
            free(temp);
        }
    }

    // success
    return true;
}