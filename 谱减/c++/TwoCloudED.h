#pragma once
#include"paillier.h"

class TwoCloudSolution:public PaillierEncryption
{
public:
	TwoCloudSolution(int modIn=128):PaillierEncryption(modIn){}
	void multiply(mpz_t out,const mpz_t c_m1,const mpz_t c_m2);
	void divide(mpz_t out,const mpz_t c_m1,const mpz_t c_m2,
			const mpz_t quantizer,mpz_t r=NULL);
	void sqRoot(mpz_t out,const mpz_t c_m,
			const mpz_t quantizer,mpz_t r=NULL);
	void bigger(mpz_t out,const mpz_t c_m1,const mpz_t c_m2);
};