import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import altair as alt


st.set_page_config(page_title='Ticketing dashboard',page_icon=':bar_chart:',layout='wide')
st.title(':bar_chart: Ticketing Dashboard')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

@st.cache_data
def load_model(model_name):
    data = pd.read_excel(model_name)
    return data
data = load_model('Raw_Data.xlsx')

#Side Bar data
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)

start_date = pd.to_datetime(st.sidebar.date_input('Start Date',pd.to_datetime(data['Date']).min()))
end_date = pd.to_datetime(st.sidebar.date_input('End Date',pd.to_datetime(data['Date']).max()))

df_date = data[(pd.to_datetime(data['Date'])>=start_date) & (pd.to_datetime(data['Date'])<=end_date)].copy()

#Filters
zone = st.sidebar.multiselect(
    'Select Zone', 
    options=df_date['Zoho.Zone'].unique(),
    default=df_date['Zoho.Zone'].unique()   
)
branch = st.sidebar.multiselect(
    'Select Branch', 
    options=df_date['Location'].unique(),
    default=df_date['Location'].unique()
    )
category = st.sidebar.multiselect(
    'Select Category', 
    options=df_date['Categories'].unique(),
    default=df_date['Categories'].unique()
    
)
df = df_date.query(
    "`Zoho.Zone`==@zone & Location==@branch & Categories==@category"
) 


# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Tickets Count
tc = df['Location'].count()
Branch_count = df['Location'].nunique()
ticket_closed = df['Eng. Status'].value_counts()['Closed']
ticket_open = df['Eng. Status'].value_counts()['open']

# Donut Data
tic_nontic = df['CIC/NON-CIC'].count()
tic = df['CIC/NON-CIC'].value_counts()['CIC']
tic_Percentage = round((tic/tic_nontic)*100)
nontic_percentage = round(((tic_nontic-tic)/tic_nontic)*100)

donut_chart_tic = make_donut(tic_Percentage, 'Inbound Migration', 'green')
donut_chart_nontic = make_donut(nontic_percentage, 'Outbound Migration', 'red') 
# CSS styling
st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #393939;
    border-left: 10px solid #F71938;
    padding: 15px 0;
    border-radius: 5px;
    box-shadow:#F71938;
}
[data-testid="stMetricLabel"] {
  display: flex;
  padding-left: 20px;
  color: white;
  justify-content: center;
  align-items: center;
}
[data-testid="stMetricValue"] {
  display: flex;
  padding-left: 20px;
  color: white;
  justify-content: center;
  align-items: center;
}

</style>
""", unsafe_allow_html=True)

col1, col2,col3 = st.columns(3)

with col1:
    st.subheader('Dataset Metrics', divider='rainbow',)
    c1, c2, = st.columns(2)
    
    c1.metric(label="Total Tickets ", value="{:,}".format(tc))
    c2.metric(label="Total Branches", value= "{:,}".format(Branch_count))
    
    c3,c4 = st.columns(2)
    c3.metric(label="Total Tickets Closed ", value="{:,}".format(ticket_closed))
    c4.metric(label="Total Tickets Open", value="{:,}".format(ticket_open))
    
    c5,c6 = st.columns(2)
    c5.markdown("<style>div.stMarkdown {text-align: center}</style>", unsafe_allow_html=True)
    c6.markdown("<style>div.stMarkdown {text-align: center}</style>", unsafe_allow_html=True)

    with c5:
        st.write('CIC Ticket Raised %')
        st.altair_chart(donut_chart_tic)
    with c6:
        st.write('NON-CIC Ticket Raised %')
        st.altair_chart(donut_chart_nontic)

with col2:
    st.subheader('Priority Status', divider='rainbow',)
    # Pie Chart
    priority_counts = df['Priority'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']

    # Create an interactive pie chart using Plotly Express
    fig = px.pie(priority_counts, values='Count', names='Priority')

    # Display the pie chart
    st.plotly_chart(fig, use_container_width=True)

Branchwise = df['Location'].value_counts().reset_index().rename(columns={'Location': 'Branch', 'count': 'Total_Tickets'})

with col3:
    st.subheader('Branch Wise Tickets', divider='rainbow',)

    st.dataframe(Branchwise,
                 column_order=("Branch", "Total_Tickets"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Branch": st.column_config.TextColumn(
                        "Branch",
                    ),
                    "Total_Tickets": st.column_config.ProgressColumn(
                        "Total_Tickets",
                        format="%f",
                        min_value=0,
                        max_value=max(Branchwise.Total_Tickets),
                     )} 
                 )
    
# Select only the columns 'Zoho.Zone' and 'Eng. Days Range'
subset_df = df[['Zoho.Zone', 'Eng. Days Range']]

# Pivot the DataFrame to reshape it
pivot_df = subset_df.pivot_table(index='Zoho.Zone', columns='Eng. Days Range', aggfunc='size', fill_value=0).rename_axis(index='Zone')

# Define the custom order for the index labels
custom_order = ['Zone 1A', 'Zone 1B', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5', 'Zone 6', 'Zone 7', 'Zone 8', 'Zone 9', 'Zone 10']

# Reindex the DataFrame with the custom order
pivot_df = pivot_df.reindex(custom_order)

col4, col5 = st.columns([0.3,0.7])

with col4:
    # Display the pivot table
    st.subheader('Zone & Bracket Wise Tickets', divider='rainbow',)
    st.write(pivot_df)
    
subdata = df[['Eng. Status','Eng. Days Range']]
p_df = subdata.pivot_table(index='Eng. Days Range', columns='Eng. Status',aggfunc='size',fill_value=0).rename_axis(index='Days_Range') 
# Reset index
p_df.reset_index(inplace=True)
with col5:
    trace_closed = go.Bar(
        x=p_df['Days_Range'],
        y=p_df['Closed'],
        name='Closed',
        marker=dict(color='#7d3f05'),
        text=p_df['Closed'],  # Use the 'Closed' values as text labels
        textposition='auto'  # Automatically position the text
    )
    trace_open = go.Bar(
        x=p_df['Days_Range'],
        y=p_df['open'],
        name='Open',
        marker=dict(color='#edc6a1'),
        text=p_df['open'],  # Use the 'Open' values as text labels
        textposition='auto'  # Automatically position the text
    )

    # Layout
    layout = go.Layout(
        xaxis=dict(title='Days Range'),
        yaxis=dict(title='Number of Tickets')
    )

    # Plot
    fig = go.Figure(data=[trace_closed, trace_open], layout=layout)
    st.subheader('Number of Tickets by Days Range', divider='rainbow',)
    st.plotly_chart(fig, use_container_width=True)
    
col6,col7 = st.columns(2)
zsubdata = df[['Eng. Status','Zoho.Zone']]
zp_df = zsubdata.pivot_table(index='Zoho.Zone', columns='Eng. Status',aggfunc='size',fill_value=0).rename_axis(index='Zone') 

zp_df = zp_df.reindex(custom_order)
# Reset index
zp_df.reset_index(inplace=True)

with col6:
    trace_closed = go.Bar(
            y=zp_df['Zone'],  # Switched to y-axis
            x=zp_df['Closed'],      # Switched to x-axis
            name='Closed',
            orientation='h',       # Set orientation to horizontal
            marker=dict(color='#393939'),
            text=zp_df['Closed'],   # Use the 'Closed' values as text labels
            textposition='auto',    # Automatically position the text
            textfont=dict(size=18)
        )
    trace_open = go.Bar(
            y=zp_df['Zone'],  # Switched to y-axis
            x=zp_df['open'],        # Switched to x-axis
            name='Open',
            orientation='h',       # Set orientation to horizontal
            marker=dict(color='red'),
            text=zp_df['open'],     # Use the 'Open' values as text labels
            textposition='auto',    # Automatically position the text
            textfont=dict(size=18)
        )

    # Layout
    layout = go.Layout(
        xaxis=dict(title='Number of Tickets'),  # Adjust axis labels accordingly
        yaxis=dict(title='Days Range'),           # Adjust axis labels accordingly
        height=600,  # Increase the height of the plot
        margin=dict(l=200)  # Adjust the left margin to accommodate larger labels
    )

    # Plot
    fig = go.Figure(data=[trace_closed, trace_open], layout=layout)
    st.subheader('Zone Wise Ticket Status', divider='rainbow',)
    st.plotly_chart(fig, use_container_width=True)
    
d_catogeries = df['Sub-Category'].value_counts().reset_index().rename(columns={'count': 'Total_Tickets'})

with col7:
    # Define the color scale using the min and max values of your data
    min_value = d_catogeries['Total_Tickets'].min()
    max_value = d_catogeries['Total_Tickets'].max()
    color_scale = [[0, '#393939'], [1, '#ff0000']]  # Using black (#393939) for minimum value and red (#ff0000) for maximum value

    tickets = go.Bar(
        x=d_catogeries['Total_Tickets'],
        y=d_catogeries['Sub-Category'],
        name='Total Tickets',
        orientation='h',
        marker=dict(color=d_catogeries['Total_Tickets'], coloraxis='coloraxis'),
        text=d_catogeries['Total_Tickets'],  # Use the 'Total_Tickets' values as text labels
        textposition='auto'  # Automatically position the text
    )
    # Layout
    layout = go.Layout(
        coloraxis=dict(colorscale=color_scale),
        xaxis=dict(title='Number of Tickets'),  # Adjust axis labels accordingly
        yaxis=dict(title='Categories'),           # Adjust axis labels accordingly
        height=600,  # Increase the height of the plot
        margin=dict(l=200)  # Adjust the left margin to accommodate larger labels
    )

    # Plot
    fig = go.Figure(data=tickets, layout=layout)
    st.subheader('Category Wise Ticket Status', divider='rainbow',)
    st.plotly_chart(fig, use_container_width=True)

st.subheader('TICKETS DATASET', divider='rainbow',)   
with st.expander("VIEW TICKETS DATASET"):
    showData=st.multiselect('Filter: ',df.columns,default=["Date","Zoho.Zone","Location","ServiceRequestNo","Categories","Sub-Category","Priority","Status","Eng. Status","Eng. Days Range","Ops.Status","OpsDays Range"])
    st.dataframe(df[showData],use_container_width=True)



