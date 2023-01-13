# Import CMS-specific Python classes and functions.
import FWCore.ParameterSet.Config as cms
# Imports necessary to output ROOT files.
import FWCore.Utilities.FileUtils as FileUtils
# Imports to use json files.
import FWCore.PythonUtilities.LumiList as LumiList
import FWCore.ParameterSet.Types as CfgTypes

# Imports for using command-line arguments.
import sys
for arg in sys.argv[2:]:
        opt = arg[0:arg.find("=")]
        if opt=="file_name":
         file_name = arg[arg.find("=")+1:]

# sys.argv takes the parameters given as input cmsRun PhysObjectExtractor/python/poet_cfg.py <>
# e.g: cmsRun PhysObjectExtractor/python/poet_cfg.py data
# NB the first two parameters are always "cmsRun" and the config file name
# mc -> work with MC, data -> work with data, <> -> work with data.
# This needs to be in agreement with the input files/datasets below.
#if(len(sys.argv) > 3):
#    sys.exit('Too many arguments!')
#if(len(sys.argv) == 3):
#    if(sys.argv[2].lower() == 'mc'):
#        isData = False
#    elif(sys.argv[2].lower() == 'data'):
#        isData = True
#    else:
#        sys.exit('Unknown argument!')
#else:
#    isData = True
#
#isMC = True
#if isData: isMC = False

process = cms.Process("Electron")

# Configure the framework messaging system
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMessageLogger
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = "WARNING"
process.MessageLogger.categories.append("Electron")
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
    limit=cms.untracked.int32(-1)
)
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

# Select the maximum number of events to process (if -1, run over all events)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

#Define the test source files to be read using the
#xrootd protocol (root://),
#or local files (file:)
#process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
#    fileNames = cms.untracked.vstring(
        #'file:myfile.root'
        #'root://eospublic.cern.ch//eos/opendata/cms/mc/RunIIFall15MiniAODv2/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/00000/0005EA25-8CB8-E511-A910-00266CF85DA0.root'
#        'root://eospublic.cern.ch//eos/opendata/cms/mc/RunIIFall15MiniAODv2/TT_TuneCUETP8M1_13TeV-powheg-pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12_ext3-v1/00000/02837459-03C2-E511-8EA2-002590A887AC.root'
#    )
#)


#if isData:
#    process.source.fileNames = cms.untracked.vstring(
        #'root://eospublic.cern.ch//eos/opendata/cms/Run2015D/DoubleMuon/MINIAOD/16Dec2015-v1/10000/000913F7-E9A7-E511-A286-003048FFD79C.root'
#        'root://eospublic.cern.ch//eos/opendata/cms/Run2015D/SingleElectron/MINIAOD/08Jun2016-v1/10000/001A703B-B52E-E611-BA13-0025905A60B6.root'
#    )

# Read from a list of files on eos.
process.source = cms.Source("PoolSource",
   fileNames = cms.untracked.vstring(
   file_name
)
)


# Apply the data quality JSON file filter. This example is for 2015 data
# It needs to be done after the process.source definition
# Make sure the location of the file agrees with your setup
goodJSON = "/afs/cern.ch/user/a/ahussein/OpenData/CMSSW_7_6_7/src/Electron_Analyzer/v5/data/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt"
myLumis = LumiList.LumiList(filename=goodJSON).getCMSSWString().split(",")
process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
process.source.lumisToProcess.extend(myLumis)

# Needed configuration for dealing with transient tracks if required.
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

# These two lines are needed if you require access to the conditions database,
# E.g., to get jet energy corrections, trigger prescales, etc.
process.load("Configuration.StandardSequences.Services_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
# If the container has local DB files available, uncomment lines like the ones below instead of the corresponding lines above
#if isData: 
process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_dataRun2_16Dec2015_v0.db')
#else: 
#process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_mcRun2_asymptotic_RunIIFall15DR76_v1.db')
# The global tag must correspond to the needed epoch (comment out if no conditions needed)
#if isData: 
process.GlobalTag.globaltag = '76X_dataRun2_16Dec2015_v0'
#else: 
#process.GlobalTag.globaltag = "76X_mcRun2_asymptotic_RunIIFall15DR76_v1"

# Configure the Electron Analyzer.
process.load("Electron_Analyzer.v5.electronAnalyzer_cff")
# Change the default value of the parameter "testBool".
# You can even initialize new parameters in additional to those in the _cfi file.
process.electronAnalyzer.testBool = cms.bool(False)

# Attach the FileService module to the proces.
process.TFileService = cms.Service("TFileService", fileName=cms.string("mynewelectrons.root"))

#if isData:
#    process.p = cms.Path(process.electronAnalyzer)
#else:
#    process.p = cms.Path(process.electronAnalyzer)
process.p = cms.Path(process.electronAnalyzer)
