#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // resize multiplier. Remember to use atof as we need to convert it to float not integer.
    float resize = atof(argv[1]);

    // get filenames
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
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER and create equal outfile BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(inptr);
        fclose(outptr);
        fprintf(stderr, "Unsupported file format \n");
        return 4;
    }

    // calculate new image size. Thanks to mareksuscak (github) for the suggestion on using floors
    // and separate calculation stage for easier process
    int oldWidth = bi.biWidth;
    int oldHeight = bi.biHeight;
    int newWidth = floor(oldWidth * resize);
    int newHeight = floor(oldHeight * resize);

    // determine padding for both infile and outfile
    // by doing this we know if we need to add any padding
    int padding = (4 - (oldWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int outPadding = (4 - (newWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // resize image
    bi.biWidth = newWidth;
    bi.biHeight = newHeight;

    // change outfile BITMAPFILEHEADER and BITMAPINFOHEADER size specification
    bi.biSizeImage = ((sizeof(RGBTRIPLE) * newWidth) + outPadding) * abs(newHeight);
    bf.bfSize = bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // calculate resize ratio to later use in case of larger or smaller image
    double widthRatio = (double) oldWidth / (double) newWidth;
    double heightRatio = (double) oldHeight / (double) newHeight;

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // allocate a memory to store one scanline
    RGBTRIPLE scanline[oldWidth * sizeof(RGBTRIPLE)];
    int sScanline = -1;


    // thanks to mareksuscak (github) for suggestion to use coordinates
    // iterate over rows in the file
    for (int i = 0, biHeight = abs(newHeight); i < biHeight; i++)
    {
        // compute Y coordinate
        int row = i * heightRatio;

        // read scanlines from the input image
        if (sScanline != row)
        {
            // seek & read the image
            fseek(inptr, sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + (((sizeof(RGBTRIPLE) * oldWidth) + padding) * row), SEEK_SET);
            fread(scanline, sizeof(RGBTRIPLE), oldWidth,inptr);
            sScanline = row;
        }

        // for all columns in the new image
        for (int j = 0; j < newWidth; j++)
        {
            // compute X coordinate
            int column = j * widthRatio;

            // write image
            fwrite(&scanline[column], sizeof(RGBTRIPLE), 1, outptr);
        }

        // write new padding
        for (int j = 0; j < outPadding; j++)
        {
            // padding text
            fputc(0x00, outptr);
        }
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    return 0;
}