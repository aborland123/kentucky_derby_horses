import shlex
import subprocess
from pathlib import Path
import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client, Client
import plotly.express as px
import pandas as pd
import modal


load_dotenv()

streamlit_script_local_path = Path(__file__).parent / "streamlit_run.py"
streamlit_script_remote_path = "/root/streamlit_run.py"
image = (
    modal.Image.debian_slim(python_version="3.9")
    .uv_pip_install("streamlit", "supabase", "pandas", "plotly", "python-dotenv")
    .env({"FORCE_REBUILD": "true"})  # 🚨 Add this line to force a rebuild
    .add_local_file(streamlit_script_local_path, streamlit_script_remote_path)
)
app = modal.App(name="usage-dashboard", image=image)

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "Hey your starter streamlit isnt working"
    )

@app.function(
    allow_concurrent_inputs=100, secrets=[modal.Secret.from_name("super-secret-alli")]
)
@modal.web_server(8000)
def run():
    target = shlex.quote(streamlit_script_remote_path)
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    # Build environment variables, filtering out None values
    env_vars = {}
    if os.getenv("SUPABASE_KEY"):
        env_vars["SUPABASE_KEY"] = os.getenv("SUPABASE_KEY")
    if os.getenv("SUPABASE_URL"):
        env_vars["SUPABASE_URL"] = os.getenv("SUPABASE_URL")
    
    # Include current environment to ensure PATH and other essential vars are available
    env_vars.update(os.environ)
        
    subprocess.Popen(cmd, shell=True, env=env_vars)


def load_data():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        st.error("Missing SUPABASE_URL or SUPABASE_KEY in environment.")
        st.stop()

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        response = supabase.table("Kentucky Derby").select("*").execute()
        data = response.data or []
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        st.stop()

def main():
    st.title("Kentucky Derby")
    st.write("By Alli Borland")

    df = load_data()
    if df.empty:
        st.warning("No data found in 'Kentucky Derby' table.")
        return

    st.success("Data retrieved successfully")
    st.dataframe(df, use_container_width=True)


    with st.container():
        st.subheader("Kentucky Derby Winners")
        id_counts = df.value_counts("title").reset_index()
        id_counts.columns = ["title", "count"]
        fig1 = px.bar(id_counts, x="title", y="count", title="Winners Per Year")
        st.plotly_chart(fig1, use_container_width=True)

if __name__ == "__main__":
    main()