#include<gmp.h>
#include"TwoCloudED.h"
#include"paillier.h"
#include<iostream>

void TwoCloudSolution::multiply(mpz_t out,const mpz_t c_m1,const mpz_t c_m2){
	mpz_t temp1, temp2, r1, r2, minus_r1,minus_r2, c_r1,c_r2, c_minus_part;
	mpz_inits(temp1,temp2,r1,r2,minus_r1,minus_r2,c_r1,c_r2,c_minus_part,NULL);

	randomZStarN(r1);
	randomZStarN(r2);
	mpz_sub(minus_r1,n,r1);	//minus_r1=-r1
	encrypt(c_r1,r1);	//c_r1=E(r1)
	mpz_sub(minus_r2,n,r2);	//minus_r2=-r2
	encrypt(c_r2,r2);	//c_r2=E(r2)

	//c_minus_part=E(-r2m1-r1m2-r1r2)
	mpz_powm(c_minus_part,c_m1,minus_r2,nsquare);
	mpz_powm(temp1,c_m2,minus_r1,nsquare);
	multiplyAndModulo(c_minus_part,c_minus_part,temp1,nsquare);
	mpz_mul(temp1,minus_r1,r2);
	encrypt(temp1,temp1);
	multiplyAndModulo(c_minus_part,c_minus_part,temp1,nsquare);

	mpz_mul(temp1,c_m1,c_r1);	//tmp1=E(m1+r1)
	mpz_mul(temp2,c_m2,c_r2);	//tmp2=E(m2+r2)

	//在第二个云中解密计算，temp1=E(D(temp1)*D(temp2))=E((m1+r1)*(m2+r2))
	decrypt(temp1,temp1);
	decrypt(temp2,temp2);
	mpz_mul(temp1,temp1,temp2);
	encrypt(temp1,temp1);

	//out = E((m1+r1)*(m2+r2))*E(-r2m1-r1m2-r1r2) = E(m1*m2)
	multiplyAndModulo(out,temp1,c_minus_part,nsquare);

	mpz_clears(temp1,temp2,r1,r2,minus_r1,minus_r2,c_r1,c_r2,c_minus_part,NULL);
}

void TwoCloudSolution::divide(mpz_t out,const mpz_t c_m1,const mpz_t c_m2,
				const mpz_t quantizer,mpz_t r){
//注意quantizer为放大因子，quantizer/m2为实际精度
//随机扰乱r作为输入之一，可事先生成适当r以保证除法过程不发生溢出

	mpz_t s,temp1,temp2;
	mpz_inits(s,temp1,temp2,NULL);

	//若未给定r值,则默认m2<n^0.5,随机生成r
	if(r==NULL){
		r=temp2;
		mpz_urandomb(r,state,modLength/2);
	}

	//s=r*quantizer,temp1=E(r*m2)
	mpz_mul(s,r,quantizer);
	mpz_powm(temp1,c_m2,r,nsquare);

	//解密计算,temp1=E(s/D(temp1))=E(quantizer/m2)
	decrypt_and_recovery(temp1,temp1);
	mpz_div(temp1,s,temp1);
	encrypt(temp1,temp1);

	//调用密文乘法方案计算out=E(m1*quantizer/m2)
	multiply(out,c_m1,temp1);
	
	mpz_clears(s,temp1,temp2,NULL);
}

void TwoCloudSolution::sqRoot(mpz_t out,const mpz_t c_m,const mpz_t quantizer,mpz_t r){
	mpz_t s,c_100m,temp1,temp2,rtemp;
//注意quantizer为放大因子，quantizer/m为实际精度

	mpz_inits(s,c_100m,temp1,temp2,rtemp,NULL);
	mpz_powm_ui(c_100m,c_m,100,nsquare);

	//若未给定r值,则默认m<n^0.5,随机生成r
	if(r==NULL){
		r=rtemp;
		mpz_urandomb(r,state,modLength/4);
	}

	//s=10r*quantizer,temp1=E(r^2*(100m+1)),其中100m+1是为了防止分母为零
	mpz_mul(s,r,quantizer);
	mpz_mul_ui(s,s,10);
	mpz_mul(temp1,r,r);
	encrypt(temp2,temp1);
	mpz_powm(temp1,c_100m,temp1,nsquare);
	multiplyAndModulo(temp1,temp1,temp2,nsquare);

	//在第二个云中解密计算，temp1=E(s/D(temp1)^0.5)=E(quantizer/(m+0.01)^0.5)
	decrypt(temp1,temp1);
	mpz_sqrt(temp1,temp1);
	mpz_div(temp1,s,temp1);
	encrypt(temp1,temp1);

	//调用密文乘法方案计算out=E(m*quantizer/(m+0.01)^0.5),约等于E(quantizer*m^0.5)
	multiply(out,c_m,temp1);

	mpz_clears(s,temp1,temp2,rtemp,NULL);
}

void TwoCloudSolution::bigger(mpz_t out,const mpz_t c_m1,const mpz_t c_m2){
	mpz_t r1,r2,temp1,temp2;
	mpz_inits(r1,r2,temp1,temp2,NULL);

	//temp1=E(r1*(m1-m2))
	mpz_powm(temp1,c_m2,minus_1,nsquare);
	multiplyAndModulo(temp1,c_m1,temp1,nsquare);
	mpz_urandomb(r1,state,modLength/2);	//默认m1-m2<n^0.5
	mpz_powm(temp1,temp1,r1,nsquare);

	//在第二个云中解密计算,D(temp1)=r1*(m1-m2),i=r1*(m1-m2)>0?0:1,temp1=E(i)
	decrypt(temp1,temp1);
	int i=mpz_cmp(temp1,n_half_)<0?0:1;
	mpz_set_ui(temp1,i);
	encrypt(temp1,temp1);

	//l[0]=E(r20*i+m1+r1)
	//l[1]=E(r21*(i-1)+m2+r1)
	mpz_t l[2];
	mpz_inits(l[0],l[1],NULL);
	randomZStarNSquare(r1);
	randomZStarN(r2);	//r20
	mpz_powm(l[0],temp1,r2,nsquare);
	multiplyAndModulo(l[0],l[0],c_m1,nsquare);
	multiplyAndModulo(l[0],l[0],r1,nsquare);
	randomZStarN(r2);	//r21
	encrypt(temp2,minus_1);
	multiplyAndModulo(l[1],temp1,temp2,nsquare);
	mpz_powm(l[1],l[1],r2,nsquare);
	multiplyAndModulo(l[1],l[1],c_m2,nsquare);
	multiplyAndModulo(l[1],l[1],r1,nsquare);

	//在第二个云中解密l[i],得temp1=D(l[i])=max{m1,m2}+r1,令temp1=E(temp1)
	decrypt(temp1,l[i]);
	encrypt(temp1,temp1);

	//out=temp1*E(-r1)=E(max{m1,m2})
	mpz_powm(temp2,r1,minus_1,nsquare);
	multiplyAndModulo(out,temp1,temp2,nsquare);

	mpz_clears(r1,r2,temp1,temp2,l[0],l[1],NULL);
}