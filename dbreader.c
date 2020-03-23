// dbreader.c
// Licensed under the NCSA Open source license Copyright (c) 2019-2020 Lawrence Angrave, All rights reserved.

// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal with the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimers. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimers in the documentation and/or other materials provided with the distribution. Neither the names of Lawrence Angrave, University of Illinois nor the names of its contributors may be used to endorse or promote products derived from this Software without specific prior written permission.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE. 

//Example compile:
// gcc -std=c99 -o dbreader dbreader.c -lgdbm
// libgdbm.so.6 can be found in old rpms e.g.
// http://rpmfind.net/linux/rpm2html/search.php?query=libgdbm.so.6

// Example use:
// for d in *.db ; do ./dbreader $d ; done

#define _GNU_SOURCE 
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <gdbm.h>
void badchar(char* mesg) {
  fprintf(stderr,"Unexpected Character:%s\n",mesg)

}

void check_characters(char*s, int len) {
  while(len--) {
    char c = *s;
    if (!c) badchar("Found NUL character");
    else if (c==9) badchar("Found tab character");
    else if (c=='\n') badchar("Found newline character");
    s++;
  }
}


int process(GDBM_FILE g,FILE*f) {
   datum key = gdbm_firstkey (g);
   while (key.dptr)
     {
        fwrite(key.dptr,1,key.dsize,f);
        fputc('\t',f);
     
	      datum value = gdbm_fetch(g, key);
        fwrite(value.dptr,1,value.dsize,f);
        free(value.dptr);
        fputc('\n',f);

        datum nextkey = gdbm_nextkey (g, key);
        free (key.dptr);
        key = nextkey;
     } 
     return 1;
}

int main(int argc, char** argv) {
  if(argc == 1) {

    printf("Usage: %s file1.db file2.db ....\n Creates file1.db.tsv file2.db.tsv etc\n", *argv);
    exit(1);
  }
  int ok = 1;  
  char* infile;
  while((infile = argv[1])) {
     argv++;

     char* outfile;
     asprintf(&outfile,"%s.tsv", infile);
     printf("Input : %s\nOutput : %s\n", infile,outfile);

     GDBM_FILE db = gdbm_open (infile,0, GDBM_READER, 0, 0);
     // Open for writing and truncate if exists
     FILE * out_f = db ? fopen(outfile,"w") : NULL;

     if(db && out_f) ok = process(db,out_f) && ok; 
     else printf("Skipping %s\n",infile);
     if(out_f) fclose(out_f);
     if(db) gdbm_close(db);
     free(outfile);
  }
  return 1 - ok;
}
