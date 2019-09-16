#include"paillier.h"
#include<gmp.h>
#include<time.h>
#include<stdlib.h>


PaillierEncryption::PaillierEncryption(int modLengthIn) {
	initAllVar();
	modLength = modLengthIn;

	generate_p_q();
	generateKeys();// 生成密钥
}

PaillierEncryption::PaillierEncryption(const mpz_t pIn, const mpz_t qIn, int modLengthIn) {
    modLength = modLengthIn;

    // 初始化所有的mpz_t变量
    initAllVar();

    mpz_set(p, pIn);
    mpz_set(q, qIn);

    generateKeys();

}

void PaillierEncryption::initAllVar() {    // 初始化随机环境

    //随机生成种子
    srand((unsigned)time(0));
    seed=rand();

    gmp_randinit_default(state);  //generated random number
    gmp_randseed_ui(state, seed); // choosing seed is critical

    // 初始化所有的mpz_t变量
    mpz_inits(p, q, lambda, n, nsquare, g, mu, tmp1, tmp2, r, n_half_, minus_1, NULL); //set 0; 
}

void PaillierEncryption::generate_p_q() {
    // a random prime
    mpz_urandomb(p, state, modLength / 2); //generate a uniformly distributed random interges in range 
    mpz_nextprime(p, p); //set p1 to the next primer greater than p2

    // a random prime (distinct from p)
    do {
        mpz_urandomb(q, state, modLength / 2);
        mpz_nextprime(q, q);
    } while (mpz_cmp(p, q) == 0);
}

void PaillierEncryption::generateKeys() {

    mpz_mul(n, p, q);            // n = p*q
    mpz_mul(nsquare, n, n);        // nsquare = n*n
    mpz_sub_ui(tmp1, p, 1);
    mpz_sub_ui(tmp2, q, 1);
    mpz_lcm(lambda, tmp1, tmp2);    // lambda = lcm(p-1, q-1)

    do {
        // generate g, a random integer in Z*_{n^2}
        randomZStarNSquare(g);

        mpz_powm(tmp1, g, lambda, nsquare);
        mpz_sub_ui(tmp1, tmp1, 1);
        mpz_cdiv_q(tmp1, tmp1, n);
        mpz_gcd(tmp1, tmp1, n);
    }
        // verify g, the following must hold: gcd(L(g^lambda mod n^2), n) = 1, where L(u) = (u-1)/n
    while (mpz_cmp_ui(tmp1, 1));

    // mu = (L(g^lambda mod n^2))^{-1} mod n, where L(u) = (u-1)/n
    mpz_powm(mu, g, lambda, nsquare);
    Lfunction(mu, mu, n);        // L(mu)=(mu-1)/n
    mpz_invert(mu, mu, n);

    // generate a random integer in Z*_n,
    randomZStarN(r);

    mpz_fdiv_q_2exp(n_half_, n, 1);
    mpz_sub_ui(minus_1,n,1);
}

void PaillierEncryption::encrypt(mpz_t ciphertext, const mpz_t plaintext) {
    // if m is not in Z_n
    // 因为还不懂怎么写C++的异常抛出，这里没有写
    // 以后懂了，再补上

    mpz_mod(ciphertext,plaintext,n);//负数修正，另外由于引入负数，名文值域范围变为-n/2~n/2

    randomZStarN(r);    //使得每次加密结果不同

    mpz_powm(tmp1, g, ciphertext, nsquare);        // g^m mod n^2
    mpz_powm(tmp2, r, n, nsquare);        // r^n mod n^2
    multiplyAndModulo(ciphertext, tmp1, tmp2, nsquare); // c = g^m * r^n mod n^2
}


void PaillierEncryption::decrypt(mpz_t plaintext, const mpz_t ciphertext) {
    // if c is not in Z*_{n^2}
    // 以后用C++异常抛出，补上，用return 0或者-1是不合理的
    // 而且函数也没有返回参数

    // m = L(c^lambda mod n^2) * mu mod n, where L(u) = (u-1)/n
    mpz_powm(plaintext, ciphertext, lambda, nsquare);
    Lfunction(plaintext, plaintext, n);
    multiplyAndModulo(plaintext, plaintext, mu, n);
}

void PaillierEncryption::decrypt_and_recovery(mpz_t plaintext, const mpz_t ciphertext) {
    // if c is not in Z*_{n^2}
    // 以后用C++异常抛出，补上，用return 0或者-1是不合理的
    // 而且函数也没有返回参数
    decrypt(plaintext, ciphertext);
    if (mpz_cmp(plaintext, n_half_) > 0) // 如果plaintext大于n^2/2
    {
        mpz_sub(plaintext, plaintext, n); // 则用plaintext-n
    }
}

void PaillierEncryption::compute_new_mu() {
    // mu = (L(g^lambda mod n^2))^{-1} mod n, where L(u) = (u-1)/n
    mpz_powm(mu, g, lambda, nsquare);
    Lfunction(mu, mu, n);        // L(mu)=(mu-1)/n
    mpz_invert(mu, mu, n);
}

void PaillierEncryption::set_g_compute_mu(const mpz_t gIn) {
    set_g(gIn);
    compute_new_mu();
}

void PaillierEncryption::Lfunction(mpz_t result, const mpz_t u, const mpz_t modulus) {
	mpz_sub_ui(result, u, 1);
	mpz_cdiv_q(result, result, modulus);

}


// 先相乘，再作模运算，将这一常用功能写成函数
void PaillierEncryption::multiplyAndModulo(mpz_t result, const mpz_t multiplier1, const mpz_t multiplier2, const mpz_t modulus) {
    mpz_mul(result, multiplier1, multiplier2);
    mpz_mod(result, result, modulus);
}

// 先乘以第二个因子的逆，再作模运算，将这一常用功能写成函数
void PaillierEncryption::multiply_invert_modulo(mpz_t result, const mpz_t multiplier1, const mpz_t multiplier2, const mpz_t modulus) {
    mpz_invert(result, multiplier2, modulus);
    mpz_mul(result, multiplier1, result);
    mpz_mod(result, result, modulus);
}

// return a random integer in Z*_n
void PaillierEncryption::randomZStarN(mpz_t elemInZStarN) {
    do { 
        mpz_urandomb(elemInZStarN, state, modLength);
        mpz_gcd(tmp1, elemInZStarN, n);
    } 
    while (mpz_cmp(elemInZStarN, n) >= 0 || mpz_cmp_ui(tmp1,1)!=0);
}

// return a random integer in Z*_{n^2}
void PaillierEncryption::randomZStarNSquare(mpz_t elemInZStarNSquare) {
    do {
        mpz_urandomb(elemInZStarNSquare, state, modLength * 2);
        mpz_gcd(tmp1, elemInZStarNSquare, nsquare);
    } while (mpz_cmp(elemInZStarNSquare, nsquare) >= 0 || mpz_cmp_ui(tmp1, 1) != 0);
}


unsigned int PaillierEncryption::bitrev(unsigned int n, unsigned int bits) {
    unsigned int nrev, N;
    unsigned int count;
    N = 1 << bits;
    count = bits - 1;   // initialize the count variable
    nrev = n;
    for (n >>= 1; n; n >>= 1) {
        nrev <<= 1;
        nrev |= n & 1;
        count--;
    }
    nrev <<= count;
    nrev &= N - 1;
    return nrev;
}

/*
* This function converts an unsigned binary
* number to reflected binary Gray code.
*
* The operator >> is shift right. The operator ^ is exclusive or.
*/
unsigned int PaillierEncryption::binaryToGray(unsigned int num) {
    return num ^ (num >> 1);
}

/*
* This function converts a reflected binary
* Gray code number to a binary number.
* Each Gray code bit is exclusive-ored with all
* more significant bits.
*/
unsigned int PaillierEncryption::grayToBinary(unsigned int num) {
    unsigned int mask;
    for (mask = num >> 1; mask != 0; mask = mask >> 1) {
        num = num ^ mask;
    }
    return num;
}

/*
* A more efficient version, for Gray codes of 32 or fewer bits.
*/
unsigned int PaillierEncryption::grayToBinary32(unsigned int num) // 我算了一下，32位数最大是8589934591
{
    num = num ^ (num >> 16);
    num = num ^ (num >> 8);
    num = num ^ (num >> 4);
    num = num ^ (num >> 2);
    num = num ^ (num >> 1);
    return num;
}


void PaillierEncryption::printValues() {
    gmp_printf("p:       %Zd\n", p);
    gmp_printf("q:       %Zd\n", q);
    gmp_printf("lambda:  %Zd\n", lambda);
    gmp_printf("n:       %Zd\n", n);
    gmp_printf("nsquare: %Zd\n", nsquare);
    gmp_printf("n/2: %Zd\n", n_half_);
    gmp_printf("g:       %Zd\n", g);
    gmp_printf("r:       %Zd\n", r);
    gmp_printf("mu:      %Zd\n", mu);
}

// 销毁所有的mpz_t变量
PaillierEncryption::~PaillierEncryption() {
    mpz_clears(p, q, lambda, n, nsquare, g, mu, tmp1, tmp2, r, n_half_, minus_1, NULL);
}