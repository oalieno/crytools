

# This file was *autogenerated* from the file cry-sage/asymmetric/rsa.sage
from sage.all_cmdline import *   # import sage library

_sage_const_2 = Integer(2); _sage_const_0 = Integer(0); _sage_const_1 = Integer(1); _sage_const_4 = Integer(4); _sage_const_10 = Integer(10); _sage_const_5 = Integer(5)#!/usr/bin/env python3
import subprocess
from pathlib import Path

from ..utils import timeout

class RSA:
    def __init__(self, n, e, d = None, p = None, q = None):
        self.n = Integer(n)
        self.e = Integer(e)
        self.p = Integer(p)
        self.q = Integer(q)
        self.d = Integer(d)
    
    @staticmethod
    def _is_power_of_2(x):
        while x % _sage_const_2  == _sage_const_0 :
            x //= _sage_const_2 
        return x == _sage_const_1 
    
    @staticmethod
    def _solve(a, b, c):
        d = b * b - _sage_const_4  * a * c
        if d < _sage_const_0  or not is_square(d):
            return []
        sd = isqrt(d)
        return [int((-b + sd) // (_sage_const_2  * a)), int((-b - sd) // (_sage_const_2  * a))]

    def factor_n_with_d(self, d):
        while True:
            k = self.e * d - _sage_const_1 
            g = randint(_sage_const_2 , self.n - _sage_const_1 )
            while True:
                if k % _sage_const_2  == _sage_const_1 :
                    break
                k //= _sage_const_2 
                x = int(pow(g, k, self.n))
                if x > _sage_const_1  and _sage_const_1  < gcd(x - _sage_const_1 , self.n) < self.n:
                    p = gcd(x - _sage_const_1 , self.n)
                    self.provide_factor(p)
                    return p

    def provide_factor(self, p):
        if _sage_const_1  < p < self.n and self.n % p == _sage_const_0 :
            self.p = p
            self.q = self.n // p

    def provide_factors(self, ps):
        for p in ps:
            self.provide_factor(p)

    def encrypt(self, m):
        return pow(m, self.e, self.n)
    
    def decrypt(self, c):
        if not self.decryptable():
            raise AssertionError("RSA not decryptable")
        if self.d:
            return pow(c, self.d, self.n)
        phi = (self.p - _sage_const_1 ) * (self.q - _sage_const_1 )
        if gcd(self.e, phi) == _sage_const_1 :
            self.d = inverse_mod(self.e, phi)
            return pow(c, self.d, self.n)
        else:
            print("Warning: gcd(e, phi) != 1")
            gp, dp, _ = xgcd(self.e, self.p - _sage_const_1 )
            gq, dq, _ = xgcd(self.e, self.q - _sage_const_1 )
            dp %= self.p - _sage_const_1 
            dq %= self.q - _sage_const_1 
            if gp != gq or not self._is_power_of_2(gp):
                raise AssertionError("RSA not decryptable")
            g = gp
            zp = Zmod(self.p)
            zq = Zmod(self.q)
            cps = [pow(c, dp, self.p)]
            cqs = [pow(c, dq, self.q)]
            while g % _sage_const_2  == _sage_const_0 :
                _cps, _cqs = [], []
                for cp, cq in zip(cps, cqs):
                    xp = zp(cp).sqrt()
                    xq = zq(cq).sqrt()
                    _cps += [xp, -xp]
                    _cqs += [xq, -xq]
                cps, cqs = _cps, _cqs
                g //= _sage_const_2 
            ms = []
            for mp in cps:
                for mq in cqs:
                    m = crt([int(mp), int(mq)], [self.p, self.q])
                    ms.append(m)
            return ms

    def decryptable(self):
        return bool(self.d or (self.p and self.q))

    def factordb(self):
        import requests
        result = requests.get('http://factordb.com/api', params = {'query': str(self.n)}).json()
        if result['status'] == 'FF':
            self.provide_factor(int(result['factors'][_sage_const_0 ][_sage_const_0 ]))

    def _pollard_pm1(self):
        import sympy
        B = _sage_const_10 
        while True:
            p = sympy.pollard_pm1(self.n, B)
            if p:
                self.provide_factor(p)
                return p
            B *= _sage_const_10 

    @timeout(_sage_const_5 )
    def pollard_pm1(self):
        self._pollard_pm1()

    def _fermat(self):
        a = isqrt(self.n)
        b2 = a * a - self.n
        while b2 < _sage_const_0  or not is_square(b2):
            a = a + _sage_const_1 
            b2 = a * a - self.n
        b = isqrt(b2)
        self.provide_factors([a + b, a - b])
        return [a + b, a - b]

    @timeout(_sage_const_5 )
    def fermat(self):
        self._fermat()

    def _yafu(self, path = None):
        if not path:
            path = str(Path(__file__).parent.parent.parent / Path('yafu'))
        p = subprocess.Popen([path, f'factor({self.n})'], stdout = subprocess.PIPE)
        result = p.communicate()[_sage_const_0 ].decode()
        for line in result.partition('***factors found***')[_sage_const_2 ].split('\n'):
            x = line.partition(' = ')[_sage_const_2 ]
            if x.isnumeric():
                self.provide_factor(int(x))

    @timeout(_sage_const_5 )
    def yafu(self, path = None):
        self._yafu(path)

    def factor(parallel = False):
        if parallel:
            pass
        else:
            methods = [self.pollard_pm1, self.fermat, self.factordb, self.yafu]
            for method in methods:
                method()

    def wiener(self):
        '''
        Condition:
            d < 1/3 * n ^ 1/4
        '''
        #kd = Rational(f'{self.e} / {self.n}').continued_fraction().convergents()
        kd = (self.e / self.n).continued_fraction().convergents()
        for x in kd:
            k, d = x.numerator(), x.denominator()
            if k == _sage_const_0 :
                continue
            phi = (self.e * d - _sage_const_1 ) // k
            roots = self._solve(_sage_const_1 , phi - self.n - _sage_const_1 , self.n)
            if len(roots) == _sage_const_2 :
                p, q = roots
                if p * q == self.n:
                    self.provide_factors([p, q])
                    return [p, q]


