**************************
Playing with the libraries
**************************

Load the environment and start ipython::

    . activateC2Test
    ipython

Once in ipython:::

    >>> import wtoAlgorithm as wto
    >>> import ephem
    >>> import pandas as pd
    >>> datas = wto.Algorithm(path='./wto_testing/')

And the run the following script. You can copy the code, and then paste into
python with :command:`%paste`, or :download:`donwload the file <../runwto.py>`,
and then load the function with :command:`execfile('runwto.py')`:

   .. code-block:: python

      def runwto(pwv, array_name=None, d=None, num_ant=34):
          datas.query_arrays()
          if array_name == 'default':
              array_name = None
              datas.set_bl_prop(array_name)
          else:
              array_name = datas.bl_arrays.AV1.values[0]
              datas.set_bl_prop(array_name)
              datas.array_ar = 61800 / (100. * datas.ruv.max())
          if d == None:
              d = ephem.now()
          if num_ant != 34:
              datas.num_ant = num_ant
          datas.array_name = array_name
          datas.update()
          datas.date = d
          datas.pwv = pwv
          datas.selector('12m')
          datas.scorer('12m')
          print datas.score12m.sort(
              'score', ascending=False).query(
              'band != "ALMA_RB_04" and band '
              '!= "ALMA_RB_08" and isPolarization == False')[
              ['score','CODE','SB_UID','name','SB_state','band','maxPWVC', 'HA',
               'elev','etime', 'execount','Total','arrayMinAR','arcorr',
               'arrayMaxAR','tsysfrac', 'blfrac','frac','sb_array_score',
               'sb_cond_score', 'DEC','RA', 'isTimeConstrained',
               'integrationTime', 'PRJ_ARCHIVE_UID']].head(25)
          datas.num_ant_user = 34

The to run the wto algorithm use a pwv value between 0 and 20, with steps of
0.05 (e.g., 0.4, 0.45, but no 0.42), and assuming the latest BL Array. Set
``array_name='default'`` when running ``runwto`` (e.g.
``runwto(X.XX, array_name='default')``) to use the Current configuration parameters
calculated with arrayConfigurationTools and 34 antennas. Also, to change the
date to current date use ``runwto(X.XX, d=ephem.Date('2014-06-28 03:45')``

This will display the top 25 values of datas.scorer12m dataFrame. To check full
output in an excel table run:::

    datas.score12m.to_excel('output_path/score.xls')

Where output_path is the full path to the directory where you want to save the
score.xls excel spreadsheet.
