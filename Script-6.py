# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 15:59:02 2023

@author: Jeroen
"""
import ipywidgets as wd
import matplotlib.pyplot as plt
import cool as cc
import psychro as psy
# %matplotlib inline  # uncomment for inline figure
# %matplotlib qt      # uncomment for figure in separate window
# plt.show()

plt.rcParams["figure.figsize"] = (10, 7.7)
font = {'size': 16}
plt.rc('font', **font)

# constants
c = 1e3         # J/kg K, air specific heat
l = 2496e3      # J/kg, latent heat
ρ = 1.2         # kg/m3, density

# Building dimensions
length = 20     # m
width = 30      # m
height = 3.5    # m
persons = 100   # m

sens_heat_person = 60       # W / person
latent_heat_person = 40     # W / person
load_m2 = 15        # W/m2
solar_m2 = 150      # W/m2 of window area
ACH = 1             # Air Cnhnages per Hour
U_wall = 0.4        # W/K, overall heat transfer coeff. walls
U_window = 3.5      # W/K, overall heat transfer coeff. windows

θo, φo = 5, 0.5    # outdoor temperature & relative humidity
θI, φI = 26, 0.5    # indoor temperature & relative humidity
wo = psy.w(θo, φo)
wI = psy.w(θI, φI)

floor_area = length * width
surface_floor = 2 * (length + width) * height + floor_area
surface_wall = 0.9 * surface_floor
surface_window = surface_floor - surface_wall

UA = U_wall * surface_wall + U_window * surface_window
mi = ACH * surface_floor * height / 3600 * ρ

solar_gains = solar_m2 * surface_window
electrical_load = load_m2 * surface_floor
Qsa = persons * sens_heat_person + solar_gains + electrical_load
Qla = persons * latent_heat_person

QsTZ = (UA + mi * c) * (θo - θI) + Qsa
QlTZ = mi * l * (wo - wI) + Qla

θS = θI - 15        # °C supply air temperature
m = QsTZ / c / (θI - θS)

print(f'QsTZ = {QsTZ:.0f} W, QlTZ = {QlTZ:.0f} W')
print(f'UA = {UA:.0f} W/K, mi = {mi:.2f} kg/s,\
      Qsa = {Qsa:.0f} W, Qla = {Qla:.0f} W')
print(f'm = {m:.3f} kg/s')

Kθ, Kw = 1e10, 0     # Kw can be 0
β = 0.2              # by-pass factor

m, mo = 3.1, 1.      # kg/s, mass flow rate: supply & outdoor (fresh) air
θo, φo = 5., 0.5    # outdoor conditions
θIsp, φIsp = 26., 0.5        # set point for indoor condition

mi = 1.35            # kg/s, mass flow rate of infiltration air
UA = 675.            # W/K, overall heat coefficient of the building
Qsa, Qla = 34000., 4000.     # W, auxiliary loads: sensible & latent

parameters = m, mo, β, Kθ, Kw
inputs = θo, φo, θIsp, φIsp, mi, UA, Qsa, Qla


cool6 = cc.MxCcRhTzBl(parameters, inputs)
Kw = 1e10
cool6.actual[4] = Kw
wd.interact(cool6.VAV_wd, value='θS', sp=(14, 21), θo=(1, 9), φo=(0.4, 1),
            θIsp=(22, 26), φIsp=(0.4, 0.8),
            mi=(0.5, 3, 0.1), UA=(500, 800, 10), Qsa=(0, 60_000, 500), Qla=(0, 20_000, 500));

