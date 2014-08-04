*******************
The WTO Data Frames
*******************

wtoDatabase.obsprojects
=======================

Main obsproject table ingested from queries to the archive.

======================  ========================================================
COLUMN                  VALUE
======================  ========================================================
PRJ_ARCHIVE_UID         *(string)* Project UID (1)
DELETED                 *(boolean int)* Is Deleted? (2)
PI                      *(string)* Principal Investigator (3)
PRJ_NAME                *(string)* Project Name (4)
** CODE                 *(string)* Project Code (5)
PRJ_TIME_OF_CREATION    *(string)* Project creation timestamp (6)
PRJ_SCIENTIFIC_RANK     *(int64)* Project Rank (7)
PRJ_VERSION             *(string)* Project Version (8)
PRJ_LETTER_GRADE        *(string)* Project Grade (9)
DOMAIN_ENTITY_STATE     *(string)* Project Status (10)
OBS_PROJECT_ID          *(string)* Project UID (11)
EXEC                    *(string)* Executive (12)
timestamp               *(datetime64[ns])* Project latest update date (13)
obsproj                 *(string)* Obsproject XML filename (14)

======================  ========================================================

1. ALMA.BMMV_OBSPROJECT.PRJ_ARCHIVE_UID
2. ALMA.BMMV_OBSPROJECT.DELETED
3. ALMA.BMMV_OBSPROJECT.PI
4. ALMA.BMMV_OBSPROJECT.PRJ_NAME
5. ALMA.BMMV_OBSPROJECT.CODE
6. ALMA.BMMV_OBSPROJECT.PRJ_TIME_OF_CREATION
7. ALMA.BMMV_OBSPROJECT.PRJ_SCIENTIFIC_RANK
8. ALMA.BMMV_OBSPROJECT.PRJ_VERSION
9. ALMA.BMMV_OBSPROJECT.PRJ_LETTER_GRADE
10. ALMA.BMMV_OBSPROJECT.DOMAIN_ENTITY_STATE
11. ALMA.BMMV_OBSPROJECT.OBS_PROJECT_ID
12. ALMA.BMMV_OBSPROPOSAL.ASSOCIATEDEXEC
13. ALMA.XML_OBSPROJECT_ENTITIES.TIMESTAMP
14. link to ALMA.XML_OBSPROJECT_ENTITIES.XML


wtoDatabase.sciencegoals
========================

==================   ===========================================================
COLUMN               VALUE
==================   ===========================================================
CODE                 *(string)* Project Code (1)
** partId            *(string)* Science Goal partId (2)
AR                   *(float64)* Desired angular resolution (arcsec) (3)
LAS                  *(float64)* Largest scale (arcsec) (4)
bands                *(string)* ALMA Band (5)
isSpectralScan       *(boolean)* (6)
isTimeConstrained    *(boolean)* (7)
useACA               *(boolean)* (8)
useTP                *(boolean)* (9)
ps                   *(boolean)* Is point source?
SBS                  *(list of strings)* :ref:`ScienceGoals SBs <sgsb>`
startRime            *(string)* Time constrain start (10)
endTime              *(string)* Time constrain end (11)
allowedMargin        *(float64)* TC allowed margin (12)
allowedUnits         *(string)* units (13)
repeats              *(int)* (14)
note                 *(string)* Time constraint notes (15)
isavoid              *(boolean)* Time constrait is to avoid (16)
==================   ===========================================================

1. ALMA.BMMV_OBSPROJECT.CODE
2. ``xml:ObsProject.ObsProgram.ScienceGoal.ObsUnitSetRef['partId']``
3. ``xml:...PerformanceParameters.desiredAngularResolution``
4. ``xml:...PerformanceParameters.desiredLargestScale``
5. ``xml:...requiredReceiverBands``
6. ``xml:...SpectralSetupParameters.SpectralScan``
7. ``xml:...PerformanceParameters.isTimeConstrained``
8. ``xml:...PerformanceParameters.useACA``
9. ``xml:...PerformanceParameters.useTP``
10. ``xml:...sciencegoal.PerformanceParameters.TemporalParameters.startTime``
11. ``xml:...sciencegoal.PerformanceParameters.TemporalParameters.endTime``
12. ``xml:...sciencegoal.PerformanceParameters.TemporalParameters.allowedMargin``
13. (idem)
14. ``xml:...PerformanceParameters.TemporalParameters.repeats``
15. ``xml:...PerformanceParameters.TemporalParameters.note``
16. ``xml:...PerformanceParameters.TemporalParameters.isAvoidConstraint``

.. _sgsb:

Extracting Science Goals' SBs.
------------------------------

To get the Scheduling Blocks that are part of a ScienceGoal entity the partId
is used.

wtoDatabase.schedblocks
=======================

==================   ===========================================================
COLUMN               VALUE
==================   ===========================================================
SB_UID               *(string)* SB UID
partId               *(string)* Science Goal partId
timestamp            *(datetime64[ns])* Project latest update date (13)
sb_xml               *(string)* SchedBlock XML filename
==================   ===========================================================


wtoDatabase.schedblock_info
===========================
==================   ===========================================================
COLUMN               VALUE
==================   ===========================================================
SB_UID               *(string)* SB UID
partId               *(string)* Science Goal partId
name                 *(string)* SB Name
status_xml           *(string)* SB status (from xml entity)
repfreq              *(float64)* SB representative frequency (GHz)
band                 *(string)* SB requested Band
array                *(string)* SB type of array
RA                   *(float64)* Representative RA (degrees)
DEC                  *(float64)* Representative DEC (degrees)
minAR_old            *(float64)* Original minimum angular resolution (arcsec)
maxAR_old            *(float64)* Original maximum angular resolution (arcsec)
execount             *(float64)* Requested executions
isPolarization       *(boolean)* Is a polarization SB?
amplitude            *(string)* AmplitudeParameters partId
baseband             *(string)* BasebandParameteres partId
polarization         *(string)* PolarizationParameters partId
phase                *(string)* PhaseParameters partId
delay                *(string)* DelaryParameters partId
science              *(string)* ScienceParameters partId
integrationTime      *(float64)* Science target integration time (sec)
subScandur           *(float64)* Science target subscan duration (sec)
maxPWVC              *(float64)* PWV asumed by the OT (mm)
==================   ===========================================================

wtoDatabase.target
==================
==================   ================================================
COLUMN               VALUE
==================   ================================================
SB_UID               *(string)*
specRef              *(string)*
fieldRef             *(string)*
paramRef             *(string)*
==================   ================================================

wtoDatabase.fieldsource
=======================
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
========================
==================   ================================================
COLUMN               VALUE
==================   ================================================
specRef              object
SB_UID               object
BaseBands            float64
SPWs                 float64
==================   ================================================

wtoDatabase.sb_summary
======================
===========================   ============
COLUMN                        VALUE
===========================   ============
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
===========================   ============

wtoDatabase.qa0
===============
==================   =========================
COLUMN               VALUE
==================   =========================
SCHEDBLOCKUID        object
QA0STATUS            object
==================   =========================

wtoDatabase.scheduling_proj
===========================

Queries project data from the SCHEDULING_AOS archive tables.
::

    SELECT *
    FROM SCHEDULING_AOS.OBSPROJECT
    WHERE regexp_like (CODE, '^201[23].*\.[AST]')

===========================   ================================================
COLUMN                        VALUE
===========================   ================================================
OBSPROJECTID                  SQL index
OBSPROJECT_UID                OBSPROJECT xml entity UID
CODE                          Project CODE
NAME                          Project Name
VERSION                       Project Version
PI                            Principal Investigator user name
SCIENCE_SCORE                 Science Score
SCIENCE_RANK                  Science Ranking
SCIENCE_GRADE                 Project letter grade
STATUS                        Project status in SCHEDULING_AOS
TOTAL_EXEC_TIME
CSV                           Is CSV?
MANUAL                        Is Manual Mode?
OBSUNITID                     Obsunit part ID
STATUS_ENTITY_ID
STATUS_ENTITY_ID_ENCRYPTED
STATUS_ENTITY_TYPE_NAME
STATUS_SCHEMA_VERSION
STATUS_DOCUMENT_VERSION
STATUS_TIMESTAMP
===========================   ================================================

wtoDatabase.scheduling_sb
=========================

Queries scheduling block data from SCHEDULING_AOS tables.::

    SELECT ou.OBSUNIT_UID,sb.NAME,sb.REPR_BAND,
           sb.SCHEDBLOCK_CTRL_EXEC_COUNT,sb.SCHEDBLOCK_CTRL_STATE,
           sb.MIN_ANG_RESOLUTION,sb.MAX_ANG_RESOLUTION,
           ou.OBSUNIT_PROJECT_UID
    FROM SCHEDULING_AOS.SCHEDBLOCK sb, SCHEDULING_AOS.OBSUNIT ou
    WHERE sb.SCHEDBLOCKID = ou.OBSUNITID AND sb.CSV = 0

===========================   ================================================
COLUMN                        VALUE
===========================   ================================================
OBSUNIT_UID                    object
NAME                           object
REPR_BAND                       int64
SCHEDBLOCK_CTRL_EXEC_COUNT      int64
SCHEDBLOCK_CTRL_STATE          object
MIN_ANG_RESOLUTION            float64
MAX_ANG_RESOLUTION            float64
OBSUNIT_PROJECT_UID            object
===========================   ================================================

wtoDatabase.sbstate
===================

