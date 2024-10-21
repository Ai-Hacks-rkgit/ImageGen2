
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pymongo.mongo_client import MongoClient
import bcrypt
import base64

st.set_page_config(
    page_title="Ai Hacks ImageGen",
    page_icon=":sparkles:",  # You can use an emoji
)
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



hashed_password = b'$2b$12$tAG95vHR3BrGk3.aEx4qjudNfMh0iObUhzejaINe1E0RswdMyxVAa'

def check_password(input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)

# MongoDB setup
uri = "mongodb+srv://aihacks:aihacksimagegen@cluster0.qbdoi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['db1']  # Replace with your database name
participants_collection = db['participants']  # Replace with your collection name

# Fixed sequence of images and their corresponding actual prompts
image_prompts=[{'image': 'image1.jpg',
  'prompt': 'Y3V0ZSBCaXJkIG9uIGEgd2hpdGUgYmFja2dyb3VuZCB3b29sIGNvbG9yZnVs'},
 {'image': 'image2.jpg',
  'prompt': 'ZHJhd2luZyBvbiBhIGJsYWNrIGJhY2tncm91bmQgb2YgYSBmaXNoIGJvd2w='},
 {'image': 'image3.jpg',
  'prompt': 'Y2xvc2UgdXAgb2YgYW4gY2hpbmNoaWxsYSBsb29raW5nIGF0IHRoZSBjYW1lcmEgb3JhbmdlIGJhY2tncm91bmQ='},
 {'image': 'image4.jpeg',
  'prompt': 'ZXh0cmVtZSBjbG9zZXVwIHBvcnRyYWl0IG9mIGEgaGlnaCBlbmQgbWVjaGEgcm9ib3QgaXJvbiBtYW4gbWlycm9yZWQgZmFjZSBzaGllbGQgbWV0YWxsaWMgcmVkIGFuZCBibHVlIGdsb3dpbmcgZXllcyBkYXJrIGJhY2tncm91bmQ='},
 {'image': 'image5.jpeg',
  'prompt': 'Um9ib3QgR29kemlsbGEgdXNpbmcgY2hvcHN0aWNrcyBzcGFjZSByb2NrZXQgVGhlIHJvY2tldCBib29zdGVyIGZpcmVzIGEgeWVsbG93IHBsdW1lIG9mIGZpcmUgYXQgaXRzIGJvdHRvbSBlYXJseSBtb3JuaW5nIG9uIHRoZSBiZWFjaCBvY2Vhbg=='}]

def decode_prompt(encoded_prompt):
    return base64.b64decode(encoded_prompt.encode('utf-8')).decode('utf-8')

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
                actual_prompt = decode_prompt(img_info["prompt"])
                score = calculate_similarity(guessed_prompt, actual_prompt)
                save_scores_to_mongodb(name, idx + 1, score)
                st.write(f"Your similarity score for Image {idx + 1} is: {score:.2f}")

participant_view()

