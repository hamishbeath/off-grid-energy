#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:20:07 2018

@author: Hamish Beath
"""

import numpy as np
import matplotlib.pyplot as plt

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
        rebuild_fixed,
        degradation_rate):
    """
    # Find Cheapest Build Plan Function

    """

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
            rebuild_fixed,
            degradation_rate)

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
    plt.ylabel("LCUE (kWh)")
    plt.show()


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
        rebuild_fixed,
        degradation_rate):
    """
    # Set incremental installations to create PV size array

    Function that splits the operating period into any number of increments
    and provides an array of PV sizes and the final operating years

    :param initial_daily_demand: Energy demand of the communmity at year 0 in Watts
    :param operating_period: Lifetime of project in years
    :param capacity_factor: in % terms
    :param demand_increase: % terms
    :param number_increment: n
    :param base_bos_cost: $/watt
    :param base_module_cost: $/watt
    :param operation_cost: $/watt
    :param bos_reduction: % terms
    :param module_reduction: % terms
    :param discount_rate: %
    :param rebuild_fixed: $
    :param degradation_rate: %

    :return: returns levelized cost

    """

    operating_array = np.arange(0, operating_period)   # sets the array of the operating period to be split
    inc_array = np.array_split(operating_array, number_increment, axis=0) # array of sub_arrays for time periods

    # =====================================================
    # Sub procedure for calcuting total PV sizes
    # =====================================================

    # Total PV sizes at the end of each increment in Watts
    total_pv_array = np.array([])
    pv_build_array = np.array([])       # Create array of PV size additions
    first_year_array =  np.array([])    # Array of first years of each increment
    final_year_array = np.array([])     # Array of last years of each increment

    # calculate pv_sizes, total_pv_array
    for i, sub_array in enumerate(inc_array):         # For loop calculates the pv size steps
        last_val = sub_array[-1]        # Takes last value of each sub array within inc_array
        first_val = sub_array[0]
        pv_size = pv_size_recursive(initial_daily_demand, last_val, capacity_factor, demand_increase)

        # appends the total pv array with a value for each increment
        # final year by calling the pv size function with appropriate values
        total_pv_array = np.append(total_pv_array, pv_size)

        if i == 0:
            # First item doesn't need subtraction, as it has
            # no previous increments
            prev_value = 0
        else:
            prev_value = total_pv_array[i-1]

        additional_build_needed = pv_size - prev_value

        # appends with subtraction to give values of additional build needed
        pv_build_array = np.append(pv_build_array, additional_build_needed)

        # appends the final year array with final year from each increment
        final_year_array = np.append(final_year_array, last_val)
        first_year_array = np.append(first_year_array, first_val)

    # =====================================================
    # Sub procedure for calcuting degraded PV amount
    # =====================================================

    count_deg = 0 # Count for function
    pv_total_deg = 0 # running total for degradation calculation
    degraded_pv_array = np.array([]) #

    for count_deg, pv_build in enumerate(pv_build_array):

        num_years_in_increment = len(inc_array[count_deg])
        period_deg = num_years_in_increment * degradation_rate

        # calculates degradation pecentage for the period
        # calculates extra needed for the period given the degradation
        extra_pv = pv_build - (pv_build * (1 - period_deg))

        if count_deg == 0:
            extra_from_total = 0
        else:
            extra_from_total = pv_total_deg - (pv_total_deg * (1 - period_deg))

        pv_total_deg += (pv_build + extra_pv + extra_from_total)
        degraded_pv = pv_build + extra_pv + extra_from_total
        # appends the degraded_pv array with the next install amount
        degraded_pv_array = np.append(degraded_pv_array, degraded_pv)

    # =====================================================
    # Calls npc function (below) to calculate the total npc
    # =====================================================

    net_present_cost = npc(
            degraded_pv_array,
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

    # ===============================================
    # Calculates total discounted electricity (below)
    # ===============================================

    total_lifetime_energy = energy_output(      # calls the total lifetime energy function (below) with respective arguments
            initial_daily_demand,
            operating_period,
            demand_increase,
            discount_rate)

    # ===============================================
    # Calculates LCUE (below)
    # TODO: move to seperate function
    # ===============================================

    levelised_cost = simple_lcoe(  # calls the lcoe function (below) in order to
            net_present_cost,
            total_lifetime_energy)


    print("The increment array = ",inc_array)
    #print("The total PV array =",total_pv_array)
    print("The pv build array = ",degraded_pv_array)
    print("Total NPC is $ %.2f " % net_present_cost )
    print("Total Discounted Energy Production is %.2f watt hours " % total_lifetime_energy)
    print("The levelised cost of used electricity is $ %.2f / kWh" % levelised_cost)
    return levelised_cost



def npc(pv_build_array,
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
    """
    # Callable Net Present Cost Calculator Function
    Function uses generated data to calculate NPC of energy system
    """
    build_cost = 0                  # Sets empty variable to accumulate build cost
    operation_total = 0             # Sets empty O and M variable to accumulate from for-loop

    for i in range(len(pv_build_array)):  # Uses length of one of the arrays (all same length) to iterate

        # sets the variables to be the respective iterables
        first_year, final_year, pv, total_pv  = first_year_array[i], final_year_array[i], pv_build_array[i], total_pv_array[i]
        if first_year == 0:                 # if 0th year, no cost reduction
            bos_cost = base_bos_cost * pv       # gives initial build BOS cost
            pv_cost = base_module_cost * pv     # gives initial year module costs
            build_cost += (bos_cost + pv_cost + rebuild_fixed)  # adds to total build cost

        else:
            bos_cost = (base_bos_cost * pv)     # Calculates the BOS costs for the nth increment build, with respective cost reductions

            if bos_reduction > 0.00:
                bos_cost = bos_cost * ((1-bos_reduction)**first_year)
            pv_cost = (base_module_cost * pv)   # Calculates the module costs for the nth increment build, with respective cost reductions

            if module_reduction > 0.00:
                pv_cost = pv_cost * ((1-module_reduction)**first_year)

            build_cost += (bos_cost + pv_cost + rebuild_fixed)  # Build cost totaled and discounted to the build year.

        for i in range(int(first_year), int(final_year+1)): #   For-loop for calculating the O&M costs- done separately as calculated each year.

            if i == 0:                                      #   For year 0, no discount rate
                operation_total += operation_cost * total_pv
            else:
                operation_total += (operation_cost * total_pv) * ((1-discount_rate) ** i) # Future years discounted

    print("the total build cost is ",build_cost)
    total_npc = build_cost + operation_total    # total_npc = sum of discounted build costs at each build point and O&M costs
    return total_npc

def energy_output(initial_daily_demand, operating_period, demand_increase, discount_rate):
    """
    # Callable Function for Lifetime Energy Production

    As generation is exactly matching demand, uses discounted annual demand
    growing on a compound basis
    """
    annual_demand = initial_daily_demand * 365      # Converts initial daily demand into base annual figure
    total_generation = 0                            # Sets empty variable for total generation

    for year in range(0, operating_period):         # Runs the for-loop for 0 - end of project life
        total_generation += (annual_demand * (demand_increase ** year)) / ((1 + discount_rate) ** year)

    return float(total_generation)                  # Returns total figure to main function


def pv_size_recursive(initial_daily_demand, operating_period, capacity_factor, demand_increase):
    """
    # Callable PV Calculation Function, incorportates demand growth + degradation

    PV size function that is recursive and can be used as parts of other functions. Factors in up-sizing
    for degradation, and also demand increase for the given period.
    """

    annual_demand = (initial_daily_demand * 365) #converts daily demand to annual

    increased_demand = dem_end_period(annual_demand, operating_period, demand_increase) # calls function that takes the end demand for the specific period
    print(increased_demand)

    #degradedpv = pv_degradation_percent(degradation_rate, operating_period) # calls function that calculates degradation for the period
    #print(degradedpv)
    newpv = pv_deg_incdem(increased_demand, capacity_factor) # Calls function that
    return newpv #returns the pv size needed for each increment.

def dem_end_period(annual_demand, period, deminc):
    """
    # Callable sub-function for end of period demand

    Function used to generate the end of period demand ammount to be used in
    PV size function
    """

    new_demand = annual_demand * (deminc ** period)  # Calculates the final year of period demand
    return new_demand

def pv_deg_incdem(demand, capacity_factor):

    hourly = (demand/8760)
    # assumes demand is the same across every hour
    pv = (hourly/capacity_factor)   # calculates the pv capacity needed based
    return pv

def simple_lcoe(npc, total_energy):
    """
    # LCUE Calculator
    """
    lcoe = npc / (total_energy / 1000)
    return lcoe

#=============================================================================================================
#=============================================================================================================
#=============================================================================================================


# Instructions for Use in Spyder:
#
# 1. Load main code into the console. The main code (3) is below functions 1 and 2.
# 2. Adjust the keyworded params for either incremental build (runs once) or find cheapest
# 3. Run either incremental build or find cheapest by inserting the function into console.
#
#
#%%
# =========================================
# 1. Runs below scenario for incremental build
# =========================================
# Runs one case eg. 3 increments

# incremental_build(
#         initial_daily_demand=1000,  # in watt hours
#         operating_period=10,        # in years
#         capacity_factor=0.1,        # % terms 0.1 = 10 %
#         demand_increase=1.10,       # in % terms 1.1 = 10% increase (NB change)
#         number_increment=3,         # number of increments explicitly defined
#         base_bos_cost=1.00,         # in $ per watt installed
#         base_module_cost=1.00,      # in $ per watt installed
#         operation_cost=0.50,        # in $ per watt installed
#         bos_reduction=0.01,         # in % terms 0.1 = 10% reduction
#         module_reduction=0.01,      # in % terms 0.1 = 10% reduction
#         discount_rate=0.05,         # in % terms 0.1 = 10% discount rate
#         rebuild_fixed=0,            # Fixed rebuild cost in $USD"""
#         degradation_rate=0.02)      # PV degradation rate in

#%%
# ====================================
# 2. Runs below scenario to find cheapest
# ====================================
# Steps through all cases 1 to max (Operating period)

find_cheapest(
        initial_daily_demand=1000,  # in watt hours
        operating_period=10,        # in years
        capacity_factor=0.21,        # % terms 0.1 = 10 %
        demand_increase=1.15,       # in % terms 1.1 = 10% increase (NB change)
        base_bos_cost=1.50,         # in $ per watt installed
        base_module_cost=1.00,      # in $ per watt installed
        operation_cost=0.50,        # in $ per watt installed
        bos_reduction=0.02,         # in % terms 0.1 = 10% reduction
        module_reduction=0.05,      # in % terms 0.1 = 10% reduction
        discount_rate=0.1,         # in % terms 0.1 = 10% discount rate
        rebuild_fixed=0,
        degradation_rate=0.02)            # Fixed rebuild cost in $USD















