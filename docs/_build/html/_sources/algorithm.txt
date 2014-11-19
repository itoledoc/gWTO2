******************************
Selection and Score algorithms
******************************

.. _selection:

Selection and Data preparation
==============================

(:py:func:`wtoAlgorithm.WtoAlgorithm.selector`)

#. **Calculate observability using the pyephem libraries.**

   For all the science field sources of an SB and fixed calibration sources,
   we calculate the current elevation, rise LST and set LST.
   If a field source is a Solar System object, or an ephemeris
   source, we calculate first the current RA and DEC, and then the other
   parameters. The current elevation for the SB comes from the source with the
   minimun elevation; the rise LST for the SB is the LST of the source that
   would rise last; and the set LST for the SB is the LST of the source that
   would set first. The rise and set LST are calculated using the elevation
   limit (`horizon`) gave as an input for gWTO.

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.FieldSource['solarSystemObject']
   * SchedBlock.FieldSource.sourceCoordinates.longitude
   * SchedBlock.FieldSource.sourceCoordinates.latitude
   * SchedBlock.FieldSource.isQuery
   * SchedBlock.FieldSource.sourceEphemeris
   * Date, horizon limit.

#. **Select SB by array type: 12m, 7m, TP.**

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.ObsUnitControl['arrayRequested']
   * Array Type.

#. **Calculate opacity, airmass and sky Temperature.**

   For both the OT asumed conditions and current, actual, conditions,
   based on the current PWV.

   The implementation has several steps:

    #. First, a table with values of Tau as fuction of PWV and representative
       frequencies was created. The file with this tables, in csv format, is
       called **tau.csv**. The frequencies are between 84.0 and 720.0 GHz, with
       steps of 100 MHz; pwv values are between 0.0 and 20.0 mm, in steps of
       0.05. The values were calculated using the atmosphere model algorithms from
       CASA 4.2.1, using as input variables :math:`P=580.0`, :math:`H=20.0`,
       :math:`T=270.0`, :math:`altitude=5059` and :math:`chansep=0.1`.
    #. A table with Tsky values as function of PWV and representative
       frequencies was also create. The file with this table, in csv format,
       is called **tskyR.csv**. Description of columns, rows, and values is the
       same as the table tau.csv, the only addition, is that the Tsky in the
       tables assumes the airmass of a source at Zenith.
    #. Internaly, four columns are created for all SBs: *tau_org* and *tsky_org*,
       storing the value of tau and tsky for the conditions assumed by the OT,
       i.e., pwv from maxPWVC; *tau* and *tsky*, storing
       the values of tau and tsky for the current conditions, i.e.,
       pwv from the gui's PWV variable.

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.Preconditions.WeatherConstraints.maxPWVC
   * SchedBlock.SchedulingConstraints.representativeCoordinates.latitude
   * SchedBlock.SchedulingConstraints.representativeFrequency
   * Date, current PWV
   * Tsky and Tau tables.

#. **Calculate system Temperatures.**

   Two columns are genrated for each SB: *tsys_org* and *tsys*, one for the
   OT's assumed conditions and the other for the current conditions.
   Tsys, for both cases, is calculated using:

       .. math::
          T_{sys} = \frac{1 + g}{\eta_{eff} e^{-\tau \cdot \sec Z}}
          \left(T_{rx} + T_{sky,Z=0} \left(\frac{1-e^{-\tau \cdot \sec Z}}{e^{-\tau}}\right)
          \eta_{eff} + (1-\eta_{eff}) T_{amb}\right)

   Where :math:`g` is the sideband gain ratio (:math:`g=0` for SSB and 2SB
   receivers, :math:`g=1` for DSB); :math:`\eta_{eff}` is the forward efficiency,
   which is set to a value of 0.95; :math:`T_{rx}` is the receiver characteristic
   temperature; :math:`\tau` is the oppacity for a source at zenithal distance
   :math:`Z=0`; :math:`Z` is the zenithal distance of the representative source
   at transit: :math:`T_{sky}` is the sky temperature at :math:`Z=0`; and
   :math:`T_{amb}` is the ambient temperature, set to a fixed value of
   :math:`270K`.

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.SchedulingConstraints.requiredReceiverBands

#. **SBs within spectral ranges with transmission higher than 50% are first**
   **selected.**

   For gWTO1, we use to have a limit of 70%, which change to 50% when the pwv
   was under 0.6 mm. For gWTO2 we set the limit to 50%, and a more accurate
   selection is applied later using :math:`T_{sys}`
   The transmission is calculated from the previously found :math:`tau` for
   the current conditions:

   .. math::
      e^{-\tau_{\rm{sb,pwv}}\cdot \sec Z_{\rm{sb,HA}=0}} > 0.5

   where :math:`\tau_{\rm{sb,pwv}}` is the oppacity for the representative source
   of a scheduling block *sb* and with the current PWV :math:`pwv`; and
   :math:`Z_{sb,\rm{HA}=0}` is the zenithal distance for the representative source
   of *sb* at transit.

   Relavant XML child/tag or gWTO2 variables:

   * :math:`\tau_{\rm{sb,pwv}}`

#. **Select SBs within given HA limits.**

   .. math::
      \rm{minHA} < \rm{HA}_{sb,time} < \rm{maxHA}

   (mihHA = -5 and maxHA =  3 by default).

   Relavant XML child/tag or gWTO2 variables:

   * :math:`\rm{HA}_{sb,time}`
   * :keyword:`LST`

#. **Select SBs over the given elevation limit (20 deg. default) and that won't**
   **set for at least 1 1/2 hours.**

   .. math::
      \left( \rm{elev} > \rm{horizon} \right) \rm{\ AND\ } \left(
      \rm{SB}_{\rm{set\ time}} > 1.5\rm{hours\ from\ now} \right)

   Relavant XML child/tag or gWTO2 variables:

   * :keyword:`LST`
   * :keyword:`Horizon Limit`
   * :keyword:`SB set time`

#. **Remove SBs with states Phase2Submitted, FullyObserved and Deleted.**

   Relavant XML child/tag or gWTO2 variables:

   * This information comes from the ALMA.SCHED_BLOCK_STATUS.

#. **Remove SBs that belongs to projects with status Phase2Submitted or Completed.**

   Relavant XML child/tag or gWTO2 variables:

   * This information comes from the ALMA.OBS_PROJECT_STATUS, and is crosschecked
     against ALMA.BMMV_OBSPROJECT

#. **Remove SBs that have names like "Do not".**

   Currently the OT is not able to handle the SB status "Deleted", so SBs
   that are supposed to be deleted are set to status "Suspended", and the
   name changed to a varation of "DO NOT OBSERVE", "Do_not_observe", "DO not
   observe descoped", etc., depending on the mood of the P2G. The only thing
   in common is the presence of a "do not". Any SB with those words in the name
   is removed.

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.name

#. **Remove SBs where the number of requested executions has been achieved**

   Given the requested number of executions of a SB (executionCount), check
   if any EB are associated to this SB, and add up the ones with QA0 flags
   *Unset* and *Pass*. If this last number is equal or higher than
   executionCount we don't select the SB.

   When a QAO *Unset* flag is set to *Fail* or *Semipass*, the number of
   assoc. EB will go down, and then an SB can be back on the list. This method
   avoids over-observing of an SB.

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.SchedBlockControl.executionCount
   * QA0STATUS column FROM ALMA.AQUA_EXECBLOCK

#. **Select SBs that can be executed with the current array's**
   **angular resolution**

   Using the minAR and maxAR limits, corrrected by Stéphane's script and transformed
   to the equivalent AR at 100GHz, we select SBs that would accept current array's
   configuration as set in :guilabel:`Array AR:`:

   .. math::
      \rm{minAR}_{\rm{SB}} < \rm{AR}_{\rm{array}} < \rm{maxAR}_{\rm{SB}}

   Relavant XML child/tag or gWTO2 variables:

   * SchedBlock.SchedulingConstraints.minAcceptableAngResolution
   * SchedBlock.SchedulingConstraints.maxAcceptableAngResolution
   * :keyword:`minAR`, :keyword:`maxAR`, Stéphane's script
   * :guilabel:`Array AR:`

#. **Calculate tsysfrac, blfrac and frac columns**

   Three new variables are calculated for each SB, that will help to do a final
   selection and assign scores. :keyword:`tsysfrac` is the multiplicative factor
   the science target integration time should be corrected by, so given the
   current weather conditions (:math:`\rm{T}_{\rm{sys}}`, :math:`\tau`)
   the execution would achieve the requested sensitivity:

   .. math::

      \rm{tsysfrac} = \left(\frac{\rm{Tsys}}{\rm{Tsys\_org}}\right)^{2}

   :keyword:`blfrac` is the multiplicative factor the science target integration
   time should be corrected by to account for differences between current array's
   characteristics (:math:`AR`, :math:`\rm{Number_of_Baselines}`) and requested
   array:

   .. math::

      \rm{blfrac} = \frac{offered\_baselines}{\rm{available\_baselines}}

   The offered_baselines will depend on Cycle (32 for cycle 1, 34 for cycle 2).

   Finally, :keyword:`frac` is the total multiplicative factor accounting for
   both previous factors:

   .. math::
      \rm{frac} = \rm{tsysfrac} \times\rm{blfrac}

.. _score:

Score and ranking
=================


#. **SB completion score**

   A score between 4 and 10, where 4 is given to SBs that has not been started
   yet, and it rises as the SB gets closer to completion.

   .. math::
      \rm{Score}_{\rm{SB\ completion}} =
      4 + 6 \times \frac{\rm{QA0\ Pass} + \rm{QA0\ Unset}}{\rm{Expected\ Executions}}

#. **SB Grade/Cycle Score**

   .. math:: \rm{Score}_{\rm{grade}} = 10 ; \rm{if\ grade\ is\ A\ and\ Cycle\ 2}
      :label: gA

   .. math:: \rm{Score}_{\rm{grade}} = 9 ; \rm{if\ grade\ is\ A\ and\ Cycle\ 1}

   .. math:: \rm{Score}_{\rm{grade}} = 8  ; \rm{if\ grade\ is\ B\ and\ Cycle\ 1}
      :label: gBc1


   .. math:: \rm{Score}_{\rm{grade}} = 4  ; \rm{if\ grade\ is\ B\ and\ Cycle\ 2}
      :label: gBc2

   .. math:: \rm{Score}_{\rm{grade}} = -100 ; \rm{if\ grade\ is\ C}
      :label: gC


#. **SB Science Score**

   .. math::
      \rm{Score}_{\rm{science\ rank}} =
      10 \times \frac{\rm{max(rank)} - \rm{SB}_{\rm{rank}}}{\rm{max(rank)}}

#. **SB Array Score**

   .. math:: \rm{Score}_{\rm{array}} = 10 ; \rm{\ if\ array\ is\ TP\ or\ 7m}
      :label: tp

   .. math::  \rm{Score}_{\rm{array}} = 10 ; \rm{\ if\ } 0.9 \rm{SB}_{\rm{AR}}
              <= \rm{Array}_{\rm{AR}} <= 1.1 \rm{SB}_{\rm{AR}}
      :label: match

   .. math:: \rm{Score}_{\rm{array}} = 9 ; \rm{\ if\ } 0.7 \rm{SB}_{\rm{AR}}
             <= \rm{Array}_{\rm{AR}} < 0.9 \rm{SB}_{\rm{AR}}
      :label: low

   .. math:: \rm{Score}_{\rm{array}} = 8.5\frac{\rm{Array}_{\rm{AR}} - \rm{SB}_{\rm{minAR}}}{0.7\rm{SB}_{\rm{AR}} - \rm{SB}_{\rm{minAR}}}
             ; \rm{\ if\ } \rm{Array}_{\rm{AR}} < 0.7 \rm{SB}_{\rm{AR}}
      :label: toolow

   .. math:: \rm{Score}_{\rm{array}} = \frac{10}{1.1\rm{SB}_{\rm{AR}} - \rm{SB}_{\rm{maxAR}}} \left(\rm{Array}_{\rm{AR}} - \rm{SB}_{\rm{maxAR}}\right)
             ; \rm{\ if\ } \rm{Array}_{\rm{AR}} > 1.1 \rm{SB}_{\rm{AR}}
      :label: high

   .. figure:: figure_1.png
      :align: center
      :scale: 50%

      In this example, the requested array resolution (:math:`\rm{SB}_{\rm{AR}}`)
      is 2.8 arcsec, with a minimun acceptable resolution
      :math:`\rm{SB}_{\rm{minAR}} = 0.5` and maximum
      :math:`\rm{SB}_{\rm{maxAR}} = 3.5`

#. **SB Executive Score**

   .. math:: \rm{Score}_{\rm{executive}} = 10; \rm{default\ to\ all\ executives}
      :label: exscore

#. **SB Condition Score**

   If :math:`\rm{frac} < 1`:

   .. math:: \rm{Score}_{\rm{cond}} = 10 \left(1- (\rm{frac}-1)^{10}\right) \rm{pwv}_{\rm{close}}
      :label: frac_und_1

   If :math:`\rm{frac} = 1`:

   .. math:: \rm{Score}_{\rm{cond}} = 10; \rm{frac = 1}
      :label: frac_1

   If :math:`1.3 > \rm{frac} > 1`:

   .. math:: \rm{Score}_{\rm{cond}} = 10 \left(1 - (\frac{\rm{frac} -1}{0.3})^{3}\right) \rm{pwv}_{\rm{close}}
      :label: frac_over_1

   Where :math:`\rm{pwv}_{\rm{close}}`

   .. math:: \rm{pwv}_{\rm{close}} = 1 - \left|\frac{\rm{pwv} - \rm{maxPWV}}{6}\right|
      :label: pwv_close

   .. figure:: figure_2.png
      :align: center
      :scale: 50%

      The condition scoring funtion in 3D, dependant on frac and pwv.


#. **SB Total Score**

.. _check-obs:

Checking observability
======================

