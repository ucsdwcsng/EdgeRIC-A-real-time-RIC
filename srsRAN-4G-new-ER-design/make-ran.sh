# hey there
cd srsRAN_4G-ER
sudo rm -rf build
mkdir build
cd build
cmake ../
make -j 20

cd ../../srsRAN_4G-ER-ue1
sudo rm -rf build
mkdir build
cd build
cmake ../
make -j 20

cd ../../srsRAN_4G-ER-ue2
sudo rm -rf build
mkdir build
cd build
cmake ../
make -j 20

# cd ../../UE3
# sudo rm -rf build
# mkdir build
# cd build
# cmake ../
# make -j 20