// Declares a dictionary's functionality
// Ensures that clang will compile dictionary.h only once!
#ifndef DICTIONARY_H
#define DICTIONARY_H

#include <stdbool.h>

// Maximum length for a word
// This is a constant that will be used in our program.
// Quite literally, it replaces any mention of LENGHT in the code with 45.
// So it is not a variable but rathera find-and-replace trick.
// (e.g., pneumonoultramicroscopicsilicovolcanoconiosis)
#define LENGTH 45

// Prototype functions
// LOAD
bool load(const char *dictionary);
// can be also rewritten as bool load(const string dictionary);
// const means that those strings passed in the function will remain constant and cannot be changed - pretty neat

// SIZE
unsigned int size(void);

// CHECK
bool check(const char *word);
// can be also rewritten as bool check(const string word);
// const means that those strings passed in the function will remain constant and cannot be changed - pretty neat

// UNLOAD
bool unload(void);

// end
#endif // DICTIONARY_H
