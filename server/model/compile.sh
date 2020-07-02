#!/bin/sh
set -ex

g++ -c main.cpp \
    -g1 -O3 \
    -std=c++17
    # -D_GLIBCXX_USE_CXX11_ABI=0 \
    # -Wabi-tag 
  
g++ -Wl,-rpath,"." -o prog main.o -I. -L. -lTGRAINS


./prog

rm main.o
