
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pymongo.mongo_client import MongoClient



# Hide the default Streamlit menu
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    #GithubIcon {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# MongoDB setup
uri = "mongodb+srv://aihacks:aihacksimagegen@cluster0.qbdoi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['db1']  # Replace with your database name
participants_collection = db['participants']  # Replace with your collection name

# Fixed sequence of images and their corresponding actual prompts
image_prompts = [
    {"image": "image1.jpg", "prompt": "cute Bird on a white background wool colorful"},
    {"image": "image2.jpg", "prompt": "drawing on a black background of a fish bowl"},
    {"image": "image3.jpg", "prompt": "close up of an chinchilla looking at the camera orange background"},
    {"image": "image4.jpeg", "prompt": "extreme closeup portrait of a high end mecha robot mirrored face shield metallic red and blue glowing eyes dark background"},
    {"image": "image5.jpeg", "prompt": "Robot Godzilla using chopsticks space rocket The rocket booster fires a yellow plume of fire at its bottom early morning on the beach ocean"}
]

# Function to calculate similarity between guessed and actual prompts
def calculate_similarity(guess, actual):
    vectorizer = TfidfVectorizer().fit_transform([guess, actual])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0][1]  # Similarity score between 0 and 1

def score_LT(score):
    return 100 + (score * 899)

# Function to save score to MongoDB
def save_scores_to_mongodb(name, img_index, score):
    participant_data = participants_collection.find_one({"name": name})
    
    if participant_data:
        participants_collection.update_one(
            {"name": name},
            {"$set": {f'score{img_index}': score}}
        )
    else:
        participants_collection.insert_one({"name": name, f'score{img_index}': score})

# Admin dashboard with password protection
def admin_view():
    st.title("Admin Dashboard")
    password = st.text_input("Enter admin password", type="password")
    if password == "aihacks.club@image-gen69#$%1459fc^,":
        st.success("Access granted!")

        # Fetch and display participant scores from MongoDB
        
        data = list(participants_collection.find())
        df = pd.DataFrame(columns=['Participant', 'Score1', 'Score2', 'Score3', 'Score4', 'Score5', 'Total Score'])

        for participant in data:
            scores = [
                score_LT(participant.get('score1', 0)),
                score_LT(participant.get('score2', 0)),
                score_LT(participant.get('score3', 0)),
                score_LT(participant.get('score4', 0)),
                score_LT(participant.get('score5', 0))
            ]
            total_score = sum(scores)
            row = [participant['name']] + scores + [total_score]
            df.loc[len(df)] = row

        st.dataframe(df)

    else:
        st.error("Incorrect password. Access denied.")

# Participant view to submit guesses
def participant_view():
    st.title("Guess the Prompt")
    name = st.text_input("Enter your Team name")
    if name:
        for idx, img_info in enumerate(image_prompts):
            st.image(img_info["image"], caption=f"Describe Image {idx + 1}")
            guessed_prompt = st.text_input(f"Enter your prompt for Image {idx + 1}")
            if st.button(f"Submit for Image {idx + 1}"):
                actual_prompt = img_info["prompt"]
                score = calculate_similarity(guessed_prompt, actual_prompt)
                save_scores_to_mongodb(name, idx + 1, score)
                st.write(f"Your similarity score for Image {idx + 1} is: {score:.2f}")

# Main application flow
mode = st.sidebar.selectbox("Select Mode", ("Participant", "Admin"))

if mode == "Participant":
    participant_view()
elif mode == "Admin":
    admin_view()
