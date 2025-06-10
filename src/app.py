import json
from pathlib import Path
import streamlit as st
from glg.core import run_full_glg_workflow
from datetime import datetime
from video_engine import generate_skit_media, generate_skit_slides_and_audio

def format_ideas(ideas):
    """
    Takes ideas that can be a string or list and splits them into full ideas.
    If it's a string without newlines, it will return it as a single idea.
    """
    if isinstance(ideas, str):
        # If the string contains line breaks, split by them; otherwise, treat as one idea.
        ideas_list = ideas.splitlines() if "\n" in ideas else [ideas]
    else:
        ideas_list = ideas
    return "\n".join(f"• {idea.strip()}" for idea in ideas_list if idea.strip())

# Setup page and state
st.set_page_config(page_title="Green Light Go UI", layout="wide")
st.title("🛑🚦 Green Light Go - AI Decision Assistant")

# Load team profiles
teams_path = Path(__file__).parent / "config" / "teams.json"
teams_config = json.load(open(teams_path))
# Only show actual profiles (exclude ones like 'skit' if present)
profiles = [p for p in teams_config.keys() if p != 'skit']

# Team selection – block the rest if none is selected
profile = st.sidebar.selectbox("Team Profile", profiles, index=0)
if not profile:
    st.warning("Please select a team to proceed.")
    st.stop()  # halt further app execution until a team is picked

st.sidebar.markdown("### Team Members")
for agent in teams_config.get(profile, []):
    name = agent.get('name', '')
    spec = agent.get('specialty', '')
    st.sidebar.write(f"**{name.title()}**: {spec}")
st.sidebar.markdown("---")

# Add a prompt example for the skit
st.sidebar.markdown("### Skit Prompt Example")
st.sidebar.info(
    "**Example Prompt:**\n"
    "Imagine you're a team of experts brainstorming ideas for a new product launch. "
    "Each team member brings a unique perspective based on their specialty. "
    "Discuss challenges, propose solutions, and highlight how your expertise contributes to the success of the project."
)

# Ensure the skit preview is only created after a team is picked.
if st.session_state.get("selected_team") != profile:
    team_agents = teams_config.get(profile, [])

    # Create a list of voice styles to assign uniquely 
    voice_styles = ["confident", "witty", "analytical", "cheerful", "observant", "innovative"]

    # Define dialogue templates for each voice style.
    dialogue_templates = {
        "confident": "I bring fearless {spec} that conquers every challenge!",
        "witty": "My {spec} keeps everyone chuckling while solving problems with style.",
        "analytical": "I dissect {spec} to reveal patterns that pave our way to success.",
        "cheerful": "With sparkling {spec}, I light up the room and boost our morale!",
        "observant": "I notice every subtle detail of {spec} others might overlook.",
        "innovative": "I transform {spec} into groundbreaking ideas that shift paradigms."
    }

    story_lines = []
    story_lines.append(f"One bright morning at Green Light Go, team {profile} gathered for a crucial strategy meeting.")

    # Add team-specific goals
    if profile.lower() == "engineering":
        story_lines.append("The team was tasked with designing an innovative transportation solution to address urban congestion.")
        story_lines.append("Their goal was to create a sustainable and efficient system that could handle the demands of a growing city.")
    elif profile.lower() == "marketing":
        story_lines.append("The marketing team was brainstorming ways to showcase the company's groundbreaking transportation projects to potential clients.")
    elif profile.lower() == "finance":
        story_lines.append("The finance team debated how to allocate resources effectively for the upcoming infrastructure projects.")

    # Let each agent speak with a unique voice reacting to their personality.
    for i, agent in enumerate(team_agents):
        name = agent.get("name", "Agent").title()
        spec = agent.get("specialty", "unique expertise").lower()
        voice = voice_styles[i % len(voice_styles)]
        dialogue_line = dialogue_templates.get(voice, "I showcase my skills in {spec}.").format(spec=spec)
        story_lines.append(f'{name} ({voice} voice): "{dialogue_line}"')
        if i > 0:  # Add interaction with the previous agent
            prev_agent = team_agents[i - 1]
            prev_name = prev_agent.get("name", "Agent").title()
            story_lines.append(f"{name}: \"What do you think, {prev_name}? Does this align with your {prev_agent.get('specialty', 'expertise').lower()}?\"")

    # Add team-specific humor
    if profile.lower() == "engineering":
        story_lines.append("The engineers joked about how every project starts with 'it can't be done' and ends with 'we did it anyway.'")
    elif profile.lower() == "it":
        story_lines.append("The IT team joked about how the servers always crash right before a big launch.")
    elif profile.lower() == "hr":
        story_lines.append("The HR team laughed about how everyone suddenly becomes 'busy' during compliance training.")

    # Add additional narrative to tie the conversation together.
    story_lines.append("Amid playful banter, the diverse voices created a vibrant, dynamic atmosphere,")
    story_lines.append("leading to a brainstorming session filled with unexpected insights and bold visions.")
    story_lines.append("By the end of the meeting, it was clear: teamwork at Green Light Go was truly unstoppable!")

    # Add custom closing statements
    if profile.lower() == "engineering":
        story_lines.append("The team left the meeting with a clear vision to revolutionize transportation infrastructure.")
    elif profile.lower() == "marketing":
        story_lines.append("The team left the meeting energized, ready to create a campaign that would go viral.")
    elif profile.lower() == "engineering":
        story_lines.append("The team left the meeting with a clear plan to tackle the technical challenges ahead.")

    default_script = "\n\n".join(story_lines)

    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    slides, audio_path = generate_skit_slides_and_audio(profile, default_script, f"skit_preview_{ts}")
    st.session_state.selected_team = profile
    st.session_state.preview = {"slides": slides, "audio_path": audio_path}

if "preview" in st.session_state:
    st.sidebar.markdown("### Skit Preview")
    st.sidebar.audio(st.session_state.preview["audio_path"])
    for idx, slide in enumerate(st.session_state.preview["slides"]):
        st.sidebar.image(slide, caption=f"Slide {idx+1}", use_container_width=True)

# Now allow idea input only after a team has been selected
topic = st.text_input("Enter your idea or topic:")

if st.button("Run Workflow"):
    if not topic.strip():
        st.warning("Please enter a valid idea or topic.")
    else:
        with st.spinner("Running Green Light Go workflow..."):
            context = run_full_glg_workflow(topic, profile_name=profile) if 'profile_name' in run_full_glg_workflow.__code__.co_varnames else run_full_glg_workflow(topic)

        # Display transcript with monospace formatting
        st.subheader("Conversation Transcript")
        transcript = context.get('full_transcript', [])
        transcript_text = "\n".join(transcript) if isinstance(transcript, list) else str(transcript)
        st.markdown("```\n" + transcript_text + "\n```")

        # Display decisions and analysis using two columns
        st.subheader("Decisions & Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Executive Summary")
            st.write(context.get('executive_summary', ''))
        with col2:
            st.markdown("#### Auditor Review")
            st.write(context.get('auditor_review', ''))

        # Show decisions, ensuring each idea is a full idea bullet
        red_ideas = context.get('red_light_ideas')
        if red_ideas:
            st.error("🔴 Red Light Ideas:\n" + format_ideas(red_ideas))
        yellow_ideas = context.get('yellow_light_ideas')
        if yellow_ideas:
            st.warning("🟡 Yellow Light Ideas:\n" + format_ideas(yellow_ideas))
        green_ideas = context.get('green_light_ideas')
        if green_ideas:
            st.success("🟢 Green Light Ideas:\n" + format_ideas(green_ideas))

        st.success("Workflow completed.")

        # Skit simulation – option to generate a skit after workflow run
        multi = st.checkbox("Multi-Slide Skit")
        if st.button("Play Skit"):
            with st.spinner("Generating presentation..."):
                script_text = context.get("executive_summary", f"Hello, this is {profile} from Green Light Go.")
                ts = datetime.now().strftime('%Y%m%d%H%M%S')
                if multi:
                    slides, audio_path = generate_skit_slides_and_audio(profile, script_text, f"skit_{ts}")
                else:
                    img_path, audio_path = generate_skit_media(profile, script_text, f"skit_{ts}")
                    slides = [img_path]
            st.audio(audio_path)
            for idx, slide in enumerate(slides):
                st.image(slide, caption=f"Slide {idx+1}", use_container_width=True)
