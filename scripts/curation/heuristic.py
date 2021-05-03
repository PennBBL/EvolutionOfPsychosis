'''
Heuristic to curate the Evolution_833922 project.
Katja Zoner
Updated: 04/27/2021
'''

import os

##################### Create keys for each acquisition type ####################

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

# Structural scans
t1w = create_key(
    'sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w')

# Field maps - fMRI
fmap_fmriAP = create_key(
    'sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-fmri_dir-AP_epi')
fmap_fmriPA = create_key(
    'sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-fmri_dir-PA_epi')

# fMRI scans
rest = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_dir-AP_bold')
er40 = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-e40_dir-AP_bold')
socialapproach = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-socialapproach_dir-AP_bold')

# ASL scans
perf = create_key(
    'sub-{subject}/{session}/perf/sub-{subject}_{session}_acq-se_asl')

# Diffusion weighted scans
dwi = create_key(
    'sub-{subject}/{session}/dwi/sub-{subject}_{session}_dwi')

# Field maps - dwi ??? two PA scans?
fmap_dwiAP= create_key(
    'sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-dwi_dir-AP_epi')
fmap_dwiPA = create_key(
    'sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-dwi_dir-PA_epi')

# T2star weighted
t2starw = create_key(
    'sub-{subject}/{session}/anat/sub-{subject}_{session}_T2starw')

# T2w
t2w = create_key(
    'sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w')

# Old T2w_ABCD sequence (present for several early subjects)
t2w_ABCD = create_key(
    'sub-{subject}/{session}/anat/sub-{subject}_{session}_acq-ABCD_T2w')
############################ Define heuristic rules ############################

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
    allowed template fields - follow python string module:
    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    #last_run = len(seqinfo)

    # Info dictionary to map series_id's to correct create_key key
    info = {
        t1w: [], 
        rest: [], er40: [], socialapproach: [],
        fmap_fmriAP: [], fmap_fmriPA: [],
        fmap_dwiAP: [], fmap_dwiPA: [],
        perf: [], dwi: [],
        t2starw: [], t2w: [], t2w_ABCD: []
        }

    def get_latest_series(key, s):
        info[key].append(s.series_id)

    for s in seqinfo:
        protocol = s.protocol_name.lower()

        # T1w structural scans
        if "mprage" in protocol and "navsetter" not in s.series_description:
            get_latest_series(t1w, s)

        # fMRI scans
        elif "task-rest" in protocol:
            get_latest_series(rest, s)
        elif "task-er40" in protocol:
            get_latest_series(er40, s)
        elif "task-socialapproach" in protocol:
            get_latest_series(socialapproach, s)
        
        # Fieldmap scans
        elif "fmap" in protocol:
            # fMRI fmaps
            if "acq-fmri" in protocol:
                if "dir-ap" in protocol:
                    get_latest_series(fmap_fmriAP, s)
                elif "dir-pa" in protocol:
                    get_latest_series(fmap_fmriPA, s)
            # dwi fmaps
            elif "acq-dwi" in protocol:
                # PhaseEncodingDirection= 'j-' --> PA
                # PhaseEncodingDirection= 'j' --> AP
                ## TODO: adjust for scans w/out PhaseEncodingDirection field
                if "-" in s.PhaseEncodingDirection:
                    get_latest_series(fmap_dwiPA, s)
                else: 
                    get_latest_series(fmap_dwiAP, s)
        
        # perf
        elif "pcasl" in protocol and not s.is_derived:
            get_latest_series(perf, s)

        # dwi
        elif "dwi-multishell" in protocol:
            get_latest_series(dwi, s)

        elif "t2star" in protocol:
            get_latest_series(t2starw, s)

        elif "t2w" in protocol and "navsetter" not in s.series_description:
            if "abcd" in protocol:
                get_latest_series(t2w_ABCD, s)
            # Disinclude T2w_SPC scan for now
            elif "spc" not in protocol:
                get_latest_series(t2w, s)

        else:
            print("Series not recognized!: ", s.protocol_name, s.dcm_dir_name)

    return info

################## Hardcode required params in MetadataExtras ##################
## TODO: no clu ;(
'''
MetadataExtras = {    
    perf: {
        "ArterialSpinLabelingType": "PCASL",

        "BackgroundSuppression": False, # required
        "InterPulseSpacing": 4,
        "LabelingDistance": 2,
        "LabelingDuration": 1.2, # required 
        "LabelingEfficiency": 0.72,
        "LabelingSlabLocation": "X", # correct
        "LabelingType": "PCASL", #?? unsure
        "M0Type": "Absent", # required 
        "PostLabelingDelay": 1.517, # required 2.0 us
        "PulseSequenceType": "2D",
        "RepetitionTimePreparation": 0, # required
    }
}
'''

# Should any other scans be listed here, or just fmri/dwi's?
IntendedFor = {
    fmap_fmriAP: [
        '{session}/func/sub-{subject}_{session}_task-rest_dir-AP_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-er40_dir-AP_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-socialapproach_dir-AP_bold.nii.gz'
    ],
    fmap_fmriPA:  [
        '{session}/func/sub-{subject}_{session}_task-rest_dir-AP_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-er40_dir-AP_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-socialapproach_dir-AP_bold.nii.gz'
    ],
    fmap_dwiPA: [
        '{session}/dwi/sub-{subject}_{session}_dwi.nii.gz'
    ]
}

# TODO: Need to get events tsv files
'''
def AttachToSession():
    NUM_VOLUMES=40
    data = ['control', 'label'] * NUM_VOLUMES
    data = '\n'.join(data)
    data = 'volume_type\n' + data # the data is now a string; perfect!

    # define asl_context.tsv file
    asl_context = {
        'name': 'sub-{subject}/{session}/perf/sub-{subject}_{session}_aslcontext.tsv',
        'data': data,
        'type': 'text/tab-separated-values'
    }

    import pandas as pd 

    df = pd.read_csv("info/task-idemo_events.tsv", sep='\t') 

    # define idemo events.tsv file
    idemo_events = {
        'name': 'sub-{subject}/{session}/func/sub-{subject}_{session}_task-idemo_events.tsv',
        'data': df.to_csv(index=False, sep='\t'),
        'type': 'text/tab-separated-values'
    }

    
    # define jolo events.tsv file
    jolo_events = {
        'name': 'sub-{subject}/{session}/func/sub-{subject}_{session}_task-jolo_events.tsv',
        'data': df.to_csv(index=False, sep='\t'),
        'type': 'text/tab-separated-values'
    }
    
    return [asl_context, idemo_events]
'''

####################### Rename session and subject labels #######################

# Use flywheel to gather a dictionary of all session session_labels
# with their corresponding index by time, within the subject
def gather_session_indices():

    import flywheel
    fw = flywheel.Client()

    proj = fw.projects.find_first('label="{}"'.format("Evolution_833922"))
    subjects = proj.subjects()

    # Initialize session dict
    # Key: existing session label
    # Value: new session label in form <proj_name><session idx>
    session_labels = {}

    for s in range(len(subjects)):

        # Get a list of the subject's sessions
        sessions = subjects[s].sessions()

        if sessions:
            # Sort session list by timestamp
            sessions = sorted(sessions, key=lambda x: x.timestamp)
            # loop through the subject's sessions, assign each session an index
            for i, sess in enumerate(sessions):
                session_labels[sess.label] = "EVO" + str(i + 1)

    return session_labels

session_labels = gather_session_indices()

# Replace session label with <proj_name><session_idx>
def ReplaceSession(ses_label):
    return str(session_labels[ses_label])
