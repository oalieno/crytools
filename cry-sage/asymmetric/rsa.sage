#!/usr/bin/env python3
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
        while x % 2 == 0:
            x //= 2
        return x == 1
    
    @staticmethod
    def _solve(a, b, c):
        d = b * b - 4 * a * c
        if d < 0 or not is_square(d):
            return []
        sd = isqrt(d)
        return [int((-b + sd) // (2 * a)), int((-b - sd) // (2 * a))]

    def factor_n_with_d(self, d):
        while True:
            k = self.e * d - 1
            g = randint(2, self.n - 1)
            while True:
                if k % 2 == 1:
                    break
                k //= 2
                x = int(pow(g, k, self.n))
                if x > 1 and 1 < gcd(x - 1, self.n) < self.n:
                    p = gcd(x - 1, self.n)
                    self.provide_factor(p)
                    return p

    def provide_factor(self, p):
        if 1 < p < self.n and self.n % p == 0:
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
        phi = (self.p - 1) * (self.q - 1)
        if gcd(self.e, phi) == 1:
            self.d = inverse_mod(self.e, phi)
            return pow(c, self.d, self.n)
        else:
            print("Warning: gcd(e, phi) != 1")
            gp, dp, _ = xgcd(self.e, self.p - 1)
            gq, dq, _ = xgcd(self.e, self.q - 1)
            dp %= self.p - 1
            dq %= self.q - 1
            if gp != gq or not self._is_power_of_2(gp):
                raise AssertionError("RSA not decryptable")
            g = gp
            zp = Zmod(self.p)
            zq = Zmod(self.q)
            cps = [pow(c, dp, self.p)]
            cqs = [pow(c, dq, self.q)]
            while g % 2 == 0:
                _cps, _cqs = [], []
                for cp, cq in zip(cps, cqs):
                    xp = zp(cp).sqrt()
                    xq = zq(cq).sqrt()
                    _cps += [xp, -xp]
                    _cqs += [xq, -xq]
                cps, cqs = _cps, _cqs
                g //= 2
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
            self.provide_factor(int(result['factors'][0][0]))

    def _pollard_pm1(self):
        import sympy
        B = 10
        while True:
            p = sympy.pollard_pm1(self.n, B)
            if p:
                self.provide_factor(p)
                return p
            B *= 10

    @timeout(5)
    def pollard_pm1(self):
        self._pollard_pm1()

    def _fermat(self):
        a = isqrt(self.n)
        b2 = a * a - self.n
        while b2 < 0 or not is_square(b2):
            a = a + 1
            b2 = a * a - self.n
        b = isqrt(b2)
        self.provide_factors([a + b, a - b])
        return [a + b, a - b]

    @timeout(5)
    def fermat(self):
        self._fermat()

    def _yafu(self, path = None):
        if not path:
            path = str(Path(__file__).parent.parent.parent / Path('yafu'))
        p = subprocess.Popen([path, f'factor({self.n})'], stdout = subprocess.PIPE)
        result = p.communicate()[0].decode()
        for line in result.partition('***factors found***')[2].split('\n'):
            x = line.partition(' = ')[2]
            if x.isnumeric():
                self.provide_factor(int(x))

    @timeout(5)
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
        kd = (self.e / self.n).continued_fraction().convergents()
        for x in kd:
            k, d = x.numerator(), x.denominator()
            if k == 0:
                continue
            phi = (self.e * d - 1) // k
            roots = self._solve(1, phi - self.n - 1, self.n)
            if len(roots) == 2:
                p, q = roots
                if p * q == self.n:
                    self.provide_factors([p, q])
                    return [p, q]

