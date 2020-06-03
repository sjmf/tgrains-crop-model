#!/bin/sh
set -ex

g++ -c testmodel.cpp \
    -g1 -O3 \
    -D_GLIBCXX_USE_CXX11_ABI=0 \
    -std=c++17 \
    -Wabi-tag 
  
g++ -Wl,-rpath,"." -o prog testmodel.o -I.. -L.. -lLandscape2019_LinuxSO

ln -sfn ../libLandscape2019_LinuxSO.so libLandscape2019_LinuxSO.so
rm testmodel.o

./prog

rm libLandscape2019_LinuxSO.so prog
