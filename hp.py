#
# This is a standalone Python script to help me thinking about modifications to
# engines, mostly little two stroke scooter engines. This is a standalone script
# that can run without any additional modules, runs on Python 2 and Python 3, runs
# on Windows, Mac, Linux, IOS (Pythonista) and Android. I take some care to make
# sure it keeps running on IOS, since I often drag my iPad out to the garage.
#
# I would really like to depend on the physics module, since it will give me
# quantities with units attached. In the 1990s, I would write a lot of these
# type of functions on a TI-89 and TI-92plus. Both of these carry the units
# along with the number and its great for balancing out equations.
#
# I like to dump out various forms of the measurements because the use of units
# is all over the board in papers, books, etc. For example, in electric cars, the
# seem to tend to use Newton meters and kilowatts, and lots of hot rod articles
# are only HP, and foot lbs.
#
from __future__ import print_function
import math
import sys

# Try to include modules we would like to use.
# Really, right now, we just want mpmath to get more precision, this helps with
# rounding errors when converting back and forth
libnames = ['numpy', 'scipy', 'operator', 'mpmath', 'pylab']
for libname in libnames:
    try:
        lib = __import__(libname)
    except:
        print('No module - ',libname)
    else:
        globals()[libname] = lib

try: input = raw_input
except NameError: pass

# Units
# temperature      - I want internal variables to hold temperatures in celsius, C
# pressure         - I want internal variables to hold pressure in kilo pascals, kPa
# distance         - I want internal variables to hold distance in millimeters, mm
# area             - I want internal variables to hold area in millimeters squared, mm^2
# angular velocity - I want internal variables to hold angular velocity in RPM

#
# Next Steps
# * Compute HP loss or gain based on Barometric Pressure and Temperature
# * Can I make an estimate of manifold vacuum at wide open throttle
#   based on a carb that is too small?
#
# Done
# * Manifold Pressure
# * Inches of Water
#
# https://gist.github.com/edt11x/52c69a6448f7a379ad19
#
# NC50
# Port Timing Table
#
# From http://hondaspree.net/wiki/index.php5?title=Cylinder_Port_Timing
#
# Variator Equipped Transmission
# 1987 SE 50  83-84 Aero 50   85-87 Aero 50   88-93 Elite SA50    94/2001 Elite SA50  Urban Express NU50  1982 Express Sr NX50
# BBDC    Exhaust Open    78  71  76  80  79  67.5    67
# ABDC    Exhaust Close   78  71  76  80  79  67.5    67
# BBDC    Scavenge Open   57  52  57  56  56  47.5    47
# ABDC    Scavenge Close  57  52  57  56  56  47.5    47
#
# Fixed Ratio Transmission
# Spree 84/85 Spree 86/87 Iowa Spree 84/85    Iowa Spree 86/87    Elite SB50  Elite SB50P 1977-81 Express NC50
# BBDC    Exhaust Open    71  73  70  71  77  74  65
# ABDC    Exhaust Close   71  73  70  71  77  74  65
# BBDC    Scavenge Open   52  54  50  52  60  57  47
# ABDC    Scavenge Close  52  54  50  52  60  57  47

# guard against dividing by zero
def too_small_guard(val):
    if (val < 1.0e-9):
        val = 1.0e-9
    return val

# Compression ratio should not be less than one in any normal circumstance I
# can think of.
def cr_guard(cr):
    if (cr < 1.0):
        cr = 1.0
    return cr

#
# Conversion routines
#

# Percentage
PERCENT_DIVISOR = 100

def decimal_to_percent(decimal):
    return decimal * PERCENT_DIVISOR

def percent_to_decimal(percent):
    return percent / PERCENT_DIVISOR

# Gravity

# http://hyperphysics.phy-astr.gsu.edu/hbase/work.html
# in meters per second squared, m/s^2
STANDARD_GRAVITY = 9.80665

# Temperature

FAHRENHEIT_OFFSET = 32.0
KELVIN_OFFSET = 273.15
RANKINE_OFFSET = 459.67
CELSIUS_TO_FAHREN_RATIO = (9.0/5.0)

# Reynolds number, Universal gas constant
# R - Universal gas constant, 8.314510 J/(mol * K)
# R - 1545 ft lbf / degrees Rankin
CONST_R = 8.314510 # J/(mol * K)

# Kelvin exactly Celsius + 273.15
#
# it establishes the difference between the two scales null
# points as being precisely 273.15 degrees Celsius (-273.15
# C = 0 K and 0 C = 273.15 K).
#
# https://en.wikipedia.org/wiki/Celsius
def celsius_to_fahrenheit(temp):
    return ((temp*CELSIUS_TO_FAHREN_RATIO) + FAHRENHEIT_OFFSET)
def fahrenheit_to_celsius(temp):
    return ((temp - FAHRENHEIT_OFFSET) / CELSIUS_TO_FAHREN_RATIO)
def celsius_to_kelvin(temp):
    return (temp + KELVIN_OFFSET)
def kelvin_to_celsius(temp):
    return temp - KELVIN_OFFSET
def fahrenheit_to_kelvin(temp):
    return celsius_to_kelvin(fahrenheit_to_celsius(temp))
def fahrenheit_to_rankine(temp):
    return temp + RANKINE_OFFSET
def celsius_to_rankine(temp):
    return fahrenheit_to_rankine(celsius_to_fahrenheit(temp))
def rankine_to_fahrenheit(temp):
    return temp - RANKINE_OFFSET
def rankine_to_celsius(temp):
    return fahrenheit_to_celsius(rankine_to_fahrenheit(temp))

# Mass and Weight

# The modern definition of the avoirdupois pound is exactly 0.45359237 kilograms.
KG_PER_LB = 0.45359237
# There are exactly 16 ounces in the avoirdupois pound
OUNCES_PER_LB = 16

# https://en.wikipedia.org/wiki/Kilogram
#
# The avoirdupois (or international) pound, used in both the
# Imperial system and U.S. customary units, is defined as
# exactly 0.45359237 kg
#
def lbs_to_kg(lbs):
    return lbs * KG_PER_LB
def kg_to_lbs(kg):
    return kg / KG_PER_LB
def per_lb_to_per_kg(per_lb):
    return per_lb / KG_PER_LB
def per_kg_to_per_lb(per_kg):
    return per_kg * KG_PER_LB

# Force
# 
# Force = Mass * Acceleration
#
# 1 Newton = 1 kg * meters/(second^2)
def newtons_to_kg(newtons):
    return newtons / STANDARD_GRAVITY
def kg_to_newtons(kg):
    return kg * STANDARD_GRAVITY
def lbs_to_newtons(lbs):
    return kg_to_newtons(lbs_to_kg(lbs))
def newtons_to_lbs(newtons):
    return kg_to_lbs(newtons_to_kg(newtons))

# Distance

MM_PER_CM   = 10
MM_PER_M    = 1000
MM_PER_INCH = 25.4
M_PER_KM = 1000
CM_PER_INCH = MM_PER_INCH / MM_PER_CM
INCHES_PER_FOOT = 12
FEET_PER_YARD = 3
YARDS_PER_MILE = 1760

def inches_to_mm(inches):
    return inches * MM_PER_INCH
def inches_to_feet(inches):
    return inches / INCHES_PER_FOOT
def inches_to_yards(inches):
    return feet_to_yards(inches_to_feet(inches))
def inches_to_miles(inches):
    return yards_to_miles(inches_to_yards(inches))
def feet_to_inches(feet):
    return feet * INCHES_PER_FOOT
def feet_to_mm(feet):
    return inches_to_mm(feet_to_inches(feet))
def feet_to_yards(feet):
    return feet / FEET_PER_YARD
def feet_to_miles(feet):
    return yards_to_miles(feet_to_yards(feet))
def miles_to_feet(miles):
    return yards_to_feet(miles_to_yards(miles))
def miles_to_inches(miles):
    return feet_to_inches(miles_to_feet(miles))
def miles_to_mm(miles):
    return inches_to_mm(miles_to_inches(miles))
def yards_to_feet(yards):
    return yards * FEET_PER_YARD
def yards_to_miles(yards):
    return yards / YARDS_PER_MILE
def miles_to_yards(miles):
    return miles * YARDS_PER_MILE
def miles_to_feet(miles):
    return yards_to_feet(miles_to_yards(miles))
def miles_to_inches(miles):
    return feet_to_inches(miles_to_feet(miles))
def miles_to_mm(miles):
    return inches_to_mm(miles_to_inches(miles))
def miles_to_meters(miles):
    return mm_to_meters(miles_to_mm(miles))
def yards_to_inches(yards):
    return feet_to_inches(yards_to_feet(yards))
def yards_to_mm(yards):
    return inches_to_mm(yards_to_inches(yards))
def mm_to_inches(mm):
    return mm / MM_PER_INCH
def mm_to_cm(mm):
    return mm / MM_PER_CM
def mm_to_meters(mm):
    return mm / MM_PER_M
def meters_to_km(meters):
    return meters / M_PER_KM
def mm_to_km(mm):
    return meters_to_km(mm_to_meters(mm))
def meters_to_mm(meters):
    return meters * MM_PER_M
def meters_to_inches(meters):
    return mm_to_inches(meters_to_mm(meters))
def meters_to_feet(meters):
    return inches_to_feet(meters_to_inches(meters))
def meters_to_yards(meters):
    return feet_to_yards(meters_to_feet(meters))
def meters_to_miles(meters):
    return yards_to_miles(meters_to_yards(meters))
def km_to_meters(km):
    return km * M_PER_KM
def km_to_mm(km):
    return meters_to_mm(km_to_meters(km))
def feet_to_meters(feet):
    return mm_to_meters(inches_to_mm(feet_to_inches(feet)))
def mm_to_feet(mm):
    return inches_to_feet(mm_to_inches(mm))
def mm_to_yards(mm):
    return feet_to_yards(mm_to_feet(mm))
def mm_to_miles(mm):
    return yards_to_miles(mm_to_yards(mm))

def sq_inches_to_sq_mm(sq_inches):
    return inches_to_mm(inches_to_mm(sq_inches))
def sq_feet_to_sq_mm(sq_feet):
    return feet_to_mm(feet_to_mm(sq_feet))
def sq_m_to_sq_mm(sq_m):
    return meters_to_mm(meters_to_mm(sq_m))
def sq_km_to_sq_mm(sq_km):
    return km_to_mm(km_to_mm(sq_km))
def sq_yards_to_sq_mm(sq_yards):
    return yards_to_mm(yards_to_mm(sq_yards))
def sq_miles_to_sq_mm(sq_miles):
    return miles_to_mm(miles_to_mm(sq_miles))

# Angle

FULL_ROT_DEGREES = 360
HALF_ROT_DEGREES = FULL_ROT_DEGREES / 2

def bbdc_to_atdc_deg(degrees):
    return HALF_ROT_DEGREES - degrees
def bbdc_to_atdc_rad(rad):
    return math.pi - rad
def atdc_to_bbdc_deg(degrees):
    return HALF_ROT_DEGREES - degrees
def atdc_to_bbdc_rad(rad):
    return math.pi - rad

# Time

SEC_PER_MIN = 60
MIN_PER_HOUR = 60

def sec_to_min(sec):
    return sec / SEC_PER_MIN
def min_to_sec(minutes):
    return minutes * SEC_PER_MIN
def per_sec_to_per_min(per_sec):
    return per_sec * SEC_PER_MIN
def per_sec_to_per_hour(per_sec):
    return per_sec_to_per_min(per_sec) * MIN_PER_HOUR
def per_min_to_per_sec(per_min):
    return per_min / SEC_PER_MIN
def per_min_to_per_hour(per_min):
    return per_min * MIN_PER_HOUR
def per_hour_to_per_min(per_hour):
    return per_hour / MIN_PER_HOUR
def per_hour_to_per_sec(per_hour):
    return per_min_to_per_sec(per_hour_to_per_min(per_hour))

# Volume

ML_PER_LITER = 1000
CC_PER_LITER = ML_PER_LITER

def cubic_mm_to_cc(cubic_mm):
    return cubic_mm / (MM_PER_CM * MM_PER_CM * MM_PER_CM)
def cc_to_ml(cc):
    return cc
def cc_to_liters(cc):
    return cc_to_ml(cc) / ML_PER_LITER
def liters_to_cc(liters):
    return liters * CC_PER_LITER
def liters_to_ci(liters): # cubic inches
    return cc_to_ci(liters_to_cc(liters))
def cc_to_ci(cc): # cubic centimeters to cubic inches
    return cc / (CM_PER_INCH * CM_PER_INCH * CM_PER_INCH)
def ci_to_cc(ci):
    return ci * (CM_PER_INCH * CM_PER_INCH * CM_PER_INCH)
def cc_to_cf(cc): # cubic centimeters to cubic feet
    return cc_to_ci(cc) / (INCHES_PER_FOOT * INCHES_PER_FOOT * INCHES_PER_FOOT)
def cf_to_cc(cf): # cubic feet to cubic centimeters
    return ci_to_cc(cf) * (INCHES_PER_FOOT * INCHES_PER_FOOT * INCHES_PER_FOOT)

# Volumetric Capacity

# Cubic Centimeters per second to Cubic Feet per Minute
def cc_sec_to_cfm(cc_sec):
    return per_sec_to_per_min(cc_to_cf(cc_sec))
def cc_sec_to_liters_sec(cc_sec):
    return cc_to_liters(cc_sec)
def cc_sec_to_liters_min(cc_sec):
    return per_sec_to_per_min(cc_sec_to_liters_sec(cc_sec))

# Liquid Capacity

# The US gallon, which is equal to approximately 3.785 L, is
# legally defined as 231 cubic inches.
#
# https://en.wikipedia.org/wiki/Gallon
CI_PER_US_LIQUID_GALLON = 231
QUARTS_PER_US_LIQUID_GALLON = 4
PINTS_PER_QUART = 2
FLUID_OUNCES_PER_PINT = 16

def us_liquid_gallons_to_ci(gallons):
    return gallons * CI_PER_US_LIQUID_GALLON
def ci_to_us_liquid_gallons(ci):
    return ci / CI_PER_US_LIQUID_GALLON
def us_liquid_gallons_to_cc(gallons):
    return ci_to_cc(us_liquid_gallons_to_ci(gallons))
def cc_to_us_liquid_gallons(cc):
    return ci_to_us_liquid_gallons(cc_to_ci(cc))
def us_liquid_gallons_to_ml(gallons):
    return cc_to_ml(us_liquid_gallons_to_cc(gallons))
def ml_to_us_liquid_gallons(ml):
    return cc_to_us_liquid_gallons(ml_to_cc(ml))
def us_liquid_gallons_to_liters(gallons):
    return cc_to_liters(us_liquid_gallons_to_cc(gallons))
def liters_to_us_liquid_gallons(liters):
    return cc_to_us_liquid_gallons(liters_to_cc(liters))
def us_liquid_gallons_to_quarts(gallons):
    return gallons * QUARTS_PER_US_LIQUID_GALLON
def quarts_to_us_liquid_gallons(quarts):
    return quarts / QUARTS_PER_US_LIQUID_GALLON
def cc_to_quarts(cc):
    return us_liquid_gallons_to_quarts(cc_to_us_liquid_gallons(cc))
def quarts_to_cc(quarts):
    return us_liquid_gallons_to_cc(quarts_to_us_liquid_gallons(quarts))
def quarts_to_pints(quarts):
    return quarts * PINTS_PER_QUART
def pints_to_quarts(pints):
    return pints / PINTS_PER_QUART
def us_liquid_gallons_to_pints(gallons):
    return quarts_to_pints(us_liquid_gallons_to_quarts(gallons))
def pints_to_us_liquid_gallons(pints):
    return quarts_to_us_liquid_gallons(pints_to_quarts(pints))
def cc_to_pints(cc):
    return quarts_to_pints(cc_to_quarts(cc))
def pints_to_cc(pints):
    return quarts_to_cc(pints_to_quarts(pints))
def pints_to_fluid_ounces(pints):
    return pints * FLUID_OUNCES_PER_PINT
def fluid_ounces_to_pints(fluid_ounces):
    return fluid_ounces / FLUID_OUNCES_PER_PINT
def us_liquid_gallons_to_fluid_ounces(gallons):
    return pints_to_fluid_ounces(us_liquid_gallons_to_pints(gallons))
def fluid_ounces_to_us_liquid_gallons(fluid_ounces):
    return pints_to_us_liquid_gallons(fluid_ounces_to_pints(fluid_ounces))
def cc_to_fluid_ounces(cc):
    return pints_to_fluid_ounces(cc_to_pints(cc))
def fluid_ounces_to_cc(fluid_ounces):
    return pints_to_cc(fluid_ounces_to_pints(fluid_ounces))

# Velocity

def meters_sec_to_miles_hour(ms):
    return per_sec_to_per_hour(meters_to_miles(ms))
def meters_sec_to_feet_sec(ms):
    return meters_to_feet(ms)
def meters_sec_to_feet_min(ms):
    return per_sec_to_per_min(meters_sec_to_feet_sec(ms))
def meters_sec_to_km_hour(ms):
    return per_sec_to_per_hour(meters_to_km(ms))
def miles_hour_to_meters_sec(mph):
    return per_hour_to_per_sec(miles_to_meters(mph))
def feet_sec_to_meters_sec(feet_sec):
    return feet_to_meters(feet_sec)
def feet_min_to_meters_sec(feet_min):
    return feet_sec_to_meters_sec(per_min_to_per_sec(feet_min))
def km_hour_to_meters_sec(kmh):
    return per_hour_to_per_sec(km_to_meters(kmh))

# Pressure

# 1 pascal is 1 Newton per square meter
# 1 Newton is the force required to accelerate 1 kg 1 meter per sec
# https://en.wikipedia.org/wiki/Inch_of_water
# 1 inH2O is defined as 248.84 pascals at 60F
def kPa_to_Pa(kPa):
    return kPa * 1000.0
def Pa_to_kPa(pa):
    return pa / 1000.0
def inHg_to_psi(inHg):
    return inHg * 0.49109778
def inHg_to_Pa(inHg):
    return inHg * 1000.0 / 0.295299830714
def inHg_to_kPa(inHg):
    return Pa_to_kPa(inHg_to_Pa(inHg))
def inHg_to_mmHg(inHg):
    return inches_to_mm(inHg)
def kPa_to_inHg(kPa):
    return 0.295299830714 * kPa
def kPa_to_inH2O(kPa):
    return kPa_to_Pa(kPa) / 248.84
def kPa_to_MPa(kPa):
    return kPa / 1000.0
def kPa_to_bar(kPa):
    return kPa * 0.01
def kPa_to_psi(kPa):
    return 0.145037738 * kPa
# Standard atmosphere is defined as 101.325 kilopascal (kPa)
# https://en.wikipedia.org/wiki/Atmosphere_(unit)
def kPa_to_std_atm(kPa):
    return kPa / 101.325
def std_atm_to_kPa(atm):
    return atm * 101.325
# One atmosphere is exactly 760 torr
# https://en.wikipedia.org/wiki/Atmosphere_(unit)
def std_atm_to_torr(atm):
    return 760.0 * atm
def torr_to_std_atm(torr):
    return torr / 760.0
def psi_to_kPa(psi):
    return 6.89475729 * psi
# One Bar is exactly equal to 100,000 Pa
# https://en.wikipedia.org/wiki/Bar_(unit)
def bar_to_kPa(bar):
    return bar * 100.0
# 1 torr is exactly 101,325/760 pascals
# https://en.wikipedia.org/wiki/Torr
def kPa_to_torr(kPa):
    return std_atm_to_torr(kPa_to_std_atm(kPa))
def torr_to_kPa(torr):
    return std_atm_to_kPa(torr_to_std_atm(torr))

# Work, Energy or Torque
#
# Energy is the capacity for doing work.  You must have energy to accomplish
# work - it is like the "currency" for performing work.  To do 100 joules of
# work, you must expend 100 joules of energy.
#
# Work refers to an activity involving a force and movement in the directon of
# the force. A force of 20 newtons pushing an object 5 meters in the direction
# of the force does 100 joules of work.
#
# Work = Force * Distance
#
# remember
#
# Force = Mass * Acceleration
#
# The rate of doing work is equal to the rate of using energy since the a force
# transfers one unit of energy when it does one unit of work. A horsepower is
# equal to 550 ft lb/s, and a kilowatt is 1000 watts.
#
# The British thermal unit (BTU or Btu) is a traditional unit of work equal to
# about 1055 joules.  A BTU is the amount of heat required to rasie the
# temperature of 1 avoirdupois bound of liquid water by 1 degree Fahrenheit at
# a constant pressure of 1 atmosphere.  ISO Standard Definition of BTU 1055.056
# joules, but this is an approximation and different measurements are used in
# different contexts:
# https://en.wikipedia.org/wiki/British_thermal_unit
JOULES_PER_BTU = 1055.056
JOULES_PER_CALORIE = 4.184
# A BTU is defined as 1054.3503 Joules
# https://en.wikipedia.org/wiki/British_thermal_unit

def joules_to_KJ(joules):
    return joules / 1000
def joules_to_MJ(joules):
    return joules_to_KJ(joules) / 1000
def KJ_to_joules(kj):
    return kj * 1000
def MJ_to_joules(mj):
    return KJ_to_joules(mj * 1000)
def btus_to_joules(btus):
    return btus * JOULES_PER_BTU
def joules_to_btus(j):
    return j / JOULES_PER_BTU
def btus_per_lb_to_MJ_per_kg(btus_per_lb):
    return per_lb_to_per_kg(joules_to_MJ(btus_to_joules(btus_per_lb)))
def MJ_per_kg_to_btus_per_lb(MJ_per_kg):
    return per_kg_to_per_lb(joules_to_btus(MJ_to_joules(MJ_per_kg)))
def ft_lbs_to_inch_lbs(ft_lbs_force):
    return feet_to_inches(ft_lbs_force)
def ft_lbs_to_kg_m(ft_lbs_force):
    return lbs_to_kg(feet_to_meters(ft_lbs_force))
def kg_m_to_ft_lbs(kg_m):
    return kg_to_lbs(meters_to_feet(kg_m))
# newton-meter is kg-m * gravity, kg-m * m/s^2, kg-m * 9.8 m/s^2
# https://en.wikipedia.org/wiki/Newton_metre
def kg_m_to_newton_m(kg_m):
    return kg_m * STANDARD_GRAVITY
def newton_m_to_kg_m(newtons):
    return newtons / STANDARD_GRAVITY
def ft_lbs_to_newton_m(ft_lbs_force):
    return kg_m_to_newton_m(ft_lbs_to_kg_m(ft_lbs_force))
def newton_m_to_ft_lbs(newton_meters):
    return kg_m_to_ft_lbs(newton_m_to_kg_m(newton_meters))
# newton-meters and joules are dimensionally equivalent
def ft_lbs_to_joules(ft_lbs_force):
    return ft_lbs_to_newton_m(ft_lbs_force)
def joules_to_ft_lbs(joules):
    return newton_m_to_ft_lbs(joules)
def ft_lbs_to_btus(ft_lbs_force):
    return joules_to_btus(ft_lbs_to_joules(ft_lbs_force))
def btus_to_ft_lbs(btus):
    return joules_to_ft_lbs(btus_to_joules(btus))
# Thermochemical calorie is defined as 4.184 joules
# https://en.wikipedia.org/wiki/Calorie
def ft_lbs_to_calories(ft_lbs_force):
    return ft_lbs_to_joules(ft_lbs_force) / JOULES_PER_CALORIE

# Power
#
# Power is the rate of doing work or the rate of using energy, which are
# numerically the same. If you do 100 joules of work in one second (using 100
# joules of energy), the power is 100 watts.
#
# Power = Work / time
#
# or
#
# Power = Force * velocity
#
HP_TO_FT_LBS_PER_SEC = 550
HP_TO_FT_LBS_PER_MIN = HP_TO_FT_LBS_PER_SEC * SEC_PER_MIN
WATTS_PER_KILOWATT = 1000
# It is defined by standard as 9.80665 m/s^s
# https://en.wikipedia.org/wiki/Standard_gravity
KG_M_PER_SEC_PER_METRIC_HP = 75
# 550 ft-lbs per second is exactly 33,000 ft-lbs per minute
def ft_lbs_per_sec_to_ft_lbs_per_min(ftLbsPerSec):
    return per_sec_to_per_min(ftLbsPerSec)
# Imperial Horsepower is defined as exactly 550 ft-lbs (force) per second
# https://en.wikipedia.org/wiki/Horsepower
def ft_lbs_per_sec_to_imperial_hp(ftLbsPerSec):
    return ftLbsPerSec / HP_TO_FT_LBS_PER_SEC
def ft_lbs_per_min_to_imperial_hp(ftLbsPerMin):
    return ft_lbs_per_sec_to_imperial_hp(per_min_to_per_sec(ftLbsPerMin))
def ft_lbs_per_hour_to_imperial_hp(ftLbsPerHour):
    return ft_lbs_per_sec_to_imperial_hp(per_hour_to_per_sec(ftLbsPerMin))
def btus_per_hour_to_imperial_hp(btusPerHour):
    return ft_lbs_per_sec_to_imperial_hp(btus_to_ft_lbs(per_hour_to_per_sec(btusPerHour)))
# Imperial Horsepower is defined as exactly 550 ft-lbs/second
def imperial_hp_to_ft_lbs_per_sec(hp):
    return hp * HP_TO_FT_LBS_PER_SEC
def imperial_hp_to_ft_lbs_per_min(hp):
    return per_sec_to_per_min(imperial_hp_to_ft_lbs_per_sec(hp))
# convert from ft-lbs/sec to m-kg/sec
def ft_lbs_per_sec_to_kg_m_per_sec(ftLbsPerSec):
    return feet_to_meters(lbs_to_kg(ftLbsPerSec))
def kg_m_per_sec_to_ft_lbs_per_sec(kg_m_per_sec):
    return meters_to_feet(kg_to_lbs(kg_m_per_sec))
def imperial_hp_to_kg_m_per_sec(hp):
    return ft_lbs_per_sec_to_kg_m_per_sec(imperial_hp_to_ft_lbs_per_sec(hp))
def kg_m_per_sec_to_imperial_hp(kg_m_per_sec):
    return ft_lbs_per_sec_to_imperial_hp(kg_m_per_sec_to_ft_lbs_per_sec(kg_m_per_sec))
# Mechanical horsepower
# https://en.wikipedia.org/wiki/Horsepower#Metric_horsepower_.28PS.2C_cv.2C_hk.2C_pk.2C_ks.2C_ch.29
#
# Assuming the third CGPM (1901, CR 70) definition of standard gravity,
# gn=9.80665 m/s^2, is used to define the pound-force as well as the kilogram
# force, and the international avoirdupois pound (1959), one mechanical
# horsepower is:
#
# 1 hp = 33,000 ft-lbf/min by definition
# = 550 ft-lbf/s since 1 min = 60 s
# = 550x0.3048x0.45359237 m-kgf/s since 1 ft = 0.3048 m and
# = 76.0402249068 kgf-m/s 1 lb = 0.45359237 kg
# = 76.0402249068x9.80665 kg-m^2/s^3 g = 9.80665 m/s^2
# = 745.69987158227 W since 1 W = 1 J/s = 1 N-m/s = 1 (kg-m/s2)-(m/s)
# Or given that 1 hp = 550 ft-lbf/s, 1 ft = 0.3048 m,
# 1 lbf is approx 4.448 N, 1 J = 1 N-m, 1 W = 1 J/s: 1 hp = 746 W
# Imperial Horsepower to Watts
def watts_to_kilowatts(watts):
    return watts / WATTS_PER_KILOWATT
def kilowatts_to_watts(kilowatts):
    return kilowatts * WATTS_PER_KILOWATT
def kg_m_per_sec_to_watts(kg_m_per_sec):
    return kg_m_per_sec * STANDARD_GRAVITY
def watts_to_kg_m_per_sec(watts):
    return watts / STANDARD_GRAVITY
def kilowatts_to_kg_m_per_sec(kilowatts):
    return watts_to_kg_m_per_sec(kilowatts_to_watts(kilowatts))
def imperial_hp_to_watts(hp):
    return kg_m_per_sec_to_watts(imperial_hp_to_kg_m_per_sec(hp))
def imperial_hp_to_kilowatts(hp):
    return watts_to_kilowatts(imperial_hp_to_watts(hp))
def watts_to_imperial_hp(watts):
    return kg_m_per_sec_to_imperial_hp(watts_to_kg_m_per_sec(watts))
def kilowatts_to_imperial_hp(kilowatts):
    return kg_m_per_sec_to_imperial_hp(kilowatts_to_kg_m_per_sec(kilowatts))
def hp_to_hp_uk(hp):
    return (hp / 746.0) * 745.7
# DIN 66036 defines one metric horsepower as the power to
# raise a mass of 75 kg against the earth's gravitational
# force over a distance of one metre in one second; this is
# equivalent to 735.49875 W or 98.6% of an imperial
# mechanical horsepower.
def kg_m_per_sec_to_metric_hp(kg_m_per_sec):
    return kg_m_per_sec / KG_M_PER_SEC_PER_METRIC_HP
def imperial_hp_to_metric_hp(hp):
    return kg_m_per_sec_to_metric_hp( imperial_hp_to_kg_m_per_sec(hp) )
def metric_hp_to_kg_m_per_sec(metric_hp):
    return metric_hp * KG_M_PER_SEC_PER_METRIC_HP
def metric_hp_to_imperial_hp(metric_hp):
    return kg_m_per_sec_to_imperial_hp(metric_hp_to_kg_m_per_sec(metric_hp))
def newtons_and_meters_per_sec_to_watts(newtons, m_per_sec):
    watts = newtons * m_per_sec
    return watts

# Energy

# one watt is defined as one joule per second
# defined mostly for documentation
def watts_to_joules_per_sec(watts):
    return watts

def joules_per_sec_to_watts(jps):
    return jps

# we can internally self consistently go from hp to watts
# now we can go from watts to joules/sec
# now we can go from joules/sec to BTUs/sec
def imperial_hp_to_btus_per_sec(hp):
    return joules_to_btus(watts_to_joules_per_sec(imperial_hp_to_watts(hp)))
def imperial_hp_to_btus_per_minute(hp):
    return per_sec_to_per_min(imperial_hp_to_btus_per_sec(hp))
def imperial_hp_to_btus_per_hour(hp):
    return per_sec_to_per_hour(imperial_hp_to_btus_per_sec(hp))

# Frequency of Rotation

# revolutions per minute to revolutions per second (hz)
def rpm_to_rps(rpm):
    return per_min_to_per_sec(rpm)
def rps_to_rpm(rps):
    return per_sec_to_per_min(rps)
def rps_to_rad_per_sec(rps):
    return rps * 2 * math.pi
def rpm_to_rad_per_sec(rpm):
    return rps_to_rad_per_sec(rpm_to_rps(rpm))
def rpm_to_deg_per_sec(rpm):
    return math.degrees(rpm_to_rad_per_sec(rpm))

#
# Geometry routines
#

# http://www.ajdesigner.com/phpcircle/circle_arc_length_s.php

def calc_geom_radius_to_diameter(radius):
    return 2 * radius

def calc_geom_diameter_to_radius(diameter):
    return diameter / 2

def calc_geom_circumference(diameter):
    return diameter * math.pi

def calc_geom_radius_from_circumference(circum):
    return calc_geom_diameter_to_radius(circum / math.pi)

# (pi * r^2) or ((pi * d^2) / 4)
def calc_geom_area_of_circle(diameter):
    return (diameter * diameter * math.pi) / 4

def calc_geom_volume_of_cylinder(diameter, height):
    return calc_geom_area_of_circle(diameter) * height

# The length a of the arc is a fraction of the length of the
# circumference which is 2 * pi * r. So arc length = r * angle
def calc_geom_arc_length(radius, angle_rads):
    return radius * angle_rads

# Just rearrange the equation l = r * angle, r = l / angle
def calc_geom_circ_radius_from_arc(arc_length, angle_rads):
    return arc_length / angle_rads

# Again, rearrange the equation l = r * angle, angle = l / r
def calc_geom_arc_central_angle_rad(arc_length, radius):
    return arc_length / radius

# https://en.wikipedia.org/wiki/Circular_segment
# c = chord length
# r = radius
# A = angle
# chord length is c = 2 * r * sin(A / 2)
def calc_geom_chord_from_angle_radius(angle_rads, radius):
    return 2 * radius * math.sin(angle_rads / 2)

def calc_geom_chord_from_arc_length(arc_length, radius):
    angle_rads = calc_geom_arc_central_angle_rad(arc_length, radius)
    chord = calc_geom_chord_from_angle_radius(angle_rads, radius)
    return chord
#
# Calculation routines
#

# duration is the time to the bottom and then back up
# Calculate the Exhaust Port Open Duration
def calc_epo_duration_rad(epo_rad_ATDC):
    return 2 * atdc_to_bbdc_rad(epo_rad_ATDC)

def calc_epo_duration_deg(epo_deg_ATDC):
    return 2 * atdc_to_bbdc_deg(epo_deg_ATDC)

# Crank radius is half the stroke
def calc_crank_radius(stroke):
    return stroke / 2

# https://en.wikipedia.org/wiki/Piston_motion_equations
# Distance from the center of the crank, x, is given by
# l = connecting rod length
# r = crank radius, half the stroke
# A = crank angle after top dead center in radians
# using the cosine law
#
# l^2 = r^2 + x^2 - 2 * r * x * cos(A)
#
# solving for x
#
# x = r * cos(A) + sqrt( l^2 - r^2 * (sin(A))^2)
#
# Top of the stroke is given by
#
# l + r
#
# Distance from the top of the stroke is
#
# distance from top dead center = l + r - x
#
def calc_piston_position_from_angle(crl, stroke, angle_ATDC):
    l = crl
    r = calc_crank_radius(stroke)
    a = angle_ATDC
    return (l+r) - (r*math.cos(a) + math.sqrt(l**2 - r**2 * (math.sin(a))**2))

# To solve for angle, same equation, we just re-arrange to
# solve for A remember for distance from the top of the
# stroke there will be two angle solutions.
#
# l^2 = r^2 + x^2 - 2 * r * x * cos(A)
#
# l^2 - (r^2 + x^2) = - 2 * r * x * cos(A)
# (l^2 - (r^2 + x^2)) / (- 2 * r * x) =  cos(A)
# swapping the minus signs around
# ((r^2 + x^2) - l^2) / ( 2 * r * x) =  cos(A)
# A = arccos(((r^2 + x^2) - l^2) / ( 2 * r * x))
#
# As before, we need to convert distance from Top Dead
# Center to the distance from the center of the crankshaft
# (dftdc)
#
# The value returned is for both solutions, the angle before
# top dead center and the angle after top dead center.
#
def calc_angle_from_piston_position(crl, stroke, dftdc):
    l = crl
    r = calc_crank_radius(stroke)
    x = crl + r - dftdc
    cos_a = ((r**2 + x**2) - l**2) / (2 * r * x)
    if (cos_a < -1):
        cos_a = -1 # could be just outside the domain
    if (cos_a > 1):
        cos_a = 1  # could be just outside the domain
    return math.acos(cos_a)

def calc_displacement(bore, stroke, cylinders):
    return cubic_mm_to_cc(calc_geom_volume_of_cylinder(bore, stroke)) * cylinders

def calc_squish_area_ratio(bore, bowl):
    area_bore = calc_geom_area_of_circle(bore)
    area_bowl = calc_geom_area_of_circle(bowl)
    return (area_bore - area_bowl) / area_bore

NC50_OVERALL_GEAR_RATIO = 14.220
NC50_TIRE_DIAMETER_IN_INCHES = 18.5

def calc_nc50_mph(gear_ratio, tire_circum_inches, rpm):
    # Service manual gives the Gear Ratio as 14.220 : 1
    # MPH = (RPM * WheelCirc/GearRatio * ft / 12inches * mile / 5280 ft * 60 mins/hour)
    # 38.7 MPH = 10000rpm * 18.5 * pi / 14.220 / 12 / 5280 * 60
    return ( inches_to_miles(per_min_to_per_hour(rpm * tire_circum_inches) /
        gear_ratio) )

def calc_nc50_rpm(gear_ratio, tire_circum_inches, mph):
    return ( per_hour_to_per_min(mph) * gear_ratio /
            inches_to_miles( tire_circum_inches ) )

def calc_tuned_rpm(epo_deg_ATDC, ws, tl):
    # Find the tuned length of 2 stroke
    # expansion chamber
    # epo - Exhaust Port Open,deg past TDC
    # ws  - Wave Speed in m/s
    # tl  - Tuned Length in mm
    # rpm - Revolutions Per Minute
    eo = calc_epo_duration_deg(epo_deg_ATDC)
    ws = ws * 1000 / (12 * 25.4)
    rpm = inches_to_mm(eo * ws) / tl
    return rpm

def calc_tuned_length(epo_deg_ATDC, ws, rpm):
    # Find the tuned length of 2 stroke
    # expansion chamber
    # epo - Exhaust Port Open,deg past TDC
    # ws  - Wave Speed in m/s
    # tl  - Tuned Length in mm
    # rpm - Revolutions Per Minute
    eo = calc_epo_duration_deg(epo_deg_ATDC)
    ws = ws * 1000 / (12 * 25.4)
    tl = inches_to_mm(eo * ws) / rpm
    return tl

# http://hyperphysics.phy-astr.gsu.edu/hbase/sound/souspe3.html#c1
# The speed of sound in an ideal gas is given by the relationship
# a = sqrt( k * R * T / m )
# I will use celsius as the input temp
# k - is the adiabatic constant, Cp/Cv, sometimes represented by greek gamma
# k - Specific Heat ratio for Exhaust 1.343
# k - Specific Heat ratio for dry air 1.40
# m - molecular weight of gas, 28.95 for dry air, 29 for exhaust
# m - 0.02895 kg per mol
# R - Universal gas constant, 8.314510 J/(mol * K)
# R - 1545 ft lbf / degrees Rankin
def calc_vel_sound_perfect_gas(k, T, m):
    return math.sqrt( k * CONST_R * celsius_to_kelvin(T) / (m / 1000) )

# stroke is in mm, result is in meters, so divide by 1000
# rpm is revolutions per minute, we need per second so
# divide by 60.0 piston has to transverse the stroke twice,
# once up, once down.
#
# In Jennings, the mean piston speed is given by
# piston speed in ft/min = 0.166 * stroke in inches * RPM
# Piston has to travel twice the stroke and we need to
# convert inches to feet so we multiply by 2/12 or 0.16667
# So Jennings equations make sense.
def calc_mean_piston_speed_from_rpm(stroke, rpm):
    return 2 * rpm_to_rps(rpm) * mm_to_meters(stroke)

def calc_rpm_from_mean_piston_speed(stroke, mps):
    return rps_to_rpm(mps / (2 * mm_to_meters(stroke)))

def calc_estimate_scavange_ratio(cr):
# A guess at the scavange ratio is
# (compression_ratio - 1) / compression_ratio
# The idea is the area left over at top dead
# center is not scavanged. Efficient engines
# with headers, should scavanage better, 
# engines with back pressure or samll exhaust
# valves or ports could be worse.
    return (cr_guard(cr) - 1) / cr_guard(cr)

#
# Thermodynamics
#
def calc_heat_added_per_unit_mass_gas(btuslb,stoich,scarat):
    return btuslb * scarat / stoich

def calc_adiabatic_ratio(cp, cv):
# k - is the adiabatic constant, Cp/Cv, sometimes represented by greek gamma
    return cp / too_small_guard(cv)

def calc_thermal_efficiency(cr, k):
# cr - compression ratio
# k  - is the adiabatic constant, Cp/Cv, sometimes represented by greek gamma
    return 1 - math.pow((1/cr_guard(cr)),(k-1))

def calc_pressure_ratio(intake_pressure, boost_pressure_added):
    return (intake_pressure + boost_pressure_added) / too_small_guard(intake_pressure)

# From Wikipedia
# https://en.wikipedia.org/wiki/Adiabatic_process
# https://en.wikipedia.org/wiki/Isentropic_process
#
# t2 = t1 * (p2/p1) ^ ((k-1)/k)
#
# which is actually:
#
# https://en.wikipedia.org/wiki/Isentropic_process
# (t2/t1) ^ (1/k-1) == (p2/p1) ^ (1/k) == V1/V2
#
# t2 - the resulting temperature
# t1 - the starting absolute temperature
# p2 - the ending pressure
# p1 - the starting temperature
# k - is the adiabatic constant, Cp/Cv, someeitmes represented by greek gamma
#
# we will take temperature in celsius and return temperature in celsius
#
def calc_isentropic_temperature(t1, k, p1, p2):
    t2 = kelvin_to_celsius(celsius_to_kelvin(t1) * math.pow((p2/too_small_guard(p1)), (k-1)/too_small_guard(k)))
    return t2

# Boost temperature is the calculated isentropic temperature / compressor efficiency
# Super charger or turbo charger efficiency can be 63% to 75% efficient
# Roots style blowers (GMC 671) can be much less efficient, 43%.
def calc_boost_temperature(t1, k, p1, p2, compressor_eff):
    t2 = calc_isentropic_temperature(t1, k, p1, p2) / compressor_eff
    return t2

def calc_a(qpri, cv, inTempC):
    a = qpri / too_small_guard(cv * celsius_to_rankine(inTempC))
    return a

def calc_mep_over_p1(a, thermeff, k, cr):
    mepp1 = a * thermeff/too_small_guard( (k-1) * (1 - (1/cr_guard(cr))) )
    return mepp1

# Mean Effective Pressure
def calc_mep(a, thermeff, k, cr, presskPa):
    return kPa_to_psi(presskPa) * calc_mep_over_p1(a, thermeff, k, cr)

def calc_indicated_mep(mecheff, mep):
# mecheff - mechanical efficiency
# mep     - mean effective pressure
    return mecheff * mep

def calc_carb_size(k, sv, numcarbs, rpm):
    return k * math.sqrt(cc_to_liters(sv / numcarbs) * rpm)

def calc_intake_strokes_per_rev(cycles):
    return 2 / cycles

def calc_cubic_feet_per_min(sv, rpm, cycles, voleff):
    return cc_to_cf(sv) * rpm * calc_intake_strokes_per_rev(cycles) * voleff

def calc_oil_ratio(gallons_of_gas, ounces_of_oil):
    return us_liquid_gallons_to_fluid_ounces(gallons_of_gas) / ounces_of_oil

def calc_oil_ounces_from_gallons_gas_and_ratio(gallons_of_gas, ratio):
    return us_liquid_gallons_to_fluid_ounces(gallons_of_gas) / ratio

def calc_gallons_of_gas_from_oil_ounces_ratio(oil_ounces, ratio):
    return fluid_ounces_to_us_liquid_gallons(oil_ounces) * ratio

def mep_to_hp(mep, sv, rpm, cycles):
    hp = ft_lbs_per_sec_to_imperial_hp(mep * cc_to_ci(sv) * rpm_to_rps(rpm) * 2 / (12 * cycles))
    return hp

def hp_to_mep(hp, sv, rpm, cycles):
    mep = imperial_hp_to_ft_lbs_per_sec(hp) * (12 * cycles) / (cc_to_ci(sv) * rpm_to_rps(rpm) * 2)
    return mep

def hp_and_mep_to_rpm(hp, mep, sv, cycles):
    rpm = rps_to_rpm(imperial_hp_to_ft_lbs_per_sec(hp) * (12 * cycles) / (cc_to_ci(sv) * mep * 2))
    return rpm

def hp_and_mep_to_sv(hp, mep, rpm, cycles):
    sv = ci_to_cc(imperial_hp_to_ft_lbs_per_sec(hp) * (12 * cycles) / (rpm_to_rps(rpm) * mep * 2))
    return sv

def torque_to_hp(torque_ft_lbs, rpm):
    return torque_ft_lbs * rpm / (HP_TO_FT_LBS_PER_MIN / (2 * math.pi))

def hp_to_torque(hp, rpm):
    return (hp * (HP_TO_FT_LBS_PER_MIN / (2 * math.pi))) / rpm

# mostly just for documentation
def ft_lbs_to_torque_ft_lbs(torque_arm_in_feet, brake_load_in_lbs):
    return torque_arm_in_feet * brake_load_in_lbs

def newton_m_to_torque_newton_m(torque_arm_in_meters, brake_load_in_newtons):
    return torque_arm_in_meters * brake_load_in_newtons

# Flow Though the Venturi (flow through a carb)
# From Internal Combustion Fundamentals
# John B. Heywood. 
# Appendix C - Equations for Fluid Flow through a Restriction
# 7.2 Carburetors
#
# Cd = (actual mass flow) / (ideal mass flow)
#
# The Discard Coefficient really feels like a kluge. Quoting Heywood:
#
# The discharge coefficient Cd in Eq (7.5) represents the effect of all
# deviations from the ideal one-dimensional isentropic flow. It is influenced
# by many factors of which the most important are the following: (1) fluid mass
# flow rate; (2) orifice length/diameter ratio; (3) orifice/approach-area
# ratio; (4) orifice surface area; (5) orifice surface roughness; (6) orifice
# inlet and exit chamfers; (7) fluid specific gravity; (8) fluid viscosity; and
# (9) fluid surface tension. The use of teh orifice Reynolds number Re =
# rho*V*D0/mu as a correlating paramter for the discharge coefficient accounts
# for the effects of mass flow rate, fluid density and viscosity, and length
# scale to a good first approximation.
#
# Under reasonable pressure differences Cd varies from 0.8 to 1.0. 0.9 might be
# a good guess.
#
# Again from Heywood:
#
# Alternatively, the flow or discharge coefficient can be defined in terms of
# an effective cross-sectional area of the duct and a reference area. The
# reference area Ar is usually taken as the minimum cross-sectional area. The
# effective area of the flow restriction Ae is then the cross-sectional area of
# the throat of a frictionless nozzle which would pass the measured mass flow
# between a large upstream reservoir at the upstream stagnation pressure and a
# large downstream reservoir at the downstream measured static pressure. Thus
#
# Cd = Ae / Ar
#
# Estimate the Coefficient of Discharge
# AT - area of the flow restriction, area of the venturi of the carb, area of throat
# Ar - area of the flow reference, I will use the area of the pipe into the
#      engine, the area of the manifold pipe
def estimate_Cd(AT, Ar):
    return AT / too_small_guard(Ar)
#
# Using SI units
# Cd - Coefficient of Discharge, 0.9 might be a good guess
# AT - Area of the venturi throat, the area of the smallest part of the carb, 
#      the slide area in meters squared
# p0 - Pressure at the input to the carb, probably close to atmospheric, in pascals
# pT - Pressure at the venturi throat, in pascals
# k  - Adiabtic Ratio, ratio of specific heats Cp/Cv, heat capacity ratio
# T0 - Temperature in Kelvin at input
#
# Returns mass flow rate of the gas through the restriction, using SI units
# AT - in meters squared
# p0 - in pascals
# pT - in pascals
# T0 - in Kelvin
#
# This routine should then return kilograms per second
# 
def flow_through_venturi(Cd, AT, p0, pT, k, T0):
    a = (Cd * AT * p0) / math.sqrt( CONST_R * T0 )
    b = math.pow( (pT / p0), (1.0 / k) )
    c1 = 1.0 - math.pow( (pT / p0), ((k - 1.0) / k) )
    c2 = (2.0 * k) / (k - 1.0)
    c = math.sqrt( c2 * c1 )
    return a * b * c

#
# How can we find the maximum CFM through the carb? We should be able to
# determine the maximum amount of horsepower for that given amount of air.
#
# Again from Heywood:
#
# For given values of p0 and T0, the maximum mass flow occurs when the velocity
# at the minimum area or throat equals the velocity of sound. This condition is
# called chocked or critical flow. When the flow is choked the pressure at the
# throat, pT, is related to the stagnation pressure p0 as follows:
#
# pT/p0 = (2 / (k + 1)) ^ (k / (k - 1))
#
# This tells us that the critical pressure ratio is just dependant on the heat
# capacity ratio and we can use the assumption that p0 is close to the
# atmospheric value to find the pressure at the throat, the pressure at the
# smallest constriction of the carbuerator.
#
def choked_throat_pressure(p0, k):
    return p0 * math.pow( (2.0 / (k+1.0)), (k / too_small_guard(k - 1.0)) )

# List routines

# http://www.ford-y-block.com/dimensions.htm
#
# Y-Block Dimensions and weights         ford-y-block.com
#
# Bore &  Stroke          rod length  R:S ratio   pin diam  pin wt   piston wt.  rod wt.   comp. ht.
# 239 cu.in. 3.50X 3.10"  EBU 6.324"  2.038:1     .9122"       gr    24.06oz     680gr     1.858"
# 256 cu.in 3.62X 3.10"   EBU 6.324"  2.038:1     .9122"       gr    24.06oz     680gr     1.858"
# 272 cu.in. 3.62X 3.30"  EBU 6.324"  1.915:1     .9122"    161gr    531gr       680gr     1.768"
# 292 cu.in 3.75X 3.30"   EBU 6.324"  1.915:1     .9122"    143gr    555gr       680gr     1.768"
# 292 cu.in. 3.75X 3.30"  C2AE 6.324" 1.915:1     .9122"    143gr    555gr       695gr     1.768"
# 292 HD trk 3.75X 3.30"  C1TE 6.252" 1.894:1     .9122"       gr    663gr                 1.830"
# 312 cu.in 3.80X 3.44"   ECZ 6.252"  1.816:1     .9122"    143gr    585gr       638gr     1.768"
#
# 239 & 256 used EBU 3.10" stroke crankshaft       ford-y-block.com
# 272 & 292 used EC 3.30" crankshaft               see CRANKSHAFT IDENTIFICATION
# 312 used ECZ 3.44" crankshaft
#
# Rod journal diameter: all                        2.1880-2.1888" standard
# Main journal diameter 239-256-272-292:           2.4980-2.4988" standard
# Main journal diameter 312:                       2.6240-2.6248" standard
#
# Block deck:                                      9.775"
#
# APPROXIMATE WEIGHTS
# BARE BLOCK                                       155 pounds
# LONG BLOCK                                       535 pounds
# COMPLETE ENGINE                                  610 pounds
# CYLINDERHEAD   BARE                              49 pounds        Aluminum 24.5#
# CYLINDERHEAD COMPLETE                            56 pounds        Aluminum 28#
# CRANKSHAFT      292                              53 pounds
# CRANKSAHFT      312                              58 pounds
# CRANKSHAFT      292 STEEL                        60 pounds
# TIMING COVER                                     16 pounds        Mummert aluminum 9 pounds
# FLYWHEEL                                         30 pounds        Mummert aluminum 15 pounds
# INTAKE MANIFOLD                                  31 pounds        Mummert aluminum 14 pounds
#
# https://en.wikipedia.org/wiki/Mazda_K_engine
def list_bore_strokes():
    print('From Heywood')
    print('Bore/Stroke small and medium engines 0.8 to 1.2')
    print('Bore/Stroke large slow speed CI engines 0.5 to 0.8')
    print('NC50 stock  bore -  40.0 , stroke  39.6 , cyl 1, b/s', str(round(40.0/39.6,2)))
    print('NC50 shocko bore -  44.0 , stroke  39.6 , cyl 1, b/s', str(round(44.0/39.6,2)))
    print('NC50 athena bore -  47.6 , stroke  39.6 , cyl 1, b/s', str(round(47.6/39.6,2)))
    print('NC50 metra  bore -  47.0 , stroke  39.6 , cyl 1, b/s', str(round(47.0/39.6,2)))
    print('TRX250R     bore -  66.0 , stroke  72.0 , cyl 1, b/s', str(round(66.0/72.0,2)))
    print('ZXI  1100   bore -  80.0 , stroke  71.0 , cyl 3, b/s', str(round(80.0/71.0,2)))
    print('06 SXR 800  bore -  82.0 , stroke  74.0 , cyl 2, b/s', str(round(82.0/74.0,2)))
    print('56 272 Yblk bore - ',str(round(inches_to_mm(3.62),1)),', stroke ',
                                str(round(inches_to_mm(3.30),1)),', cyl 8, b/s',
                                str(round(3.62/3.30,2)))
    print('77 Cad  425 bore - 103.7 , stroke 103.0 , cyl 8, b/s', str(round(103.7/103.0,2)))
    print('87 Must 5.0 bore - 101.6 , stroke  76.2 , cyl 8, b/s', str(round(101.6/76.2,2)))
    print('95 Probe2.5 bore -  84.5 , stroke  74.2 , cyl 6, b/s', str(round(84.5/74.2,2)))
    print('04 MC SC3.8 bore - ',str(round(inches_to_mm(3.8),1)),', stroke ',
                                str(round(inches_to_mm(3.44),1)),', cyl 6, b/s',
                                str(round(3.8/3.44,2)))
    print('04 Must 4.6 bore -  90.2 , stroke  90.0 , cyl 8, b/s', str(round(90.2/90.0,2)))
    print('16 Ford 5.2 bore -  94.0 , stroke  93.0 , cyl 8, b/s', str(round(94.0/93.0,2)))
    print('18 Ford 5.0 bore -  93.0 , stroke  92.7 , cyl 8, b/s', str(round(93.0/92.7,2)))

def list_carb_bores():
    print('NC50 stock    carb bore - 12.0mm')
    print('Dellorto      carb bore - 15.0mm')
    print('VM20          carb bore - 20.0mm')
    print('TRX250R stock carb bore - 34.0mm')

def list_manifold_bores():
    print('MLM 20mm  manifold bore - 21.6mm')

def list_connecting_rod_lengths():
    print('1985-1986 TRX250R - 125.3 mm')
    print('1987-1989 TRX250R - 130.3 mm')
    print('1977 NC50         -  80.0 mm')
    print('56 272 Yblk       - ', str(round(inches_to_mm(6.324),1)), 'mm')
    print('87 Must 5.0       - 129.286 mm, 5.090 in')
    print('04 Must 4.6       - 150.7 mm')
    print('04 Monte Carlo SC - 143.0 mm')
    print('16 Ford 5.2 Voodo - 150.7 mm')

# http://www.ridermagazine.com/manufacturer/honda/retrospective-honda-ncna50-express-1977-1983.htm/
#
# NC50
# Rev this little 1/20th-liter engine with a 6.5:1
# compression ratio up to 7,000 rpm and it would make over
# four horsepower 4.5 on the dyno.
#
# Numbers are given in rear wheel horsepower for wheeled
# vehicles.
#
# 04 Mustang is 213 based on numerous dyno runs that people
# have posted. Edmunds and numerous other quote the Ford
# values:
#
# Engine & Performance
# BASE ENGINE SIZE 4.6 L	CAM TYPE Single overhead cam (SOHC)
# CYLINDERS V8	VALVES 16
# TORQUE 302 ft-lbs. @ 4000 rpm	HORSEPOWER 260 hp @ 5250 rpm
# TURNING CIRCLE 38.1 ft.
# So the Mustang is losing about 260-213, 47 hp or 18%
# through the # drive train and this seems correct. The old
# general rule is 15%. All wheel drive cars are expected to
# lose 25 to 35%.
#
# http://www.edmunds.com/ford/mustang/2004/st-100299264/features-specs/
#
def list_peak_hp_rpms():
    print('NC50 stock rated  HP   2.5 @7000')
    print('NC50 stock        HP   4.5 @7000')
    print('NC50 shocko       HP   9.0 @8800')
    print('TRX250R           HP  42.0 @7500')
    print('06 SXR 800 Stock  HP  80.0 @6250')
    print('ZXI 1100 Stock    HP 120.0 @6750')
    print('ZXI 1100 dry pipe HP 150.0 @8000')
    print('77 Cad  425       HP 185.0 @4000')
    print('87 Must 5.0       HP 220.0 @4200')
    print('95 Probe GT 2.5l  HP 164.0 @5600')
    print('04 Monte SC Stock HP 190.0 @5200')
    print('04 Must 4.6 Stock HP 213.0 @4400')
    print('04 Must 4.6 Tuned HP 252.0 @5250')
    print('16 Ford Voodo 5.2 HP 526.0 @7500')
    print('18 Ford Coyete5.0 HP 460.0 @7000')

def list_rolling_resistance_factors():
    print('NC50 Rolling Resistance Factor 0.015')

def list_coefficient_of_drag():
    print('Unfaired Recumbent Bicycle 0.77')
    print('NC50 guess                 0.32')

# http://www.zeperfs.com/en/fiche767-ford-probe-2-5-24v.htm
def list_peak_torque():
    print('87 Must 5.0       300 ft-lbs @3200')
    print('04 Monte SC Stock 280 ft-lbs @3600')
    print('04 Must 4.6 Stock 285 ft-lbs @3500')
    print('04 Must 4.5 Tuned 293 ft-lbs @4300')
    print('95 Probe GT 2.5l  156 ft-lbs @4800')
    print('16 Ford Voodo 5.2 439 ft-lbs @4750')
    print('18 Ford Coyote5.0 420 ft-lbs @4750')

# https://en.wikipedia.org/wiki/Mean_piston_speed
# http://www.zeperfs.com/en/fiche767-ford-probe-2-5-24v.htm
def list_mean_piston_speed():
    print('Automotive        - 16 m/s')
    print('High RPM          - 20 m/s')
    print('Practical Limit   - 25 m/s')
    print('')
    print('Wikipedia')
    print('Low Speed Diesels -  8.5 m/s')
    print('Med Speed Diesels - 11.0 m/s')
    print('Hi  Speed Diesels - 14.0 m/s')
    print('Med Speed Gasoline- 16.0 m/s')
    print('Hi  Speed Gasoline- 20.0 m/s')
    print('Hi  Speed Gasoline- 25.0 m/s')
    print('NASCAR Sprint Cup - 25.0 m/s')
    print('Formula One       - 30.0 m/s')
    print('')
    print('95 Probe GT 2.5l  - 13.6 m/s')

def list_compression_ratios():
    print('CR = (Swept_Volume + Clearance_Volume) / Clearance_Volume')
    print(' or ')
    print('CR = Maximum Cylinder Volume / Minimum Cylinder Volume')
    print('From Heywood:')
    print('Spark       Ignition (SI) 8 to 12')
    print('Compression Ignition (CI) 12 to 24')
    print('NC50 stock        - 6.5')
    print('NC50 shocko       - 6.5')
    print('TRX250R           - 10.0')
    print('06 SXR 800 Stock  - 7.2')
    print('ZXI 1100 stock    - 5.8')
    print('57 272 Yblk       - 7.8')
    print('77 Cad  425       - 8.2')
    print('87 Must 5.0       - 9.0')
    print('04 Monte SC 3800  - 8.5')
    print('04 Must GT 4.6L   - 9.4')
    print('95 Probe GT 2.5l  - 9.2')
    print('16 Ford Voodo 5.2 - 12.0')
    print('18 Ford Coyote5.0 - 12.0')

def list_gear_ratios():
    print('NC50 stock        - 14.2207792208')
    print('NC50 26 tooth     - 12.3246753247')

# From https://www.fueleconomy.gov/feg/atv.shtml
def list_power_losses():
    print('Engine Losses')
    print('  Thermal radiator, exh heat : 56 - 60%')
    print('  Combustion                 : 3%')
    print('  Pumping Losses             : 3%')
    print('  Friction                   : 3%')
    print('Parasitic Losses')
    print('  Water Pump, Alternator     : 3 - 4%')
    print('Power to Wheels')
    print('  Wind Resistance            : 13 - 19%')
    print('  Rolling Resistance         : 6 - 9%')
    print('Drivetrain Losses            : 4 - 7%')

# Many values from https://en.wikipedia.org/wiki/Energy_density
# http://hypertextbook.com/facts/2003/ArthurGolnik.shtml
def list_fuel_specific_energy():
    print('Fuel Specific Energy in BTUs/lb')
    print('Energy from Combustion (Cooling Effect)')
    print('Hydrogen                                   = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(142)),
            'BTUs/lb,      ', round(142,2), 'MJ/kg')
    print('Methane                                    = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(55.5)),
            'BTUs/lb,      ', round(55.5,2), 'MJ/kg')
    print('Diesel/Fuel Oil                            = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(48)),
            'BTUs/lb,      ', round(48,2), 'MJ/kg')
    print('LPG/Propane/Butane                         = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(46.4)),
            'BTUs/lb,      ', round(46.4,2), 'MJ/kg')
    print('Jet fuel/Kerosene                          = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(46)),
            'BTUs/lb,      ', round(46,2), 'MJ/kg')
    print('Animal/Veg. Fat                            = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(37)),
            'BTUs/lb,      ', round(37,2), 'MJ/kg')
    print('Dimethy Ether DME                          = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(28.8)),
            'BTUs/lb,      ', round(28.8,2), 'MJ/kg')
    print('Ethonal E100                               = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(26.4)),
            'BTUs/lb,      ', round(26.4,2), 'MJ/kg')
    print('Methonal M100                              = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(19.7)),
            ' BTUs/lb,      ', round(19.7,2), 'MJ/kg')
    print('Gasoline Zittel, Werner & Reinhold Wurster = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(45.7)),
            'BTUs/lb,      ', round(45.7,2), 'MJ/kg')
    print('Gasoline Caldirola, Manuela                = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(47.5)),
            'BTUs/lb,      ', round(47.5,2), 'MJ/kg')
    print('Gasoline Thomas, George - Sandia Labs      = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(44.4)),
            'BTUs/lb,      ', round(44.4,2), 'MJ/kg')
    print('Gasoline Low Range Val - Nommensen, Arthur = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(36.4)),
            'BTUs/lb,      ', round(36.4,2), 'MJ/kg')
    print('Gasoline Hi  Range Val - Nommensen, Arthur = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(49.6)),
            'BTUs/lb,      ', round(49.6,2), 'MJ/kg')
    print('Gasoline Harrison, Reid R.                 = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(44.0)),
            'BTUs/lb,      ', round(44.0,2), 'MJ/kg')
    print('Gasoline E10                               = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(43.54)),
            'BTUs/lb,      ', round(43.54,2), 'MJ/kg')
    print('Gasoline E85                               = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(33.10)),
            'BTUs/lb,      ', round(33.10,2), 'MJ/kg')
    print('VP C-12                                    = 18,834 BTUs/lb,      ', 
            round(btus_per_lb_to_MJ_per_kg(18834),2),'MJ/kg')
    print('Pump Gas                                   = 17,920 BTUs/lb,      ',
            round(btus_per_lb_to_MJ_per_kg(17920),2),'MJ/kg')
    print('Acetone                                    = 12,000 BTUs/lb (225),',
            round(btus_per_lb_to_MJ_per_kg(12000),2),'MJ/kg')
    print('Benzole                                    = 17,000 BTUs/lb (153),',
            round(btus_per_lb_to_MJ_per_kg(17000),2),'MJ/kg')
    print('Ether                                      = 15,000 BTUs/lb (153),',
            round(btus_per_lb_to_MJ_per_kg(15000),2),'MJ/kg')
    print('Methonal                                   =  9,770 BTUs/lb (472),',
            round(btus_per_lb_to_MJ_per_kg(9770),2), 'MJ/kg')
    print('Nitrobenzene                               = 10,800 BTUs/lb (143),',
            round(btus_per_lb_to_MJ_per_kg(10800),2),'MJ/kg')
    print('Nitromethane                               =  5,000 BTUs/lb (258),',
            round(btus_per_lb_to_MJ_per_kg(5000),2), 'MJ/kg')
    print('Prop. Oxide                                = 14,000 BTUs/lb (220),',
            round(btus_per_lb_to_MJ_per_kg(14000),2),'MJ/kg')
    print('Diborane                                   = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(78.2)),
            'BTUs/lb,      ', round(78.2,2), 'MJ/kg')
    print('Natural Gas, LNG at -160C, CNG at 250 bar  = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(53.6)),
            'BTUs/lb,      ', round(53.6,2), 'MJ/kg')
    print('Cude Oil                                   = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(46.3)),
            'BTUs/lb,      ', round(46.3,2), 'MJ/kg')
    print('Residential Heating Oil                    = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(46.2)),
            'BTUs/lb,      ', round(46.2,2), 'MJ/kg')
    print('Diesel fuel                                = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(45.6)),
            'BTUs/lb,      ', round(45.6,2), 'MJ/kg')
    print('Jet A Aviation Fuel/Kerosene               = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(42.80)),
            'BTUs/lb,      ', round(42.80,2), 'MJ/kg')
    print('Biodiesel oil/Vegetable Oil                = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(42.20)),
            'BTUs/lb,      ', round(42.20,2), 'MJ/kg')
    print('Dimethylfuran (DMF)                        = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(42.00)),
            'BTUs/lb,      ', round(42.00,2), 'MJ/kg')
    print('Body Fat metabolism                        = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(38.00)),
            'BTUs/lb,      ', round(38.00,2), 'MJ/kg')
    print('Hydrazine                                  = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(19.50)),
            'BTUs/lb,      ', round(19.50,2), 'MJ/kg')
    print('Liquid Ammonia                             = {:,.0f}'.format(MJ_per_kg_to_btus_per_lb(18.00)),
            'BTUs/lb,      ', round(18.00,2), 'MJ/kg')

GASOLINE_STOICHIOMETRIC = 14.7
E10_STOICHIOMETRIC = 14.08
E15_STOICHIOMETRIC = 13.79
E85_STOICHIOMETRIC = 9.765
ETHANOL_STOICHIOMETRIC = 9.0078
METHANOL_STOICHIOMETRIC = 6.45
PROPANE_STOICHIOMETRIC = 15.7

def air_fuel_ratio_to_lambda(af_ratio,stoich):
    return af_ratio / stoich

def af_ratio_and_lambda_to_str(af_ratio,stoich):
    return "%5.2f, lambda - %.4f" % (af_ratio,air_fuel_ratio_to_lambda(af_ratio,stoich))

# http://www.hotrod.com/articles/wideband-oxygen-sensor/
def list_air_fuel_ratio():
    print('Air/Fuel Ratio')
    print('Gasoline Lean               - ',af_ratio_and_lambda_to_str(15.0,GASOLINE_STOICHIOMETRIC))
    print('Gasoline Stoichiometric     - ',af_ratio_and_lambda_to_str(14.7,GASOLINE_STOICHIOMETRIC))
    print('Gasoline Max Power Rich     - ',af_ratio_and_lambda_to_str(12.5,GASOLINE_STOICHIOMETRIC))
    print('Gasoline Max Power Lean     - ',af_ratio_and_lambda_to_str(13.23,GASOLINE_STOICHIOMETRIC))
    print('Gasoline E10 Stoichiometric - ',af_ratio_and_lambda_to_str(14.08,E10_STOICHIOMETRIC))
    print('Gasoline E10 Max Power Rich - ',af_ratio_and_lambda_to_str(12.0,E10_STOICHIOMETRIC))
    print('Gasoline E10 Max Power Lean - ',af_ratio_and_lambda_to_str(12.7008,E10_STOICHIOMETRIC))
    print('Gasoline E15 Stoichiometric - ',af_ratio_and_lambda_to_str(13.79,E15_STOICHIOMETRIC))
    print('Gasoline E15 Max Power Rich - ',af_ratio_and_lambda_to_str(11.75,E15_STOICHIOMETRIC))
    print('Gasoline E15 Max Power Lean - ',af_ratio_and_lambda_to_str(12.4362,E15_STOICHIOMETRIC))
    print('Gasoline E85 Stoichiometric - ',af_ratio_and_lambda_to_str(9.75,E85_STOICHIOMETRIC))
    print('Gasoline E85 Max Power Rich - ',af_ratio_and_lambda_to_str(6.975,E85_STOICHIOMETRIC))
    print('Gasoline E85 Max Power Lean - ',af_ratio_and_lambda_to_str(8.469,E85_STOICHIOMETRIC))
    print('Ethanol Stoichiometric      - ',af_ratio_and_lambda_to_str(9.0078,ETHANOL_STOICHIOMETRIC))
    print('Ethanol Max Power Rich      - ',af_ratio_and_lambda_to_str(6.429,ETHANOL_STOICHIOMETRIC))
    print('Ethanol Max Power Lean      - ',af_ratio_and_lambda_to_str(7.8,ETHANOL_STOICHIOMETRIC))
    print('Acetone  Max Power          - ',af_ratio_and_lambda_to_str(9.4,9.4))
    print('Benzole  Max Power          - ',af_ratio_and_lambda_to_str(10.8,10.8))
    print('Ether    Max Power          - ',af_ratio_and_lambda_to_str(9.8,9.8))
    print('Methonal Stoichiometric     - ',af_ratio_and_lambda_to_str(6.45,METHANOL_STOICHIOMETRIC))
    print('Methonal Max Power          - ',af_ratio_and_lambda_to_str(4.5,METHANOL_STOICHIOMETRIC))
    print('Methonal Peak Torque        - ',af_ratio_and_lambda_to_str(4.0,METHANOL_STOICHIOMETRIC))
    print('Propane  Stoichiometric     - ',af_ratio_and_lambda_to_str(15.7,PROPANE_STOICHIOMETRIC))
    print('Propane  Max Power Rich     - ',af_ratio_and_lambda_to_str(13.18,PROPANE_STOICHIOMETRIC))
    print('Nitrobenzene Max            - ',af_ratio_and_lambda_to_str(8.1,8.1))
    print('Nitromethane Rich Consv.    - ',af_ratio_and_lambda_to_str(10.1,6.5))
    print('Nitromethane Conservative   - ',af_ratio_and_lambda_to_str(6.5,6.5))
    print('Nitromethane Max Power      - ',af_ratio_and_lambda_to_str(2.5,6.5))
    print('Nitromethane Max Power      - ',af_ratio_and_lambda_to_str(0.5,6.5))
    print('Propylene Oxide Max         - ',af_ratio_and_lambda_to_str(9.6,9.6))

def list_volumetric_efficiency():
    print('Volumetric Efficiency')
# From http://www.widman.biz/English/Calculators/CFM.html
    print('The volumetric efficiency is a factor determined by')
    print('the efficiency of the turbo, the electronic control')
    print('systems, the type of carb or fuel injection and the')
    print('variation of valve timing or opening.')
    print('')
    print('A carburated engine normally has a vol eff of 0.70-0.80')
    print('but electronics can raise this figure as high as 2.0.')
    print('')
    print('A diesel engine (2 cycle or 4 cycle) normally has a')
    print('volumetric efficiency of 0.90.')
    print('')
    print('A turbo can raise the volumetric efficiency to between')
    print('1.5 and 3.0. If you do not know this value for your')
    print('turbo, it is best to use 3.0')
    print('')
    print('60s-80s Stock Engines = 0.75 - 0.85')
    print('Modern  Stock Engines = 0.85 - 0.95')
    print('Mild Built            = 0.85 - 0.90')
    print('Racing Engines        = 0.90 - 1.00')
    print('2Stroke Good Pipe     = 1.00')
    print('2Stroke OK   Pipe     = 0.90')
    print('1950s or 1960s cars   = 0.85')
    print('1980s or 1990s cars   = 0.90')
    print('Well designed normal aspirated engines 1.0')

def list_clearance_volume():
    print('Clearance Volume')
    print('The volume in cc with the piston at Top Dead Center (TDC)')
    print('NC50 stock        - 8cc')

# https://en.wikipedia.org/wiki/Mean_effective_pressure
# http://www.zeperfs.com/en/fiche767-ford-probe-2-5-24v.htm
# This is not the peak pressure, the peak pressure or the
# pressure at combustion is much higher. This is the mean
# or for me it is easier to think of as the average,
# pressure across the whole stroke. So at combustion the
# pressure is very high, at the bottom of the stroke it
# is very low and we find the average of that pressure.
def list_bmep():
    print('Typical Mean Effective Pressure at max Torque')
    print('Natural asp. spark-ign : 8.5-10.5 bar 850-1050kPa 125-150 psi')
    print('Boosted spark ignition : 12.5-17  bar 1.25-1.7MPa 180-250 psi')
    print('Natural asp. 4s diesels:    7-9   bar 700-900 kPa 100-130 psi')
    print('Boosted car 4s diesels : 14-18    bar 1.4-1.8 MPa 200-269 psi')
    print('Large low speed 2s dies: up to 19 bar 1.9 MPa 275 psi.')
    print('Ultra boosted engines  : up to 28 bar 32 bar for the Agera R')
    print('Top Fuel dragster      : 80-100   bar 8.0-10MPa 1160-1450 psi')
    print('')
    print('Jennings Two Stroke Tuners Handbook')
    print('2s low speed smooth    :  4.8      bar (70 psi)')
    print('2s ported and plumbing :  7.9      bar (115 psi)')
    print('2s highly developed    :  8.6      bar (125 psi)')
    print('2s Enduro              :  8.0      bar (116 psi)')
    print('2s Motocross           :  9.0      bar (130 psi)')
    print('2s Road Race           : 11.0      bar (160 psi)')
    print('')
    print('95 Probe GT 2.5l       : 10.6      bar')
    print('')

def list_specific_power():
    print('95 Probe GT 2.5l       : 0.32 kW/cm2')
    print('')

def list_exhaust_temperatures():
    print('Average exhaust temperature in pipe')
    print('Blair average temperature estimates')
    print('GP - 650')
    print('MX - 600 (TRX250R 6 inches down on the header)')
    print('Enduro - 500')
    print('JetSki - 400')

def list_exhaust_port_open():
    print('Exhaust Port Open (epo) in Degrees After Top Dead Center (ATDC)')
    print('NC50     - ', 130.0)
    print('TRX250R  - 88.5')

def list_exhaust_port_close():
    print('Exhaust Port Close (epc) in Degrees After Top Dead Center (ATDC)')
    print('NC50     - 180.0')

def list_moped_tire_sizes():
    print('Moped Tire Sizes')
    print('PA50 - Honda Hobbit   - Tire (Size 2.25x17)')
    print('NC50 - Honda Express  - Tire (Size 2.25x14)')
    print('QT50 - Yamahopper     - Tire (Size 2.25x14)')
    print('FA50 - Suzuki Shuttle - Tire (Size 2.25x14)')
    print('SH50 - Yamaha Razz    - Tire (Size 2.50x10)')
    print('NU50 - Honda Urban Express')
    print('Includes (2) Tire Sizes - (1) 2.75x14 and (1) 2.25x16 NU50 Models')
    print('CG50/CY50 Yamaha Jogs (Size 3.00x10)')
    print('Metric Size for the Yamaha Jogs CG50/CY50 (Size 80/90x10)')

def list_moped_rim_sizes():
    print('NC50 Stock - 14 inches')
    print('NU50 Rear  - 16 inches')

# https://en.wikipedia.org/wiki/Atmosphere
def list_specific_heat_ratios():
    print('Heat capacity ratio or Adiabatic index or')
    print('ratio of specific heats or Poisson constant')
    print('is the ration of the heat capacity at a')
    print('constant pressure to the heat capacity at a')
    print('constant volume. gamma = Cp/Cv')
    print('Dry Air contains')
    print(' -- 78.09 % Nitrogen, N2')
    print(' -- 20.95 % Oxygen,   O2')
    print(' --  0.93 % Argon,    Ar')
    print(' --  0.039% Carbon Dioxide, CO2')
    print('Air contains')
    print(' -- about 1%   water vapor at sea level')
    print(' -- about 0.4% over the entire atmospher')
    print('1.403 - Ratio Specific Heats Dry Air      0C')
    print('1.400 - Ratio Specific Heats Dry Air     20C')
    print('1.401 - Ratio Specific Heats Dry Air    100C')
    print('1.398 - Ratio Specific Heats Dry Air    200C')
    print('1.393 - Ratio Specific Heats Dry Air    400C')
    print('1.365 - Ratio Specific Heats Dry Air   1000C')
    print('1.088 - Ratio Specific Heats Dry Air   2000C')
    print('1.470 - Ratio Specific Heats N2        -181C')
    print('1.404 - Ratio Specific Heats N2          15C')
    print('1.450 - Ratio Specific Heats O2        -181C')
    print('1.415 - Ratio Specific Heats O2         -76C')
    print('1.400 - Ratio Specific Heats O2          20C')
    print('1.399 - Ratio Specific Heats O2         100C')
    print('1.397 - Ratio Specific Heats O2         200C')
    print('1.394 - Ratio Specific Heats O2         400C')
    print('1.400 - Ratio Specific Heats NO2         20C')
    print('1.310 - Ratio Specific Heats CO2          0C')
    print('1.300 - Ratio Specific Heats CO2         20C')
    print('1.281 - Ratio Specific Heats CO2        100C')
    print('1.235 - Ratio Specific Heats CO2        400C')
    print('1.195 - Ratio Specific Heats CO2       1000C')
    print('1.320 - Ratio Specific Heats CH4 Methane 20C')
    print('1.343 - Ratio Specific Heats Gasoline Exhaust')

# From Wikipedia Speed of Sound article
def list_speed_of_sound():
    print('Wikipedia Speed of Sound 20C in dry air - 768 mph')

# From https://www.brisbanehotairballooning.com.au/calculate-air-density/
def list_specific_gas_constants():
    print('Specific gas contant for dry air, 287.05 J/(kg * degK)')

# Display Subroutines

def display_ratio(title, ratio):
    print(title)
    print('Ratio                  : ', ratio)
    print('')

def display_pressure(title, kPa):
    print(title)
    print('Pounds per Square Inch : ', kPa_to_psi(kPa))
    print('Bar                    : ', kPa_to_bar(kPa))
    print('Pascals                : ', kPa_to_Pa(kPa))
    print('Kilo Pascals           : ', kPa)
    print('Mega Pascals           : ', kPa_to_MPa(kPa))
    print('Inches of Mercury      : ', kPa_to_inHg(kPa))
    print('Inches of Water        : ', kPa_to_inH2O(kPa))
    print('Standard Atmospheres   : ', kPa_to_std_atm(kPa))
    print('Torr                   : ', kPa_to_torr(kPa))
    print('')

def display_distance(title, mm):
    print(title)
    print('Millimeters            : ', mm)
    print('Centimeters            : ', mm_to_cm(mm))
    print('Meters                 : ', mm_to_meters(mm))
    print('Inches                 : ', mm_to_inches(mm))
    print('Feet                   : ', mm_to_feet(mm))
    print('Yards                  : ', mm_to_yards(mm))
    print('Kilometers             : ', mm_to_km(mm))
    print('Miles                  : ', mm_to_miles(mm))
    print('')

def display_area(title, square_mm):
    print(title)
    print('Square Millimeters     : ', square_mm)
    print('Square Centimeters     : ', mm_to_cm(mm_to_cm(square_mm)))
    print('Square Meters          : ', mm_to_meters(mm_to_meters(square_mm)))
    print('Square Inches          : ', mm_to_inches(mm_to_inches(square_mm)))
    print('Square Feet            : ', mm_to_feet(mm_to_feet(square_mm)))
    print('Square Yards           : ', mm_to_yards(mm_to_yards(square_mm)))
    print('Square Kilometers      : ', mm_to_km(mm_to_km(square_mm)))
    print('Square Miles           : ', mm_to_miles(mm_to_miles(square_mm)))
    print('')

def display_angle(title, degrees):
    print(title)
    print('Degrees                : ', degrees)
    print('Radians                : ', math.radians(degrees))
    print('')

def display_angular_velocity(title, rpm):
    print(title)
    print('Revolutions/Minute     : ', rpm)
    print('Revolutions/Second(Hz) : ', rpm_to_rps(rpm))
    print('Radians per Second     : ', rpm_to_rad_per_sec(rpm))
    print('Degrees per Second     : ', rpm_to_deg_per_sec(rpm))
    print('')

# Quite often people talk about BTUs, they really are saying BTUs/hour
def display_hp(title, hp):
    print(title)
    print('HP US or Imperial      : ', hp)
    print('HP metric (aka PS)     : ', imperial_hp_to_metric_hp(hp))
    print('HP (UK)                : ', hp_to_hp_uk(hp))
    print('Watts                  : ', imperial_hp_to_watts(hp))
    print('Kilo Watts             : ', imperial_hp_to_kilowatts(hp))
    print('BTUs per Second        : ', imperial_hp_to_btus_per_sec(hp))
    print('BTUs per Minute        : ', imperial_hp_to_btus_per_minute(hp))
    print('BTUs per Hour(aka BTUs): ', imperial_hp_to_btus_per_hour(hp))
    print('Foot-Lbs  per Second   : ', imperial_hp_to_ft_lbs_per_sec(hp))
    print('Foot-Lbs  per Minute   : ', imperial_hp_to_ft_lbs_per_min(hp))
    print('kg-meters per Second   : ', imperial_hp_to_kg_m_per_sec(hp))
    print('')

def display_hp_per_liter(title, hp, sv):
    print(title)
    print('HP US or Imperial/liter: ', hp / cc_to_liters(sv))
    print('HP metric(aka PS)/liter: ', imperial_hp_to_metric_hp(hp) / cc_to_liters(sv))
    print('HP (UK)          /liter: ', hp_to_hp_uk(hp) / cc_to_liters(sv))
    print('')

def display_energy(title, ft_lbs_force):
    print(title)
    print('Energy in Pound Feet   : ', ft_lbs_force)
    print('Energy in Pound Inches : ', ft_lbs_to_inch_lbs(ft_lbs_force))
    print('Energy in Kg Meters    : ', ft_lbs_to_kg_m(ft_lbs_force))
    print('Energy in Newton Meters: ', ft_lbs_to_newton_m(ft_lbs_force))
    print('Energy in Joules       : ', ft_lbs_to_joules(ft_lbs_force))
    print('Energy in BTUs         : ', ft_lbs_to_btus(ft_lbs_force))
    print('Energy in calories     : ', ft_lbs_to_calories(ft_lbs_force))
    print('')

def display_specific_energy(title, MJ_per_kg):
    print(title)
    print('Specific Energy MJ/kg  : ', round(MJ_per_kg,2))
    print('Specific Energy BTUs/lb: ', round(MJ_per_kg_to_btus_per_lb(MJ_per_kg),2))
    print('')

def display_temperature(title, temp):
    print(title)
    print('Celsius                : ', temp)
    print('Kelvin                 : ', celsius_to_kelvin(temp))
    print('Fahrenheit             : ', celsius_to_fahrenheit(temp))
    print('Rankine                : ', celsius_to_rankine(temp))
    print('')

def display_volume(title, cc):
    print(title)
    print('Volume in cc           : ',cc)
    print('Volume in liters       : ',cc_to_liters(cc))
    print('Volume in milliliters  : ',cc_to_ml(cc))
    print('Volume in cubic inches : ',cc_to_ci(cc))
    print('Volume in cubic feet   : ',cc_to_cf(cc))
    print('')
def display_mass(title, kg):
    print(title)
    print('Mass   in kilograms    : ',kg)
    print('Mass   in pounds (lb)  : ',kg_to_lbs(kg))
    print('')

def display_force(title, newtons):
    print(title)
    print('Force  in newtons      : ',newtons)
    print('Force  in kilograms    : ',newtons_to_kg(newtons))
    print('Force  in pounds (lbf) : ',newtons_to_lbs(newtons))
    print('')

def display_liquid_capacity(title, cc):
    display_volume(title, cc)
    print('Volume in gallons      : ',cc_to_us_liquid_gallons(cc))
    print('Volume in quarts       : ',cc_to_quarts(cc))
    print('Volume in pints        : ',cc_to_pints(cc))
    print('Volume in fluid ounces : ',cc_to_fluid_ounces(cc))

def display_velocity(title, ms):
    print(title)
    print('Meters     per second  : ', ms)
    print('Feet       per second  : ', meters_sec_to_feet_sec(ms))
    print('Feet       per minute  : ', meters_sec_to_feet_min(ms))
    print('Kilometers per hour    : ', meters_sec_to_km_hour(ms))
    print('Miles      per hour    : ', meters_sec_to_miles_hour(ms))
    print('')

def display_volumetric_capacity(title, cc_sec):
    print(title)
    print('Cubic CM (CC) per Second : ', cc_sec)
    print('Cubic Feet per Min (CFM) : ', cc_sec_to_cfm(cc_sec))
    print('Liters per Second        : ', cc_sec_to_liters_sec(cc_sec))
    print('Liters per Minute        : ', cc_sec_to_liters_min(cc_sec))
    print('')

# http://pelagiaresearchlibrary.com/advances-in-applied-science/vol3-iss4/AASR-2012-3-4-1915-1922.pdf
def display_thermal_efficiency(title, eff):
    print(title)
    print('Increasing the compression ratio of an')
    print('engine can improve the thermal efficiency')
    print('of the engine by producing more power output.')
    print('The ideal theoretical cycle, the Otto cycle,')
    print('upon which spark ignition (SI) engines are')
    print('based, has a thermal efficiency, which')
    print('increases with compression ratio, and is')
    print('given by ')
    print('1 - (1/cr) ** (k-1), where k = 1.4 for air')
    print('Thermal Efficiency       : ', eff)
    print('Efficiency as Percentage : ', decimal_to_percent(eff))
    print('')

def display_mep(title, mep):
    print(title)
    list_bmep()
    display_pressure('', mep)
    print('')

def display_mean_piston_speed(title, ms):
    print(title)
    list_mean_piston_speed()
    display_velocity('', ms)
    print('')

def prompt(s, default):
    val = input((s % default) + ' : ')
    print('')
    return float(val or default)

def selection():
    print('')
    return input('Selection : ').strip()

#
# Ask routines
#

def ask_specific_heat_ratio(k=1.343):
    print('Ratio of Specific Heats')
    list_specific_heat_ratios()
    k = prompt('Computed Adiabatic Ratio or Constant[%s]', k)
    print('')
    return k

def ask_gear_ratio(ratio=14.2207792208):
    print('Gear Ratios')
    list_gear_ratios()
    ratio = prompt('Gear Ratio[%s]', ratio)
    print('')
    return ratio

def ask_fuel_specific_energy_btus_per_lb():
    print('Fuel Specific Energy')
    list_fuel_specific_energy()
    btuslb = prompt('Fuel Energy in BTUs/lb [%s]', 17920)
    print('')
    return btuslb

def ask_fuel_specific_energy_MJ_per_kg():
    print('Fuel Specific Energy')
    list_fuel_specific_energy()
    btuslb = prompt('Fuel Energy in MJ/kg [%s]', 41.6819258225)
    print('')
    return btuslb

def ask_fuel_air_ratio():
    print('Fuel Air Ratio')
    list_air_fuel_ratio()
    ratio = prompt('Fuel Air Ratio [%s]', 14.6)
    print('')
    return ratio

def ask_boost():
    print('Forced Air Induction')
    boostPSI  = prompt('Super/Turbo Charger Boost in PSI [%s]', 0)
    boostkPa =  psi_to_kPa(boostPSI)
    print('')
    return boostkPa

def ask_cycles():
    cycles = 0
    while (cycles != 2) and (cycles != 4):
        print('Two Stroke or Four Stroke?')
        cycles = prompt('Number of Engine Cycles [%s]', 2)
    print('')
    return cycles

def ask_air_temperature(title, default):
    inTempC = fahrenheit_to_celsius(prompt(title + 'in deg F [%s]', default))
    display_temperature(title, inTempC)
    return inTempC

def ask_baro_pressure():
    print('Barometric Pressure (check weather app)')
    print('or enter manifold pressure if partial throttle')
    print('Fully closed throttle is probably 12 inHg')
    print('Wide Open Throttle is probably close to Barometric')
    print('There is about 1 inHg per 1000 feet of altitude')
    presskPa  = inHg_to_kPa(prompt('Barometric Pressure in inHg [%s std]', 29.92))
    display_pressure('',presskPa)
    return presskPa

def ask_comp_efficiency():
    print('Enter the compressor efficiency in percent')
    print('Roots blowers tend to be 40 to 50 % efficient')
    print('Centrifical blowers tend to be 70 to 85 % efficient')
    comp_efficiency = prompt('Enter compressor efficiency [%s]', 70)
    # convert from percent to decimal 70% to 0.70
    return percent_to_decimal(comp_efficiency)

def ask_length(title, default):
    length = prompt(title + ' in mm [%s]', default)
    display_distance(title, length)
    return length

def ask_lbs_mass(title, default):
    lbs = prompt(title + ' in lbs mass [%s]', default)
    display_mass(title, lbs_to_kg(lbs))
    return lbs

def ask_sq_ft_area(title, default):
    sq_ft_area = prompt(title + 'in square feet [%s]', default)
    display_area(title, feet_to_mm(feet_to_mm(sq_ft_area)))
    return sq_ft_area

def ask_mph(title, default):
    mph = prompt(title + ' in MPH [%s]', default)
    display_velocity(title, miles_hour_to_meters_sec(mph))
    return mph

def ask_cylinder_head_bowl_diameter():
    band = ask_length('Inner Diameter of Squish Band', 30)
    return band

def ask_diameter(title, default):
    diameter = ask_length(title, default)
    return diameter

def ask_arc_segment_length(title, default):
    length = ask_length(title, default)
    return length

def ask_angle(title, default):
    angle = prompt(title + ' in degrees [%s]', default)
    display_angle('Angle', angle)
    return angle

def ask_bore():
    list_bore_strokes()
    bore = ask_length('Bore', 40.0)
    return bore

def ask_carb_bore():
    list_carb_bores()
    bore = ask_length('Carb Bore', 20.0)
    return bore

def ask_manifold_bore():
    list_manifold_bores()
    bore = ask_length('Manifold Bore', 21.6)
    return bore

def ask_stroke():
    list_bore_strokes()
    stroke = ask_length('Stroke', 39.6)
    return stroke

def ask_connecting_rod_length():
    list_connecting_rod_lengths()
    crl = ask_length('Connecting Rod Length', 80)
    return crl

def ask_exhaust_port_open():
    list_exhaust_port_open()
    epo = ask_angle('Exhaust Port Open ATDC', 115.0)
    return epo

def ask_exhaust_port_close():
    list_exhaust_port_close()
    epc = ask_angle('Exhaust Port Close ATDC', 180.0)
    return epc

def ask_crank_angle_atdc():
    epo = ask_angle('Crank Angle After Top Dead Center (ATDC)', 88.5)
    display_angle('Crank Angle', epo)
    return epo

def ask_cylinders():
    cyl = prompt('Cylinders [%s]', 1)
    print('')
    return cyl

def ask_rpm():
    list_peak_hp_rpms()
    rpm = prompt('RPM [%s]', 7000.0)
    print('')
    return rpm

def ask_rolling_resistance_factor():
    list_rolling_resistance_factors()
    Cr = prompt('Rolling Resistance Factor [%s]', 0.005)
    return Cr

def ask_coefficient_of_drag():
    list_coefficient_of_drag()
    Cd = prompt('Coefficient of Drag [%s]', 0.32)
    return Cd

def ask_specific_gas_constant():
    list_specific_gas_constants()
    R = prompt('Specific Gas Contstant [%s]', 287.05)
    return R

def ask_air_density():
    # rho = p / (R * T)
    # rho - density of dry air in kg/(m^3)
    # p - pressure in Pascals, Pa
    # R - Specific gas contant for dry air, 287.05 J/(kg * degrees Kelvin)
    # T - Temperature in Kelvin
    p = kPa_to_Pa(ask_baro_pressure())
    T = celsius_to_kelvin(ask_air_temperature('Outside Air Temperature', 60))
    R = ask_specific_gas_constant()
    rho = p / (R * T)
    return rho

def ask_mean_piston_speed():
    list_mean_piston_speed()
    mps = prompt('Mean Piston Speed in m/s [%s]', 16)
    print('')
    return mps

def ask_mep():
    list_bmep()
    mep = prompt('Mean Effective Pressure in PSI [%s]', 100)
    print('')
    return mep

def ask_ft_lbs_force():
    list_peak_torque()
    ft_lbs_force = prompt('Foot Lbs Force [%s]', 550)
    print('')
    return ft_lbs_force

def ask_btus():
    btus = prompt('BTUs [%s]', 45000)
    print('')
    return btus

def ask_newton_meters_force():
    list_peak_torque()
    newton_m = prompt('Newtons Meters [%s]', 1)
    print('')
    return newton_m

def ask_hp():
    list_peak_hp_rpms()
    hp = prompt('Horsepower [%s]', 1)
    print('')
    return hp

def ask_watts():
    watts = prompt('Watts [%s]', 745.69987158227)
    print('')
    return watts

def ask_kilowatts():
    kilowatts = prompt('KiloWatts [%s]', 0.74569987158227)
    print('')
    return kilowatts

def ask_ft_lbs_per_sec():
    ft_lbs_per_sec = prompt('Foot Lbs per Second [%s]', 550)
    print('')
    return ft_lbs_per_sec

def ask_ft_lbs_per_min():
    ft_lbs_per_min = prompt('Foot Lbs per Minute [%s]', 33000)
    print('')
    return ft_lbs_per_min

def ask_kg_m_per_sec():
    kg_m_sec = prompt('KG Meters per Second [%s]', 75)
    print('')
    return kg_m_sec

def ask_btus_per_hour():
    btus_per_hour = prompt('BTUs per Hour [%s]', 45000)
    print('')
    return btus_per_hour

def ask_volumetric_eff():
    list_volumetric_efficiency()
    voleff = prompt('Volumetric Efficiency [%s]',0.9)
    print('')
    return voleff

def ask_clearance_volume():
    list_clearance_volume()
    clear_vol = prompt('Clearance Volume in cc [%s]',8.0)
    print('')
    return clear_vol

def ask_scavange_ratio(cr):
    sr = calc_estimate_scavange_ratio(cr)
    print('Scavange Ratio')
    print('Est. of Scavange Ratio based on Compression - ', sr)
    sr = prompt('Scavange Ratio [%s]', sr)
    print('')
    return sr

def ask_compression_ratio():
    list_compression_ratios()
    cr = prompt('Effective Compression Ratio [%s]', 6.5)
    print('')
    return cr

def ask_overall_mechanical_efficiency():
    list_power_losses()
    mecheff = prompt('Overall Mechanical Efficiency [%s]', 0.53)
    print('')
    return mecheff

def ask_heat_added_per_unit_mass_gas(btuslb,stoich,scarat):
    qpri = calc_heat_added_per_unit_mass_gas(btuslb,stoich,scarat)
    print("Heat added per unit mass of gas (Q') in btus/lb")
    print("Q' Computed", qpri)
    qpri = prompt("Value to use for Q' [%s] ",qpri)
    print('')
    return qpri

def ask_cp():
    cp = prompt('Cp(Specific Heat at Constant Press)  Btu/lbm F [%s] ', 0.24)
    return cp

def ask_cv():
    cv = prompt('Cv(Specific Heat at Constant Volume) Btu/lbm F [%s] ', 0.1715)
    return cv

def ask_adiabatic_ratio():
    cp = ask_cp()
    cv = ask_cv()
    k = calc_adiabatic_ratio(cp, cv)
# let the user modify it, if so desired.
    k = ask_specific_heat_ratio(k)
    print('')
    return cp, cv, k

def ask_moped_rim_size():
    list_moped_rim_sizes()
    rim_inches = prompt('Rim Size in Inches [%s]', 14)
    return rim_inches

def ask_moped_tire_size():
    list_moped_tire_sizes()
    tire_width_inches = prompt('Tire Width Inches [%s]', 2.25)
    return tire_width_inches

def ask_tire_circumference(circ):
    tire_circumference_inches = prompt('Tire Circumference Inches [%s]', circ)
    return tire_circumference_inches

def horsepower_torque_from_mep(mep, sv, rpm, cycles):
    hp = mep_to_hp(mep, sv, rpm, cycles)
    list_peak_hp_rpms()
    print('')
    display_hp('\nHorsepower', hp)
    display_hp_per_liter('\nHorsepower per liter', hp, sv)
    torque = hp_to_torque(hp, rpm)
    display_energy('\nTorque', torque)

def mep_from_horsepower(hp, sv, rpm, cycles):
    mep = hp_to_mep(hp, sv, rpm, cycles)
    display_mep('BMEP', psi_to_kPa(mep))

def rpm_from_hp_and_mep(hp, mep, sv, cycles):
    rpm = hp_and_mep_to_rpm(hp, mep, sv, cycles)
    display_angular_velocity('RPM', rpm)

def sv_from_hp_mep_and_rpm(hp, mep, rpm, cycles):
    cc = hp_and_mep_to_sv(hp, mep, rpm, cycles)
    display_volume('Displacement per Cylinder', cc)

def prompt_bhp_from_bmep():
    print('\nCompute Brake Horsepower from BMEP\n')
    cycles   = ask_cycles()
    sv       = ask_displacement()
    rpm      = ask_rpm()
    mep      = ask_mep()
    horsepower_torque_from_mep(mep, sv, rpm, cycles)

def prompt_bmep_from_bhp():
    print('\nCompute BMEP from Brake Horsepower\n')
    cycles   = ask_cycles()
    sv       = ask_displacement()
    rpm      = ask_rpm()
    hp       = ask_hp()
    mep_from_horsepower(hp, sv, rpm, cycles)

def prompt_rpm_from_bmep_and_bhp():
    print('\nCompute RPM needed given BMEP and HP\n')
    cycles   = ask_cycles()
    sv       = ask_displacement()
    hp       = ask_hp()
    mep      = ask_mep()
    rpm_from_hp_and_mep(hp, mep, sv, cycles)

def prompt_sv_from_hp_mep_and_rpm():
    print('\nCompute Swept Volume (Displacement) needed given BMEP, HP and RPM\n')
    cycles   = ask_cycles()
    hp       = ask_hp()
    mep      = ask_mep()
    rpm      = ask_rpm()
    sv_from_hp_mep_and_rpm(hp, mep, rpm, cycles)

def display_cylinder_pressures_and_temperatures(p1kPa, t1C, qpri, cr, cv, k):
    display_pressure('Cylinder Pressure at Intake Close', p1kPa)
    display_temperature('Mixture Temperature at Intake Close', t1C)
    p2kPa = p1kPa * math.pow(cr_guard(cr), k)
    t2C = kelvin_to_celsius(celsius_to_kelvin(t1C)* (p2kPa/(cr_guard(cr)*p1kPa)) )
    display_pressure('Cylinder Pressure at Peak Compression', p2kPa)
    display_temperature('Mixture Temperature at Peak Compression', t2C)
    t1r = celsius_to_rankine(t1C)
    t2r = celsius_to_rankine(t2C)
    t3r = t2r + qpri/cv
    t4r = t1r * (t3r/t2r)
    p3kPa = p2kPa * (t3r/t2r)
    p4kPa = p3kPa * math.pow(1/cr_guard(cr),k)
    display_pressure('Cylinder Pressure at Combustion', p3kPa)
    display_temperature('Cylinder Temperature at Combustion',
            rankine_to_celsius(t3r))
    display_pressure('Cylinder Pressure at Exhaust', p4kPa)
    display_temperature('Cylinder Temperature at Exhaust',
            rankine_to_celsius(t4r))

def prompt_air_cycle():
    print('\nCharles Fayette Taylor Air Cycle Computation of HP\n')
    print('First we can calculate Mean Effective Pressure independent')
    print('of the geometry, just from thermodynamics\n')
# *** First ***
# Things we can know without bore, stroke, displacement, cycles, etc.
# ie Thermodynamics Intrinsic calculations
    cp, cv, k = ask_adiabatic_ratio()
    presskPa  = ask_baro_pressure()
    inTempC   = ask_air_temperature('Intake Air Temperature', 100)
    boostkPa  = ask_boost()
# if we have a supercharger or turbocharger
    if (boostkPa > 0):
        comp_efficiency = ask_comp_efficiency()
        display_pressure('Total Boost', presskPa + boostkPa)
        display_ratio('Pressure Ratio', (presskPa + boostkPa) / too_small_guard( presskPa))
        inTempC = calc_boost_temperature(inTempC, k, presskPa, presskPa + boostkPa, comp_efficiency)
        display_temperature('Post Boost Temperature', inTempC)
        presskPa += boostkPa
    cr       = ask_compression_ratio()
    btuslb   = ask_fuel_specific_energy_btus_per_lb()
    stoich   = ask_fuel_air_ratio()
    voleff   = ask_volumetric_eff()
    scarat   = ask_scavange_ratio(cr)
    qpri     = ask_heat_added_per_unit_mass_gas(btuslb,stoich,scarat) * voleff
    thermeff = calc_thermal_efficiency(cr, k)
    display_thermal_efficiency('Thermal Efficiency', thermeff)
    a        = calc_a(qpri, cv, inTempC)
    print("Q' / (T1 * Cv)          : ", a)
    print('')
    mep      = calc_mep(a, thermeff, k, cr, presskPa)
    mecheff  = ask_overall_mechanical_efficiency()
    display_mep('\nCalculated Mean Effective Pressure before efficiency', psi_to_kPa(mep))
    imep     = calc_indicated_mep(mecheff, mep)
    display_mep('\nIndicated  Mean Effective Pressure', psi_to_kPa(imep))
    display_cylinder_pressures_and_temperatures(presskPa, inTempC, qpri, cr, cv, k)
# *** Next ***
# Things we need bore, stroke, cycles, etc.
# ie Thermodynamics Extrinsic calculations
    ask_extrinsic_outcome(imep, voleff)

#
# Once we have the thermodynamic intrinsics calculations, we can do other
# calculations:
# - calculate the necessary RPM needed for a specifc horsepower
# - calculate the CFM required for a specific horsepower
#
def ask_extrinsic_outcome(imep, voleff):
    display_mep('\nCurrent Indicated Mean Effective Pressure', psi_to_kPa(imep))
    choice = ''
    while choice.strip() != 'x':
        print('\nBMEP Menu')
        print('1. Find HP from Displacement, Cycles and RPM')
        print('2. Find RPM from Cycles, Displacement and HP')
        print('3. Find Displacement from HP, Cycles and RPM')
        print('4. Find Intake CFM from IMEP, Displacement, Cycles and RPM')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            cycles   = ask_cycles()
            sv       = ask_displacement()
            rpm      = ask_rpm()
            cfm      = calc_cubic_feet_per_min(sv, rpm, cycles, voleff)
            display_volumetric_capacity('Intake CFM, Cubic Feet per Minute', per_min_to_per_sec(cf_to_cc(cfm)))
            horsepower_torque_from_mep(imep, sv, rpm, cycles)
        if choice == '2':
            cycles   = ask_cycles()
            sv       = ask_displacement()
            hp       = ask_hp()
            rpm_from_hp_and_mep(hp, imep, sv, cycles)
        if choice == '3':
            cycles   = ask_cycles()
            hp       = ask_hp()
            rpm      = ask_rpm()
            sv_from_hp_mep_and_rpm(hp, imep, rpm, cycles)
        if choice == '4':
            cycles   = ask_cycles()
            sv       = ask_displacement()
            rpm      = ask_rpm()
            cfm      = calc_cubic_feet_per_min(sv, rpm, cycles, voleff)
            display_volumetric_capacity('Intake CFM, Cubic Feet per Minute', per_min_to_per_sec(cf_to_cc(cfm)))

def prompt_mean_piston_speed_from_rpm():
    print('\nMean Piston Speed from RPM')
    stroke = ask_stroke()
    rpm = ask_rpm()
    mps = calc_mean_piston_speed_from_rpm(stroke, rpm)
    display_mean_piston_speed('Mean Piston Speed', mps)

def prompt_rpm_from_mean_piston_speed():
    print('\nRPM from Mean Piston Speed')
    stroke = ask_stroke()
    mps = ask_mean_piston_speed()
    rpm = calc_rpm_from_mean_piston_speed(stroke, mps)
    display_angular_velocity('RPM', rpm)

def prompt_carb_size():
    print('\nJennings Carb Sizing')
    cycles = ask_cycles()
    sv     = ask_displacement()
    rpm    = ask_rpm()
    voleff = ask_volumetric_eff()
    cfm    = calc_cubic_feet_per_min(sv, rpm, cycles, voleff)
    display_volumetric_capacity('Intake CFM, Cubic Feet per Minute', per_min_to_per_sec(cf_to_cc(cfm)))
    numcarbs = prompt('Number of Carbs or Venturis [%s]', 1)
    print('Min  Carb Bore ', calc_carb_size(0.65, sv, numcarbs, rpm))
    print('Safe Carb Bore ', calc_carb_size(0.80, sv, numcarbs, rpm))
    print('Max  Carb Bore ', calc_carb_size(0.90, sv, numcarbs, rpm))

def prompt_scooter_mph_from_hp():
    print('\nCalculate Possible Max Scooter MPH from HP')
    # 
    # This all got started when I was looking at a modern scooter and they
    # advertised 3 ft-lbs of torque as the only motor spec.  This felt like not
    # enough, so the question was how fast could you go on a scooter with only
    # 3 ft-lbs of torque.
    #
    # There are two major parts of the puzzle, rolling resistance and
    # aerodynamic drag. Rolling resistance is the major factor at low speed and
    # a small component at high speed, but at the speeds we see for a scooter,
    # we have to consider both.
    #
    # Not much info on rolling resistance and the coefficient of drag in
    # scooters, but, there is a good bit of info about cycling drag on bicycles
    # and electric motorcycles. From Wikipedia [1], the drag equation is
    #
    # Fd = 1/2 * p * v^2 Cd * A
    #
    # where:
    # Fd: drag force
    # p: mass density of the fluid
    # v: is the flow speed of the object retative to the fluid, the velocity
    # A: is the reference area
    # 
    # [1]: https://en.wikipedia.org/wiki/Drag_coefficient
    #
    # Right now, the suggested values are garbage, but I have a plan for that
    # I have captured pictures to measure the frontal area of me ridding the
    # scooter.
    #
    # For rolling resistance, I am going to make multiple runs, doing a throttle chop
    # at 5, 10, 15, and 20 MPH and measure the distance I coast until it stops moving.
    #
    # From https://visforvoltage.org/forum-topic/general/526-horsepower-calculations
    #
    # Following is from Bidwell's "Secrets of El Ninja":
    # Force required = Cr x Wt + (Cd x A x V^2)/391
    # This is assuming a flat surface and steady speed and zero relative wind. Using what you have, and integrating with #s provided by Bidwell...
    # Cr: Rolling resistance factor = .015
    # Wt: Weight in pounds = 100 + [your weight] = 250 lbs
    # Cd: coefficient of drag = .77 (for unfaired recumbent bicycle)
    # A: Area = 4 square feet (just a guss)
    # V: Velocity in mph = 40
    # Force Required = (.015 x 250 lbs) + (.77 x 4 x 1600)/(391) = 16.35
    # I think the unit for force is pounds.
    # Pick say an arbitrary wheel size of 1 ft, then the torque required would be 16.35 ft lbs. Given 40 mph, it will need to spin at 560.5 rpm.
    # Following is from http://en.wikipedia.org/wiki/Torque :
    # Power (hp) = (torque (lbf x ft) x angular speed (rpm))/5252 = 1.745 hp or 1301.97 watts.
    # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
    # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
    # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
    Cr = ask_rolling_resistance_factor()
    scooter_newtons = lbs_to_newtons(ask_lbs_mass('Scooter weight in lbs', 100))
    rider_newtons = lbs_to_newtons(ask_lbs_mass('Rider and backpack weight in lbs', 200))
    Cd = ask_coefficient_of_drag()
    A = ask_sq_ft_area('Frontal area in square feet', 6)
    mph = ask_mph('Maximum Velocity', 25)
    rolling_resistance = (Cr * (scooter_newtons + rider_newtons))
    rho = ask_air_density()
    print('Air Density' , rho)
    v = miles_hour_to_meters_sec(mph)
    drag_force = rho * v * v * Cd * feet_to_meters(feet_to_meters(A)) / 2
    force = rolling_resistance + drag_force
    display_force('Rolling Resistance', rolling_resistance)
    display_force('Drag Force ', drag_force)
    display_force('Force required', force)
    # now we need the radius of the wheel for ft-lbs
    circum_inches = prompt_moped_tire_circumference()
    radius_feet = inches_to_feet(calc_geom_radius_from_circumference(circum_inches))
    display_distance('Tire Radius', feet_to_mm(radius_feet))
    torque = newtons_to_lbs(force) * radius_feet
    display_energy('Torque', torque)
    # We know torque, we know RPM, therefore, we know HP, HP = Force * Velocity
    watts = newtons_and_meters_per_sec_to_watts(force, v)
    hp = watts_to_imperial_hp(watts)
    display_hp('Horsepower', hp)
    ratio = ask_gear_ratio()
    rpm = calc_nc50_rpm(ratio, circum_inches, mph)
    display_angular_velocity('RPM',rpm)
    # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
    # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
    # XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX

# This is a calculation of the maximum mass flow through a carb,
# through a venturi. This happens when the speed of the fluid, air,
# through the venturi approachs the speed sound.
def prompt_carb_mass_flow():
    print('\nCompute Max Mass Flow through a Carb')
    bore            = ask_carb_bore()
    AT              = calc_geom_area_of_circle(bore)
    display_area('\nArea of Carb Bore', AT)
    manifold_bore   = ask_manifold_bore()
    Aref            = calc_geom_area_of_circle(manifold_bore)
    display_area('\nArea of Manifold Bore', Aref)
    Cd              = estimate_Cd(AT, Aref)
    print('\nEstimate of Coefficient of Discharge : ', Cd, '\n')
    presskPa        = ask_baro_pressure()
    cp, cv, k       = ask_adiabatic_ratio()
    inTempC         = ask_air_temperature('Intake Air Temperature', 100)
    pT              = choked_throat_pressure(presskPa, k)
    display_pressure('\nChoked Throat Pressure', pT)
    print('\nCritical Pressure Ratio: ', pT / too_small_guard(presskPa))
    # convert to SI units
    AT              = mm_to_meters(mm_to_meters(AT))
    p0              = kPa_to_Pa(presskPa)
    pT              = kPa_to_Pa(pT)
    T0              = celsius_to_kelvin(inTempC)
    flow_kg_per_sec = flow_through_venturi(Cd, AT, p0, pT, k, T0)
    print('\nFlow in Kg per Second  : ', flow_kg_per_sec)

def prompt_bore_stroke():
    print('\nDisplacement')
    bore = ask_bore()
    stroke = ask_stroke()
    crl = ask_connecting_rod_length()
    display_ratio('Ratio of Bore to Stroke', bore / too_small_guard(stroke))
    display_ratio('Ratio of Connecting Rod Length to Crank Radius', crl / too_small_guard(calc_crank_radius(stroke)))
    display_ratio('Ratio of Connecting Rod Length to Stroke      ', crl / too_small_guard(stroke))
    cc = calc_displacement(bore, stroke, 1)
    display_volume('Displacement per Cylinder', cc)
    cyl = ask_cylinders()
    cc = calc_displacement(bore, stroke, cyl)
    display_volume('Displacement', cc)
    return cc

def prompt_swept_volume():
    cc = prompt('calc_displacement (Swept Volume) in cc [%s]', 250)
    display_volume('Displacement', cc)
    return cc

def prompt_squish_ratio():
    print('\nSquish Area Ratio')
    bore = ask_bore()
    bowl = ask_cylinder_head_bowl_diameter()
    ratio = calc_squish_area_ratio(bore, bowl)
    display_ratio('Squish Area Ratio', ratio)

def prompt_trapped_compression_ratio():
    print('\Trapped Compression Ratio')
    sv = ask_displacement()
    crl = ask_connecting_rod_length()
    epo = ask_exhaust_port_open()
    print('Not Done Yet, More Code to Write')

def prompt_connecting_rod():
    print('\nFind Connnecting Rod Length')
    upper_bearing_diameter = ask_diameter('Upper Bearing', 20)
    lower_bearing_diameter = ask_diameter('Lower Bearing', 29.5)
    length = ask_length('Distance from top of upper bearing to bottom of lower bearing', 104.75)
    length = length - ((upper_bearing_diameter / 2) + (lower_bearing_diameter / 2))
    display_distance('Connecting Rod Length', length)
    display_distance('Crank Radius', calc_crank_radius(length))

def prompt_piston_position(title):
    print(title)
    stroke = ask_stroke()
    crl = ask_connecting_rod_length()
    a = ask_crank_angle_atdc()
    d = calc_piston_position_from_angle(crl, stroke, math.radians(a))
    display_distance('Distance from Top of Stroke', d)
    return d

def prompt_piston_pos_from_crank_angle():
    prompt_piston_position('\nFind Piston Position from Crank Angle')

def prompt_piston_angle():
    print('\nFind Crank Angle Before or After Top Dead Center')
    stroke = ask_stroke()
    crl = ask_connecting_rod_length()
    dftdc = ask_length('Distance from Top Dead Center', 0)
    angle = calc_angle_from_piston_position(crl, stroke, dftdc)
    display_angle('Angle Before or After Top Dead Center', math.degrees(angle))

def prompt_moped_tire_circumference():
    rim_inches = ask_moped_rim_size()
    tire_width_inches = ask_moped_tire_size()
    circum_inches = calc_geom_circumference(rim_inches + 2 * tire_width_inches)
    circum_inches = ask_tire_circumference(circum_inches)
    display_distance('Tire Circumference', inches_to_mm(circum_inches))
    return circum_inches

def prompt_nc50_mph():
    print('\nNC50 MPH from RPM')
    circum_inches = prompt_moped_tire_circumference()
    rpm = prompt('RPM [%s]', 10000.0)
    ratio = ask_gear_ratio()
    mph = calc_nc50_mph(ratio, circum_inches, rpm)
    display_velocity('Velocity', miles_hour_to_meters_sec(mph))

def prompt_nc50_rpm():
    print('\nNC50 RPM from MPH')
    circum_inches = prompt_moped_tire_circumference()
    mph = prompt('MPH [%s]', 40.0)
    ratio = ask_gear_ratio()
    display_angular_velocity('RPM',calc_nc50_rpm(ratio, circum_inches, mph))

def prompt_tuned_rpm():
    print('Tuned RPM for Expansion Chamber')
    epo = ask_exhaust_port_open()
    list_exhaust_temperatures()
    T  = prompt('Temperature of Exhaust Gas degC [%s]', 400)
    ws = prompt('Exhaust Wave Speed in m/s       [%s]',
            calc_vel_sound_perfect_gas(1.343, T, 29.0))
    tl = ask_length('Tuned Length', 740)
    display_angular_velocity('RPM',calc_tuned_rpm(epo, ws, tl))

def prompt_tuned_length():
    print('Tuned Length for Expansion Chamber, given RPM')
    epo = ask_exhaust_port_open()
    list_exhaust_temperatures()
    T  = prompt('Temperature of Exhaust Gas degC [%s]', 400)
    ws = prompt('Exhaust Wave Speed in m/s       [%s]',
            calc_vel_sound_perfect_gas(1.343, T, 29.0))
    rpm = ask_rpm()
    len = calc_tuned_length(epo, ws, rpm)
    display_distance('', len)

def prompt_speed_sound():
    list_speed_of_sound()
    print('Speed of Sound in an Ideal Gas')
    cp, cv, k = ask_adiabatic_ratio()
    T = prompt('Temperature of Gas degC [%s]', 100)
    print('28.95 - Dry Air')
    print('29.00 - Exhaust')
    m = prompt('Molecular Mass of Gas [%s]', 28.95)
    display_velocity('Speed of Sound', calc_vel_sound_perfect_gas(k, T, m))

def prompt_ft_lbs_force():
    ft_lbs_force = ask_ft_lbs_force()
    display_energy('Energy', ft_lbs_force)

def prompt_btus():
    btus = ask_btus()
    display_energy('Energy', btus_to_ft_lbs(btus))

def prompt_newtons_meters_force():
    newton_meters = ask_newton_meters_force()
    display_energy('Energy', newton_m_to_ft_lbs(newton_meters))

def prompt_btus_per_lb_specific_energy():
    btus_per_lb = ask_fuel_specific_energy_btus_per_lb()
    display_specific_energy('Specific Energy',
            btus_per_lb_to_MJ_per_kg(btus_per_lb))

def prompt_MJ_per_kg_specific_energy():
    MJ_per_kg = ask_fuel_specific_energy_MJ_per_kg()
    display_specific_energy('Specific Energy', MJ_per_kg)

def prompt_horsepower():
    hp = ask_hp()
    display_hp('Horsepower', hp)

def prompt_metric_horsepower():
    hp = ask_hp()
    display_hp('Horsepower', metric_hp_to_imperial_hp(hp))

def prompt_watts():
    watts = ask_watts()
    display_hp('Horsepower', watts_to_imperial_hp(watts))

def prompt_kilowatts():
    kilowatts = ask_kilowatts()
    display_hp('Horsepower', kilowatts_to_imperial_hp(kilowatts))

def prompt_ft_lbs_per_sec():
    ft_lbs_per_sec = ask_ft_lbs_per_sec()
    display_hp('Horsepower', ft_lbs_per_sec_to_imperial_hp(ft_lbs_per_sec))

def prompt_ft_lbs_per_min():
    ft_lbs_per_min = ask_ft_lbs_per_min()
    display_hp('Horsepower', ft_lbs_per_min_to_imperial_hp(ft_lbs_per_min))

def prompt_kg_m_per_sec():
    kg_m_per_sec = ask_kg_m_per_sec()
    display_hp('Horsepower', kg_m_per_sec_to_imperial_hp(kg_m_per_sec))

def prompt_btus_per_hour():
    btus_per_hour = ask_btus_per_hour()
    display_hp('Horsepower', btus_per_hour_to_imperial_hp(btus_per_hour))

def prompt_port_segment():
    bore = ask_bore()
    segment_length = ask_arc_segment_length('Port Segment Length', 20)
    display_distance('Chord Length',
            calc_geom_chord_from_arc_length(segment_length,
                bore / 2))

def bmep_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nBMEP Menu')
        print('1. Find HP from BMEP')
        print('2. Find BMEP from HP')
        print('3. Find RPM given HP, BMEP, Displacement, and Cycles')
        print('4. Find Displacement given HP, BMEP, RPM and Cycles')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            prompt_bhp_from_bmep()
        if choice == '2':
            prompt_bmep_from_bhp()
        if choice == '3':
            prompt_rpm_from_bmep_and_bhp()
        if choice == '4':
            prompt_sv_from_hp_mep_and_rpm()

def horsepower_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nHorsepower Menu')
        print('1. Convert Horsepower')
        print('2. Convert Metric Horsepower')
        print('3. Convert Watts')
        print('4. Convert KiloWatts')
        print('5. Convert Foot Lbs  per Second')
        print('6. Convert Foot Lbs  per Minute')
        print('7. Convert KG Meters per Second')
        print('8. Convert BTUs per Hour')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            prompt_horsepower()
        if choice == '2':
            prompt_metric_horsepower()
        if choice == '3':
            prompt_watts()
        if choice == '4':
            prompt_kilowatts()
        if choice == '5':
            prompt_ft_lbs_per_sec()
        if choice == '6':
            prompt_ft_lbs_per_min()
        if choice == '7':
            prompt_kg_m_per_sec()
        if choice == '8':
            prompt_btus_per_hour()

def ideal_gas_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nIdeal Gas Menu')
        print('1. Speed Sound in an Ideal Gas')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            prompt_speed_sound()

def ask_bore_stroke_or_swept_volume():
    choice = ''
    while (choice.strip() != 'b') and (choice.strip() != 'd'):
        print('\nChoose Displacement Calculation')
        print('b. Bore - Stroke - Cyl')
        print('d. Final Displacement (Swept Volume)')
        choice = selection()
        print('Choice is - ', choice)
    return choice.strip()

def ask_displacement():
    choice = ask_bore_stroke_or_swept_volume()
    if (choice == 'b'):
        disp = prompt_bore_stroke()
    else:
        disp = volume_menu()
    print('')
    return disp

def oil_ratio_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nOil Ratio Menu')
        print('1. Find Oil Ratio from Gallons of Gas and Ounces of Oil')
        print('2. Find Ounces of Oil from Gallons of Gas and Oil Ratio')
        print('3. Find Gallons of Gas from Ounces of Oil and Oil Ratio')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            gallons_of_gas = prompt('Gallons of Gas [%s]', 5)
            ounces_of_oil = prompt('Ounces of Oil [%s]', 16)
            print('Oil Ratio : ', calc_oil_ratio(gallons_of_gas, ounces_of_oil), 'to 1')
        if choice == '2':
            gallons_of_gas = prompt('Gallons of Gas [%s]', 5)
            oil_ratio = prompt('Oil Ratio [%s]', 40)
            print('Ounces of Oil : ', calc_oil_ounces_from_gallons_gas_and_ratio(gallons_of_gas, oil_ratio))
        if choice == '3':
            ounces_of_oil = prompt('Ounces of Oil [%s]', 16)
            oil_ratio = prompt('Oil Ratio [%s]', 40)
            print('Gallons of Gas : ', calc_gallons_of_gas_from_oil_ounces_ratio(ounces_of_oil, oil_ratio))

def distance_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nDistance Menu')
        print('1. Convert Feet')
        print('2. Convert Inches')
        print('3. Convert Millimeters')
        print('4. Convert Yards')
        print('5. Convert Miles')
        print('6. Convert Kilometers')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            feet = prompt('Feet [%s]', 1)
            display_distance('', feet_to_mm(feet))
        if choice == '2':
            inches = prompt('Inches [%s]', 1)
            display_distance('', inches_to_mm(inches))
        if choice == '3':
            mm = prompt('Millimeters [%s]', MM_PER_INCH)
            display_distance('', mm)
        if choice == '4':
            yards = prompt('Yards [%s]', YARDS_PER_MILE)
            display_distance('', yards_to_mm(yards))
        if choice == '5':
            miles = prompt('Miles [%s]', 1)
            display_distance('', miles_to_mm(miles))
        if choice == '6':
            km = prompt('Kilometers [%s]', 1)
            display_distance('', km_to_mm(km))

def area_menu():
    choice = ''
    sq_mm = 1
    while choice.strip() != 'x':
        print('\nArea Menu')
        print('1. Convert Square Feet')
        print('2. Convert Square Inches')
        print('3. Convert Square Millimeters')
        print('4. Convert Square Meters')
        print('5. Convert Square Kilometers')
        print('6. Convert Square Yards')
        print('7. Convert Square Miles')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            feet = prompt('Square Feet [%s]', 1)
            sq_mm = sq_feet_to_sq_mm(feet)
            display_area('', sq_mm)
        if choice == '2':
            sq_inches = prompt('Square Inches [%s]', 1)
            sq_mm = sq_inches_to_sq_mm(sq_inches)
            display_area('', sq_mm)
        if choice == '3':
            sq_mm = prompt('Square Millimeters [%s]', 1)
            display_area('', sq_mm)
        if choice == '4':
            sq_m = prompt('Square Meters [%s]', 1)
            sq_mm = sq_m_to_sq_mm(sq_m)
            display_area('', sq_mm)
        if choice == '5':
            sq_km = prompt('Square Kilometers [%s]', 1)
            sq_mm = sq_km_to_sq_mm(sq_km)
            display_area('', sq_mm)
        if choice == '6':
            sq_yards = prompt('Square Yards [%s]', 1)
            sq_mm = sq_yards_to_sq_mm(sq_yards)
            display_area('', sq_mm)
        if choice == '7':
            sq_miles = prompt('Square Miles [%s]', 1)
            sq_mm = sq_miles_to_sq_mm(sq_miles)
            display_area('', sq_mm)
    return sq_mm

def velocity_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nVelocity Menu')
        print('1. Convert Meters/Second (m/s)')
        print('2. Convert Feet/Second')
        print('3. Convert Feet/Minute')
        print('4. Convert Kilometers/Hour (kph)')
        print('5. Convert Miles/Hour (mph)')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            meters_sec = prompt('Meters/Second (m/s) [%s]', 10)
            display_velocity('', meters_sec)
        if choice == '2':
            feet_sec = prompt('Feet/Second [%s]', 88)
            display_velocity('', feet_sec_to_meters_sec(feet_sec))
        if choice == '3':
            feet_min = prompt('Feet/Minute [%s]', 4000)
            display_velocity('', feet_min_to_meters_sec(feet_min))
        if choice == '4':
            km_hour = prompt('Kilometers/Hour (kph) [%s]', 100)
            display_velocity('', km_hour_to_meters_sec(km_hour))
        if choice == '5':
            mph = prompt('Miles/Hour (mph) [%s]', 60)
            display_velocity('', miles_hour_to_meters_sec(mph))

def angular_velocity_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nAngular Velocity Menu')
        print('1. Convert Revolutions/Minute (RPM)')
        print('2. Convert Revolutions/Second (RPS or Hz)')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            rpm = prompt('Revolutions/Minute (RPM) [%s]', 10000)
            display_angular_velocity('', rpm)
        if choice == '2':
            rps = prompt('Revolutions/Minute (RPS or Hz) [%s]', 50.0/3.0)
            display_angular_velocity('', rps_to_rpm(rps))

def volume_menu_print():
        print('1. Convert Cubic Centimeters')
        print('2. Convert Cubic Inches')
        print('3. Convert Cubic Feet')
        print('4. Convert Liters')

def volume_menu():
    choice = ''
    cc = 1
    while choice.strip() != 'x':
        print('\nVolume Menu')
        volume_menu_print()
        print('x. Exit')
        choice = selection()
        if choice == '1':
            cc = prompt('Cubic Centimeters, CCs, [%s]', 250)
            display_volume('', cc)
        if choice == '2':
            ci = prompt('Cubic Inches, CI, [%s]', 302)
            cc = ci_to_cc(ci)
            display_volume('', cc)
        if choice == '3':
            cf = prompt('Cubic Feet, CF, [%s]', 1)
            cc = cf_to_cc(cf)
            display_volume('', cc)
        if choice == '4':
            liters = prompt('Liters [%s]', 1)
            cc = liters_to_cc(liters)
            display_volume('', cc)
    return cc

def mass_menu_print():
    print('1. Convert Pounds')
    print('2. Convert Kilograms')

def mass_menu():
    choice = ''
    kg = 1
    while choice.strip() != 'x':
        print('\nMass Menu')
        mass_menu_print()
        print('x. Exit')
        choice = selection()
        if choice == '1':
            m = prompt('Pounds, [%s]', 100)
            kg = lbs_to_kg(m)
            display_mass('', kg)
        if choice == '2':
            kg = prompt('Kilograms, [%s]', 100)
            display_mass('', kg)
    return kg

def liquid_capacity_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nVolume Menu')
        volume_menu_print()
        print('5. Convert Gallons')
        print('6. Convert Quarts')
        print('7. Convert Pints')
        print('8. Convert Fluid Ounces')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            cc = prompt('Cubic Centimeters, CCs, [%s]', 250)
            display_liquid_capacity('', cc)
        if choice == '2':
            ci = prompt('Cubic Inches, CI, [%s]', 302)
            display_liquid_capacity('', ci_to_cc(ci))
        if choice == '3':
            cf = prompt('Cubic Feet, CF, [%s]', 1)
            display_liquid_capacity('', cf_to_cc(cf))
        if choice == '4':
            liters = prompt('Liters [%s]', 1)
            display_liquid_capacity('', liters_to_cc(liters))
        if choice == '5':
            gallons = prompt('Gallons [%s]', 1)
            display_liquid_capacity('', us_liquid_gallons_to_cc(gallons))
        if choice == '6':
            quarts = prompt('Quarts [%s]', 4)
            display_liquid_capacity('', quarts_to_cc(quarts))
        if choice == '7':
            pints = prompt('Pints [%s]', 8)
            display_liquid_capacity('', pints_to_cc(pints))
        if choice == '8':
            fluid_ounces = prompt('Fluid Ounces [%s]', 128)
            display_liquid_capacity('', fluid_ounces_to_cc(fluid_ounces))

def temperature_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nTemperature Menu')
        print('1. Convert Celsius')
        print('2. Convert Fahrenheit')
        print('3. Convert Kelvin')
        print('4. Convert Rankine')
        print('x. Exit')
        choice = selection()
        if choice == '1':
            temp = prompt('Celsius Temperature [%s]', 100.0)
            display_temperature('', temp)
        if choice == '2':
            temp = prompt('Fahrenheit Temperature [%s]', 100.0)
            display_temperature('', fahrenheit_to_celsius(temp))
        if choice == '3':
            temp = prompt('Kevin Temperature [%s]', 273.15)
            display_temperature('', kelvin_to_celsius(temp))
        if choice == '4':
            temp = prompt('Rankine Temperature [%s]', 459.67)
            display_temperature('', rankine_to_celsius(temp))

def pressure_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nPressure Menu')
        print('1. Convert Bar')
        print('2. Convert PSI')
        print('3. Convert kPa')
        print('4. Convert Pascals')
        print('5. Convert torr')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            bar = prompt('Bar [%s]', 20.0)
            display_pressure('', bar_to_kPa(bar))
        if choice == '2':
            psi = prompt('PSI [%s]', 100.0)
            display_pressure('', psi_to_kPa(psi))
        if choice == '3':
            kPa = prompt('KiloPascals [%s]', 1.0)
            display_pressure('', kPa)
        if choice == '4':
            Pa = prompt('Pascals [%s]', 1000.0)
            display_pressure('', Pa_to_kPa(Pa))
        if choice == '5':
            torr = prompt('Torr [%s]', 1.0)
            display_pressure('', torr_to_kPa(torr))

def mean_piston_speed_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nMean Piston Speed Menu')
        print('1. Calculate Mean Piston Speed from RPM')
        print('2. Calculate RPM from Mean Piston Speed')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            prompt_mean_piston_speed_from_rpm()
        if choice == '2':
            prompt_rpm_from_mean_piston_speed()

def energy_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nEnergy (Torque) Menu')
        print('1. Convert Ft-Lbs of Force')
        print('2. Convert Newtons/Meters of Force')
        print('3. Convert BTUs')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            prompt_ft_lbs_force()
        if choice == '2':
            prompt_newtons_meters_force()
        if choice == '3':
            prompt_btus()

def specific_energy_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nSpecific Energy Menu')
        print('1. Convert BTUs/lb')
        print('2. Convert MJ/kg')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            prompt_btus_per_lb_specific_energy()
        if choice == '2':
            prompt_MJ_per_kg_specific_energy()

def port_mapping_menu():
    choice = ''
    while choice.strip() != 'x':
        print('\nPort Mapping Menu')
        print('1. Port Segment Measurement')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            prompt_port_segment()

def prompt_cr_w_cyl_wall_ports():
    print('CR = (Swept_Volume + Clearance_Volume) / Clearance_Volume')
    print(' or ')
    print('CR = Maximum Cylinder Volume / Minimum Cylinder Volume')
    print('With Cylinder Wall Ports, there are two Compression Ratios')
    print('to consider. The static compression ratio which is from the')
    print('point where the exhaust port fully closes to top dead center.')
    print('The full compression ratio from the bottom of the exhaust')
    print('port opening to top dead center. This assumes that at maximum')
    print('efficiency, the exhaust pipe reflection will be able to fully')
    print('plug the exhaust port on the compression stroke.')
    clear_vol = ask_clearance_volume()
    display_volume('Clearance Volume', clear_vol)
    bore = ask_bore()
    stroke = ask_stroke()
    display_ratio('\nRatio of Bore to Stroke', bore / too_small_guard(stroke))
    crl = ask_connecting_rod_length()
    epo = ask_exhaust_port_open()
    epc = ask_exhaust_port_close()
    d = calc_piston_position_from_angle(crl, stroke, math.radians(epo))
    print('\nStroke Length for Static Compression : ', d)
    cc = calc_displacement(bore, d, 1)
    print('\nStatic Compression Ratio : ',(cc + clear_vol)/too_small_guard(clear_vol))
    d = calc_piston_position_from_angle(crl, stroke, math.radians(epc))
    cc = calc_displacement(bore, d, 1)
    print('Full   Compression Ratio : ',(cc + clear_vol)/too_small_guard(clear_vol))

def prompt_cr_wo_cyl_wall_ports():
    print('CR = (Swept_Volume + Clearance_Volume) / Clearance_Volume')
    print(' or ')
    print('CR = Maximum Cylinder Volume / Minimum Cylinder Volume')
    clear_vol = ask_clearance_volume()
    display_volume('Clearance Volume', clear_vol)
    disp = ask_displacement()
    print('Compression Ratio : ', (disp + clear_vol) / too_small_guard(clear_vol))

def prompt_compression_ratio():
    choice = ''
    while choice.strip() != 'x':
        print('\nCompression Ratio Menu')
        print('1. With Cylinder Wall Ports')
        print('2. Without Cylinder Wall Ports')
        print('x. Exit')
        choice = selection()
        print('')
        if choice == '1':
            prompt_cr_w_cyl_wall_ports()
        if choice == '2':
            prompt_cr_wo_cyl_wall_ports()

def test_menu():
    pylab.plot([5,6,7,8],[7,3,8,3])
    pylab.show()

choice = ''
while choice.strip() != 'x':
    dispatch = {
            '1'  : ask_displacement,
            '2'  : prompt_air_cycle,
            '3'  : prompt_nc50_mph,
            '4'  : prompt_nc50_rpm,
            '5'  : prompt_tuned_rpm,
            '6'  : prompt_tuned_length,
            '7'  : mean_piston_speed_menu,
            '8'  : prompt_carb_size,
            '9'  : prompt_carb_mass_flow,
            '10' : prompt_squish_ratio,
            '11' : prompt_connecting_rod,
            '12' : prompt_piston_pos_from_crank_angle,
            '13' : prompt_piston_angle,
            '14' : prompt_compression_ratio,
            '15' : oil_ratio_menu,
            '16' : port_mapping_menu,
            '17' : prompt_scooter_mph_from_hp,
            'A'  : area_menu,
            'a'  : angular_velocity_menu,
            'b'  : bmep_menu,
            'd'  : distance_menu,
            'e'  : energy_menu,
            'h'  : horsepower_menu,
            'i'  : ideal_gas_menu,
            'l'  : liquid_capacity_menu,
            'm'  : mass_menu,
            'p'  : pressure_menu,
            's'  : specific_energy_menu,
            't'  : temperature_menu,
            'v'  : velocity_menu,
            'w'  : volume_menu,
            'z'  : test_menu
            }
    print('\nMenu')
    print(' 1. Calculate Displacement')
    print(' 2. Air Cycle')
    print(' 3. NC50 MPH from RPM')
    print(' 4. NC50 RPM from MPH')
    print(' 5. Find Tuned RPM of Exhaust')
    print(' 6. Find Tuned Length of Exhaust')
    print(' 7. Mean Piston Speed')
    print(' 8. Carb Sizing')
    print(' 9. Carb Mass Flow')
    print('10. Cylinder Head Squish Ratio')
    print('11. Find Connecting Rod Length')
    print('12. Find Piston Position from Angle')
    print('13. Find Crank Angle from Piston Position')
    print('14. Find Compression Ratio')
    print('15. Oil Ratio Mixture')
    print('16. Port Mapping')
    print('17. Calculate Scooter MPH from HP')
    print(' A. Convert Area')
    print(' a. Convert Angular Velocity')
    print(' b. Convert BMEP')
    print(' d. Convert Distance')
    print(' e. Convert Energy (Torque)')
    print(' h. Convert Horsepower (Power)')
    print(' i. Ideal Gas')
    print(' l. Convert Liquid Capacity')
    print(' m. Convert Mass')
    print(' p. Convert Pressure')
    print(' s. Convert Specific Energy')
    print(' t. Convert Temperature')
    print(' v. Convert Velocity')
    print(' w. Convert Volume')
    print(' x. Exit')
    print(' z. Test Something')
    choice = selection()
    if choice in dispatch:
        dispatch[choice]()
print('Done.')

# #!perl
# use strict;
# use Math::Complex;
# use Math::Trig;
# #
# # Supporting subroutines.
# #
#
# # degrees to radians
# sub dtor {
#    my($deg) = @_;
#    return $deg * pi / 180.0;
# }
#
# # radians to degrees
# sub rtod {
#    my($rad) = @_;
#    return $rad * 180.0 / pi;
# }
#
# # piston position
# sub pistPos {
#   my($strokeMeters, $crankMeters, $connRodLenMeters, $rad,
#   	$heightTop, $heightBottom) = @_;
#
#   $$heightTop = $crankMeters + $connRodLenMeters - $crankMeters *
#   	cos($rad) - sqrt($connRodLenMeters * $connRodLenMeters -
# 	($connRodLenMeters * sin($rad)) * ($connRodLenMeters * sin($rad)));
#   $$heightBottom = $strokeMeters - $$heightTop;
# }
#
# sub crankFact {
# # From Page 515 of Blair
# # YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
# my($thisCrank) = @_;
# # CRT = 50
# my($crt) = 50;
# # XCL = 330
# my($xcl) = 330;
# # XCAL = CRT / CRNK
# my($scal) = $crt / $thisCrank;
# # BOR = BO * SCAL / 2;
#
# # XCL = 330
# my($xcl) = 330;
#
# # ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
# # Working Backwords from the end
# # of the Subroutine.....
# # ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
#
#
# # REM VALUES FOR THE SQ VEL PLOT
# # XPLOT = XL3 + 5
# my($xSquishPlotMin) = $xL3 + 5;
# # XSMAX = XPLOT + 150
# # I think here he is just giving some valid range to plot
# my($xSquishPlotMax) = $xSquishPlotMin + 150;
# # XSQ1 = XPLOT
# my($xSquish1) = $xSquishPlotMin;
# # X(1) = XPLOT
# my($xMinPlot) = $xSquishPlotMin;
# # YSQ1 = YET
# my($ySquish1) = $yet;
# # Y(1) = YET
# my($yMinPlot) = $yet;
# # J=1
# my($j) = 1;
# # XV10 = XPLOT + 10 * (XSMAX-XPLOT)/25
# my($xVelocity10Pos) = $xSquishPlotMin+10*($xSquishPlotMax - $xSquishPlotMin)/25;
# # XV20 = XPLOT + 20 * (XSMAX-XPLOT)/25
# my($xVelocity20Pos) = $xSquishPlotMin+20*($xSquishPlotMax - $xSquishPlotMin)/25;
# }
#
# sub getInput {
#    my($bore, $stroke, $connRodLen, $rpm, $exhaustOpen, $trappedCompressionRatio,
# 	$squishClearance, $squishAreaRatio) = @_;
#     print "Enter Bore   Size           in mm  (TRX =  66)   : ";
#     $$bore              = <>;
#
#     if (($$bore eq "") || ($$bore == 0)) {
#    	$$bore = 66;
#     }
#
#     print "Enter Stroke Length         in mm  (TRX =  72)   : ";
#     $$stroke            = <>;
#
#     if (($$stroke eq "") || ($$stroke == 0)) {
#    	$$stroke = 72;
#     }
#
#     print "Enter Connecting Rod Length in mm  (TRX = 125.3) : ";
#     $$connRodLen        = <>;
#
#     if (($$connRodLen eq "") || ($$connRodLen == 0)) {
#     	$$connRodLen = 125.3;
#     }
#
#     print "Enter Engine RPM                   (TRX = 9500)  : ";
#     $$rpm               = <>;
#
#     if (($$rpm eq "") || ($$rpm == 0)) {
#     	$$rpm = 9500;
#     }
#
#     print "Exhaust Port Opens in Degrees ATDC (TRX = 88.5)  : ";
#     $$exhaustOpen       = <>;
#
#     if (($$exhaustOpen eq "") || ($$exhaustOpen == 0)) {
#     	$$exhaustOpen = 88.5;
#     }
#
#     print "Enter Trapped Compression Ratio    (TRX = 8.63)  : ";
#     $$trappedCompressionRatio = <>;
#
#     if (($$trappedCompressionRatio eq "") || ($$trappedCompressionRatio == 0)) {
#     	$$trappedCompressionRatio = 8.63;
#     }
#
#     print "Enter Squish  Area        Ratio    (TRX = 30)    : ";
#     $$squishAreaRatio         = <>;
#
#     if (($$squishAreaRatio eq "") || ($$squishAreaRatio == 0)) {
#     	$$squishAreaRatio = 30;
#     }
#
#     print "Enter Squish  Clearance     in mm  (TRX = 1)     : ";
#     $$squishClearance   = <>;
#
#     if (($$squishClearance eq "") || ($$squishClearance == 0)) {
#     	$$squishClearance = 1;
#     }
#
#     # print "Exhaust Closes    in Degrees BTDC : ";
#     # $exhaustClose      = <>;
#     # print "Piston to Head Clearance    in mm : ";
#     # $squish            = <>;
#     # print "Piston Crown Radius         in mm : ";
#     # $pistonCrownRadius = <>;
#     # print "Squish Band  Radius         in mm : ";
#     # $squishBandRadius  = <>;
#     # print "Bowl Chamber Radius         in mm : ";
#     # $radiusChamber     = <>;
#     # print "Squish Blending Radius      in mm : ";
#     # $radiusSquish      = <>;
#     # print "Squish Area Ratio                 : ";
#     # $$squishAreaRatio   = <>;
# }
#
# sub mainCalc {
#    my($bore, $stroke, $connRodLen, $rpm, $exhaustOpen,
# 		$squishClearance, $trappedCompressionRatio,
# 		$squishAreaRatio) = @_;
#     my($heightTop)               = 0; # height to the top    of the stroke
#     my($heightBottom)            = 0; # height to the bottom of the stroke
#     my($pMax)                    = 1;
#     my($sqVMax)                  = 0;
#     my($sweptVolume)             = 0;
#     my($strokeVolume)            = 0;
#     my($crank)                   = 0;
#     my($crankMeters)             = 0;
#     my($squishClearMeters)       = 0;
#     my($exhaustPortRadians)      = 0;
#     my($heightExhaustOpenTop)    = 0;
#     my($heightExOpenTopMeters)   = 0;
#     my($heightExhaustOpenBot)    = 0;
#     my($heightExOpenBotMeters)   = 0;
#     my($angleDown)               = 0;
#     my($trappedSweptVolume)      = 0;
#     my($clearanceVolume)         = 0;
#     my($areaSquishArea)          = 0;
#     my($bowlArea)                = 0;
#     my($volumeSquishBand)        = 0;
#     my($volumeBowlSquished)      = 0;
#     my($volumeBowl)              = 0;
#     my($depthBowl)               = 0;
#     my($diameterBowl)            = 0;
#     my($volumeSquish1)           = 0;
#     my($volumeBowl1)             = 0;
#     my($volumeCylAtExOpen)       = 0;
#     my($volumeTrapped)           = 0;
#     my($GASR)                    = 0;
#     my($pressureTrapped)         = 0;
#     my($tempatureTrapped)        = 0;
#     my($pressureCylinderPoint1)  = 0;
#     my($tempatureCylinderPoint1) = 0;
#     my($GAMMA)                   = 0;
#     my($massOfTrapped)           = 0;
#     my($pressureSquish1)         = 0;
#     my($pressureBowl1)           = 0;
#     my($tempatureSquish1)        = 0;
#     my($tempatureBowl1)          = 0;
#     my($ratioHeatOfSquish1)      = 0;
#     my($ratioHeatOfBowl1)        = 0;
#     my($massSquish1)             = 0;
#     my($massBowl1)               = 0;
#     my($degreeChange)            = 0;
#     my($deltaTime)             = 0;
#
#     my($boreMeters)       = $bore / 1000.0;
#     my($strokeMeters)     = $stroke / 1000.0;
#     my($connRodLenMeters) = $connRodLen / 1000.0;
#
#     # PA = PI * BOM * BOM / 4
#     print "Bore Meters - $boreMeters\n";
#     my($pistonArea)       = pi * $boreMeters * $boreMeters / 4.0;
#   # print "Squish Area Ratio                  : ";
#     print "Piston Area   in meters squared    : $pistonArea \n";
#
#     # SV = PA * STM
#     $strokeVolume     = $pistonArea * $strokeMeters;
#     print "Stroke Volume in meters cubed      : $strokeVolume \n";
#
#     # CRNK = ST / 2
#     $crank            = $stroke / 2;
#     print "Crank Distance in mm               : $crank \n";
#
#     # CRNKM = CRL / 1000
#     $crankMeters      = $crank / 1000.0;
#     print "Crank Distance   in Meters         : $crankMeters \n";
#
#     # SQM = SQ / 1000
#     $squishClearMeters  = $squishClearance / 1000.0;
#     print "Squish Clearance in Meters         : $squishClearMeters \n";
#
#     # SV = PA * STM
#     $sweptVolume        = $pistonArea * $strokeMeters;
#     print "Swept Volume (in meters cubed)     : $sweptVolume \n";
#     $exhaustPortRadians = &dtor(360 - $exhaustOpen);
#     print "Exhaust Port Radians               : $exhaustPortRadians \n";
#     &pistPos($strokeMeters, $crankMeters, $connRodLenMeters,
#     	$exhaustPortRadians,
#   	\$heightTop, \$heightBottom);
#
#     $heightExOpenTopMeters = $heightTop;
#     $heightExhaustOpenTop  = $heightTop * 1000;
#     print "Piston Height Exhaust Open Top     : $heightExhaustOpenTop\n";
#
#     $heightExOpenBotMeters = $heightBottom;
#     $heightExhaustOpenBot  = $heightBottom * 1000;
#     print "Piston Height Exhaust Open Bottom  : $heightExhaustOpenBot\n";
#
#     $angleDown             = 360 - $exhaustOpen;
#     $trappedSweptVolume    = $pistonArea * $heightExOpenTopMeters;
#     print "Trapped Swept Volume               : $trappedSweptVolume\n";
#     #
#     # We know the volume trapped in the head, the clearance volume,
#     # is the sum of the volume of the bown + the volume of the
#     # squish area. See figure 4.2
#     #
#     # We also know (Trapped Swept Volume + the Clearance Volume)
#     # divided by the Clearance Volume gives us the trapped
#     # compression ratio. In this case we use the trapped
#     # compression ratio as an input, so we calculate the resulting
#     # clearance volume
#     #
#     # TCR = (TSV+CV)/CV -- Solve for CV
#     #
#     # TCR * CV = TSV + CV
#     #
#     # TCR * CV - CV = TSV
#     #
#     # CV = TSV / (TCR - 1)
#     #
#     $clearanceVolume = $trappedSweptVolume / ($trappedCompressionRatio - 1);
#     print "Clearance Volume                   : $clearanceVolume\n";
#
#     # ASQ = PA * SAR
#     $areaSquishArea = $squishAreaRatio * $pistonArea;
#     print "Area of the Squish Area            : $areaSquishArea\n";
#
#     $bowlArea       = $pistonArea - $areaSquishArea;
#     print "Bowl Area                          : $bowlArea\n";
#
#     # Note this assumes a flat area
#     $volumeSquishBand = $squishClearMeters * $areaSquishArea;
#     print "Volumes of the Squish Band         : $volumeSquishBand\n";
#
#     $volumeBowlSquished = $squishClearMeters * $bowlArea;
#     print "Volume of Squish Under Bowl        : $volumeBowlSquished\n";
#
#     # Again if we assume that the squish area is flat, we can compute
#     # the area of the bowl by whats left over.
#     $volumeBowl = $clearanceVolume - $volumeBowlSquished - $volumeSquishBand;
#     print "Volume of the Bowl                 : $volumeBowl\n";
#
#     #
#     # area of circle = pi * diameter * diameter / 4
#     #
#     $diameterBowl = sqrt(4 * $bowlArea / pi);
#     print "Diameter of the Bowl               : $diameterBowl\n";
#
#     # volume of area to be squished when the exhaust closes
#     # VS1 = HEOT1 * ASQ + VSQBAND
#     $volumeSquish1 = $heightExOpenTopMeters * $areaSquishArea + $volumeSquishBand;
#     print "Volume Squish at Exhaust Close     : $volumeSquish1\n";
#
#     # volume of area of the bowl when the exhaust closes
#     # VB1 = HEOT1*ABL+VBS+VBOWL
#     $volumeBowl1 = $heightExOpenTopMeters * $bowlArea + $volumeBowlSquished + $volumeBowl;
#     print "Volume Bowl   at Exhaust Close     : $volumeBowl1\n";
#
#     # VCYL1 = HEOT1*PA+CVOL
#     $volumeCylAtExOpen = $heightExOpenTopMeters * $pistonArea + $clearanceVolume;
#     print "Volume of Cylinder @ Exhaust Close : $volumeCylAtExOpen\n";
#
#     # VTRAP = VCYL1
#     $volumeTrapped = $volumeCylAtExOpen;
#     print "Trapped Volume of the Cylinder     : $volumeTrapped\n";
#
#     # Constant
#     $GASR = 287;
#
#     # PTRAP = 101325
#     # Pressure at the Trap Point
#     $pressureTrapped = 101325;
#
#     # Page 513
#     # TTRAP = 293
#     # Tempature at the Trap Point
#     $tempatureTrapped = 293;
#
#     # PCYL1 = PTRAP
#     $pressureCylinderPoint1  = $pressureTrapped;
#     print "Pressure of Cylinder at Point 1    : $pressureCylinderPoint1\n";
#
#     # TCYL1 = TTRAP
#     $tempatureCylinderPoint1 = $tempatureTrapped;
#     print "Tempature of Cylinderat Point 1    : $tempatureCylinderPoint1\n";
#
#     # GAMMA = 1.4
#     $GAMMA = 1.4;
#
#     # MTRAP = PTRAP * VTRAP/(GASR * TTRAP)
#     # Mass is conserved
#     $massOfTrapped = $pressureTrapped * $volumeTrapped /
#                         ($GASR * $tempatureTrapped);
#     print "Mass of Gas Trapped in Cylinder    : $massOfTrapped\n";
#
#     # Everything must start in balance and end in balance
#     # PS1 = PCYL1
#     $pressureSquish1 = $pressureCylinderPoint1;
#     print "Pressure of Squish at Point 1      : $pressureSquish1\n";
#
#     # PB1 = PCYL1
#     $pressureBowl1   = $pressureCylinderPoint1;
#     print "Pressure of Bowl   at Point 1      : $pressureBowl1\n";
#
#     # TS1 = TCYL1
#     $tempatureSquish1 = $tempatureCylinderPoint1;
#     print "Tempature of Squish at Point 1     : $tempatureSquish1\n";
#
#     # TB1 = TCLY1
#     $tempatureBowl1   = $tempatureCylinderPoint1;
#     print "Tempature of Bowl   at Point 1     : $tempatureBowl1\n";
#
#     # RHOS1 = PS1/(GASR*TS1)
#     $ratioHeatOfSquish1 = $pressureSquish1 / ($GASR * $tempatureSquish1);
#     print "Ratio of Heat of Squish Point 1    : $ratioHeatOfSquish1\n";
#
#     # RHOB1 = PB1/(GASR*TB1)
#     $ratioHeatOfBowl1   = $pressureBowl1   / ($GASR * $tempatureBowl1);
#     print "Ratio of Heat of Bowl   Point 1    : $ratioHeatOfBowl1\n";
#
#     # MS1 = MTRAP*VS1/VCYL1
#     $massSquish1        = $massOfTrapped * $volumeSquish1 / $volumeCylAtExOpen;
#     print "Mass  of Gas at Squish Point  1    : $massSquish1\n";
#
#     # MB1 = MTRAP - MS1
#     $massBowl1          = $massOfTrapped - $massSquish1;
#     print "Mass  of Gas at Bowl   Point  1    : $massBowl1\n";
#
#     # DC = 1
#     $degreeChange       = 1;
#     print "Degree Change                      : $degreeChange\n";
#
#     # DT=DC/(6*RPM)
#     # The equation is partially reduced.
#     #  DC      Rev      min    60 sec
#     # ---- * ------- * ----- * ------
#     #        360 Deg    Rev      min
#     $deltaTime = $degreeChange / (6 * $rpm);
#     print "Delta Time                         : $deltaTime\n";
#     # GOSUB CRANKFACT
#     &crankFact($crank);
#
#
# # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#
# }
#
#
# #
# # MAINLINE
# #
# print "Ed's Cheap 2 Stroke Hemi-Spherical Squish Design\n";
# print << "WHYDOIT";
#
# Why create another program to do the the 2 stroke squish calculations?
#
# A couple of reasons. First I want to solve for specific parameters that
# are inputs to Dr. Blairs program. The other reason is that I want to build
# this program is that I am interested in playing with the algorithms for
# computing the maximum squish velocity.
#
# WHYDOIT
#
# my($i)                       = 0;
# my($bore)                    = 0;
# my($stroke)                  = 0;
# my($connRodLen)              = 0;
# my($rpm)                     = 0;
# my($exhaustOpen)             = 0;
# my($trappedCompressionRatio) = 0;
# my($squishClearance)         = 0;
# my($squishAreaRatio)         = 0;
#
#    &getInput(\$bore, \$stroke, \$connRodLen, \$rpm, \$exhaustOpen,
#              \$trappedCompressionRatio, \$squishClearance,
# 	     \$squishAreaRatio);
#
# for ($i = 0; $i < 360; $i++) {
# }
#
#    &mainCalc($bore, $stroke, $connRodLen, $rpm, $exhaustOpen,
# 		$squishClearance, $trappedCompressionRatio,
# 		$squishAreaRatio);
# 1;
