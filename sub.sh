#!/bin/sh
wd=$(echo "$PWD")
#awd = ${wd}/ElectronAnalyzer
cd /afs/cern.ch/user/a/ahussein/OpenData/CMSSW_7_6_7/src/
eval `scram runtime -sh`
cd -
cd tmp/
cmsRun ${wd}/ElectronAnalyzer.py file_name=${1}
#cmsRun /afs/cern.ch/user/a/ahussein/OpenData/CMSSW_7_6_7/src/Electron_Analyzer/v5/test/cond_py/ElectronAnalyzer.py file_name=${1}
#cmsRun $(pwd)/ElectronAnalyzer.py file_name=${1}

echo "${1}" >> temp
sed -i "s/\///g" temp
sed -i "s/ //g" temp
sed -i "s/-//g" temp
new_name=$(cat temp)
echo "$new_name"

# To output to AFS.
#cp -r mynewelectrons.root /afs/cern.ch/user/a/ahussein/OpenData/CMSSW_7_6_7/src/Electron_Analyzer/v5/test/cond_py/results/output/${new_name}

# To output to EOS.
# Change to your EOS output path.
cp -r mynewelectrons.root /eos/user/a/ahussein/trials/test_condor/runs_output/out/${new_name}
