.. gWTO documentation master file, created by
   sphinx-quickstart on Tue Jun 17 02:08:58 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The gWTO2 Documentation
=======================

.. contents:: Table of Contents

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



The WTO Data Frames
===================

wtoDatabase.obsprojects
-----------------------

======================  =============================================
COLUMN                  VALUE
======================  =============================================
PRJ_ARCHIVE_UID         *(string)* Project UID
DELETED                 *(boolean int)* Is Deleted?
PI                      *(string)* Principal Investigator
PRJ_NAME                *(string)* Project Name
** CODE                 *(string)* Project Code (**Index**)
PRJ_TIME_OF_CREATION    *(string)* Project creation timestamp
PRJ_SCIENTIFIC_RANK     *(int64)* Project Rank
PRJ_VERSION             *(string)* Project Version
PRJ_ASSIGNED_PRIORITY   *(object)* None
PRJ_LETTER_GRADE        *(string)* Project Grade
DOMAIN_ENTITY_STATE     *(string)* Project Status (ProTrack)
OBS_PROJECT_ID          *(string)* Project UID
EXEC                    *(string)* Executive
timestamp               *(datetime64[ns])* Project latest update date
obsproj                 *(string)* Obsproject XML filename
======================  =============================================



wtoDatabase.sciencegoals
------------------------

==================   ================================================
COLUMN               VALUE
==================   ================================================
CODE                 *(string)* Project Code
** partId            *(string)* Science Goal partId (**Index**)
AR                   *(float64)* Desired angular resolution (arcsec)
LAS                  *(float64)* Largest scale (arcser)
bands                *(string)* ALMA Band
isSpectralScan       *(boolean)*
isTimeConstrained    *(boolean)*
useACA               *(boolean)*
useTP                *(boolean)*
SBS                  *(list of str)* ScienceGoal SBs
startRime            *(string)* Time constrain start
endTime              *(string)* Time constrain end
allowedMargin        *(float64)* TC allowed margin
allowedUnits         *(string)* units
repeats              *(int)*
note                 *(string)* Time constrain notes
isavoid              *(boolean)*
==================   ================================================

wtoDatabase.schedblocks
-----------------------

==================   ================================================
COLUMN               VALUE
==================   ================================================
SB_UID               object
partId               object
timestamp            datetime64[ns]
sb_xml               object
==================   ================================================


wtoDatabase.schedblock_info
---------------------------
==================   ================================================
COLUMN               VALUE
==================   ================================================
SB_UID               *(string)*
partId               *(string)*
name                 *(string)*
status_xml           *(string)*
repfreq              *(float64)*
band                 *(string)*
array                *(string)*
RA                   *(float64)*
DEC                  *(float64)*
minAR_old            *(float64)*
maxAR_old            *(float64)*
execount             *(float64)*
isPolarization       *(boolean)*
amplitude            *(string)*
baseband             *(string)*
polarization         *(string)*
phase                *(string)*
delay                *(string)*
science              *(string)*
integrationTime      *(float64)*
subScandur           *(float64)*
maxPWVC              *(float64)*
==================   ================================================

wtoDatabase.target
------------------
==================   ================================================
COLUMN               VALUE
==================   ================================================
SB_UID               *(string)*
specRef              *(string)*
fieldRef             *(string)*
paramRef             *(string)*
==================   ================================================

wtoDatabase.fieldsource
-----------------------
==================   ================================================
COLUMN               VALUE
==================   ================================================
fieldRef             object
SB_UID               object
solarSystem          object
sourcename           object
name                 object
RA                   float64
DEC                  float64
isQuery              object
intendedUse          object
qRA                  object
qDEC                 object
use                  object
search_radius        object
rad_unit             object
ephemeris            object
pointings            float64
isMosaic             object
==================   ================================================

wtoDatabase.spectralconf
------------------------
specRef       object
SB_UID        object
BaseBands    float64
SPWs         float64

wtoDatabase.sb_summary (*"view"*)
---------------------------------
CODE                           object
OBS_PROJECT_ID1                object
partId                         object
SB_UID                         object
name                           object
status_xml                     object
bands                          object
repfreq                       float64
array                          object
RA                            float64
DEC                           float64
minAR                         float64
maxAR                         float64
arrayMinAR                    float64
arrayMaxAR                    float64
execount                      float64
PRJ_SCIENTIFIC_RANK           float64
PRJ_LETTER_GRADE               object
EXEC                           object
OBSUNIT_UID                    object
NAME                           object
REPR_BAND                     float64
SCHEDBLOCK_CTRL_EXEC_COUNT    float64
SCHEDBLOCK_CTRL_STATE          object
MIN_ANG_RESOLUTION            float64
MAX_ANG_RESOLUTION            float64
OBSUNIT_PROJECT_UID            object
DOMAIN_ENTITY_STATE            object
OBS_PROJECT_ID                 object
QA0Unset                      float64
QA0Pass                       float64
Total_exe                     float6


wtoDatabase.qa0
---------------
SCHEDBLOCKUID    object
QA0STATUS        object

wtoDatabase.scheduling_proj
---------------------------
OBSPROJECTID                    int64
OBSPROJECT_UID                 object
CODE                           object
NAME                           object
VERSION                        object
PI                             object
SCIENCE_SCORE                 float64
SCIENCE_RANK                    int64
SCIENCE_GRADE                  object
STATUS                         object
TOTAL_EXEC_TIME               float64
CSV                             int64
MANUAL                          int64
OBSUNITID                       int64
STATUS_ENTITY_ID               object
STATUS_ENTITY_ID_ENCRYPTED     object
STATUS_ENTITY_TYPE_NAME        object
STATUS_SCHEMA_VERSION          object
STATUS_DOCUMENT_VERSION        object
STATUS_TIMESTAMP               object

wtoDatabase.scheduling_sb
-------------------------
OBSUNIT_UID                    object
NAME                           object
REPR_BAND                       int64
SCHEDBLOCK_CTRL_EXEC_COUNT      int64
SCHEDBLOCK_CTRL_STATE          object
MIN_ANG_RESOLUTION            float64
MAX_ANG_RESOLUTION            float64
OBSUNIT_PROJECT_UID            object



The WTO API
===========

.. automodule:: wtoDatabase
   :members: