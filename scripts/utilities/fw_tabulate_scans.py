# fw_tabulate_scans.py
#
# Query flywheel to gather csv of available nifti files and associated 
# metadata across a given project.
#
# Author:   Katja Zoner
# Updated:  08/17/2021      

import flywheel
import pandas as pd
import numpy as np
import argparse
from datetime import date, datetime

# Get API_KEY from FW profile
API_KEY = "upenn.flywheel.io:47vhOSDkwMxGRNxFq0"

def getProject(projectLabel):
    
    # Get client
    fw = flywheel.Client(API_KEY)
    assert fw, "Your Flywheel CLI credentials aren't set!"

    # Get project object
    project = fw.projects.find_first('label="{}"'.format(projectLabel))
    assert project, f"Project {projectLabel} not found!"
    
    return project

def queryFlywheel(project):
    """ 
    Query Flywheel to create a dictionary of nifti files available in project.
    
    Arguments:
        project - Flywheel project object
        
    Returns: info dict, where:
        info[fileId] = [subId, sesId, acqLabel, filename, seriesNum, timestamp]
    """

    # Create info dict with entries for each subject.
    info = dict()

    # Loop through subjects in project
    #for sub in subjects:
    for sub in project.subjects():

        # Loop through sessions in subject
        for ses in sub.sessions():
            ses = ses.reload()

            # Loop through acquisitions in session
            for acq in ses.acquisitions():
                acq = acq.reload()

                # Loop through files in acquisition
                for f in acq.files:
                    
                    # Skip over non-nifti files
                    if f.type != 'nifti':
                        next

                    # Get Flywheel fileId to use as unique identifier
                    fileId = f.id

                    # Try to get timestamp (sometimes DateTime field isn't present.) 
                    try:
                        timestamp = f.info['AcquisitionDateTime']
                    except KeyError:
                        try:
                            timestamp = f.info['AcquisitionDate']
                        # Set to None if field isn't present
                        except:
                            timestamp = pd.NaT
                    
                    # Try to get series number (sometimes field isn't present.) 
                    try:
                        seriesNum = f.info['SeriesNumber']
                    # Set to None if field isn't present
                    except:
                        np.NaN                        
                    # Add the folowing metadata to study info dict:
                    # fileID: [subId, sesId, acqLabel, fileName, seriesNum, timestamp]
                    info[fileId] = [sub.label, ses.label, acq.label, f.name, seriesNum, timestamp]
    
    # Return project info dict
    return info


def main():

    # Use FW client to get project object
    project = getProject("Evolution_833922")
    
    # Build info dict containing metadata on all scans in FW project
    info = queryFlywheel(project)

    # Convert info dict to pandas dataframe and rename columns
    df = pd.DataFrame.from_dict(info, orient='index').reset_index()
    df.columns=['FlywheelFileId','SubjectId', 'SessionId', 'AcqLabel', 'Filename', 'SeriesNumber','Timestamp']
    
    # Export dataframe to csv
    filename = f'flywheel_scans_{date.today()}.csv'
    df.to_csv(filename,index=False)

if __name__== "__main__":
    main()
