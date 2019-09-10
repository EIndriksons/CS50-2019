#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // filenames
    int resize = atoi(argv[1]);
    char *infile = argv[2];
    char *outfile = argv[3];

    // ensures proper usage - 1) positive integer less than or equal to 100 2) infile 3) outfile
    if (argc != 4 || resize > 100 || resize < 0)
    {
        fprintf(stderr, "Usage: resize resize infile outfile\n");
        return 1;
    }

    // open input file - read mode
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        // if failed, print error
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file - write mode
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        // if failed, close input file & print error
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER and create equal outfile BITMAPFILEHEADER
    BITMAPFILEHEADER bf, bfR;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);
    bfR = bf;

    // read infile's BITMAPINFOHEADER and create equal outfile BITMAPINFOHEADER
    BITMAPINFOHEADER bi, biR;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);
    biR = bi;

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(inptr);
        fclose(outptr);
        fprintf(stderr, "Unsupported file format \n");
        return 4;
    }

    // change outfile BITMAPINFOHEADER specifications to resize it
    biR.biWidth = bi.biWidth * resize;
    biR.biHeight = bi.biHeight * resize;

    // determine padding for both infile and outfile
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int outpadding = (4 - (biR.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // change outfile BITMAPFILEHEADER and BITMAPINFOHEADER size specification
    biR.biSizeImage = ((biR.biWidth * sizeof(RGBTRIPLE)) * abs(biR.biHeight)) + abs(biR.biHeight) * outpadding;
    bfR.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + biR.biSizeImage;

    // write outfile's BITMAPFILEHEADER
    fwrite(&bfR, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&biR, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines aka height/rows
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        // multiplying height by resize
        for (int j = 0; j < resize; j++)
        {
            // iterate over infile's scanlines aka width/columns
            for (int k = 0; k < bi.biWidth; k++)
            {
                // temporary storage
                RGBTRIPLE triple;

                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                // write RGB triple to outfile resize x times
                for (int l = 0; l < resize; l++)
                {
                    fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                }
            }

            // add padding
            for (int pad = 0; pad < outpadding; pad++)
            {
                fputc(0x00, outptr);
            }

            // reversing pointer location back to the start of the current row
            if (j < resize - 1)
            {
                fseek(inptr, -bi.biWidth * sizeof(RGBTRIPLE), SEEK_CUR);
            }
        }

        // skip over padding if any
        fseek(inptr, padding, SEEK_CUR);
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}