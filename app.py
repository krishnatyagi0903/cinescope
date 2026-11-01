import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="CineScope | Movie Intelligence",
    page_icon="🎬",
    layout="wide"
)

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #10121f, #191d30);
    color: #ffffff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, p, label {
    color: white !important;
}

.hero {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(120deg, #30245f, #192e50);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    color: #d4d8ed !important;
}

[data-testid="stMetric"] {
    background: #252c42;
    border: 1px solid #39445f;
    padding: 18px;
    border-radius: 14px;
}

[data-testid="stMetricValue"] {
    color: #c4b5fd;
}

div[data-testid="stTabs"] button {
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SAMPLE DATA ----------------

sample_data = pd.DataFrame({
    "Title": [
        "Inception", "Interstellar", "The Dark Knight",
        "Avatar", "Titanic", "The Matrix", "Joker",
        "Avengers Endgame", "Dangal", "3 Idiots",
        "Shawshank Redemption", "Parasite"
    ],
    "Genre": [
        "Sci-Fi", "Sci-Fi", "Action", "Sci-Fi",
        "Romance", "Sci-Fi", "Drama", "Action",
        "Drama", "Comedy", "Drama", "Thriller"
    ],
    "Rating": [
        8.8, 8.7, 9.0, 7.9, 7.9, 8.7,
        8.3, 8.4, 8.3, 8.4, 9.3, 8.5
    ],
    "Year": [
        2010, 2014, 2008, 2009, 1997, 1999,
        2019, 2019, 2016, 2009, 1994, 2019
    ],
    "Platform": [
        "Netflix", "Prime Video", "Netflix", "Disney+",
        "Netflix", "Prime Video", "Netflix", "Disney+",
        "Netflix", "Prime Video", "Netflix", "Prime Video"
    ]
})

# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🎬 CineScope</h1>
    <p>Discover movies. Explore ratings. Understand entertainment trends.</p>
    <p>YOUR PERSONAL MOVIE INTELLIGENCE DASHBOARD</p>
</div>
""", unsafe_allow_html=True)

# ---------------- UPLOAD DATA ----------------

st.sidebar.title("🎥 CineScope Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload your movie dataset",
    type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success("Dataset uploaded successfully!")

    except Exception as e:
        st.error(f"Unable to read dataset: {e}")
        st.stop()

else:
    df = sample_data.copy()
    st.sidebar.info("Using sample movie dataset")

# ---------------- DATA VALIDATION ----------------

required_columns = ["Title", "Genre", "Rating"]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )
    st.info("Required columns: Title, Genre, Rating")
    st.stop()

df = df.copy()

df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Title"] = df["Title"].fillna("Unknown").astype(str)
df["Genre"] = df["Genre"].fillna("Unknown").astype(str)

if "Year" in df.columns:
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

if "Platform" not in df.columns:
    df["Platform"] = "Not specified"

df["Platform"] = df["Platform"].fillna("Not specified").astype(str)

df = df.dropna(subset=["Rating"])
df = df.drop_duplicates()

if df.empty:
    st.warning("No valid movie records were found.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------

st.sidebar.divider()
st.sidebar.subheader("🔍 Filter Movies")

genres = sorted(df["Genre"].unique())

selected_genres = st.sidebar.multiselect(
    "Movie Genres",
    genres,
    default=genres
)

platforms = sorted(df["Platform"].unique())

selected_platforms = st.sidebar.multiselect(
    "OTT Platforms",
    platforms,
    default=platforms
)

min_rating = st.sidebar.slider(
    "Minimum Rating",
    0.0, 10.0, 0.0, 0.5
)

filtered = df[
    (df["Genre"].isin(selected_genres))
    & (df["Platform"].isin(selected_platforms))
    & (df["Rating"] >= min_rating)
].copy()

if "Year" in df.columns:
    years = df["Year"].dropna()

    if not years.empty:
        min_year = int(years.min())
        max_year = int(years.max())

        if min_year < max_year:
            year_range = st.sidebar.slider(
                "Release Year",
                min_year,
                max_year,
                (min_year, max_year)
            )

            filtered = filtered[
                filtered["Year"].between(
                    year_range[0], year_range[1]
                )
            ]

st.sidebar.caption("Filters update the dashboard automatically.")

# ---------------- METRICS ----------------

st.markdown("## 📊 Entertainment Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("🎞️ Total Movies", f"{len(df):,}")

c2.metric(
    "⭐ Average Rating",
    f"{df['Rating'].mean():.2f}/10"
)

c3.metric("🎭 Genres", df["Genre"].nunique())

c4.metric("🔎 Matching Movies", f"{len(filtered):,}")

st.divider()

# ---------------- TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Overview",
    "🎬 Explore Movies",
    "💡 Recommendations",
    "📁 Data Insights"
])

# ---------------- OVERVIEW ----------------

with tab1:

    st.subheader("📈 Movie Analytics")

    if not filtered.empty:

        left, right = st.columns(2)

        with left:
            genre_data = (
                filtered["Genre"]
                .value_counts()
                .reset_index()
            )

            genre_data.columns = ["Genre", "Movies"]

            fig = px.pie(
                genre_data,
                names="Genre",
                values="Movies",
                hole=0.5,
                title="Genre Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.histogram(
                filtered,
                x="Rating",
                nbins=10,
                title="Movie Rating Distribution",
                color_discrete_sequence=["#A78BFA"]
            )

            st.plotly_chart(fig, use_container_width=True)

        if "Year" in filtered.columns:
            yearly = (
                filtered.dropna(subset=["Year"])
                .groupby("Year")
                .size()
                .reset_index(name="Movies")
            )

            if not yearly.empty:
                fig = px.line(
                    yearly,
                    x="Year",
                    y="Movies",
                    markers=True,
                    title="Movies Released Over Time"
                )

                st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No movies match your current filters.")

# ---------------- EXPLORE MOVIES ----------------

with tab2:

    st.subheader("🎬 Explore Movie Collection")

    search = st.text_input(
        "Search by movie title"
    )

    explore = filtered.copy()

    if search:
        explore = explore[
            explore["Title"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    explore = explore.sort_values(
        "Rating",
        ascending=False
    )

    st.write(f"Found {len(explore)} movies")

    st.dataframe(
        explore,
        use_container_width=True,
        hide_index=True
    )

    csv_file = explore.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Movie Results",
        csv_file,
        "cinescope_movies.csv",
        "text/csv"
    )

# ---------------- RECOMMENDATIONS ----------------

with tab3:

    st.subheader("💡 Discover Your Next Movie")

    recommend_genre = st.selectbox(
        "Choose your favourite genre",
        genres,
        key="recommend_genre"
    )

    rating_preference = st.slider(
        "Minimum recommended rating",
        0.0, 10.0, 7.0, 0.5,
        key="recommend_rating"
    )

    recommendations = df[
        (df["Genre"] == recommend_genre)
        & (df["Rating"] >= rating_preference)
    ].sort_values(
        "Rating",
        ascending=False
    )

    st.write(
        f"Found {len(recommendations)} matching recommendations."
    )

    if recommendations.empty:
        st.info("No matching movies. Try lowering the minimum rating.")
    else:
        for _, movie in recommendations.head(10).iterrows():

            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### 🎬 {movie['Title']}")
                    st.write(f"Genre: {movie['Genre']}")

                    if "Year" in movie.index:
                        if pd.notna(movie["Year"]):
                            st.write(f"Release Year: {int(movie['Year'])}")

                    st.write(f"OTT Platform: {movie['Platform']}")

                with col2:
                    st.metric("⭐ Rating", f"{movie['Rating']:.1f}/10")

# ---------------- DATA INSIGHTS ----------------

with tab4:

    st.subheader("🔍 Automatic Dataset Insights")

    if not filtered.empty:

        best_movie = filtered.loc[
            filtered["Rating"].idxmax()
        ]

        popular_genre = filtered["Genre"].mode().iloc[0]

        i1, i2 = st.columns(2)

        with i1:
            st.success(
                f"🏆 Highest-rated movie: {best_movie['Title']} "
                f"({best_movie['Rating']:.1f}/10)"
            )

        with i2:
            st.info(
                f"🎭 Most common genre: {popular_genre}"
            )

        st.write(
            f"Average movie rating: **{filtered['Rating'].mean():.2f}**"
        )

        st.write(
            f"Movies with rating 8 or higher: "
            f"**{(filtered['Rating'] >= 8).sum()}**"
        )

        st.write(
            f"Duplicate records in original dataset: "
            f"**{df.duplicated().sum()}**"
        )

    st.markdown("### Dataset Information")

    st.write(f"Rows: {len(df)}")
    st.write(f"Columns: {len(df.columns)}")

    missing_data = df.isnull().sum().reset_index()
    missing_data.columns = ["Column", "Missing Values"]

    st.dataframe(
        missing_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Original Dataset")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    "<center>🎬 CineScope | Built with Python, Pandas, "
    "Plotly & Streamlit</center>",
    unsafe_allow_html=True
)