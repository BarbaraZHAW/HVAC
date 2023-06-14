# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 08:57:01 2023

@author: Jeroen
"""

from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.pyplot as plt
import va_hum_summer

# %matplotlib inline  # uncomment for inline figure
# uncomment for figure in separate window
# %matplotlib qt
# plt.show()

plt.rcParams["figure.figsize"] = (10, 7.7)
font = {'size': 16}
plt.rc('font', **font)





def RecAirCAV_summer_wd(α=0.5, θS=30, θIsp=18, φIsp=0.5, θO=-1, φO=1):
    Qsa = 0.
    Qla = 0.
    mi = 1
    UA = 935.83
    from va_hum_summer import RecAirCAV
    RecAirCAV(α, θS, θIsp, φIsp, θO, φO, Qsa, Qla, mi, UA)



interact(RecAirCAV_summer_wd, α = (0, 1, 0.1), θS = (20, 50, 2),
    θIsp = (17, 25, 1), φIsp = (0, 1, 0.1),
    θO = (-10., 17., 2), φO = (0, 1, 0.1));

# After canges to the building
# uncomment following 15 lines to have two graphs
'''
def RecAirCAV_wd(Qsa=0, Qla=0, mi=2.12, UA=935.83):
    α = 0.5
    θSsp = 30
    θIsp = 18
    φIsp = 0.5
    θO = -1
    φO = 1
    from va_hum import RecAirCAV
    RecAirCAV(α, θSsp, θIsp, φIsp, θO, φO, 
              Qsa, Qla, mi, UA);


interact(RecAirCAV_wd, Qsa=(0, 15000, 50), Qla=(0, 15000, 50),
         mi=(0, 5, 0.2), UA=(700, 1000, 10));
'''
         

va_hum_summer.RecAirCAV(α=0.5, θS=30, θIsp=18, φIsp=0.5, θO=-1, φO=1,
                 Qsa=0, Qla=0, mi=2.12, UA=935.83)