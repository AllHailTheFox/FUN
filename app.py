import streamlit as st
import pandas as pd
from datetime import datetime
from zodiac_utils import get_western_zodiac, get_chinese_zodiac
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import uuid
import altair as alt
import base64  # <-- Needed for encoding

# 🎵 Background Audio Setup
audio_file = open(r"C:\Users\Ervyn\Downloads\FUN\birth_insight_app\videoplayback.m4a", "rb")
audio_bytes = audio_file.read()

# Optional: show player (can remove if you want it fully hidden)
st.audio(audio_bytes, format='audio/m4a')

# Encode and autoplay (correct MIME type for m4a)
b64 = base64.b64encode(audio_bytes).decode()
st.markdown(f"""
    <audio autoplay loop hidden>
        <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
        Your browser does not support the audio element.
    </audio>
""", unsafe_allow_html=True)    


# Load data
@st.cache_data
def load_birth_data():
    df = pd.read_csv(r"C:\Users\Ervyn\Downloads\FUN\birth_insight_app\births.csv")  # Ensure it has 'date' and 'count' columns
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_birth_data()

# 🎯 UI Title
st.title("🎉 Malaysian Birthdate Fun Insight Generator")

# 📅 Input: Birthdate
birthdate = st.date_input("Select your birthdate:", min_value=datetime(1920,1,1), max_value=datetime(2023,12,31))

# ✅ Data Processing
filtered = df[df['date'] == pd.to_datetime(birthdate)]
daily_births = df.groupby('date')['births'].sum().reset_index()
filtered = daily_births[daily_births['date'] == pd.to_datetime(birthdate)]
count = int(filtered['births'].values[0]) if not filtered.empty else 0

zodiac, zodiac_fact = get_western_zodiac(birthdate.month, birthdate.day)
animal, animal_fact = get_chinese_zodiac(birthdate.year)
weekday = birthdate.strftime("%A")
month = birthdate.strftime("%B")

sorted_df = daily_births.sort_values('births', ascending=False).reset_index(drop=True)

birthdate_dt = pd.to_datetime(birthdate)
match = sorted_df[sorted_df['date'] == birthdate_dt]

if not match.empty:
    rank = match.index[0] + 1
    total_days = len(sorted_df)
    percentile = 100 * (1 - rank / total_days)
else:
    rank = None
    percentile = None


# 📊 Display Insights
percentile_text = f"- 📈 Your birthday is in the **top {percentile:.1f}%** most common dates!" if percentile is not None else "- 📈 No ranking found for your birthdate."

st.markdown(f"""
## 🎂 You were born on a **{weekday}**, in **{month} {birthdate.year}**  
- 🧍 **{count} other Malaysians** share your birthday  
- ♈ Your **Western Zodiac** is **{zodiac}**  
> 🧠 *Fun Fact:* {zodiac_fact}
- 🐉 Your **Chinese Zodiac** is **{animal}**  
> 🧠 *Fun Fact:* {animal_fact}
{percentile_text}
""")


tab1, tab2 = st.tabs(["🎂 Insights", "📈 Birth Trend"])

with tab1:
# 🖼 Show stored image
    st.image(r"C:\Users\Ervyn\Downloads\FUN\birth_insight_app\wakamo.webp", caption="Fun Birthday Facts!", use_column_width=True)
    
    # 💬 Ask your bot below the image
    st.text_input("Say something about your birthday...", key="tab1_chat_input")

with tab2:
    # Filter to same month (across all years)
    month_births = df[df['date'].dt.month == birthdate.month].copy()
    month_births['day'] = month_births['date'].dt.day

    # Group by day of month and sum births
    by_day = month_births.groupby('day')['births'].sum().reset_index()

    # Mark your day
    your_day = birthdate.day

    # Altair chart with highlight on your birthday
    import altair as alt

    bars = alt.Chart(by_day).mark_bar().encode(
        x=alt.X("day:O", title=f"Month of {month}"),
        y=alt.Y("births:Q", title="Total Births (1920–2023)"),
        tooltip=["day", "births"]
    )

    highlight = alt.Chart(by_day[by_day['day'] == your_day]).mark_bar(color="orange").encode(
        x="day:O",
        y="births:Q",
        tooltip=["day", "births"]
    )

    final_chart = (bars + highlight).properties(
        title=f"📊 Births Per month in {month}",
        height=400
    )

    st.altair_chart(final_chart, use_container_width=True)



st.markdown("---")
st.subheader("💬 Ask your Birthday Bot!")

# 🧠 Personalized Birth Context
birth_context = f"""
You are a friendly Malaysian chatbot that gives fun, personalized facts based on a user's birthday.

User's birth profile:
- Date: {birthdate.strftime('%Y-%m-%d')}
- Day: {weekday}
- Month: {month}
- Western Zodiac: {zodiac}
- Chinese Zodiac: {animal}
- Shared with {count} other Malaysians
{percentile_text}

Be informative, playful, and speak in a casual tone. Answer like a fun tour guide or a birthday storyteller!
"""

# 🧠 Initialize memory and log
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)
    st.session_state.chat_log = []

# 🧠 Define LLM and Prompt
llm = Ollama(model="llama3.2:latest")  # Make sure llama3 is pulled

prompt_template = PromptTemplate.from_template("""
{context}

Conversation history:
{history}

User: {input}
Bot:
""")

# Shared memory instance
chat_memory = ConversationBufferMemory(return_messages=True)

llm_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    memory=chat_memory,
    verbose=False
)


# 💬 User input
user_input = st.text_input("Say something about your birthday...", key="chat_input")


if user_input:
    combined_input = f"{birth_context}\n\n{user_input}"
    response = llm_chain.invoke({
            "input": combined_input
    })

    # Log with UUID
    message_id = str(uuid.uuid4())[:8]
    st.session_state.chat_log.append({
        "id": message_id,
        "user": user_input,
        "bot": response
    })

    st.write(f"🤖 **Bot** (msg ID: `{message_id}`): {response}")

# 📑 Show Chat Log
with st.expander("📝 Chat Debug Log"):
    for log in st.session_state.chat_log:
        st.markdown(f"**ID**: `{log['id']}`\n- You: {log['user']}\n- Bot: {log['bot']}")
