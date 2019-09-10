#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

int main(int argc, char *argv[])
{
    // ensuring proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover filename\n");
        return 1;
    }

    // saving filename
    char *infile = argv[1];

    // open input file
    FILE *file = fopen(infile, "r");
    if (file == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // create outfile (null pointer)
    FILE *picture = NULL;

    // create arrays for the process
    unsigned char stack[512];
    char filename[8];

    // set counter
    int counter = 0;

    // set bool condition if file is currently open
    bool fileopen = false;

    // read the file by one stack/buffer of 512 bytes
    while (fread(stack, 512, 1, file) == 1)
    {
        // check if contains beginning of JPEG
        if (stack[0] == 0xff && stack[1] == 0xd8 && stack[2] == 0xff && (stack[3] & 0xe0) == 0xe0)
        {
            // if JPEG is already open - close it
            if (fileopen == true)
            {
                fclose(picture);
            }
            // found JPEG
            else
            {
                fileopen = true;
            }

            sprintf(filename, "%03i.jpg", counter);
            picture = fopen(filename, "w");
            counter++;
        }

        if (fileopen == true)
        {
            fwrite(&stack, 512, 1, picture);
        }
    }

    // close files
    fclose(file);
    fclose(picture);
}
