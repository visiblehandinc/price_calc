import streamlit as st
import plotly.express as px
from plotly import graph_objects as go
import pandas as pd

st.set_page_config(    
    page_title="True Price Calculator",
    layout='wide',
    page_icon="✋"
)

st.title("True Price Calculator")
st.write(" ")

# Hide toolbars for charts
config={'displayModeBar': False}

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
st.markdown("## Competitor's Base Cost - Tiers")
ct1, ct2, ct3 = st.columns([1,1,1])
with ct2:
    st.markdown("### Tier 2")    
    os_subscription_2 = st.slider("Subscription price (bed/month)", 10.0, 70.0, 30.0, 0.25, format="$%f")
    num_facs_start_tier_2 = st.slider("Starts at facility #", 1, 50, 26)    

with ct3:
    st.markdown("### Tier 3")  
    os_subscription_3 = st.slider("Subscription price (bed/month)", 10.0, 70.0, 20.0, 0.25, format="$%f")
    num_facs_start_tier_3 = st.slider("Starts at facility #", 1, 220, 201)     
    
with ct1:
    st.markdown("### Tier 1")
    os_subscription_1 = st.slider("Subscription price (bed/month)", 10.0, 70.0, 40.0, 0.25, format="$%f", help = f"VH Tiers are 'retroactive' in that all subscribed beds across facilities receive the the new tier price.  It is unlikely that Competitor applies tiers this way because (at the current settings) their monthly charges will drop ${(os_subscription_2-os_subscription_3)*num_facs_start_tier_3*adc:,.0f} when facility {num_facs_start_tier_3} goes live.")

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
n = num_facs
comp_tiers_chopped_df = comp_tiers_df.iloc[0:n]
avg_sub_cost_comp = comp_tiers_chopped_df['Subscription Cost'].mean()

comp_tiers_fig = px.line(comp_tiers_chopped_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
comp_tiers_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_comp, y1=avg_sub_cost_comp, line=dict(color="Gray", width=2, dash="dot"))   
comp_tiers_fig.add_annotation(x=num_facs / 2, y=avg_sub_cost_comp, text=f"Average per bed = ${avg_sub_cost_comp:.2f}", showarrow=False, yshift=10, arrowhead=1)  
comp_tiers_fig.update_yaxes(range=[0,85])
comp_tiers_fig.update_layout(title="Competitor", title_x=0.5,yaxis_title="Cost (per bed/month)",yaxis_tickprefix = '$')


# Tiers for VH
#----------------------
num_beds = num_facs * adc

vh_price = 0
if num_beds < 251:
    vh_price = 58.8
elif num_beds < 501:
    vh_price = 57.5
elif num_beds < 1001:
    vh_price = 55
elif num_beds < 2501:
    vh_price = 52.5
elif num_beds < 5001:
    vh_price = 50.0
elif num_beds < 10001:
    vh_price = 45.0
else:
    vh_price = 45.0

vh_bed_prices = [vh_price] * num_beds    

fac_num_list = []
for i in range(num_facs):
    f = [i+1] * adc
    fac_num_list.extend(f)


vh_tiers_df = pd.DataFrame({'Facility Count': fac_num_list, 'Subscription Cost': vh_bed_prices})

vh_tiers_df = vh_tiers_df.groupby('Facility Count')['Subscription Cost'].mean().reset_index()

avg_sub_cost_vh = vh_tiers_df['Subscription Cost'].mean()

vh_tiers_fig = px.line(vh_tiers_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
vh_tiers_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_vh, y1=avg_sub_cost_vh, line=dict(color="Gray", width=2, dash="dot"))
vh_tiers_fig.add_annotation(x=num_facs / 2  , y=avg_sub_cost_vh, text=f"Average per bed = ${avg_sub_cost_vh:.2f}", showarrow=False, yshift=10, arrowhead=1)  
vh_tiers_fig.update_yaxes(range=[0,85])
vh_tiers_fig.update_layout(title="VisibleHand",title_x=0.5,yaxis_title="Cost (per bed/month)",yaxis_tickprefix = '$')


# Show the competitor tier figs - we have not added in extra costs yet.
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(comp_tiers_fig, config=config)
with c2:
    st.plotly_chart(vh_tiers_fig, config=config)

st.markdown("------")

#----------------------------------------------------------------------------------------------------------------
# Wearables
#----------------------------------------------------------------------------------------------------------------

st.markdown("## Additional Costs from Wearables")
bc1, _, bc2 = st.columns([3,1,3])
with bc1:
    st.markdown("### Bands")    
    band_cost = st.slider("Cost of a single band", 0.25, 25.0, 3.0, 0.25, format="$%f",help="Bands are at best, single use. Sometimes more than 1 band might be needed for a patient during their treatment. This 'small' expense can add up quickly with volume.  Competitor has had customers churn after the initial contract term b/c of sticker shock of the consumables.")

    # single_use = st.checkbox("Single use?", True)
    # if not single_use:
    #     num_days_band_replace = st.slider("Average number of days to replace a band", 5, 365, 30)

    # assuming it is single use
    band_cost_per_bed = 30 / los * band_cost
    st.write(f"Additional per bed cost = ${band_cost_per_bed:.2f}")

with bc2:
    st.markdown("### Beacons")       
    beacon_cost = st.slider("Cost of a single beacon", 1.0, 100.0, 30.0, 0.5, format="$%f")
    num_months_beacon_life = st.slider("Average number of months until beacon replacement (usually due to battery)", 1, 60, 10, help="VisibleHand replaces all non-working beacons for free.")        
    loss_rate_per_month_beacons = st.slider("Average percent of beacons lost per month", 0, 50, 0, format="%f", help="Beacons have a large 'unplanned cost' potential if not managed well. We created a 'beacon tracker' module to help facilities better manage their loss rate to reduce costs.  In our experience, the loss rate is 10-30% depending on the facility's process control.")  

    beacon_cost_per_bed = (1-(loss_rate_per_month_beacons/100)) ** num_months_beacon_life * (beacon_cost / num_months_beacon_life) + (beacon_cost * (loss_rate_per_month_beacons/100))
    vh_addn_beacon_cost_per_bed = loss_rate_per_month_beacons/100 * 25
    st.write(f"Additional per bed cost (Competitor)= ${beacon_cost_per_bed:.2f}")
    st.write(f"Additional per bed cost (VH)= ${vh_addn_beacon_cost_per_bed:.2f}")



# add in the additional costs to the comp df
comp_tiers_chopped_df['Wearables Cost'] = comp_tiers_chopped_df['Subscription Cost'] + (band_cost_per_bed + beacon_cost_per_bed)

vh_tiers_df['Wearables Cost'] = vh_tiers_df['Subscription Cost'] + (vh_addn_beacon_cost_per_bed)


# do the new figures
# ------------------
avg_sub_cost_comp_with_wearables = comp_tiers_chopped_df['Wearables Cost'].mean()
comp_wearables_fig = px.line(comp_tiers_chopped_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
comp_wearables_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_comp_with_wearables, y1=avg_sub_cost_comp_with_wearables, line=dict(color="Gray", width=2, dash="dot"))   
comp_wearables_fig.add_annotation(x=num_facs / 2, y=avg_sub_cost_comp_with_wearables, text=f"Average per bed = ${avg_sub_cost_comp_with_wearables:.2f}", showarrow=False, yshift=10, arrowhead=1)  
comp_wearables_fig.update_yaxes(range=[0,85])
comp_wearables_fig.add_trace(go.Scatter(y=comp_tiers_chopped_df['Wearables Cost'], x=comp_tiers_chopped_df['Facility Count'], mode='lines', name='additional costs'))
comp_wearables_fig.update_layout(title="Competitor",title_x=0.5,yaxis_title="Cost (per bed/month)",yaxis_tickprefix = '$')
comp_wearables_fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=0.02, xanchor="right", x=1))

avg_sub_cost_vh_with_wearables = vh_tiers_df['Wearables Cost'].mean()
vh_wearables_fig = px.line(vh_tiers_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
vh_wearables_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_vh_with_wearables, y1=avg_sub_cost_vh_with_wearables, line=dict(color="Gray", width=2, dash="dot"))
vh_wearables_fig.add_annotation(x=num_facs / 2  , y=avg_sub_cost_vh_with_wearables, text=f"Average per bed = ${avg_sub_cost_vh_with_wearables:.2f}", showarrow=False, yshift=10, arrowhead=1)  
vh_wearables_fig.update_yaxes(range=[0,85])
vh_wearables_fig.add_trace(go.Scatter(y=vh_tiers_df['Wearables Cost'], x=vh_tiers_df['Facility Count'], mode='lines', name='additional costs'))
vh_wearables_fig.update_layout(title="VisibleHand",title_x=0.5,yaxis_title="Cost (per bed/month)",yaxis_tickprefix = '$')
vh_wearables_fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=0.02, xanchor="right", x=1))

cc1, cc2 = st.columns(2)
with cc1:
    st.plotly_chart(comp_wearables_fig, config=config)
with cc2:
    st.plotly_chart(vh_wearables_fig, config=config)

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
    st.write(f"Additional per bed cost = ${cellular_cost_per_bed:.2f}")
    
    if cellular_cost_per_phone_per_month == 0:
        st.warning("If set to $0 due to Wifi plans, note that Wifi carries additional IT and support costs b/c it tends to fail more and connectivity issues are much harder to diagnose (and rule out) with wifi than with cellular.")

with dc2:
    st.markdown("### Management & Support")    
    mdm_software_cost_per_phone_per_year = st.slider("MDM software cost, per device, per year", 10, 25, 16)
    num_devices_per_fte = st.slider("Number of devices a single FTE can fully support", 100, 1000, 300, 25, help = "Note: Lower if planning to use WiFi (see connectivity note).  \nAs a mobile application, success is inextricably linked with device performance, maintainence, security, and uptime. Offering device management (alongside connectivity & software) allows us to optimize the full scope of delivery a successful launch & long-term reliability.")
    salary_fte = st.slider("'Fully loaded' salary for new IT FTE", 50000, 150000, 90000, 5000, format="$%f", help = "Note: mid-level IT hire.  \nVH remotely manages all devices included in the subscription cost... this includes lockdown, GPS tracking & geofence alerts, software/phone updating, remote shutdown, SIM management, connection management, broadcating management alerts to the phones, etc...  All of these functions will be the responsibility of UHS if OS is used.")
    mdm_cost_per_bed = mdm_software_cost_per_phone_per_year/(12 * beds_to_device_ratio) + (salary_fte / 12) / (beds_to_device_ratio * num_devices_per_fte)
    st.write(f"Additional per bed cost = ${mdm_cost_per_bed:.2f}")


comp_tiers_chopped_df['Devices Cost'] = comp_tiers_chopped_df['Wearables Cost'] + (cellular_cost_per_bed + mdm_cost_per_bed)



# do the new figures
# ------------------
avg_sub_cost_comp_with_devices = comp_tiers_chopped_df['Devices Cost'].mean()
comp_devices_fig = px.line(comp_tiers_chopped_df, x='Facility Count', y='Subscription Cost', width=600, height=300)
comp_devices_fig.add_shape(type='line', x0=1, x1=num_facs, y0=avg_sub_cost_comp_with_devices, y1=avg_sub_cost_comp_with_devices, line=dict(color="Gray", width=2, dash="dot"))   
comp_devices_fig.add_annotation(x=num_facs / 2, y=avg_sub_cost_comp_with_devices, text=f"Average per bed = ${avg_sub_cost_comp_with_devices:.2f}", showarrow=False, yshift=10, arrowhead=1)  
comp_devices_fig.update_yaxes(range=[0,85])
comp_devices_fig.add_trace(go.Scatter(y=comp_tiers_chopped_df['Devices Cost'], x=comp_tiers_chopped_df['Facility Count'], mode='lines', name='additional costs'))
comp_devices_fig.update_layout(title="Competitor",title_x=0.5,yaxis_title="Cost (per bed/month)",yaxis_tickprefix = '$')
comp_devices_fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=0.02, xanchor="right", x=1))

ccc1, ccc2 = st.columns(2)
with ccc1:
    st.plotly_chart(comp_devices_fig, config=config)
with ccc2:
    st.plotly_chart(vh_wearables_fig, config=config)

st.markdown("------")



st.markdown("## One-Time Costs")

ccc1, _, ccc3 = st.columns([2,1,2])

total_vh = round(num_beds / beds_to_device_ratio * 275)
    
with ccc1:
    st.markdown("### Competitor")
    st.text(f"Beacons =    ${1.3* beacon_cost * num_beds:,.0f}")
    st.text(f"Devices =    ${(num_beds / beds_to_device_ratio) * 430:,.0f}")
    #install_cost = st.number_input("Install Cost", 0)
    install_cost = st.slider("Install Cost", 0, 5000, 1000, 100, format="$%d")
    st.write("--")
    total_comp = beacon_cost * num_beds + (num_beds / beds_to_device_ratio) * 430 + install_cost * num_facs
    st.text(f"Total =      ${total_comp:,.0f}")
    st.text(f"Cost Diff =  ${total_comp:,.0f} - ${total_vh:,.0f}")
    st.text(f"Cost Diff =  ${total_comp -total_vh:,.0f}")
    
    st.write(f"One Time Costs, **not included in summary**.  \nAmortized over 1 year:  \nExtra per bed per month = **${(total_comp - total_vh)/(adc * 12 * num_facs):,.2f}**")
   

with ccc3:
    st.markdown("### VisibleHand")
    st.text(f"Beacons =  $0")
    st.text(f"Devices =    ${round(num_beds / beds_to_device_ratio * 275):,.0f}")
    st.text(f"Install =    $0")
    st.text(" ")
    st.text(" ")
    st.text(" ")
    st.text(" ")
    st.text("--")
    st.text(f"Total =      ${total_vh:,.0f}")


with st.sidebar:
    comp_wearables_cost = avg_sub_cost_comp_with_wearables - avg_sub_cost_comp
    comp_devices_cost = avg_sub_cost_comp_with_devices - avg_sub_cost_comp_with_wearables
    vh_wearables_cost = avg_sub_cost_vh_with_wearables - avg_sub_cost_vh
    companies = ['Competitor', 'VH']
    fig_summary = go.Figure(data=[
        go.Bar(name='Base', x=companies, y=[round(avg_sub_cost_comp,2), round(avg_sub_cost_vh,2)]),
        go.Bar(name='Wearables', x=companies, y=[round(comp_wearables_cost,2), round(vh_wearables_cost,2)]),
        go.Bar(name='Devices', x=companies, y=[round(comp_devices_cost,2), 0], text=[f"${avg_sub_cost_comp_with_devices:.2f}", f"${avg_sub_cost_vh_with_wearables:.2f}"])
    ])
    fig_summary.update_layout(barmode='stack')
    fig_summary.update_traces(textposition='outside')
    fig_summary.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=330)
    fig_summary.update_layout(title="Average Price / Bed", template='none',title_x=0.5,yaxis_title="Cost (per bed/month)",yaxis_tickprefix = '$')
    fig_summary.update_yaxes(range=[0,85])

    # fig_summary.update_layout(showlegend=False)
    st.plotly_chart(fig_summary, config=config)   
