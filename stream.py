import streamlit as st
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.express as px 
from sqlalchemy import create_engine
from streamlit_option_menu import option_menu 
import mysql.connector

#Set name
st.set_page_config(page_title="Project - IMDb MOVIES 2024", layout="wide")

#Connect MySQL
def get_connection():
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="31byymmafmh6WEp.root",
    password="KU0Fz7gGZcxq5XwF",
    port = 4000
    database = 'imdb'
    engine = create_engine("mysql+mysqlconnector://31byymmafmh6WEp.root:KU0Fz7gGZcxq5XwF@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/imdb")
    return engine

#Load Data
def load_data():
    try:
        engine = get_connection()
        query = "SELECT * FROM imdb_2024"
        df = pd.read_sql(query, engine)
        df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
        df['Duration_hours'] = df['Duration'] / 60
        df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame() #Return empty DataFrame if loading fails
    
df = load_data()
if df.empty:
    st.stop()

#Add logo ,filters,name to page
col1, col2,col3= st.columns(3) #

with st.sidebar:
    #st.image("\SYMBOL.jpeg",width=300)
    #Add badge in top-left corner of the first column
    st.markdown("""
        <div style='
        display: inline-block;
        background-color: #96f222;
        color: Black;
        font-weight: bold;
        font-size: 35px;
        padding: 16px 75px;
        border-radius: 15px;
        font-family: Arial, sans-serif;
        '>
         IMDb
        </div>
    """, unsafe_allow_html=True)
    st.header(" 🔍 FILTER")

st.markdown("""
    <style>
    /* Main app container */
    .stApp {
        background: linear-gradient(135deg, #15071a);
        font-family: 'Poppins', sans-serif;
        color: #cd86e3;
    }

    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(180deg,#2b292b);
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
        box-shadow: 5px 0 10px rgba(0, 0, 0, 0.15);
    }

    /* Main content area */
    .main {
        background-color: #042f3d;
        margin-top: 0rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease-in-out;
    }

    </style>
""", unsafe_allow_html=True)

unique_genres = df['Genre'].unique()
selected_genres = st.sidebar.multiselect(
    "Pick your Genre",
     options=unique_genres,
     default=unique_genres,
     key="genre_selector"  
     )



votes_min = int(df["Votes"].min())
votes_max = int(df["Votes"].max())
min_votes = st.sidebar.slider(
    "Range Of Votes",
     min_value=0,
     max_value=int(df['Votes'].max()),
     value=100,
     key="min_votes_slider"  
     )

min_duration = st.sidebar.slider(
    "Duration Range",
     min_value=0,
     max_value=int(df['Duration'].max()),
     value=120,
     key="min_duration_slider"
     )

rating_min = float(df["Rating"].min())
rating_max = float(df["Rating"].max())
min_rating = st.sidebar.slider(
    "Rating Range",
     min_value=float(df['Rating'].min()),
     max_value=float(df['Rating'].max()),
     value=float(df['Rating'].min()),
     step=0.1,
     key="min_rating_slider"
    )

with col2:
   st.image("C:/Users/Velpr/Documents/IMDBProj/Image.jpg", width=300)
st.markdown("<hr style='border: 1px solid #ccc;' /hr>", unsafe_allow_html=True)


#Filters applied to dataframe
filtered_df = df[(df['Genre'].isin(selected_genres))& (df['Votes'] >= min_votes)  &
                      (df['Duration']>= min_duration)& (df['Rating']>= min_rating)]

#--------
options = [
    "Top 10 Movies", "Genre Analysis", "Average Duration by Genre", "Voting Trends by Genre", "Rating Distribution",
    "Genre-Based Rating", "Most Popular Genres by Voting", "Duration Extremes", "Ratings by Genre Heatmap", "Ratings vs Votes Correlation"
]

cols = st.columns(len(options))
selected = None

for i, option in enumerate(options):
    with cols[i % len(cols)]:
        if st.button(option, help=option):
            selected = option

if selected:
    st.title(f"📌 {selected}")
    st.write(f"Here is your **{selected}**!")

#st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)

# Content Display Based on Selection

with st.container():
    if selected == "Top 10 Movies":
       #st.title("🎖 Top 10 Movies")
        top_movies = filtered_df.sort_values(by=['Rating', 'Votes'], ascending=False).head(10)
        st.dataframe(top_movies[['Title', 'Genre', 'Rating', 'Votes']])

    elif selected == "Rating Distribution":
       #st.title("\U0001F4C8 Rating Distribution")
        fig1, ax2 = plt.subplots(figsize=(8, 4))
        sns.histplot(filtered_df["Rating"], bins=50, kde=True, ax=ax2, color='skyblue')
        ax2.set_xlabel("Rating")
        ax2.set_ylabel("Count")
        ax2.set_title("Distribution of Ratings")
        st.pyplot(fig1)

    elif selected == "Genre Analysis":
      # st.title("📊 Genre Distribution")
        fig2, ax1 = plt.subplots()
        filtered_df['Genre'].value_counts().plot(kind='bar', ax=ax1 ,color='maroon', width=0.3)
        ax1.set_xlabel("Genre")
        ax1.set_ylabel("Count")
        st.pyplot(fig2)

    elif selected == "Average Duration by Genre":
       #st.title("⏱ Average Duration by Genre")
        fig3, ax2 = plt.subplots()
        filtered_df.groupby('Genre')['Duration'].mean().sort_values().plot(kind='bar', ax=ax2,color='darkseagreen', width=0.4)
        ax2.set_xlabel("Avg Duration (min)")
        st.pyplot(fig3)

    elif selected == "Voting Trends by Genre":
       #st.title("\U0001F4CA Voting Trends by Genre")
        avg_votes = filtered_df.groupby("Genre")["Votes"].mean().sort_values(ascending=False)
        fig4 = px.bar(avg_votes, orientation='v', labels={'value': 'Average Votes', 'Genre': 'Genre'},
        title='Average Votes by Genre', color=avg_votes.values, color_continuous_scale='Blues')
        st.plotly_chart(fig4, use_container_width=True)

    elif selected == "Genre-Based Rating":
       #st.title("\U0001F451 Top-Rated Movie per Genre")
        top_per_genre = filtered_df.loc[filtered_df.groupby("Genre")["Rating"].idxmax()][["Genre", "Title", "Rating"]]
        st.dataframe(top_per_genre.sort_values(by="Rating", ascending=False), use_container_width=True)

    elif selected == "Most Popular Genres by Voting":
       #st.title("\U0001F3C6 Most Popular Genres by Voting")
        vote_sum = filtered_df.groupby("Genre")["Votes"].sum().reset_index()
        fig5 = px.pie(vote_sum, values='Votes', names='Genre', title='Total Votes by Genre',
                     color_discrete_sequence=px.colors.sequential.RdBu)
        fig5.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),  # minimize padding
        height=600,  # increase figure height
        )
        fig5.update_traces(textposition='inside', textinfo='percent+label') 
        st.plotly_chart(fig5, use_container_width=True)

    elif selected == "Duration Extremes":
      # st.title("\u23F1 Shortest and Longest Movies")
        col1, col2 = st.columns(2)
        shortest = filtered_df.loc[filtered_df["Duration"].idxmin()][["Title", "Duration"]]
        longest = filtered_df.loc[filtered_df["Duration"].idxmax()][["Title", "Duration"]]
        col1.metric("Shortest Movie", f"{shortest['Title']}", f"{shortest['Duration']} mins")
        col2.metric("Longest Movie", f"{longest['Title']}", f"{longest['Duration']} mins")

    elif selected == "Ratings by Genre Heatmap":
       #st.title("\U0001F5FA Average Ratings by Genre")
        rating_heatmap = filtered_df.pivot_table(index="Genre", values="Rating", aggfunc="mean")
        fig6, ax4 = plt.subplots(figsize=(12, 5))
        sns.heatmap(rating_heatmap, annot=True, cmap="YlOrRd", ax=ax4)
        ax4.set_title("Average Rating per Genre")
        st.pyplot(fig6)

    elif selected == "Ratings vs Votes Correlation":
       #st.title("\U0001F4C9 Rating vs Votes Correlation")
        fig7 = px.scatter(filtered_df, x="Votes", y="Rating", hover_data=['Title'],
                      color='Rating', color_continuous_scale='Viridis',
                      title="Rating vs Votes")
        st.plotly_chart(fig7, use_container_width=True)

        