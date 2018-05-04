#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:20:07 2018

@author: hamish
"""
# %%

import csv
import math
import numpy as np
import matplotlib.pyplot as plt

# %%
# input 5000, 10, 0.21, 1.02, 0.98, i, 1.50, 1.00, 0.50, 0.99, 0.98, 0.07, 1000))
# =========================
# Find Cheapest Build Plan
# =========================

"""Test Case:

    find_cheapest(1000, 10, 0.1, 1.1, 1, 1.00, 1.00, 1.00, 1, 1, 0.00, 0)
Intitial_Daily_Demand: 1000 (watts)
Operating Period in years: 10 (Index = -1)
Capacity Factor: 10% (input as 0.1)  NB regularise this so that using same format.
Demand Increase: 10% (input as 1.1)
Degradation Rate: 10% (0.9)

    """

def find_cheapest(
        initial_daily_demand,
        operating_period,
        capacity_factor,
        demand_increase,
        base_bos_cost,
        base_module_cost,
        operation_cost,
        bos_reduction,
        module_reduction,
        discount_rate,
        rebuild_fixed):

    costs_array = np.array([])
    j_array = np.array([])

    min_cost = None
    min_index = None

    for i in range(operating_period):
        j = i + 1
        cost = incremental_build(
        initial_daily_demand,
        operating_period,
        capacity_factor,
        demand_increase,
        j,
        base_bos_cost,
        base_module_cost,
        operation_cost,
        bos_reduction,
        module_reduction,
        discount_rate,
        rebuild_fixed)

        if min_cost is None or cost < min_cost:
            min_cost = cost
            min_index = j

        costs_array = np.append(costs_array, cost)
        j_array = np.append(j_array, j)

    print()
    print("The minimum cost is $ %.2f /kWh." % min_cost)
    print("The lowest cost build configuration is with %.f increment(s)." % min_index)


    plt.plot(j_array, costs_array)
    plt.xlabel("Increment Number")
    plt.ylabel("LCOE (kWh)")


# %%
# =====================================================
# Set incremental installations to create PV size array
# =====================================================
"""
 Function that splits the operating period into any number of increments
 and provides an array of PV sizes and the final operating years

"""

# input: incremental_build(5000, 10, 0.21, 1.02, 0.98, 3, 1.50, 1.00, 0.50, 0.99, 0.98, 0.07, 1000)
# initial_daily_demand = 5000 watt hours
# operating period = 10
#
#annual module cost reduction =  2 %
#annual bos cost reduction = 1 %
#dicount rate = 7 % 0.07 ()
#base_module_costs = $1.00 / watt (considerably higher than wholesale prices but this would be inflated due to small-scale and remote location)
#base_bos_costs = $1.50 / watt (need data for this)
#operation_cost = $0.50 per watt ?
# rebuild fixed = $1000 ??


import numpy as np
import matplotlib.pyplot as plt

def incremental_build(
        initial_daily_demand,
        operating_period,
        capacity_factor,
        demand_increase,
        number_increment,
        base_bos_cost,
        base_module_cost,
        operation_cost,
        bos_reduction,
        module_reduction,
        discount_rate,
        rebuild_fixed):

    operating_array = np.arange(0, operating_period)   # sets the array of the operating period to be split
    inc_array = np.array_split(operating_array, number_increment, axis=0) # array of sub_arrays for time periods
    total_pv_array = np.array([])       # Create array of total PV sizes
    pv_build_array = np.array([])       # Create array of PV size additions
    first_year_array =  np.array([])    # Array of first years of each increment
    final_year_array = np.array([])     # Array of last years of each increment

    for sub_array in inc_array:         # For loop calculates the pv size steps
        last_val = sub_array[-1]        # Takes last value of each sub array within inc_array
        first_val = sub_array[0]
        total_pv_array = np.append(total_pv_array, (pv_size_recursive(initial_daily_demand, last_val, capacity_factor, demand_increase)))
    #   ^ appends the total pv array with a value for each increment final year by calling the pv size function with appropriate values
        final_year_array = np.append(final_year_array, last_val) #appends the final year array with final year from each increment
        first_year_array = np.append(first_year_array, first_val)

    count = 0                           #  Sets zero counter to be used for below for-loop
    for item in total_pv_array:
        loop_value = item               #  Variable for iterable
        subtraction_value = total_pv_array[count-1] #  Variable for previous item in for loop

        if count == 0:                  #  If statement needed as item [0] doesn't need subtraction
            pv_build_array = np.append(pv_build_array, loop_value)
            count += 1           # Appends with first value and adds to the count
        else:
            pv_build_array = np.append(pv_build_array, loop_value - subtraction_value) # appends with subtraction to give values of additional build needed
            count += 1            # Adds to count, needed to subtract prevoious value

    net_present_cost = npc(     #calls npc function (below) to calculate the total npc of the system build configuration
            pv_build_array,
            first_year_array,
            final_year_array,
            total_pv_array,
            base_bos_cost,
            base_module_cost,
            operation_cost,
            bos_reduction,
            module_reduction,
            discount_rate,
            rebuild_fixed)

    total_lifetime_energy = energy_output(      # calls the total lifetime energy function (below) with respective arguments
            initial_daily_demand,
            operating_period,
            demand_increase,
            discount_rate)

    levelised_cost = simple_lcoe(  # calls the lcoe function (below) in order to
            net_present_cost,
            total_lifetime_energy)


    print("The increment array = ",inc_array)
    print("The total PV array =",total_pv_array)
    print("The pv build array = ",pv_build_array)
    print("Total NPC is $ %.2f " % net_present_cost )
    print("Total Energy Production is %.2f watt hours " % total_lifetime_energy)
    print("The levelised cost of electricity is $ %.2f / kWh" % levelised_cost)
    return levelised_cost



# %%

# =============================================
# Callable Net Present Cost Calculator Function
# =============================================
"""Function uses generated data to calculate NPC of energy system"""

def npc(
        pv_build_array,
        first_year_array,
        final_year_array,
        total_pv_array,
        base_bos_cost,
        base_module_cost,
        operation_cost,
        bos_reduction,
        module_reduction,
        discount_rate,
        rebuild_fixed):

    build_cost = 0                  # Sets empty variable to accumulate build cost
    operation_total = 0             # Sets empty O and M variable to accumulate from for-loop

    for i in range(len(pv_build_array)):  # Uses length of one of the arrays (all same length) to iterate

        first_year, final_year, pv, total_pv  = first_year_array[i], final_year_array[i], pv_build_array[i], total_pv_array[i]
        # ^^ sets the variables to be the respective iterables
        if first_year == 0:                 # if 0th year, no cost reduction
            bos_cost = base_bos_cost * pv       # gives initial build BOS cost
            pv_cost = base_module_cost * pv     # gives initial year module costs
            build_cost += (bos_cost + pv_cost + rebuild_fixed)  # adds to total build cost
            #print("The build cost running total year 0 is ", build_cost)


        else:
            bos_cost = (base_bos_cost * pv) * (first_year * module_reduction)   # Calculates the BOS costs for the nth increment build, with respective cost reductions
            pv_cost = (base_module_cost * pv) * (module_reduction * first_year)  # Calculates the module costs for the nth increment build, with respective cost reductions
            build_cost += (bos_cost + pv_cost + rebuild_fixed) * (1-discount_rate ** first_year) # Build cost totaled and discounted to the build year.
            #print("The running total build cost is (not year zero)", build_cost)

        for i in range(int(first_year), int(final_year+1)): #   For-loop for calculating the O&M costs- done separately as calculated each year.
            if i == 0:                                      #   For year 0, no discount rate
                operation_total += operation_cost * total_pv
                print("the runnning total cost in year zero is ", operation_total)
            else:
                operation_total += (operation_cost * total_pv) * (1-discount_rate ** i) # Future years discounted
                print("the runnning total cost in not year zero is ", operation_total)

    total_npc = build_cost + operation_total    # total_npc = sum of discounted build costs at each build point and O&M costs
    return total_npc

# %%
# ================================================
# Callable Function for Lifetime Energy Production
# ================================================
"""As generation is exactly matching demand, uses discounted annual demand
growing on a compound basis"""

# Debugging Done - no errors found

def energy_output(initial_daily_demand, operating_period, demand_increase, discount_rate):

    annual_demand = initial_daily_demand * 365      # Converts initial daily demand into base annual figure
    total_generation = 0                            # Sets empty variable for total generation

    for year in range(0, operating_period):         # Runs the for-loop for 0 - end of project life
        total_generation += (annual_demand * (demand_increase ** year)) / ((1 + discount_rate) ** year)

    return float(total_generation)                  # Returns total figure to main function

# %%

# ===========================================================================
# Callable PV Calculation Function, incorportates demand growth + degradation
# ===========================================================================
"""PV size function that is recursive and can be used as parts of other functions. Factors in up-sizing
for degradation, and also demand increase for the given period."""


def pv_size_recursive(initial_daily_demand, operating_period, capacity_factor, demand_increase):

    annual_demand = (initial_daily_demand * 365) #converts daily demand to annual
    print(annual_demand)

    increased_demand = dem_end_period(annual_demand, operating_period, demand_increase) # calls function that takes the end demand for the specific period
    print(increased_demand)

    #degradedpv = pv_degradation_percent(degradation_rate, operating_period) # calls function that calculates degradation for the period
    #print(degradedpv)

    newpv = pv_deg_incdem(increased_demand, capacity_factor) # Calls function that
    print(newpv)

    return newpv #returns the pv size needed for each increment.


# %%
# ==============================================
# Callable sub-function for end of period demand
# ==============================================

"""Function used to generate the end of period demand ammount to be used in
PV size function """

# Debugging done - no errors found.

def dem_end_period(annual_demand, period, deminc):

    new_demand = annual_demand * (deminc ** period)  # Calculates the final year of period demand
    return new_demand

# %%
"""

# ========================================
# PV Degradation Function
# ========================================
Simple initial function that returns that factor of multiplication
for degradation over the

def pv_degradation_factor(degradation, period):

    degraded = (period * degradation) / 100
    print("The degraded PV is ",degraded)
    return degraded

"""
#%%
def pv_deg_incdem(demand, capacity_factor):

    hourly = (demand/8760)
    # assumes demand is the same across every hour
    pv = (hourly/capacity_factor)   # calculates the pv capacity needed based
    return pv

# %%
# ==================
# LCOE Calculator
# ==================
def simple_lcoe(npc, total_energy):
    lcoe = npc / (total_energy / 1000)
    return lcoe

# %%

print(int(energy_output(1000, 10, 1.1, 0.0)))
assert int(energy_output(1000, 10, 1.1, 0.0)) == 5817159