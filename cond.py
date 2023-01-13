import os
import sys
import shutil
import htcondor

# Get the current working directory.
cwd = os.getcwd()
cwd = cwd + '/'
# Job name should be provided as an argument.
if(len(sys.argv) < 2):
    print('Few no. of arguments provided, expected 2')
    sys.exit()
if(len(sys.argv) > 2):
    print('Too many arguments provided, expected 2')
    sys.exit()

#print(sys.argv[1])
# Create a dir to hold all of your jobs data.
if not os.path.exists('jobs'):
        os.mkdir('jobs')

# Create a dir for your job (delete and recreate if already exists).
job_path = f'jobs/{sys.argv[1]}'
if os.path.exists(job_path):
	shutil.rmtree(job_path)
	os.mkdir(job_path)
else:
	os.mkdir(job_path)

# Create 'test' dir to contain logs.
os.mkdir(job_path+'/test')

##################################################################################
CMSSW_BASE = os.popen('echo -n $CMSSW_BASE').read()
afs_out_path = cwd + job_path + '/output'

file_info = open('info.txt')
info = [line.strip() for line in file_info]

eos_out_path = info[1]
print(eos_out_path)
eos_out_path = eos_out_path + '/out_' + sys.argv[1]
if os.path.exists(eos_out_path):
	shutil.rmtree(eos_out_path)
	os.popen(f'mkdir -p {eos_out_path}')
else:
	os.popen(f'mkdir -p {eos_out_path}')

exec_content = '\
#!/bin/sh \n\
' + f'\
cd {CMSSW_BASE}/src/ \n\
' + '\
eval `scram runtime -sh` \n\
cd - \n\
cd tmp/ \n\
' + f'\
cmsRun {cwd}{job_path}/ElectronAnalyzer.py \
' + 'file_name=${1} \n\
' + '\
echo "${1}" >> temp \n\
sed -i "s/\///g" temp \n\
sed -i "s/ //g" temp \n\
sed -i "s/-//g" temp \n\
new_name=$(cat temp) \n\
echo "$new_name" \n\
\n\
# To output to AFS. \n\
' + f'\
#cp -r mynewelectrons.root {afs_out_path}' + '/${new_name} \n\
\n\
# To output to EOS. \n\
# Change to your EOS output path. \n\
' + f'\
cp -r mynewelectrons.root {eos_out_path}' + '/${new_name} \n\
'
with open(f'{job_path}/sub.sh', 'w') as exe:
	exe.write(exec_content)
exe.close()
##################################################################################

# Copy the 'Executable', 'ListOfFiles' and 'Analyzer/producer/...' to the job dir.
#shutil.copy('sub.sh', job_path)
shutil.copy('ListOfFiles.txt', job_path)
shutil.copy('ElectronAnalyzer.py', job_path)


col = htcondor.Collector()
credd = htcondor.Credd()
credd.add_user_cred(htcondor.CredTypes.Kerberos, None)

sub = htcondor.Submit()
sub['Executable'] =  cwd + job_path +  '/sub.sh'
sub['Error'] = cwd + job_path + '/test/$(ClusterId)_$(ProcId).err'
sub['Output'] = cwd + job_path + '/test/$(ClusterId)_$(ProcId).out'
sub['Log'] = cwd + job_path + '/test/$(ClusterId)_$(ProcId).log'
sub['MY.SendCredential'] = True
sub['+JobFlavour'] = '"tomorrow"'
sub['request_cpus'] = '8'
sub['Hold']='False'

file = open('ListOfFiles.txt')
lines = [line.strip() for line in file]
schedd = htcondor.Schedd()
with schedd.transaction() as txn:
	for f in lines:
		sub['Arguments'] = f
		cluster_id = sub.queue(txn)
	print(f'Job submitted successfully to cluster: {cluster_id}')
