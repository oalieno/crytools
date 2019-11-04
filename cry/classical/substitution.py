#!/usr/bin/env python3
import os
import math
import string
import random

class Substitution:
    def __init__(self, key = None):
        self.key = key
    
    @staticmethod
    def _s2a(s):
        return list(map(lambda x: ord(x) - ord('a'), s))

    @staticmethod
    def _a2s(a):
        return ''.join(map(lambda x: chr(x + ord('a')), a))

    @staticmethod
    def _encrypt(m, key):
        return [key[ch] for ch in m]

    @staticmethod
    def _decrypt(c, key):
        return [key.index(ch) for ch in c]
    
    def encrypt(self, m):
        return self._a2s(self._encrypt(self._s2a(m), self.key))

    def decrypt(self, c):
        return self._a2s(self._decrypt(self._s2a(c), self.key))

    def random_key(self):
        self.key = list(range(26))
        random.shuffle(self.key)

    def _load_grams(self, filename):
        grams = {}
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            lines = f.read().strip().split('\n')
            for line in lines:
                gram, count = line.split(' ')
                grams[gram.lower()] = int(count)
        return grams

    def _init_key(self, cipher, monograms):
        monograms = list(map(lambda x: self._s2a(x[0])[0], sorted(monograms.items(), key = lambda kv: kv[1], reverse = True)))
        key = [0] * 26
        for i, (count, ch) in enumerate(sorted(zip([cipher.count(ch) for ch in range(26)], range(26)))):
            key[ch] = monograms[i]
        return key

    def _score(self, text, grams):
        score = 0
        for gram in grams:
            total = sum(gram.values())
            for i in range(len(text) - len(list(gram.keys())[0]) + 1):
                score += math.log10(gram.get(self._a2s(text[i:i+4]), 0.01) / total)
        return score

    def _step(self, text, key, grams):
        best_key = key
        best_score = self._score(self._decrypt(text, key), grams)
        better = False
        for i in range(26):
            for j in range(i + 1, 26):
                new_key = key[:i] + [key[j]] + key[i+1:j] + [key[i]] + key[j+1:]
                new_score = self._score(self._decrypt(text, new_key), grams)
                if new_score > best_score:
                    better = True
                    best_key, best_score = new_key, new_score
        return best_key, better

    def frequency(self, cipher):
        monograms = self._load_grams('english_monograms.txt')
        bigrams = self._load_grams('english_bigrams.txt')
        trigrams = self._load_grams('english_trigrams.txt')
        quadgrams = self._load_grams('english_quadgrams.txt')

        cipher = self._s2a(cipher)
        key = self._init_key(cipher, monograms)
        while True:
            key, better = self._step(cipher, key, [trigrams, quadgrams])
            if not better:
                break
        self.key = key
