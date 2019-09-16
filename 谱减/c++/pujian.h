#pragma once
#include "TwoCloudED.h"
#include <gmp.h> // 大整数运算
#include <mpfr.h>
#include "paillier.h"
#include <vector>

class PuJianED : public TwoCloudSolution {
public:
    int m,N;  //音频长度，帧数
    int wlen,inc,NIS;   //帧长，帧移
    int precision;  //精度
    mpz_t **dft_matrx_Re_;
    mpz_t **dft_matrx_Im_;
    mpz_t *window;
    mpz_t bridge_variable_;
    mpfr_t quantizer;
    //vector<mpz_t> quantizers;//保存所有放大因子

public:  
    PuJianED(int mIn, int wlenIn, int incIn,
        int precisionIn = 30, int modLengthIn = 512);
    ~PuJianED();

    void DFT(mpz_t *OutCoefficientsRe, mpz_t *OutCoefficientsIm, 
    		mpz_t *inputSignalRe,mpz_t *inputSignalIm = NULL);
    void enframed_windowed_dft(mpz_t **re,mpz_t **im,mpz_t *input);
    void sptr_sub(mpz_t **re,mpz_t **im, float a, float b);
    void overlap_add(mpz_t *out,mpz_t **re,mpz_t **im);
    
    //谱减
    void basic_pujian(mpz_t *outSignal,mpz_t *inSignal, float aIn=4, float bIn=0.001);
};