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

datas.obsprojects
-----------------

======================  ==========================================
COLUMN                  VALUE
======================  ==========================================
PRJ_ARCHIVE_UID         *(String)* Project UID
DELETED                 *(Boolean int)* Is Deleted?
PI                      *(String)* Principal Investigator
PRJ_NAME                *(String)* Project Name
** CODE                 *(String)* Project Code **Index**
PRJ_TIME_OF_CREATION    *(Datetime)* Project creation timestamp
PRJ_SCIENTIFIC_RANK     *(Int)* Project Rank
PRJ_VERSION             *(Int)* Project Version
PRJ_ASSIGNED_PRIORITY   *(Float)*
PRJ_LETTER_GRADE        *(Int)* Project Grade
DOMAIN_ENTITY_STATE     *(Int)* Project Status (ProTrack)
OBS_PROJECT_ID          *(String)* Project UID
EXEC                    *(String)* Executive
timestamp               *(Datetime)* Project latest update date
obsproj                 *(String)* Obsproject XML file
======================  ==========================================
Name: 2013.1.00114.S, dtype: object


The WTO API
===========

.. automodule:: wtoDatabase
   :members: