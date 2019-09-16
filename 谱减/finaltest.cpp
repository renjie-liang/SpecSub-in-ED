#include<iostream>
#include<gmp.h>
#include<mpfr.h>
#include"pujian.h"
#include<vector>

using namespace std;

int main(){
	vector<double> v;
	int m=0,wlen=400,inc=160,tempi;
	double tempd;
	while(cin>>tempd){
		v.push_back(tempd);
		m++;
	}
	PuJianED domain(m,wlen,inc);
	mpz_t signal[m],tempz1,tempz2;
	mpfr_t tempfr;
	mpfr_init(tempfr);
	mpz_inits(tempz1,tempz2);
	for(int i=0;i<m;i++){
		mpz_init(signal[i]);
		mpfr_mul_d(tempfr,domain.quantizer,v[i],GMP_RNDN);
		mpfr_get_z(tempz1,tempfr,GMP_RNDN);
		domain.encrypt(signal[i],tempz1);
	}
	domain.basic_pujian(signal,signal);
	mpz_set_ui(tempz1,0);
	for(int i=0;i<m;i++){
		domain.decrypt_and_recovery(signal[i],signal[i]);
		mpz_abs(tempz2,signal[i]);
		if(mpz_cmp(tempz2,tempz1)>0) mpz_set(tempz1,tempz2);
	}
	for(int i=0;i<m;i++){
		mpfr_set_z(tempfr,signal[i],GMP_RNDN);
		mpfr_div_z(tempfr,tempfr,tempz1,GMP_RNDN);
		tempd=mpfr_get_d(tempfr,GMP_RNDN);
		cout<<tempd<<endl;
	}
	return 0;
}
