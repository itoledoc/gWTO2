#!/usr/bin/env python
__author__ = 'ignacio'

import wtoAlgorithm as Wto

datas = Wto.WtoAlgorithm(forcenew=True)
datas.create_allsb(split=False, path='/data/Cycle2/daily-backup/')
datas.create_allsb(split=True, path='/data/Cycle2/daily-backup/')
