# Neccessary imports for the project
import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

# Configures and loads the page with a title and wide layout
st.set_page_config(page_title="F1 Race Winner Predictor", layout="wide")    

# Defines the function to predict the race winner and reads the CSV file containing all of the stats and data
def predict_winner(track_name, year, include_qualifying):
    df = pd.read_csv("F1_Race_Data.csv")

    # Clean and convert data values from the CSV file (e.g. Won, weather_code) to make it readable for the model
    df = df.dropna(subset=["Won"])
    df["Won"] = df["Won"].astype(int)
    if "constructor_strength" not in df.columns:
        df["constructor_strength"] = df["Constructor"].astype('category').cat.codes
    df["constructor_strength"] = df["constructor_strength"].astype(int)
    if "weather_code" not in df.columns or df["weather_code"].dtype == object:
        df["weather_code"] = df["Weather"].map({"Sunny": 0, "Overcast": 1, "Rainy": 2})
    df["weather_code"] = df["weather_code"].astype(int)
    df["Grid"] = df["Grid"].astype(int)


    X = df[["Grid", "constructor_strength", "weather_code"]] #This line creates a new DataFrame X that contains specific columns from the original DataFrame df.
    y = df["Won"]# This line creates a Series y that contains the target variable from the DataFrame df (e.g. Won)

    # Initialises the Decision Tree Classifier model and fits it to the data, allowing it to train
    model = DecisionTreeClassifier()
    model.fit(X, y)

    # Reads the CSV file and filters it to create a dataframe for prediction
    future_df = pd.read_csv("F1_Race_Data.csv")
    predict_rows = future_df[
        (future_df["Circuit"] == track_name) &
        (future_df["Season"] == int(year)) &
        (future_df["Won"].isnull())
    ].copy()

    # Checks if the dataframe is empty, if empty returns a message saying that the race data is not available
    if predict_rows.empty:
        return "No prediction – race data not available."

    # Prepares the data for prediction by converting categorical variables to numerical codes
    # So the model can process the data
    predict_rows["constructor_strength"] = predict_rows["Constructor"].astype('category').cat.codes
    predict_rows["weather_code"] = predict_rows["Weather"].map({"Sunny": 0, "Overcast": 1, "Rainy": 2})
    predict_rows["Grid"] = predict_rows["Grid"].astype(int)

    # Predict probabilities and stores them in a new column "win_prob"
    pred_probs = model.predict_proba(predict_rows[["Grid", "constructor_strength", "weather_code"]])
    predict_rows["win_prob"] = pred_probs[:, 1]  # probability of winning

    # Retrieve the driver with the highest win probability
    top_prediction = predict_rows.sort_values("win_prob", ascending=False).iloc[0]
    predicted_driver = top_prediction["Driver"]
    win_chance = top_prediction["win_prob"]
    return f"{predicted_driver} (Win chance: {win_chance:.2%})"
    
    # Checks if the predict_row is empty, if it is empty returns a message saying that
    #if predict_row.empty:
     #   return "No prediction – race data not available."

    #predict_row["constructor_strength"] = predict_row["Constructor"].astype('category').cat.codes
    #predict_row["constructor_strength"] = predict_row["constructor_strength"].astype(int)
    #predict_row["weather_code"] = predict_row["Weather"].map({"Sunny": 0, "Overcast": 1, "Rainy": 2})
    #predict_row["weather_code"] = predict_row["weather_code"].astype(int)
    #predict_row["Grid"] = predict_row["Grid"].astype(int)
    
    #pred_features = predict_row[["Grid", "constructor_strength", "weather_code"]]
    #prediction = model.predict(pred_features)

    #predicted_driver = predict_row.iloc[0]["Driver"] if prediction[0] == 1 else "Unknown"
    #return predicted_driver

# A header consisting of the official F1 logo, sourced from the web and formatted in HTLML to be compatible in streamlit
st.markdown(
    '<h1 style="text-align: center;">'
    '<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR4-YDCwSYl053xPyjNWAsIPyoG_y3FIzXCVg&s" width="100" height="auto"> '
    'Race Winner Predictor</h1>',
    unsafe_allow_html=True
)

# A subheader for the motto/tagline
st.markdown('<h1 style="text-align: center; font-size: 24px; color: #5c5c5a;">Powered by data. Inspired by speed.</h1>', unsafe_allow_html=True)

# Splits the UI page into two columns, one slightly bigger than the other
col1, col2 = st.columns([1, 1.2])

# Creates a header for the forst column
with col1:
    st.header("🔧 Race Settings")

    # Allows the user to select from the following race tracks
    selected_race = st.selectbox("Select Race Location:", [
        "Albert Park Grand Prix Circuit", "Circuit Gilles Villeneuve", "Miami International Autodrome", "Circuit de Monaco",
        "Baku City Circuit", "Jeddah Corniche Circuit", "Circuit Park Zandvoort", "Circuit Paul Ricard",
        "Circuit of the Americas", "Circuit de Spa-Francorchamps", "Losail International Circuit", "Suzuka Circuit",
        "Red Bull Ring", "Shanghai International Circuit", "Hungaroring", "Silverstone Circuit",
        "Circuit de Barcelona-Catalunya", "Autodromo Nazionale di Monza", "Autodromo Internazionale del Mugello",
        "Sochi Autodrom", "Nürburgring", "Autódromo Internacional do Algarve", "Autodromo Enzo e Dino Ferrari",
        "Istanbul Park", "Bahrain International Circuit", "Yas Marina Circuit", "Autódromo Hermanos Rodríguez",
        "Autódromo José Carlos Pace", "Las Vegas Strip Street Circuit"
    ])

    # Prompts the user to select a race year and allows the user to decide whether they want to include
    # qualifying data into the prediction or not and puts a predict winner button on the screen
    race_year = st.selectbox("Select Race Year:", [str(y) for y in range(2020, 2026)])
    include_qualifying = st.checkbox("Include Qualifying Data")
    st.write("Selected Race:", selected_race)

    predict_button = st.button("🚦 Predict Winner")

# Creates a header for the prediciton outcomes, and if no input is provided yet it states that
with col2:
    st.header("🏎️ Prediction Panel")
    if predict_button:
        predicted_driver = predict_winner(selected_race, race_year, include_qualifying)
        st.success(f"🏆 Predicted Winner: **{predicted_driver}**")
    else:
        st.info("Prediction will appear here once inputs are provided.")

    st.markdown("---")
    st.subheader("📊 Historical Stats")
    
    # Reads the CSV file and displays the historical winners for the past 3 years at the selected track 
    # and if the race selected is invalid it displays 'historical data not available'
    try:
        df = pd.read_csv("F1_Race_Data.csv")
        track_history = df[(df["Circuit"] == selected_race) & (df["Won"] == 1)].sort_values("Season", ascending=False).head(3)
        for _, row in track_history.iterrows():
            st.markdown(f"- {int(row['Season'])}: {row['Driver']}")
    except:
        st.write("Historical data not available.")

    # Displays some info regarding weather insights
    st.markdown("**Weather Impact Insights:**")
    st.write("Rainy races historically increase unpredictability by 32%.")

# Footer that is visible in the website
st.markdown("---")
st.caption("Made with 💻 and 🏁 by a Year 12 Data Champ")