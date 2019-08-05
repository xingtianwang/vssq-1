#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring>
#include <cstdlib>
#include <locale>
#include <cstdio>
#include <ctime>
#include <errno.h>
using namespace std;
unsigned int get_binary_from_char(char x) {
	unsigned int bar = (unsigned int)x;
	bar &= 0x000000ff;
	return bar;
}
unsigned int hex2oct(unsigned char* hex)
{
	unsigned int oct = 0;
	for (int i = 3, tmp = 1; i >= 0; --i) {
		oct += (unsigned int)hex[i] * tmp;
		tmp *= 256;
	}
	return oct;
}
unsigned int hex2oct2(unsigned char* hex)
{
	unsigned int oct = 0;
	for (int i = 1, tmp = 1; i >= 0; --i) {
		oct += (unsigned int)hex[i] * tmp;
		tmp *= 256;
	}
	return oct;
}
int oct2hex(int dec,unsigned char *hex)
{
    for (int i = 3; i >= 0; i--)  {
        hex[i] = (dec % 256) & 0xFF;
        dec /= 256;
    }
    return 0;
}


void char2Hex(char c) // ½«×Ö·ûÒÔ16½øÖÆ±íÊ¾
{
    char ch, cl;
    ch = ((c & 0xF0) >> 4) + '0';
    /*c & oxF0 °ÑcµÄµÍ4Î»±ä³É0£¬È»ºóÓÒÒÆ4Î»£¬µÃµ½Ö»ÓÐ¸ßÎ»µÄ4Î»¶þ½øÖÆÊý¡£
    4Î»µÄ¶þ½øÖÆÊý×ª»»ÎªÒ»¸ö16½øÖÆµÄÊý£¬ÓÉÓÚÕâÀïÊÇcharÀàÐÍ£¬ÒªÓÃ16½øÖÆÊý´òÓ¡³öÀ´£¬
    ÐèÒª¼ÓÉÏ0µÄASCIIÂë²Å¿ÉÒÔ£¬²»È»Ö»ÄÜ´òÓ¡10½øÖÆµÄASCIIÂë¶ÔÓ¦µÄ×Ö·û*/
    if(ch > '9')
        ch += ('A'-'9'-1);
    cl = (c & 0x0F) + '0';
    if(cl > '9')
        cl += ('A'-'9'-1);
    printf("%c%c\n", ch ,cl );
}

class TestLib  
{  
    public:  
        int mod( unsigned char rongrongtemp[], int naonaoSize,char* axmlpath);
};  

int TestLib::mod( unsigned char rongrongtemp[], int naonaoSize,char* axmlpath)
{   

    time_t t1, t2;
time(&t1);
    long filesize = 0;
    long StrCount = 0;
    long naonaoOFF = 0;//²åÈëµÄ×Ö·û´®Î»ÖÃ
    long naoOffset = 0;//²åÈëµÄ×Ö·û´®Æ«ÒÆµÄÎ»ÖÃ
    long StrChuSize = 0;
    long StrOff = 0;
    unsigned char *a = NULL;
    unsigned char *b = NULL;
    unsigned char *c = NULL;
    unsigned char buffer[4];
    unsigned char supply[2] = {0x00,0x00};


    unsigned char naonao[naonaoSize];
    memset(naonao, 0, naonaoSize);

    memcpy(naonao,rongrongtemp,naonaoSize);
    cout<<"naonaoSize is "<<naonaoSize<<endl;

//    for(int i = 0;i<naonaoSize;i++){
//         cout<<setfill('0') << setw(2)<<hex<<(unsigned int)naonao[i];
//    }

    FILE *file;
    errno = 0;
    file = fopen(axmlpath , "rb+");
    if(!file){
        cout<<"open AndroidManifest error! errno is "<<dec<<errno<<endl;
        abort();
    }
    fseek(file, 0, SEEK_END);
	filesize = ftell(file);
	fseek(file, 0, SEEK_SET);
    a = (unsigned char*)malloc((filesize + naonaoSize + 4) * sizeof(unsigned char));
    memset(a, 0, sizeof(unsigned char) * (filesize + naonaoSize + 4));
    fread(a, sizeof(unsigned char), filesize, file);


    //ÐÞ¸ÄString¸öÊý
    for(int i = 16,j = 3;j >= 0;i++,j--){
        buffer[j] = a[i];
    }
    StrCount = hex2oct(buffer) + 1;
    oct2hex(StrCount,buffer);
    for(int i = 16,j = 3;j >= 0;i++,j--){
        a[i] = buffer[j];
    }

    //²åÈënaonao×Ö·û´®Æ«ÒÆ
    for(int i = 28,j = 3;j >= 0;i++,j--){
    buffer[j] = a[i];
    }
    naoOffset = hex2oct(buffer) + 8;
    b = (unsigned char*)malloc((filesize - naoOffset) * sizeof(unsigned char));
    memset(b, 0, sizeof(unsigned char) * (filesize - naoOffset));
    fseek(file, naoOffset, SEEK_SET);
    fread(b, sizeof(unsigned char), (filesize - naoOffset), file);
    fclose(file);

    for(int i = 12,j = 3;j >= 0;i++,j--){
        buffer[j] = a[i];
    }
    naonaoOFF = hex2oct(buffer) + 8;
    oct2hex((naonaoOFF-naoOffset),buffer);
    for(int i = naoOffset,j = 3;j >= 0;i++,j--){
        a[i] = buffer[j];
    }
    memcpy(a+naoOffset+4,b,(filesize - naoOffset));
    free(b);



    //ÐÞ¸Ä×Ö·û´®ÄÚÈÝ¿ªÊ¼Î»ÖÃÆ«ÒÆ
    for(int i = 28,j = 3;j >= 0;i++,j--){
    buffer[j] = a[i];
    }
    StrOff = hex2oct(buffer) + 4;
    oct2hex(StrOff,buffer);
    for(int i = 28,j = 3;j >= 0;i++,j--){
    a[i] = buffer[j];
    }



    //²åÈë×Ö·û´®
    for(int i = 12,j = 3;j >= 0;i++,j--){
        buffer[j] = a[i];
    }
    naonaoOFF = hex2oct(buffer) + 8 + 4;
    c = (unsigned char*)malloc((filesize - naonaoOFF + 4) * sizeof(unsigned char));
    memset(c, 0, sizeof(unsigned char) * (filesize - naonaoOFF + 4));
    memcpy(c,a+naonaoOFF,(filesize - naonaoOFF + 4));
/*    if(naonaoOFF % 4 == 0){
        naonaoOFF = naonaoOFF - 2;
        filesize = filesize - 2;
    }*/
    memcpy(a+naonaoOFF,naonao,naonaoSize);
    if((naonaoOFF+naonaoSize)%4 != 0){
        memcpy(a+naonaoOFF+naonaoSize,supply,2);
        naonaoSize = naonaoSize + 2;
    }
    memcpy(a+naonaoOFF+naonaoSize,c,(filesize - naonaoOFF + 4));
    free(c);





    //ÐÞ¸ÄstringChunk´óÐ¡
    for(int i = 12,j = 3;j >= 0;i++,j--){
        buffer[j] = a[i];
    }
    StrChuSize = hex2oct(buffer) + 4 + naonaoSize;
    oct2hex(StrChuSize,buffer);
    for(int i = 12,j = 3;j >= 0;i++,j--){
        a[i] = buffer[j];
    }


    //ÐÞ¸ÄÎÄ¼þ´óÐ¡
    for(int i = 4,j = 3;j >=0;i++,j--){
        buffer[j] = a[i];
    }
    filesize = hex2oct(buffer) + 4 + naonaoSize;
    oct2hex(filesize,buffer);
    for(int i = 4,j = 3;j >= 0;i++,j--){
        a[i] = buffer[j];
    }


    //½âÎö×Ö·û´®Ë÷Òý±í
    unsigned char** stringList = NULL;
	stringList = (unsigned char**)malloc(sizeof(unsigned char*) * (StrCount));
	memset(stringList, 0, sizeof(unsigned char*) * (StrCount));
    unsigned int tmpOff = StrOff + 8;

/*       for(int i = tmpOff;i < tmpOff+4;i++){
       cout<<setfill('0') << setw(2)<<hex<<(unsigned int)a[i]<<endl;
   }*/

    unsigned char tmpbuf[2];
    int Strsize = 0;
    for(int i = 0;i < StrCount - 1;i++){
        tmpbuf[1] = a[tmpOff++];
        //cout<<setfill('0') << setw(2)<<hex<<(unsigned int)tmpbuf[1]<<"tmpbuf[1]"<<endl;
        tmpbuf[0] = a[tmpOff++];
        //cout<<setfill('0') << setw(2)<<hex<<(unsigned int)tmpbuf[0]<<"tmpbuf[0]"<<endl;
       Strsize = hex2oct2(tmpbuf);
       stringList[i] = (unsigned char*)malloc(sizeof(unsigned char) * (Strsize * 2 + 2));
       memset(stringList[i], 0, sizeof(unsigned char) * (Strsize * 2 + 2));
       memcpy(stringList[i],a+tmpOff, Strsize * 2 + 2);
       tmpOff = tmpOff + Strsize * 2 + 2;
       
/*      if(i == StrCount-2){
              for(int j = 0;j < Strsize * 2 + 2;j++){
       cout<<setfill('0') << setw(2)<<hex<<(unsigned int)stringList[i][j];

        }
        cout<<endl;
      }*/

    }

/*       for(int i = tmpOff;i < tmpOff+4;i++){
       cout<<setfill('0') << setw(2)<<hex<<(unsigned int)a[i]<<endl;
   }*/

    if((tmpOff)%4 != 0){
        tmpOff = tmpOff + 2;
    }//因为原文件的最后一个字符串有可能做了4字节对齐，这里要考虑这种情况将tmpOff加2
       tmpbuf[1] = a[tmpOff++];
        //cout<<setfill('0') << setw(2)<<hex<<(unsigned int)tmpbuf[1]<<"tmpbuf[1]"<<endl;
       tmpbuf[0] = a[tmpOff++];
        //cout<<setfill('0') << setw(2)<<hex<<(unsigned int)tmpbuf[0]<<"tmpbuf[0]"<<endl;
       Strsize = hex2oct2(tmpbuf);
       stringList[StrCount-1] = (unsigned char*)malloc(sizeof(unsigned char) * (Strsize * 2 + 2));
       memset(stringList[StrCount-1], 0, sizeof(unsigned char) * (Strsize * 2 + 2));
       memcpy(stringList[StrCount-1],a+tmpOff, Strsize * 2 + 2);
       tmpOff = tmpOff + Strsize * 2 + 2;



    //¶¨Î»applicationµÄlable±êÇ©Î»ÖÃ²¢ÐÞ¸Ä
    int tmpstep = 0;
    int tmpindex = 0;
    unsigned char buf[4] = {0x03,0x00,0x00,0x08};
    unsigned char application[24] = {0x61,0x00,0x70,0x00,0x70,0x00,0x6C,0x00,0x69,0x00,0x63,0x00,0x61,0x00,0x74,0x00,0x69,0x00,0x6F,0x00,0x6E,0x00,0x00,0x00};
    unsigned char lable[12] = {0x6C,0x00,0x61,0x00,0x62,0x00,0x65,0x00,0x6C,0x00,0x00,0x00};
/*       for(int i = tmpOff;i < tmpOff+4;i++){
       cout<<setfill('0') << setw(2)<<hex<<(unsigned int)a[i]<<endl;
   }*/
    if((tmpOff)%4 != 0){
        tmpOff = tmpOff + 2;
    }
    for(int i = tmpOff + 4,j = 3;j >=0;i++,j--){
        buffer[j] = a[i];
    }
    tmpOff =  tmpOff + hex2oct(buffer);
    while(tmpOff <= filesize){
        //cout<<"in while"<<endl;
        for(int i = tmpOff + 4,j = 3;j >=0;i++,j--){
                buffer[j] = a[i];
        }
        tmpstep = hex2oct(buffer);
        for(int i = tmpOff + 4*5,j = 3;j >=0;i++,j--){
                buffer[j] = a[i];
        }
        tmpindex = hex2oct(buffer);
        //cout<<"stringList[tmpindex   "<<(*(stringList[tmpindex]))<<endl;
        if(*(stringList[tmpindex]) == *application){
                cout<<"find application!!"<<endl;
                for(int i = tmpOff + 4*7,j = 3;j >=0;i++,j--){
                    buffer[j] = a[i];
                }
                int attrCount = hex2oct(buffer);
                tmpOff = tmpOff + 4*9;
                for(int k = 0;k < attrCount;k++){
                    for(int i = tmpOff + 4,j = 3;j >=0;i++,j--){
                        buffer[j] = a[i];
                    }
                    tmpindex = hex2oct(buffer);
                    if(*(stringList[tmpindex]) == *lable){
                        cout<<"find lable!!"<<endl;
                        oct2hex((StrCount-1),buffer);
                        for(int i = tmpOff + 4*2,j = 3;j >=0;i++,j--){
                            a[i] = buffer[j];
                        }
                        for(int i = tmpOff + 4*3,j = 3;j >=0;i++,j--){
                            a[i] = buf[j];
                        }
                        for(int i = tmpOff + 4*4,j = 3;j >=0;i++,j--){
                            a[i] = buffer[j];
                        }
                        break;
                    }
                    tmpOff = tmpOff + 4*5;
                }
                break;
        }
        tmpOff = tmpOff + tmpstep;
    }

//    for(int i = tmpOff;i<tmpOff+20;i++){
//        cout<<setfill('0') << setw(2)<<hex<<(unsigned int)a[i];
//    }

    FILE *file1;
    file1 = fopen(axmlpath , "wb+");
    fwrite(a,sizeof(unsigned char),filesize, file1);
    fclose(file1);
    free(a);


//    FILE *file1;
//    file1 = fopen("AndroidManifest1.xml" , "wb+");
//    fwrite(a,sizeof(unsigned char), filesize, file1);
//    for(int i = 0;i < 8;i++){
//        cout<<setfill('0') << setw(2)<<hex<<(unsigned int)a[i]<<endl;
//    }
time(&t2);
  cout << t2-t1 << "time is"<<endl;
    return 0;
}
extern "C"{
    TestLib obj;  
    int modtest( unsigned char rongrongtemp[], int naonaoSize,char* axmlpath) {  
        int tmpnaonaoSize = naonaoSize;


        /*for(int i = 0;i<tmpnaonaoSize;i++){
            cout<<setfill('0') << setw(2)<<hex<<(unsigned int)rongrongtemp[i]<<endl;
        }*/

        obj.mod(rongrongtemp,tmpnaonaoSize,axmlpath);

      }  
}
