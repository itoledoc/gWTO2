*******
Apendix
*******

.. _current-conf:

Assessment of Current Array's Angular Resolution
================================================

#. From the dashboard get a list of antennas and pads that are available and
   working in band 3 or 6. This should be saved in a file with the name
   YYYY-MM-DD.cfg, which is a space-separeted values file, with the antenna in the
   first column and pad in the second.

   (:download:`Example file <./2014-07-20.cfg>`)

#. Run the script :command:`arrayConfiguration.py`::

     casapy -c arrayconfiguration.py -s yes -l 2h -i <path>/YYYY-MM-DD.cfg

   Where :command:`<path>` is the path where you stored the YYYY-MM-DD.cfg file.
   The execution might fail complaining about missing C34-?.cfg files: copy them
   to the path where you are running the script from
   :file:`~/AIV/science/ArrayConfiguration/Tools/Cycle2/*.cfg`
