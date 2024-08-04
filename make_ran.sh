cd srsran-enb
#sudo 
rm -rf build
mkdir build
cd build
cmake ../
make -j 30
cd ../..

cd srsran-ue
#sudo 
rm -rf build
mkdir build
cd build
cmake ../
make -j 30
