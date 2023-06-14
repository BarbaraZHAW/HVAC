# -*- coding: utf-8 -*-
"""
Created on Sun May 14 18:26:22 2023

@author: hp

Cooling as a control & parameter optilizaton problem OOP
Recycling, Cooling & desumidification (with by-pass), reheating
GENERALITIES
========================================================================
Units
Temperatures: °C
Humidity ration: kg_vapor / kg_dry_air
Relative humidity: -
Heat flow rate: W
Mass flow rate: kg/s

Points on psychrometric chart (θ, w):
o) out      outdoor
0) M        mixed: fresh + recycled
1) s        efective coil surface temperature (ADP: Apparatus Dew Point)
2) C        coil leaving air temp. LAT (saturated and by-passed)
3) S        supply
4) I        indoor
    
System as a direct problem
--------------------------
<=4================================4============================
  mo     ||                        m                          ||
         4 (m-mo) =======0=======                             ||
         ||       ||  (1-β)m   ||                             ||
θo,φo==>[MX1]==0==||          [MX2]==2==[HC]==F==3==>[TZ]==4==||
 mo               ||           ||        /   /       //       |
                  ===0=[CC]==1===       s   m       sl        |
                       /\\   βm         |           ||        |
                      t  sl             |          [BL]<-mi   |
                      |                 |          //         |
                      |                 |         sl          |
                      |                 |                     |
                      |                 |<------[K]-----------|<-wI
                      |<------------------------[K]-----------|<-θI

Inputs:
θo, φo      outdoor temperature & humidity ratio
θIsp, φIsp  indoor temperature & humidity ratio set points
mi          infiltration mass flow rate
Qsa, Qla    auxiliary sensible and latent loads [kW]
Parameters:
m           mass flow rate of dry air
α           fraction of fresh air
β           by-pass factir od cooling coil
UA          overall heat transfer coefficient

Elements (16 equations):
MX          mixing box (2 equations)
HC1         heating coil (2 equations)
HC2         heating coil (2 equations)
TZ          thermal zone (2 equations)
BL          building (2 equations)
Kθ          indoor temperature controller (1 equation)
Kw          indoor humidity controller (1 equation)

Outputs (16 unknowns):
0, ..., 4   temperature and humidity ratio (12 unknowns)
Qt, Qs, Ql  total, sensible and latent heat of CC (3 unknowns)
Qs          sensible heat of HC (1 unknown)
Qs, Ql      sensible and latent heat of TZ (2 unknowns)
"""
import numpy as np
import pandas as pd
import psychro as psy

# constants
c = 1e3         # J/kg K, air specific heat
l = 2496e3      # J/kg, latent heat

# to be used in self.m_ls / least_squares
m_max = 100     # ks/s, max dry air mass flow rate
θs_0 = 5        # °C, initial guess for saturation temperature
class MxCcRhTzBl:
    """
    **HVAC composition**:
        mixing, cooling, reaheating, thermal zone of building, recycling
    """
    def __init__(self, parameters, inputs):
        m, mo, β, Kθ, Kw = parameters
        θo, φo, θIsp, φIsp, mi, UA, Qsa, Qla = inputs

        self.design = np.array([m, mo, β, Kθ, Kw,       # parameters
                                θo, φo, θIsp, φIsp,     # inputs air out, in
                                mi, UA, Qsa, Qla])      # --"--  building
        self.actual = np.array([m, mo, β, Kθ, Kw,
                                θo, φo, θIsp, φIsp, 
                                mi, UA, Qsa, Qla])

    def lin_model(self, θs0):

        """
   Linearized model.
       Solves a set of 16 linear equations.
       Saturation curve is linearized in θs0.

   s-point (θs, ws):

   - is on a tangent to φ = 100 % in θs0;

   - is **not** on the saturation curve (Apparatus Dew Point ADP).


   Parameter from function call
   ----------------------------
   θs0     °C, temperature for which the saturation curve is liniarized

   Parameters from object
   ---------------------
   m, mo, θo, φo, θIsp, φIsp, β, mi, UA, Qsa, Qla = self.actual

   Equations (16)
   -------------
   +-------------+-----+----+-----+----+----+----+----+----+
   | Element     |HC1 | MX | HC2 | VH | TZ | BL | Kθ | Kw |
   +=============+=====+====+=====+====+====+====+====+====+
   | N° equations|  2  | 2  |  2  |  2 | 2  | 2  |  1 |  1 |
   +-------------+-----+----+-----+----+----+----+----+----+

   Returns (12 unknowns)
   ---------------------
   x : θ0, w0, θ1, w1, θ2, w2, θ3, w3, θ4, w4, 
       QsTZ, QlTZ
    <=4================================m==========================
          ||                                                   ||
          4 (m-mo) =======0=======                             ||
          ||       ||  (1-β)m   ||                             ||
  θo,φo=>[MX1]==0==||          [MX2]==2==[HC]==F==3==>[TZ]==4==||
    mo             ||           ||        /   /       //       |
                   ===0=[CC]==1===       s   m       sl        |
                        /\\   βm         |           ||        |
                       t  sl             |          [BL]<-mi   |
                       |                 |          //         |
                       |                 |         sl          |
                       |                 |                     |
                       |                 |<------[K]-----------+<-wI
                       |<------------------------[K]-----------+<-θI
   """
        m, mo, β, Kθ, Kw, θo, φo, θIsp, φIsp, mi, UA, Qsa, Qla = self.actual
        wo = psy.w(θo, φo)      # hum. out
   """  
Zmień dane A wg mojego modelu <3 <3 displ(SendNudes)
   
        A = np.zeros((16, 16))  # coefficents of unknowns
        b = np.zeros(16)        # vector of inputs
        # MX1
        A[0, 0], A[0, 8], b[0] = m * c, -(m - mo) * c, mo * c * θo
        A[1, 1], A[1, 9], b[1] = m * l, -(m - mo) * l, mo * l * wo
        # CC
        A[2, 0], A[2, 2], A[2, 11], b[2] = (1 - β) * m * c, -(1 - β) * m * c,\
            1, 0
        A[3, 1], A[3, 3], A[3, 12], b[3] = (1 - β) * m * l, -(1 - β) * m * l,\
            1, 0
        A[4, 2], A[4, 3], b[4] = psy.wsp(θs0), -1,\
            psy.wsp(θs0) * θs0 - psy.w(θs0, 1)
        A[5, 10], A[5, 11], A[5, 12], b[5] = -1, 1, 1, 0
        # MX2
        A[6, 0], A[6, 2], A[6, 4], b[6] = β * m * c, (1 - β) * m * c,\
            - m * c, 0
        A[7, 1], A[7, 3], A[7, 5], b[7] = β * m * l, (1 - β) * m * l,\
            - m * l, 0
        # HC
        A[8, 4], A[8, 6], A[8, 13], b[8] = m * c, -m * c, 1, 0
        A[9, 5], A[9, 7], b[9] = m * l, -m * l, 0
        # TZ
        A[10, 6], A[10, 8], A[10, 14], b[10] = m * c, -m * c, 1, 0
        A[11, 7], A[11, 9], A[11, 15], b[11] = m * l, -m * l, 1, 0
        # BL
        A[12, 8], A[12, 14], b[12] = (UA + mi * c), 1, (UA + mi * c) * θo + Qsa
        A[13, 9], A[13, 15], b[13] = mi * l, 1, mi * l * wo + Qla
        # Kθ indoor temperature controller
        A[14, 8], A[14, 10], b[14] = Kθ, 1, Kθ * θIsp
        # Kw indoor humidity ratio controller
        A[15, 9], A[15, 13], b[15] = Kw, 1, Kw * psy.w(θIsp, φIsp)
        x = np.linalg.solve(A, b)
        return x
   """