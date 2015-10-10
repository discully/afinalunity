#include <cstdio>
#include <iostream>
#include <string>

// The .rac audio files are IMA ADPCM, like the .mac and .vac audio files.
// However, unlike .vac and .mac which are mono, the .rac files are stereo.
// Currently, sox will not deal with stero IMA files.
// This application strips the two channels into separate files.

int main(int argc, char* argv[])
{
	if( argc != 2 )
	{
		std::cout << "[USAGE] stereo2mono <input_file.rac>" << std::endl;
		return 0;
	}
	
	const std::string fin_name(argv[1]);
	FILE* fin = fopen(fin_name.c_str(), "r");
	
	if( ! fin )
	{
		std::cout << "[ERROR] Could not open " << fin_name << std::endl;
		return 1;
	}
	
	const std::string fout_l_name = fin_name + ".L.rac";
	const std::string fout_r_name = fin_name + ".R.rac";
	FILE* fout_l = fopen(fout_l_name.c_str(), "w");
	FILE* fout_r = fopen(fout_r_name.c_str(), "w");
	
	// From trial and error, it seems the two channels are interleaved one byte at a time.
	const unsigned int n = 1;
	
	while( ! feof(fin) )
	{
		for(unsigned int i = 0; i != n; i++)
		{
			fputc( fgetc(fin), fout_l );
		}
		for(unsigned int i = 0; i != n; i++)
		{
			fputc( fgetc(fin), fout_r );
		}
	}
	
	fclose(fin);
	fclose(fout_l);
	fclose(fout_r);
	
	return 0;
}
