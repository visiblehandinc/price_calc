import streamlit as st
import plotly.express as px
from plotly import graph_objects as go
import pandas as pd

st.set_page_config(    
    page_title="Price Calculator",
    layout='wide',
    page_icon="✋"
)

st.title("Price Calculator")
st.write(" ")

#----------------------------------------------------------------------------------------------------------------
# Sidebar - Facility Info & Summary Cost per bed
#----------------------------------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Facility Info")
    num_facs = st.slider("Number of facilities to use in calculation", 1, 220, 190)
    adc = st.slider("Average Daily Census", 50, 120, 85)
    # Note: band may have to be replaced for long los, but can ignore for now <-- can use num_days_to_replace
    los = st.slider("Average length of stay", 1, 60, 5)



#----------------------------------------------------------------------------------------------------------------
# Tiers
#----------------------------------------------------------------------------------------------------------------
st.markdown("## Base Cost - Tiers")
ct1, ct2, ct3 = st.columns([1,1,1])
with ct1:
    st.markdown("### Tier 1")
    os_subscription_1 = st.slider("Subscription price (bed/month)", 10.0, 70.0, 40.0, 0.25, format="$%f")

with ct2:
    st.markdown("### Tier 2")    
    os_subscription_2 = st.slider("Subscription price (bed/month)", 10.0, 70.0, 30.0, 0.25, format="$%f")
    num_facs_start_tier_2 = st.slider("Starts at facility #", 1, 50, 26)    

with ct3:
    st.markdown("### Tier 3")  
    os_subscription_3 = st.slider("Subscription price (bed/month)", 10.0, 70.0, 20.0, 0.25, format="$%f")
    num_facs_start_tier_3 = st.slider("Starts at facility #", 1, 220, 201)     

# Tiers for competitor
#----------------------
fac_nums = range(1,221)
# e.g., 26 - 1 = 25
comp_fac_prices_1 = [os_subscription_1] * (num_facs_start_tier_2 - 1)
# 201 - 26 = 175
comp_fac_prices_2 = [os_subscription_2] * (num_facs_start_tier_3 - num_facs_start_tier_2)
# 220 - 201 + 1 = 20
comp_fac_prices_3 = [os_subscription_3] * (220 - num_facs_start_tier_3 + 1)
comp_fac_prices = comp_fac_prices_1 + comp_fac_prices_2 + comp_fac_prices_3

comp_tiers_df = pd.DataFrame({'Facility Count': fac_nums, 'Subscription Cost': comp_fac_prices})
# chop off the df based on number of facs being used in the calc
n = num_facs - 1
comp_tiers_chopped_df = comp_tiers_df.iloc[0:n]
avg_sub_cost_comp = round(comp_tiers_chopped_df['Subscription Cost'].mean(), 2)

comp_tiers_fig = px.line(comp_tiers_chopped_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
comp_tiers_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_comp, y1=avg_sub_cost_comp, line=dict(color="Gray", width=2, dash="dot"))   
comp_tiers_fig.add_annotation(x=num_facs / 2, y=avg_sub_cost_comp, text=f"Average per bed = ${avg_sub_cost_comp}", showarrow=False, yshift=10, arrowhead=1)  
comp_tiers_fig.update_yaxes(range=[0,85])


# Tiers for VH
#----------------------
num_beds = num_facs * adc

vh_bed_prices_1 = [58.5] * 250
vh_bed_prices_2 = [57.5] * 250
vh_bed_prices_3 = [55] * 500
vh_bed_prices_4 = [52.5] * 1500
vh_bed_prices_5 = [50] * 2500
vh_bed_prices_6 = [47.5] * 5000
vh_bed_prices_7 = [45] * 10000
vh_bed_prices = vh_bed_prices_1 + vh_bed_prices_1 + vh_bed_prices_3 + vh_bed_prices_4 + vh_bed_prices_5 + vh_bed_prices_6 + vh_bed_prices_7
# chop off ones that are not being used
vh_bed_prices = vh_bed_prices[0:num_beds]

fac_num_list = []
for i in range(num_facs):
    f = [i+1] * adc
    fac_num_list.extend(f)


vh_tiers_df = pd.DataFrame({'Facility Count': fac_num_list, 'Subscription Cost': vh_bed_prices})

vh_tiers_df = vh_tiers_df.groupby('Facility Count')['Subscription Cost'].mean().reset_index()

avg_sub_cost_vh = round(vh_tiers_df['Subscription Cost'].mean(), 2)

vh_tiers_fig = px.line(vh_tiers_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
vh_tiers_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_vh, y1=avg_sub_cost_vh, line=dict(color="Gray", width=2, dash="dot"))
vh_tiers_fig.add_annotation(x=num_facs / 2  , y=avg_sub_cost_vh, text=f"Average per bed = ${avg_sub_cost_vh}", showarrow=False, yshift=10, arrowhead=1)  
vh_tiers_fig.update_yaxes(range=[0,85])


# Show the competitor tier figs - we have not added in extra costs yet.
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(comp_tiers_fig)
with c2:
    st.plotly_chart(vh_tiers_fig)

st.markdown("------")

#----------------------------------------------------------------------------------------------------------------
# Wearables
#----------------------------------------------------------------------------------------------------------------

st.markdown("## Additional Costs from Wearables")
bc1, _, bc2 = st.columns([3,1,3])
with bc1:
    st.markdown("### Bands")    
    band_cost = st.slider("Cost of a single band", 0.25, 25.0, 3.0, 0.25, format="$%f")
    # single_use = st.checkbox("Single use?", True)
    # if not single_use:
    #     num_days_band_replace = st.slider("Average number of days to replace a band", 5, 365, 30)

    # assuming it is single use
    band_cost_per_bed = 30 / los * band_cost
    st.write(f"Additional per bed cost = ${round(band_cost_per_bed, 2)}")

with bc2:
    st.markdown("### Beacons")       
    beacon_cost = st.slider("Cost of a single beacon", 1.0, 100.0, 30.0, 0.5, format="$%f")
    num_months_beacon_life = st.slider("Average number of months until beacon fails (due to battery, defects, or other breakage)", 1, 60, 10)        
    loss_rate_per_month_beacons = st.slider("Average percent of beacons lost per month", 0, 50, 15,format="%f")  

    beacon_cost_per_bed = (1-(loss_rate_per_month_beacons/100)) ** num_months_beacon_life * (beacon_cost / num_months_beacon_life) + (beacon_cost * (loss_rate_per_month_beacons/100))
    vh_addn_beacon_cost_per_bed = loss_rate_per_month_beacons/100 * 25
    st.write(f"Additional per bed cost (competitor)= ${round(beacon_cost_per_bed, 2)}")
    st.write(f"Additional per bed cost (VH)= ${round(vh_addn_beacon_cost_per_bed, 2)}")



# add in the additional costs to the comp df
comp_tiers_chopped_df['Wearables Cost'] = comp_tiers_chopped_df['Subscription Cost'] + (band_cost_per_bed + beacon_cost_per_bed)

vh_tiers_df['Wearables Cost'] = vh_tiers_df['Subscription Cost'] + (vh_addn_beacon_cost_per_bed)


# do the new figures
# ------------------
avg_sub_cost_comp_with_wearables = round(comp_tiers_chopped_df['Wearables Cost'].mean(), 2)
comp_wearables_fig = px.line(comp_tiers_chopped_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
comp_wearables_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_comp_with_wearables, y1=avg_sub_cost_comp_with_wearables, line=dict(color="Gray", width=2, dash="dot"))   
comp_wearables_fig.add_annotation(x=num_facs / 2, y=avg_sub_cost_comp_with_wearables, text=f"Average per bed = ${avg_sub_cost_comp_with_wearables}", showarrow=False, yshift=10, arrowhead=1)  
comp_wearables_fig.update_yaxes(range=[0,85])
comp_wearables_fig.add_trace(go.Scatter(y=comp_tiers_chopped_df['Wearables Cost'], x=comp_tiers_chopped_df['Facility Count'], mode='lines', name='additional'))

avg_sub_cost_vh_with_wearables = round(vh_tiers_df['Wearables Cost'].mean(), 2)
vh_wearables_fig = px.line(vh_tiers_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
vh_wearables_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_vh_with_wearables, y1=avg_sub_cost_vh_with_wearables, line=dict(color="Gray", width=2, dash="dot"))
vh_wearables_fig.add_annotation(x=num_facs / 2  , y=avg_sub_cost_vh_with_wearables, text=f"Average per bed = ${avg_sub_cost_vh_with_wearables}", showarrow=False, yshift=10, arrowhead=1)  
vh_wearables_fig.update_yaxes(range=[0,85])
vh_wearables_fig.add_trace(go.Scatter(y=vh_tiers_df['Wearables Cost'], x=vh_tiers_df['Facility Count'], mode='lines', name='additional'))

cc1, cc2 = st.columns(2)
with cc1:
    st.plotly_chart(comp_wearables_fig)
with cc2:
    st.plotly_chart(vh_wearables_fig)

st.markdown("------")


#----------------------------------------------------------------------------------------------------------------
# Devices
#----------------------------------------------------------------------------------------------------------------

st.markdown("## Additional Costs for Devices & Management")
dc1, _, dc2 = st.columns([3,1,3])
with dc1:
    st.markdown("### Beds : Device Ratio")
    beds_to_device_ratio = st.slider("Ratio of number of beds per device", 3, 20, 5, format="%d")
    st.markdown("### Connectivity")
    cellular_cost_per_phone_per_month = st.slider("Average Celluar Data cost, per device, per month", 0, 40, 18, format="$%f")
    cellular_cost_per_bed = cellular_cost_per_phone_per_month / beds_to_device_ratio
    st.write(f"Additional per bed cost = ${cellular_cost_per_bed}")

with dc2:
    st.markdown("### Management & Support")    
    mdm_software_cost_per_phone_per_year = st.slider("MDM software cost, per device, per year", 16, 20, 16)
    num_devices_per_fte = st.slider("Number of devices a single FTE can fully support", 100, 1000, 300)
    salary_fte = st.slider("'Fully loaded' salary for new IT FTE", 50000, 150000, 90000, 5000, format="$%f")
    mdm_cost_per_bed = mdm_software_cost_per_phone_per_year/(12 * beds_to_device_ratio) + (salary_fte / 12) / (beds_to_device_ratio * num_devices_per_fte)
    st.write(f"Additional per bed cost = ${round(mdm_cost_per_bed, 2)}")


comp_tiers_chopped_df['Devices Cost'] = comp_tiers_chopped_df['Wearables Cost'] + (cellular_cost_per_bed + mdm_cost_per_bed)



# do the new figures
# ------------------
avg_sub_cost_comp_with_devices = round(comp_tiers_chopped_df['Devices Cost'].mean(), 2)
comp_devices_fig = px.line(comp_tiers_chopped_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
comp_devices_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_comp_with_devices, y1=avg_sub_cost_comp_with_devices, line=dict(color="Gray", width=2, dash="dot"))   
comp_devices_fig.add_annotation(x=num_facs / 2, y=avg_sub_cost_comp_with_devices, text=f"Average per bed = ${avg_sub_cost_comp_with_devices}", showarrow=False, yshift=10, arrowhead=1)  
comp_devices_fig.update_yaxes(range=[0,85])
comp_devices_fig.add_trace(go.Scatter(y=comp_tiers_chopped_df['Devices Cost'], x=comp_tiers_chopped_df['Facility Count'], mode='lines', name='additional'))


ccc1, ccc2 = st.columns(2)
with ccc1:
    st.plotly_chart(comp_devices_fig)
with ccc2:
    st.plotly_chart(vh_wearables_fig)

st.markdown("------")





with st.sidebar:
    # fig_summary = px.bar(x=["VH", "Competitor"], y=[avg_sub_cost_vh_with_wearables, avg_sub_cost_comp_with_devices], color=['Gray', 'purple'], title="Average Price per bed per month", width=330) 
    comp_wearables_cost = avg_sub_cost_comp_with_wearables - avg_sub_cost_comp
    comp_devices_cost = avg_sub_cost_comp_with_devices - avg_sub_cost_comp_with_wearables
    vh_wearables_cost = avg_sub_cost_vh_with_wearables - avg_sub_cost_vh
    companies = ['VH', 'Competitor']
    fig_summary = go.Figure(data=[
        go.Bar(name='Base', x=companies, y=[avg_sub_cost_vh, avg_sub_cost_comp]),
        go.Bar(name='Wearables', x=companies, y=[vh_wearables_cost, comp_wearables_cost]),
        go.Bar(name='Devices', x=companies, y=[0, comp_devices_cost], text=[avg_sub_cost_vh_with_wearables, avg_sub_cost_comp_with_devices])
    ])
    fig_summary.update_layout(barmode='stack')
    fig_summary.update_traces(textposition='outside')
    fig_summary.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=330)
    fig_summary.update_layout(title="Average Price / Bed", template='none')
    fig_summary.update_yaxes(range=[0,85])

    # fig_summary.update_layout(showlegend=False)
    st.plotly_chart(fig_summary)   
