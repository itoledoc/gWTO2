.. gWTO documentation master file, created by
   sphinx-quickstart on Tue Jun 17 02:08:58 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

******************************
Welcome to gWTO2 documentation
******************************

Contents:

.. toctree::
   :titlesonly:
   :maxdepth: 2

   intro
   using
   algorithm
   play
   wtoapi
   wtodata
   apendix

Download the pdf version of the documentation from this
:download:`link <_build/latex/gWTO2.pdf>`.

.. note::

   **Latest update:**
   |today|

   **Latest changes in the code:**

   #. Fixed rank score function

.. note::

   TODO List.

   #. Deal with Total Power SBs.
   #. Add all sb option, to show all SBs with a quick explanation on why they are
      or not observable.
   #. Add explanations of different Tabs: Time Const, Polarization, Sessions, TP,
      etc.
   #. Use time constraint info to actually show or not Time Constrained SBs in the
      relevant Tab.
   #. Tune up the ranking algorithm. Maybe it would be a better practice to start
      with a base score given by what it is now called the *condition score*, and
      then punish or reward this score taking into account the other conditions.

.. warning::

   Things to be checked.

   #. Some SBs are Time Constrained, but they have not set the flag
      :keyword:`isTimeConstrained`.
   #. Need to handle some SBs that have multiple ScienceParameters.


******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
