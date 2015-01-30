************
Introduction
************

.. figure:: Selection_003.png
   :scale: 60%
   :align: center

   Screenshot of gWTO2 RC

Goal
====

gWTO2 (gui for What To Observe cycle 2) is a real-time scheduler that uses both
a selection and score algorithms to select the best SB to observe given the
current conditions. However, its main goal is to provide a flexible and dynamic
benchmark where to test and optimize the algorithms that are being use in the
official scheduling tool for ALMA: the Dynamical Schedulling Algorithm (DSA).

The criteria behind gWTO2 comes from `Alma Cycle 2 Proposer Guide
<http://almascience.eso.org/documents-and-tools/cycle-2/alma-proposers-guide>`_:

.. epigraph::

   Science observations will be executed by ALMA operations staff, taking into
   account (in rough order of priority): the weather conditions,
   the configuration of the array, target elevation and other practical
   constraints, the projects’ assigned priority group, and executive balance.
   All other things being equal, the project with the highest scientific rank
   will be observed."

   -- *Section 5.1 of the ALMA Cycle 2 Proposers Guide.*

Considerations and problem description
======================================

It is easy at any given time to use these criteria to create an algorithm that
selects the best SB to run, given the current pwv, array configuration,
number of antennas and the target's horizontal coordinates; however the
algorithm needs to be more complex to achieve an optimal efficiency in the use
of telescope time. This optimal efficiency is defined as obtaining the maximum
scientific output given the avilable observing time.

