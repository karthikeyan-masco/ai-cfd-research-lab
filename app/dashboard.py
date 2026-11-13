import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from ai_cfd_lab.debate.protocol import DebateEngine
from ai_cfd_lab.debate.report import to_markdown
from ai_cfd_lab.providers.demo import DemoProvider

st.set_page_config(page_title="AI CFD Research Laboratory", layout="wide")
st.title("AI CFD Research Laboratory")
st.caption("Milestone 1 · Structured scientific debate prototype")

question = st.text_area(
    "Research question",
    "For a Mach 2 normal shock, calculate downstream properties and identify numerical checks.",
    height=110,
)
rounds = st.slider("Debate rounds", 1, 3, 2)
st.info("Dashboard currently uses the deterministic offline provider. Live provider selection will be added after provider-specific testing.")
if st.button("Run debate", type="primary"):
    with st.spinner("Running specialist analysis and review..."):
        record = DebateEngine(DemoProvider(), max_rounds=rounds).run(question)
    st.subheader("Final verdict")
    st.write(record.final_verdict)
    st.subheader("Unresolved issues")
    for item in record.unresolved_issues:
        st.write(f"- {item}")
    st.subheader("Recommended tests")
    for item in record.recommended_tests:
        st.write(f"- {item}")
    report = to_markdown(record)
    st.download_button("Download Markdown report", report, file_name="ai_cfd_debate_report.md")
    st.download_button("Download JSON record", __import__("json").dumps(record.to_dict(), indent=2),
                       file_name="ai_cfd_debate_record.json", mime="application/json")
