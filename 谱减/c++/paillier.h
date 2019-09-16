#ifndef PAILLER_H_
#define PAILLER_H_ 

#include<gmp.h>

class PaillierEncryption {
public:        // element variables
    unsigned long int seed;
    mp_bitcnt_t modLength; //无符号长整型 used for bit counts and ranges
    gmp_randstate_t state; // algorithm selection and current state data
    mpz_t p, q, lambda, n, nsquare, g, mu, r; //intergers
    mpz_t tmp1, tmp2; 
    mpz_t n_half_,minus_1;

public:        // element methods
    PaillierEncryption(int modLengthIn=128);
    // 第二种构造函数，输入参数为p和q，不再随机生成p和q
    PaillierEncryption(const mpz_t pIn, const mpz_t qIn, int modLengthIn);

    // 初始化随机环境和大整数变量
    // 所有的构造函数下，必须第一个调用这个函数
    void initAllVar();
    void generate_p_q();
    void generateKeys();
    void encrypt(mpz_t ciphertext, const mpz_t plaintext);
    void encrypt(mpz_t ciphertext, const mpz_t plaintext, const mpz_t r);
    void decrypt(mpz_t  plaintext, const mpz_t ciphertext);

    // 解密，并把数值恢复到[-N/2,N/2]的范围
    void decrypt_and_recovery(mpz_t plaintext, const mpz_t ciphertext);
    void set_mu(const mpz_t muIn) {mpz_set(mu, muIn);}
    void set_g(const mpz_t gIn) {mpz_set(g, gIn);}
    void get_mu(mpz_t muOut) {mpz_set(muOut, mu);}
    void get_g(mpz_t gOut) {mpz_set(gOut, g);}

    void compute_new_mu();
    void set_g_compute_mu(const mpz_t gIn);


    // L(u) = (u-1)/n，将这一常用功能写成内连函数
    void Lfunction(mpz_t result, const mpz_t u, const mpz_t modulus);

    // 先相乘，再作模运算，将这一常用功能写成函数
    void multiplyAndModulo(mpz_t result, const mpz_t multiplier1, const mpz_t multiplier2, const mpz_t modulus);

    // 先乘以第二个因子的逆，再作模运算，将这一常用功能写成函数
    void multiply_invert_modulo(mpz_t result, const mpz_t multiplier1, const mpz_t multiplier2, const mpz_t modulus);

    // return a random integer in Z*_n
    void randomZStarN(mpz_t elemInZStarN);

    // return a random integer in Z*_{n^2}
    void randomZStarNSquare(mpz_t elemInZStarNSquare);

    void re_generate_random_r() {randomZStarN(r);}

    //////////////////////////////////////////////////////////////////////////
    ////////////		下面是位反序置换函数和格雷码置换函数
    //////////////////////////////////////////////////////////////////////////

    // bit-reversal function
    //The function takes 2 parameters - The value whose bits
    //need to be reversed and the number of bits in the value.
    unsigned int bitrev(unsigned int n, unsigned int bits);

    /*
    * This function converts an unsigned binary
    * number to reflected binary Gray code.
    *
    * The operator >> is shift right. The operator ^ is exclusive or.
    */
    unsigned int binaryToGray(unsigned int num);

    /*
    * This function converts a reflected binary
    * Gray code number to a binary number.
    * Each Gray code bit is exclusive-ored with all
    * more significant bits.
    */
    unsigned int grayToBinary(unsigned int num);

    /*
    * A more efficient version, for Gray codes of 32 or fewer bits.
    */
    unsigned int grayToBinary32(unsigned int num);

    void printValues();

    // 销毁所有的mpz_t变量
    ~PaillierEncryption();
}; //PaillierEncryption class


#endif