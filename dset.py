import copy
import csv
import functools
import glob
import os

from collections import namedtuple

CandidateInfoTuple = namedtuple(
    'CandidateInfoTuple',
    'isNodule_bool, diameter_mm, series_uid, center_xyz',
)

@functools.lru_cache(1)
def getCandidateInfoList(requireOnDisk_bool=True):
    # We construct a set with all series_uids that are present on disk.
    # This will let us use the data, even if we haven't downloaded all of
    # the subsets yet
    mhd_list = glob.glob('/kaggle/input/luna16/subset0/subset0/*.mhd')
    presentOnDisk_set = {os.path.split(p)[-1][:-4] for p in mhd_list}   #Takes path as input and returns the series_uuid from path



    diameter_dict = {}

    with open('/kaggle/input/luna16/annotations.csv', 'r') as f:
        for row in list(csv.reader(f))[1:]:
            series_uid = row[0]
            annotationCenter_xyz = tuple( [float(x) for x in row[1:4] ] )
            annotationDiameter_mm = float(row[4])

            diameter_dict.setdefault(series_uid, []).append(
                (annotationCenter_xyz, annotationDiameter_mm)
            )


    candidateInfo_list =  []

    with open('/kaggle/input/luna16/candidates.csv', 'r') as f:
        for row in list(csv.reader(f))[1:]:
            series_uid = row[0]

            if series_uid not in presentOnDisk_set and requireOnDisk_bool:
                continue

            isNodule_bool = bool(int(row[4]))
            candidateCenter_xyz = tuple([float(x) for x in row[1:4]])

            candidateDiameter_mm = 0.0
            for annotation_tuple in diameter_dict.get(series_uid, []):
                annotationCenter_xyz, annotationDiameter_mm = annotation_tuple
                
                for i in range(3):
                    delta_mm = abs( annotationCenter_xyz[i] - candidateCenter_xyz[i] )

                    if delta_mm > annotationDiameter_mm / 4 :
                        break
                    else:
                        candidateDiameter_mm = annotationDiameter_mm
                        break

            candidateInfo_list.append( CandidateInfoTuple(
                isNodule_bool,
                candidateDiameter_mm,
                series_uid,
                candidateCenter_xyz
            ) )

        candidateInfo_list.sort( reverse=True )

        # print(candidateInfo_list[-1][2])

        return candidateInfo_list


getCandidateInfoList()        