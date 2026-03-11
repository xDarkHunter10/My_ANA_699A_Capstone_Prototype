SIMPLE CHESS COACH - TEAM DEMO VERSION

WHAT THE APP DOES
1. Opening recommendation mode
   You pick your level, color, style, and time control.
   The app recommends an opening and explains why it fits.

2. Analyze pasted moves
   You paste moves like: e4 e5 Nf3 Nc6 Bc4
   The app builds the position and gives simple practical move ideas.

3. Use a sample position
   You choose a common position like the Italian Game.
   The app explains what kind of moves make sense there.

4. Advanced FEN - essentially text code for a chess position.
   This is for technical users only.

HOW TO RUN IT
Step 1:
Open a terminal inside the project folder.

Step 2:
Install packages:
pip install -r requirements.txt

Step 3:
Start the API:
uvicorn app.api_main:app --reload

Step 4:
Open a second terminal and start the interface:
streamlit run app/streamlit_app.py

Step 5:
Open the browser link that Streamlit prints, usually:
http://localhost:8501
