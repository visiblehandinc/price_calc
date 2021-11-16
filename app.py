from re import template
import streamlit as st
import plotly.express as px
from plotly import graph_objects as go
import pandas as pd

st.set_page_config(    
    page_title="True Cost",
    layout='wide',
    page_icon="✋",
    initial_sidebar_state='collapsed'
)
title_placeholder = st.empty()
st.write(" ")

# Hide toolbars for charts
config={'displayModeBar': False}

ac1, _ = st.columns([1,3])
# with ac1:
with st.sidebar:
    num_facs = st.slider("Number of facilities to use in calculation", 1, 220, 1)
fc1, fc2, fc3 = st.columns([2,1,1])

f_txt = 'Facility' if num_facs == 1 else 'Facilities'

title_placeholder.title(f"First Year Cost for {num_facs} {f_txt}")

with fc1:
    main_figure_placeholder = st.empty()
with fc2:
    st.write(" ")
    st.write(" ")
    st.markdown("### Competitor Cost Year 1")
    st.markdown("##### average per bed per month")
    competitor_tot_cost_pbpm_placeholder = st.empty()
    st.write(" ")
    st.markdown("##### startup costs")
    competitor_startup_costs_placeholder = st.empty()    
    st.write(" ")
    st.markdown("##### total")
    competitor_tot_cost_annual_placeholder = st.empty()
with fc3:
    st.write(" ")
    st.write(" ")
    st.markdown("### VH Cost Year 1")
    st.markdown("##### average per bed per month")
    vh_tot_cost_pbpm_placeholder = st.empty()
    st.write(" ")
    st.markdown("##### startup costs")
    vh_startup_costs_placeholder = st.empty()    
    st.write(" ")
    st.markdown("##### total")
    vh_tot_cost_annual_placeholder = st.empty()

#----------------------------------------------------------------------------------------------------------------
# Facility Info & Summary Cost per bed
#----------------------------------------------------------------------------------------------------------------
with st.sidebar:
    with st.expander("Facility Info"):
        adc = st.slider("Average Daily Census", 50, 120, 85)
        los = st.slider("Average length of stay", 1, 60, 5)

#----------------------------------------------------------------------------------------------------------------
# Tiers
#----------------------------------------------------------------------------------------------------------------
with st.sidebar:
    with st.expander("Competitor's Tiers"):
        os_subscription_1 = st.slider("Tier 1 subscription price (bed/month)", 10.0, 70.0, 45.0, 1.0, format="$%f")
        os_subscription_2 = st.slider("Tier 2 subscription price (bed/month)", 10.0, 70.0, 35.0, 1.0, format="$%f")   
        os_subscription_3 = st.slider("Tier 3 subscription price (bed/month)", 10.0, 70.0, 25.0, 1.0, format="$%f")
        st.write("---")
        num_facs_start_tier_2 = st.slider("Tier 2 starts at facility #", 1, 50, 26) 
        num_facs_start_tier_3 = st.slider("Tier 3 starts at facility #", 1, 220, 201)   


# Tiers for competitor
#----------------------
# We create a list of fac prices for each facility, from 1 to 220
fac_nums = range(1,221)
comp_fac_prices_1 = [os_subscription_1] * (num_facs_start_tier_2 - 1)
comp_fac_prices_2 = [os_subscription_2] * (num_facs_start_tier_3 - num_facs_start_tier_2)
comp_fac_prices_3 = [os_subscription_3] * (220 - num_facs_start_tier_3 + 1)
comp_fac_prices = comp_fac_prices_1 + comp_fac_prices_2 + comp_fac_prices_3

# NOTE: the common denominator for all costs in the dfs will be per bed per month.
competitor_costs_full_df = pd.DataFrame({'Facility Count': fac_nums, 'Subscription Cost': comp_fac_prices})
# chop off the df based on number of facs being used in the calc
competitor_costs_df = competitor_costs_full_df.iloc[0:num_facs]
avg_base_subscription_cost_competitor = competitor_costs_df['Subscription Cost'].mean()


# Tiers for VH
#----------------------
num_beds = num_facs * adc

vh_price = 45
if num_beds < 100:
    vh_price = 65.0
elif num_beds < 250:
    vh_price = 60.0    
elif num_beds < 500:
    vh_price = 57.5
elif num_beds < 1000:
    vh_price = 55
elif num_beds < 2500:
    vh_price = 52.5
else:
    vh_price = 50

vh_tiers_df = pd.DataFrame({'Bed Count':[1, 100, 250, 500, 1000, 2500], '$/b/m':['$65.00', '$60.00', '$57.50', '$55.00', '$52.50', '$50.00']})
vh_tiers_df['empty'] = [''] * len(vh_tiers_df)
vh_tiers_df = vh_tiers_df.set_index('empty')
with st.sidebar:
    with st.expander("VH Tiers"):
        st.table(vh_tiers_df)
        # because (at the current settings) their monthly charges will drop ${(os_subscription_2-os_subscription_3)*num_facs_start_tier_3*adc:,.0f} when facility {num_facs_start_tier_3} goes live."):
        st.success("VH Tiers are retroactive in that all subscribed beds across facilities receive the new tier price.")

vh_bed_prices = [vh_price] * num_beds    

fac_num_list = []
for i in range(num_facs):
    f = [i+1] * adc
    fac_num_list.extend(f)

# This is based off of bed counts, so we'll squash it down to be by facility count.
vh_costs_df = pd.DataFrame({'Facility Count': fac_num_list, 'Subscription Cost': vh_bed_prices})
vh_costs_df = vh_costs_df.groupby('Facility Count')['Subscription Cost'].mean().reset_index()

avg_base_subscription_cost_vh = vh_costs_df['Subscription Cost'].mean()


#----------------------------------------------------------------------------------------------------------------
# Wearables
#----------------------------------------------------------------------------------------------------------------
with st.sidebar:
    with st.expander("Wearables"):
        st.markdown("### Bands")    
        band_cost = st.slider("Cost of a single band", 0.25, 25.0, 2.0, 0.25, format="$%f",help="Bands are at best, single use. Sometimes more than 1 band might be needed for a patient during their treatment. This 'small' expense can add up quickly with volume.  Competitor has had customers churn after the initial contract term b/c of sticker shock of the consumables.")
        band_cost_competitor_pbpm = 30 / los * band_cost
        st.write(f"Additional per bed cost = ${band_cost_competitor_pbpm:.2f}")

        st.markdown("### Beacons")       
        beacon_cost_competitor = st.slider("Cost of a single beacon", 1.0, 100.0, 31.0, 0.5, format="$%f")
        num_months_beacon_life = 12 #st.slider("# of months until beacon replacement", 1, 60, 12, help="VisibleHand replaces all non-working beacons for free.")        
        loss_rate_per_month_beacons = st.slider("Average percent of beacons lost per month", 0, 50, 0, format="%f", help="Beacons have a large 'unplanned cost' potential if not managed well. We created a 'beacon tracker' module to help facilities better manage their loss rate to reduce costs.  In our experience, the loss rate is 10-30% depending on the facility's process control.")  

        beacon_cost_competitor_pbpm = (1-(loss_rate_per_month_beacons/100)) ** num_months_beacon_life * (beacon_cost_competitor / num_months_beacon_life) + (beacon_cost_competitor * (loss_rate_per_month_beacons/100))
        beacon_cost_vh_pbpm = loss_rate_per_month_beacons/100 * 25
        st.write(f"Additional per bed cost (Competitor)= ${beacon_cost_competitor_pbpm:.2f}")
        st.write(f"Additional per bed cost (VH)= ${beacon_cost_vh_pbpm:.2f}")


# add in the additional costs to the dfs
competitor_costs_df['Bands Cost'] = [band_cost_competitor_pbpm] * len(competitor_costs_df)
competitor_costs_df['Beacons Cost'] = [beacon_cost_competitor_pbpm] * len(competitor_costs_df)
competitor_costs_df['Wearables Cost'] = [band_cost_competitor_pbpm + beacon_cost_competitor_pbpm] * len(competitor_costs_df)
# competitor_costs_df['Wearables Cost'] = competitor_costs_df['Subscription Cost'] + (band_cost_per_bed_competitor + beacon_cost_per_bed_competitor)

vh_costs_df['Bands Cost'] = [0] * len(vh_costs_df)
vh_costs_df['Beacons Cost'] = [beacon_cost_vh_pbpm] * len(vh_costs_df)
vh_costs_df['Wearables Cost'] = [0 + beacon_cost_vh_pbpm] * len(vh_costs_df)


#----------------------------------------------------------------------------------------------------------------
# Devices
#----------------------------------------------------------------------------------------------------------------

with st.sidebar:
    with st.expander("Devices and Management"):
        st.markdown("### Beds : Device Ratio")
        beds_to_device_ratio = st.slider("Ratio of number of beds per device", 3, 20, 5, format="%d")
        st.markdown("### Connectivity")
        cellular_cost_per_phone_per_month = st.slider("Average Celluar Data cost, per device, per month", 0, 40, 18, format="$%f", help="Connectivity is the highest risk component of a successful implementation. Relying on local WiFi was our #1 support complaint and often very difficult to resolve. This was the main driver behind our decision to include cellular for our customers. It creates a more reliable system, reduces outages, reduces support, and - bonus - GPS tracking on all devices for better security.")
        cellular_cost_competitor_pbpm = cellular_cost_per_phone_per_month / beds_to_device_ratio
        st.write(f"Additional per bed cost = ${cellular_cost_competitor_pbpm:.2f}")
        
        if cellular_cost_per_phone_per_month == 0:
            st.warning("If set to $0 due to Wifi plans, note that Wifi carries additional IT and support costs b/c it tends to fail more and connectivity issues are much harder to diagnose (and rule out) with wifi than with cellular.")

        st.markdown("### Management & Support")    
        mdm_software_cost_per_phone_per_year = st.slider("MDM software cost, per device, per year", 10, 25, 16)
        num_devices_per_fte = st.slider("Number of devices a single FTE can fully support", 100, 1000, 350, 25, help = "Note: Lower if planning to use WiFi (see connectivity note).  \nAs a mobile application, success is inextricably linked with device performance, maintainence, security, and uptime. Offering device management (alongside connectivity & software) allows us to optimize the full scope of delivery a successful launch & long-term reliability.")
        salary_fte = st.slider("'Fully loaded' salary for new IT FTE", 50000, 150000, 90000, 5000, format="$%f", help = "Note: mid-level IT hire.  \nVH remotely manages all devices included in the subscription cost... this includes lockdown, GPS tracking & geofence alerts, software/phone updating, remote shutdown, SIM management, connection management, broadcating management alerts to the phones, etc...  All of these functions will be the responsibility of UHS if OS is used.")
        mdm_cost_competitor_pbpm = mdm_software_cost_per_phone_per_year/(12 * beds_to_device_ratio) + (salary_fte / 12) / (beds_to_device_ratio * num_devices_per_fte)
        st.write(f"Additional per bed cost = ${mdm_cost_competitor_pbpm:.2f}")


# competitor_costs_df['Devices Cost'] = competitor_costs_df['Wearables Cost'] + (cellular_cost_per_bed + mdm_cost_per_bed)
competitor_costs_df['Cellular Cost'] = [cellular_cost_competitor_pbpm] * len(competitor_costs_df)
competitor_costs_df['MDM Cost'] = mdm_cost_competitor_pbpm * len(competitor_costs_df)

vh_costs_df['Cellular Cost'] = [0] * len(vh_costs_df)
vh_costs_df['MDM Cost'] = [0] * len(vh_costs_df)


#----------------------------------------------------------------------------------------------------------------
# One-Time Costs
#----------------------------------------------------------------------------------------------------------------
avg_device_cost_competitor = 440
total_vh = round(num_beds / beds_to_device_ratio * 275)

with st.sidebar:
    with st.expander("Startup Costs"):
        st.markdown("### Competitor")
        beacon_startup_cost_competitor = 1.3 * beacon_cost_competitor * num_beds
        devices_startup_cost_competitor = (num_beds / beds_to_device_ratio) * avg_device_cost_competitor
        install_cost_competitor = st.slider("Install Cost", 0, 5000, 2500, 100, format="$%d")
        total_upfront_costs_competitor = devices_startup_cost_competitor + (install_cost_competitor * num_facs)
        
        beacon_startup_cost_competitor_pbpm = beacon_startup_cost_competitor / (adc * 12 * num_facs)
        # devices_startup_cost_competitor_pbpm = devices_startup_cost_competitor / (adc * 12 * num_facs)
        # install_cost_competitor_pbpm = install_cost_competitor / (adc * 12 * num_facs)
        # total_upfront_costs_competitor_pbpm = total_upfront_costs_competitor / (adc * 12 * num_facs)

        beacon_startup_cost_vh = 0
        devices_startup_cost_vh = num_beds / (beds_to_device_ratio) * 275
        install_cost_vh = 0
        total_upfront_costs_vh = devices_startup_cost_vh
        beacon_startup_cost_vh_pbpm = beacon_startup_cost_vh / (adc * 12 * num_facs)
        devices_startup_cost_vh_pbpm = devices_startup_cost_vh / (adc * 12 * num_facs)
        install_cost_vh_pbpm = install_cost_vh / (adc * 12 * num_facs)
        total_upfront_costs_vh_pbpm = total_upfront_costs_vh / (adc * 12 * num_facs)   

        # st.write(f"One Time Costs  \nAmortized over 1 year  \nExtra per bed per month = **${total_upfront_costs_competitor_pbpm:,.2f}**  \n**(Note: Excluded from Avg cost per bed)**  ")
        # st.text(f"Beacons =    ${beacon_startup_cost_competitor:,.0f} (+${beacon_startup_cost_competitor_pbpm:,.2f}/b/m)")
        st.text(f"Devices =    ${devices_startup_cost_competitor:,.0f}")  
        st.write("")      
        st.text(f"Total =      ${total_upfront_costs_competitor:,.0f}")    

        st.markdown("### VisibleHand")
        st.text(f"Beacons =    $0")
        st.text(f"Devices =    ${num_beds / beds_to_device_ratio * 275:,.0f}")
        st.text(f"Install =    $0")
        st.text("")
        st.text(f"Total =      ${total_vh:,.0f}")

        st.write("---")
        st.text(f"Cost Diff =  ${total_upfront_costs_competitor -total_vh:,.0f}")



# Add startup costs to standard pbpm costs
tot_base_cost_competitor_pbpm = avg_base_subscription_cost_competitor
tot_band_cost_competitor_pbpm = band_cost_competitor_pbpm

#tot_beacon_cost_competitor_pbpm = beacon_cost_competitor_pbpm * (max(0,12-num_months_beacon_life)/12) + beacon_startup_cost_competitor_pbpm
tot_beacon_cost_competitor_pbpm = beacon_cost_competitor_pbpm + beacon_startup_cost_competitor_pbpm
# tot_device_cost_competitor_pbpm = devices_startup_cost_competitor_pbpm
tot_cell_cost_competitor_pbpm = cellular_cost_competitor_pbpm
tot_mdm_cost_competitor_pbpm = mdm_cost_competitor_pbpm
# tot_install_cost_competitor_pbpm = install_cost_competitor_pbpm
tot_cost_competitor_pbpm = tot_base_cost_competitor_pbpm \
    + tot_band_cost_competitor_pbpm \
    + tot_beacon_cost_competitor_pbpm \
    + tot_cell_cost_competitor_pbpm \
    + tot_mdm_cost_competitor_pbpm 
tot_cost_competitor_annual = tot_cost_competitor_pbpm * adc * 12 * num_facs + total_upfront_costs_competitor

competitor_tot_cost_pbpm_placeholder.markdown(f'## ${tot_cost_competitor_pbpm:,.2f}')
competitor_startup_costs_placeholder.markdown(f'## ${total_upfront_costs_competitor:,.0f}')
competitor_tot_cost_annual_placeholder.markdown(f'## ${tot_cost_competitor_annual:,.0f}')


tot_base_cost_vh_pbpm = avg_base_subscription_cost_vh
tot_band_cost_vh_pbpm = 0
tot_beacon_cost_vh_pbpm = beacon_cost_vh_pbpm + beacon_startup_cost_vh_pbpm
# tot_device_cost_vh_pbpm = devices_startup_cost_vh_pbpm
tot_cell_cost_vh_pbpm = 0
tot_mdm_cost_vh_pbpm = 0
# tot_install_cost_vh_pbpm = install_cost_vh_pbpm
tot_cost_vh_pbpm = tot_base_cost_vh_pbpm \
    + tot_band_cost_vh_pbpm \
    + tot_beacon_cost_vh_pbpm \
    + tot_cell_cost_vh_pbpm \
    + tot_mdm_cost_vh_pbpm 
tot_cost_vh_annual = tot_cost_vh_pbpm * adc * 12 * num_facs + total_upfront_costs_vh

vh_tot_cost_pbpm_placeholder.markdown(f"## ${tot_cost_vh_pbpm:,.2f}")
vh_startup_costs_placeholder.markdown(f'## ${total_upfront_costs_vh:,.0f}')
vh_tot_cost_annual_placeholder.markdown(f"## ${tot_cost_vh_annual:,.0f}")

tot_consumable_cost_competitor_pbpm = tot_band_cost_competitor_pbpm + tot_beacon_cost_competitor_pbpm
tot_device_cost_competitor_pbpm = tot_mdm_cost_competitor_pbpm + tot_cell_cost_competitor_pbpm

tot_consumable_cost_vh_pbpm = tot_band_cost_vh_pbpm + tot_beacon_cost_vh_pbpm
tot_device_cost_vh_pbpm = tot_mdm_cost_vh_pbpm + tot_cell_cost_vh_pbpm

companies = ['Competitor', 'VH']
fig_summary = go.Figure(data=[
    go.Bar(name='Base', x=companies, y=[round(tot_base_cost_competitor_pbpm,2), round(tot_base_cost_vh_pbpm,2)]),
    go.Bar(name='Consumables', x=companies, y=[round(tot_consumable_cost_competitor_pbpm,2), round(tot_consumable_cost_vh_pbpm, 2)]),
    go.Bar(name='Devices', x=companies, y=[round(tot_device_cost_competitor_pbpm,2), round(tot_device_cost_vh_pbpm, 2)]),
    # go.Bar(name='Bands', x=companies, y=[round(tot_band_cost_competitor_pbpm,2), round(tot_band_cost_vh_pbpm,2)]),
    # go.Bar(name='Beacons', x=companies, y=[round(tot_beacon_cost_competitor_pbpm,2), round(tot_beacon_cost_vh_pbpm, 2)]),
    # go.Bar(name='MDM', x=companies, y=[round(tot_mdm_cost_competitor_pbpm,2), round(tot_mdm_cost_vh_pbpm, 2)]),
    # go.Bar(name='Cellular', x=companies, y=[round(tot_cell_cost_competitor_pbpm,2), round(tot_cell_cost_vh_pbpm, 2)]),
    # # go.Bar(name='Install', x=companies, y=[round(tot_install_cost_competitor_pbpm,2), round(tot_install_cost_vh_pbpm, 2)])
])
fig_summary.update_layout(barmode='stack')
fig_summary.update_traces(textposition='outside')
fig_summary.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=500)
fig_summary.update_layout(title=f"Average Cost Per Bed Per Month", template='none',title_x=0.5,yaxis_title="",yaxis_tickprefix = '$')
fig_summary.update_layout(template='simple_white')
top_num = max(tot_cost_competitor_pbpm, tot_cost_vh_pbpm)
top_num+=10
fig_summary.update_yaxes(range=[0,top_num])
vh_text_y = tot_cost_vh_pbpm + 3
fig_summary.add_annotation(x='VH', y=vh_text_y, text=f"${tot_cost_vh_pbpm:,.2f}", showarrow=False, font=dict(
        family="sans serif",
        size=20,
        color="RoyalBlue"
    ))
comp_text_y = tot_cost_competitor_pbpm + 3
fig_summary.add_annotation(x='Competitor', y=comp_text_y, text=f"${tot_cost_competitor_pbpm:,.2f}", showarrow=False, font=dict(
        family="sans serif",
        size=20,
        color="Purple"
    ))
fig_summary.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="center",
    x=0.5
))
# fig_summary.update_layout(color='Set2')
# fig_summary.update_layout(showlegend=False)
main_figure_placeholder.plotly_chart(fig_summary, config=config, use_container_width=True)   




#----------------------------------------------------------------------------------------------------------------
# Do the cumulative calcs and plot
#----------------------------------------------------------------------------------------------------------------
num_facs_for_rollout = 198 #num_facs
monthDFs = []
newFacsMonth = max(round(num_facs_for_rollout/24),1)
wearablesCompPerFac = (band_cost_competitor_pbpm + beacon_cost_competitor_pbpm) * adc  
deviceCompPerFac = (cellular_cost_competitor_pbpm + mdm_cost_competitor_pbpm ) * adc
installCompPerFac = beacon_cost_competitor * adc + (adc / beds_to_device_ratio) * avg_device_cost_competitor + install_cost_competitor
installVH = 275 * adc/beds_to_device_ratio

for month in range(1,5*12):
    
    # Calc # of beds

    facs = min(month * newFacsMonth, num_facs_for_rollout)
    beds = facs * adc
    
    # Calc comp base, install, wearables, MDM costs
    avgCostCompPerBed = competitor_costs_full_df.iloc[0:facs]['Subscription Cost'].mean()
    
    newFacs = min(month * newFacsMonth, num_facs_for_rollout) - min((month-1) * newFacsMonth, num_facs_for_rollout)
    totalCompCost = facs * (avgCostCompPerBed*adc + wearablesCompPerFac + deviceCompPerFac) + newFacs * installCompPerFac
    
    # Calc vh base, install, wearables costs
    if beds < 251:
        costVHBed = 58.5
    elif beds < 501:
        costVHBed = 57.5
    elif beds < 1001:
        costVHBed = 55
    elif beds < 2501:
        costVHBed = 52.5
    elif beds < 5001:
        costVHBed = 50.0
    elif beds < 10001:
        costVHBed = 47.50
    else:
        costVHBed = 45.0
    
    totalVHCost =  beds * (costVHBed + beacon_cost_vh_pbpm) + installVH * newFacs;
    
    monthDFs.append( {'Month':month,
                      'Facilities':facs,
                      'NewFacilities':newFacs,
                      'Beds':beds, 
                      'avgCostCompPerBed':avgCostCompPerBed,
                      'costVHBed':costVHBed,
                      'installVH':installVH,
                      'totalCompCost':totalCompCost,
                      'totalVHCost':totalVHCost} )
    
cost = pd.DataFrame.from_records( monthDFs )
cost['cumComp'] = cost.totalCompCost.cumsum()
cost['cumVH'] = cost.totalVHCost.cumsum()
cost['cumVHSavings'] = cost.cumComp - cost.cumVH

f_txt2 = 'Facility' if num_facs_for_rollout == 1 else 'Facilities'
with st.expander(f"Cumulative Costs"):
    
    t2 = f"Cumulative Costs over 5 years"
    
    st.title(f"Cumulative Costs  \n**2 year rollout of {num_facs_for_rollout} {f_txt2}**")
    st.write("")

    cum_cost_fig = px.line(cost, x='Month', y='cumComp', width=600, height=300)
    cum_cost_fig.add_trace(go.Scatter(y=cost.cumComp, x=cost.Month, mode='lines', name='Competitor'))
    cum_cost_fig.add_trace(go.Scatter(y=cost.cumVH, x=cost.Month, mode='lines', name='VH'))
    cum_cost_fig.update_layout(title=t2,title_x=0.5,yaxis_title="Cumulative $'s",yaxis_tickprefix = '$')
    cum_cost_fig.update_layout(legend=dict( orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01), template='simple_white')
    cum_cost_fig.add_vline(x=59, line_width=2, line_dash="dash", line_color="black")
    cum_cost_fig.add_vline(x=23, line_width=2, line_dash="dash", line_color="blue")
    cum_cost_fig.add_trace(go.Scatter(x=[24],y=[cost.cumComp.max() * .9],mode="text",text=[f"{num_facs_for_rollout} Installed"],textposition="middle right",showlegend = False, textfont=dict(
        family="sans serif",
        size=14,
        color="Blue"
    )))
 
    rc1, rc2, rc3 = st.columns([2,1,1])   
   
    with rc1:
        st.plotly_chart(cum_cost_fig, config=config, use_container_width=True)
    with rc2:
        st.write(" ")
        st.write(" ")
        st.markdown("### Competitor Cumulative  \nat 5 years")
        competitor_cum_tot_cost_annual_placeholder = st.empty()
    with rc3:
        st.write(" ")
        st.write(" ")
        st.markdown("### VH Cumulative  \nat 5 years")
        vh_cum_tot_cost_annual_placeholder = st.empty()

competitor_cum_tot_cost_annual_placeholder.markdown(f'## ${cost.cumComp[58]:,.0f}')
vh_cum_tot_cost_annual_placeholder.markdown(f'## ${cost.cumVH[58]:,.0f}')

#st.table( cost.iloc[-1,:] )

