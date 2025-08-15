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
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import os

#breakpoint()

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

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


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

if birthdate:  # Only proceed if a date is selected

    # ✅ Data Processing
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


tab1, tab2, tab3 = st.tabs(["🎂 Insights", "📈 Birth Trend", "Events that happened on your Birthday Month"])

with tab1:
# 🖼 Show stored image
    st.image(r"C:\Users\Ervyn\Downloads\FUN\birth_insight_app\wakamo.webp", caption="Fun Birthday Facts!", use_container_width =True)
    
    # 💬 Ask your bot below the image
    #st.text_input("Say something about your birthday...", key="tab1_chat_input")

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
    
with tab3:
    # 🔍 Fetch month events from Wikipedia
    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="en", top_k_results=5))

    month_query = f"Significant historical events in {month} (worldwide or Malaysia)"
    wiki_results = wiki.run(month_query)

    if wiki_results.strip():
        month_event_context = f"Here are verified events from Wikipedia for {month}:\n{wiki_results}"
    else:
        month_event_context = "No verified events found for this month."
    
    # Show events in a static box
    st.subheader("📜 Historical Events")
    st.write(month_event_context)


    # Store events for later use in chatbot prompt
    st.session_state.month_event_context = wiki_results.strip()


st.markdown("---")
st.subheader("💬 Ask your Birthday Bot!")

# 🧠 Define LLM and Prompt
llm = Ollama(model="llama3.2:latest")  # Make sure llama3 is pulled

# 🧠 Personalized Birth Context
birth_context = f"""
You are a friendly Malaysian chatbot that gives fun, personalized facts based on a user's birthday.

User's birth profile:
- Year: {birthdate.year}
- Month: {month}  # full month name
- Day: {birthdate.day}
- Weekday: {weekday}
- Western Zodiac: {zodiac}
- Chinese Zodiac: {animal}
- Shared with {count} other Malaysians
{percentile_text}

Be informative, playful, and speak in a casual tone. Answer like a fun tour guide or a birthday storyteller!

You must follow these rules strictly:

1) Month Event Fact (NO HALLUCINATIONS):
   - You may include ONE extra section titled "📜 This month in history".
   - ONLY use the provided month_event_context below.
   - Do not make up or guess any events if you aren't sure if the events is factual DO NOT INCLUDE.
   - Do NOT infer, guess, or add details not present in the catalog.
   - Keep it to 1–2 sentences and include the event's date (as given) and source name in parentheses.
   - If no events are listed, skip the "This month in history" section.

2) Tone & Format:
   - Be informative, playful, and casual—like a fun tour guide.
   - Keep responses concise and factual.

3) Banned Behaviors:
   - Do not invent or speculate about events.

month_event_context:
{month_event_context}
"""
# Combine both into a single history_context
if "full_context" not in st.session_state:
    st.session_state.full_context = f"{birth_context}\n\nMonth Event Context:\n{st.session_state.month_event_context}"


prompt_template = PromptTemplate(
    input_variables=["human_input", "history_context"],  # Only variables you will pass manually
    template="""
{history_context}

{chat_history}
User: {human_input}
Bot:"""
)



# 🧠 Initialize memory and log
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="human_input",
        return_messages=True
    )

    st.session_state.chat_log = []
    st.session_state.last_birthdate = birthdate

# Clear month events if birthdate changed
if st.session_state.get("last_birthdate") != birthdate:
    st.session_state.month_event_context = ""
    st.session_state.last_birthdate = birthdate

# Add static full context only once
if "full_context_added" not in st.session_state:
    st.session_state.chat_memory.chat_memory.add_user_message(st.session_state.full_context)
    st.session_state.full_context_added = True



llm_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    memory=st.session_state.chat_memory,
    verbose=False
)


# 💬 User input
user_input = st.text_input("Say something about your birthday...", key="chat_input")

if user_input:
    #breakpoint()
    response = llm_chain.invoke({
        "human_input": user_input,
        "history_context": st.session_state.full_context

    })    
    st.write(response["text"])


    # Store log
    message_id = str(uuid.uuid4())[:8]
    st.session_state.chat_log.append({
        "id": message_id,
        "user": user_input or "",
        "bot": response
    })

    st.write(f"🤖 **Bot** (msg ID: `{message_id}`): {response}")

# Save chat log to file
def save_chat_log():
    log_file = "chat_log.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=== Chat Exchanges ===\n")
        for log in st.session_state.chat_log:
            bot_reply = log['bot']
            if isinstance(bot_reply, dict) and "text" in bot_reply:
                bot_reply = bot_reply["text"]  # Extract only the bot's reply text
            f.write(f"ID: {log['id']}\n")
            f.write(f"You: {log['user']}\n")
            f.write(f"Bot: {bot_reply}\n")
            f.write("-" * 40 + "\n")

        f.write("\n=== Full Chat History (LangChain Memory) ===\n")
        if "chat_memory" in st.session_state:
            history_vars = st.session_state.chat_memory.load_memory_variables({})
            f.write(str(history_vars.get("chat_history", "")))
        else:
            f.write("[No chat history found in memory]\n")
    return log_file

# 📑 Show Chat Log
with st.expander("📝 Chat Debug Log"):
    for log in st.session_state.chat_log:
        bot_reply = log['bot']["text"] if isinstance(log['bot'], dict) and "text" in log['bot'] else log['bot']
        st.markdown(f"**ID**: `{log['id']}`\n- You: {log['user']}\n- Bot: {bot_reply}")

    if "chat_memory" in st.session_state:
        st.text("=== Full Chat History ===")
        st.text(st.session_state.chat_memory.load_memory_variables({}).get("chat_history", ""))

    if st.button("💾 Save Chat Log to TXT"):
        file_path = save_chat_log()
        st.success(f"Chat log saved as `{os.path.abspath(file_path)}`")
