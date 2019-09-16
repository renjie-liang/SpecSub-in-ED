#include <iostream>
#include <gmp.h>
#include <mpfr.h>
#include "pujian.h"
#include "paillier.h"

//注意，出于溢出保护，需保证有modLenthIn>16*precisionIn
PuJianED::PuJianED(int mIn, int wlenIn, int incIn, int precisionIn, int modLengthIn)
        : TwoCloudSolution(modLengthIn),m(mIn),wlen(wlenIn),inc(incIn),precision(precisionIn) {
    N=(m-wlen)/inc+1;
    NIS=23;

    int i, j;

    //allocate the array
    dft_matrx_Re_ = new mpz_t *[wlen];
    dft_matrx_Im_ = new mpz_t *[wlen];
    window = new mpz_t[wlen];
    for (i = 0; i < wlen; i++) {
        dft_matrx_Re_[i] = new mpz_t[wlen];
        dft_matrx_Im_[i] = new mpz_t[wlen];
    }

    mpz_init(bridge_variable_);

    // 子类自己独有的初始化
    mpfr_t pi_div_N_mul_2, pi, y, y_Re, y_Im;
    mpfr_inits(quantizer, pi_div_N_mul_2, pi, y, y_Re, y_Im, NULL);    // quantizer // 量化因子
    mpfr_set_si_2exp(quantizer, 1, precision, GMP_RNDN); // 量化因子 quantizer = 2^precision

    // 如何让一个mpfr_t变量等于pi
    mpfr_const_pi(pi, GMP_RNDN);

    mpfr_mul_si(pi_div_N_mul_2, pi, -2, GMP_RNDN); // pi*(-2)
    mpfr_div_ui(pi_div_N_mul_2, pi_div_N_mul_2, wlen, GMP_RNDN); // pi_div_N_mul_2=pi*(-2)/N
    //初始化DFT系数矩阵
    for (i = 0; i < wlen; ++i) {
        for (j = 0; j < wlen; ++j) {
            mpz_inits(dft_matrx_Re_[i][j],dft_matrx_Im_[i][j],NULL);

            mpfr_mul_si(y, pi_div_N_mul_2, i * j, GMP_RNDN);
            mpfr_cos(y_Re, y, GMP_RNDN);
            mpfr_sin(y_Im, y, GMP_RNDN);

            // 下面代码展示如何将mpfr_t变量乘以2^precision后，取其整数部分赋给mpz_t变量
            mpfr_mul(y_Re, y_Re, quantizer, GMP_RNDN);
            mpfr_get_z(dft_matrx_Re_[i][j], y_Re, GMP_RNDN);

            mpfr_mul(y_Im, y_Im, quantizer, GMP_RNDN);
            mpfr_get_z(dft_matrx_Im_[i][j], y_Im, GMP_RNDN);
        }
    }

    mpfr_mul_si(pi_div_N_mul_2, pi, 2, GMP_RNDN); // 2pi
    mpfr_div_ui(pi_div_N_mul_2, pi_div_N_mul_2, wlen-1, GMP_RNDN); // pi_div_N_mul_2=2pi/(N-1)
    float alpha=0.46;   //hamming窗参数设置,α=0.46
    //初始化窗函数(hamming窗)系数向量
    for(i = 0; i < wlen; i++){
        mpz_init(window[i]);

        mpfr_mul_si(y,pi_div_N_mul_2,i,GMP_RNDN);
        mpfr_cos(y,y,GMP_RNDN);
        mpfr_mul_d(y,y,-alpha,GMP_RNDN);
        mpfr_add_d(y,y,1-alpha,GMP_RNDN);

        mpfr_mul(y, y, quantizer, GMP_RNDN);
        mpfr_get_z(window[i], y, GMP_RNDN);        
    }

    mpfr_clears(pi_div_N_mul_2, pi, y, y_Re, y_Im, NULL);
}

PuJianED::~PuJianED() {
    int i, j;

    for (i = 0; i < wlen; ++i) {
        for (j = 0; j < wlen; ++j) {
            mpz_clears(dft_matrx_Re_[i][j], dft_matrx_Im_[i][j], NULL);
        }
        mpz_clear(window[i]);
    }
    mpz_clear(bridge_variable_);
    mpfr_clear(quantizer);

    //deallocate the array
    for (int i = 0; i < wlen; i++) {
        delete[] dft_matrx_Re_[i];
        delete[] dft_matrx_Im_[i];
    }
    delete[] dft_matrx_Re_;
    delete[] dft_matrx_Im_;
    delete[] window;
}

void PuJianED::DFT(mpz_t *OutCoefficientsRe, mpz_t *OutCoefficientsIm, mpz_t *inputSignalRe,
                 mpz_t *inputSignalIm) // 使用了默认参数的语法
{
    int i, j;
    for (i = 0; i < wlen; i++) {
        mpz_set_ui(OutCoefficientsRe[i], 1);
        mpz_set_ui(OutCoefficientsIm[i], 1);
    }

    for (i = 0; i < wlen; i++) {
        for (j = 0; j < wlen; j++) {
            // 变换系数实部
            mpz_powm(bridge_variable_, inputSignalRe[j], dft_matrx_Re_[i][j], nsquare);
            multiplyAndModulo(OutCoefficientsRe[i], OutCoefficientsRe[i],
                              bridge_variable_, nsquare);



            // 变换系数虚部
            mpz_powm(bridge_variable_, inputSignalRe[j], dft_matrx_Im_[i][j], nsquare);
            multiplyAndModulo(OutCoefficientsIm[i], OutCoefficientsIm[i],
                              bridge_variable_, nsquare);
        }
    }

    if (inputSignalIm != NULL) // 如果输入信号的虚部非空的话，还需要对
    {
        for (i = 0; i < wlen; i++) {
            for (j = 0; j < wlen; j++) {
                // 接上复数信号虚部的复变换的实部
                mpz_mul_si(bridge_variable_, dft_matrx_Im_[i][j], -1);
                mpz_powm(bridge_variable_, inputSignalIm[j], bridge_variable_, nsquare);
                multiplyAndModulo(OutCoefficientsRe[i], OutCoefficientsRe[i],
                                  bridge_variable_, nsquare);

                // 接上复数信号虚部的复变换的虚部
                mpz_powm(bridge_variable_, inputSignalIm[j], dft_matrx_Re_[i][j], nsquare);
                multiplyAndModulo(OutCoefficientsIm[i], OutCoefficientsIm[i],
                                  bridge_variable_, nsquare);
            }
        }
    }
}      

void PuJianED::enframed_windowed_dft(mpz_t **re,mpz_t **im,mpz_t *input){
    mpz_t temFrame[wlen];
    for(int i=0;i<wlen;i++)
        mpz_init(temFrame[i]);
    for(int i=0;i<N;i++){
        //加窗，每帧乘以窗函数向量
        for(int j=0;j<wlen;j++)
            mpz_powm(temFrame[j],input[i*inc+j],window[j],nsquare);
        //对加窗后的帧作DFT
        DFT(re[i],im[i],temFrame);
    }
    for(int i=0;i<wlen;i++)
        mpz_clear(temFrame[i]);
}

void PuJianED::sptr_sub(mpz_t **re,mpz_t **im,float a,float b){
    mpz_t **As=new mpz_t*[N],Ns[wlen]; 

    // mpz_t **As=new mpz_t*[N]; 
    // mpz_t ** Ns[wlen];

    mpz_t AN,BN,A_AN,q1,q2,temp1,temp2,A,B,Q;
    mpfr_t tempfr;
    mpz_inits(AN,BN,A_AN,q1,q2,temp1,temp2,A,B,Q,NULL);
    mpfr_init(tempfr);

    //精度控制
    mpz_set_ui(temp1,1);
    mpz_mul_2exp(temp2,temp1,7*precision);
    mpz_urandomb(q1,state,7*precision);
    mpz_add(q1,q1,temp2);
    mpz_mul_2exp(temp2,temp1,5*precision+3);
    mpz_urandomb(q2,state,5*precision);
    mpz_add(q2,q2,temp2);

    mpfr_mul_d(tempfr,quantizer,a,GMP_RNDN);
    mpfr_get_z(A,tempfr,GMP_RNDN);
    mpfr_mul_d(tempfr,quantizer,b,GMP_RNDN);
    mpfr_get_z(B,tempfr,GMP_RNDN);
    mpfr_mul_ui(tempfr,quantizer,NIS,GMP_RNDN);
    mpfr_get_z(Q,tempfr,GMP_RNDN);

    //As=re^2+im^2 幅值
    for(int i=0;i<N;i++){
        As[i]=new mpz_t[wlen];
        for(int j=0;j<wlen;j++){
            mpz_init(As[i][j]);
            multiply(temp1,re[i][j],re[i][j]);
            multiply(temp2,im[i][j],im[i][j]);
            multiplyAndModulo(As[i][j],temp1,temp2,nsquare);
        }
    }

    //计算Ns 平均能量值
    for(int i=0;i<wlen;i++){
        mpz_init_set_ui(Ns[i],1);
        for(int j=0;j<NIS;j++)
            multiplyAndModulo(Ns[i],Ns[i],As[j][i],nsquare);
    }

    for(int i=0;i<wlen;i++){
        mpz_powm(AN,Ns[i],A,nsquare);    //AN=A*Ns[i]
        mpz_powm(BN,Ns[i],B,nsquare);    //BN=B*Ns[i]

        for(int j=0;j<N;j++){
            //temp1=max{Q*As[j][i]-A*Ns[i],B*Ns[i]}
            mpz_powm(temp1,AN,minus_1,nsquare);
            mpz_powm(A_AN,As[j][i],Q,nsquare);
            multiplyAndModulo(A_AN,A_AN,temp1,nsquare);
            bigger(temp1,A_AN,BN);

            //re[j][i]=re[j][i]*(temp1/As[j][i])^0.5
            //im[j][i]=im[j][i]*(temp1/As[j][i])^0.5
            divide(temp1,temp1,As[j][i],q1);
            sqRoot(temp1,temp1,q2);
            multiply(re[j][i],re[j][i],temp1);
            multiply(im[j][i],im[j][i],temp1);
        }
    }

    for(int i=0;i<wlen;i++){
        mpz_clear(Ns[i]);
        for(int j=0;j<N;j++)
            mpz_clear(As[j][i]);
    }
    for(int i=0;i<N;i++)
        delete[] As[i];
    delete[] As;
    mpz_clears(AN,BN,A_AN,q1,q2,temp1,temp2,A,B,Q,NULL);
    mpfr_clear(tempfr);
}

void PuJianED::overlap_add(mpz_t *out,mpz_t **re,mpz_t **im){
    mpz_t tempre[wlen],tempim[wlen];
    for(int i=0;i<wlen;i++)
        mpz_inits(tempre[i],tempim[i],NULL);
    for(int i=0;i<m;i++)
        mpz_set_ui(out[i],1);

    //每帧作IDFT后,叠加复原一维时间信号
    for(int i=0;i<N;i++){
        DFT(tempim,tempre,im[i],re[i]); //用DFT完成IDFT(调换实部虚部位置)
        for(int j=0;j<wlen;j++)
            multiplyAndModulo(out[i*inc+j],out[i*inc+j],tempre[j],nsquare);
    }
    for(int i=0;i<wlen;i++)
        mpz_clears(tempre[i],tempim[i],NULL);
}

void PuJianED::basic_pujian(mpz_t *outSignal,mpz_t *inSignal,float aIn,float bIn){
    mpz_t **sptrRe,**sptrIm;    //保存信号频谱的变量，用实部和虚部来表示复数

    sptrRe = new mpz_t *[N];
    sptrIm = new mpz_t *[N];
    for (int i = 0; i < N; i++) {
        sptrRe[i] = new mpz_t[wlen];
        sptrIm[i] = new mpz_t[wlen];
    }
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < wlen; ++j) 
            mpz_inits(sptrRe[i][j],sptrIm[i][j],NULL);
    }
    //分帧加窗作傅里叶变换
    enframed_windowed_dft(sptrRe,sptrIm,inSignal);

    //对频谱作减法去噪
    sptr_sub(sptrRe,sptrIm,aIn,bIn);
    
    //反变换并恢复为一维时间信号
    overlap_add(outSignal,sptrRe,sptrIm);

    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < wlen; ++j) 
            mpz_clears(sptrRe[i][j],sptrIm[i][j],NULL);
    }
    for (int i = 0; i < N; i++) {
        delete[] sptrRe[i];
        delete[] sptrIm[i];
    }
    delete[] sptrRe;
    delete[] sptrIm;
}