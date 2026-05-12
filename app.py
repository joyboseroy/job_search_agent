"""
app.py

Streamlit UI for the Job Search Campaign Agent.
Ties together all agents and tools in one interface.

Run with:
    streamlit run app.py
"""

import streamlit as st
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.cover_letter_agent import CoverLetterAgent
from agents.interview_coach import InterviewCoach, BatchQuestionGenerator, TOPIC_PROMPTS
from agents.followup_drafter import FollowUpDrafter, FOLLOW_UP_TYPES
from tracker.tracker import ApplicationTracker

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Search Campaign Agent",
    page_icon="🎯",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        font-family: monospace;
        font-size: 12px;
        padding: 6px 16px;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
    .metric-num {
        font-size: 28px;
        font-weight: 600;
        color: #1a1a1a;
    }
    .metric-label {
        font-size: 11px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    code { font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ── Init session state ────────────────────────────────────────────────────────
if "coach" not in st.session_state:
    st.session_state.coach = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "tracker" not in st.session_state:
    st.session_state.tracker = ApplicationTracker()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🎯 Job Search Campaign Agent")
st.caption("Cover letters · Application tracker · Interview prep · Follow-up drafts")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "✉ Cover Letter",
    "📋 Application Tracker",
    "🧠 Interview Prep",
    "📬 Follow-up Drafter",
    "📊 Dashboard",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: COVER LETTER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("#### Inputs")
        company = st.text_input("Company", placeholder="e.g. Dell Technologies")
        role = st.text_input("Role", placeholder="e.g. Advisory Consultant, Data Scientist")
        jd = st.text_area(
            "Job Description (paste key parts)",
            height=200,
            placeholder="Paste the JD or key requirements here..."
        )
        tone = st.selectbox(
            "Tone",
            options=["senior-confident", "warm-collaborative", "technical-precise", "concise-direct"],
            format_func=lambda x: x.replace("-", " ").title()
        )
        emphasis = st.text_input(
            "Emphasise (optional)",
            placeholder="e.g. knowledge graphs, telecom AI, patents"
        )
        generate_btn = st.button("Generate Cover Letter", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### Output")
        output_placeholder = st.empty()

        if generate_btn:
            if not company and not jd:
                st.error("Enter company name or job description.")
            else:
                with st.spinner("Generating tailored cover letter..."):
                    try:
                        agent = CoverLetterAgent()
                        letter = agent.generate(
                            role=role or "Senior Applied AI role",
                            company=company or "the company",
                            jd=jd,
                            tone=tone,
                            emphasis=[e.strip() for e in emphasis.split(",")] if emphasis else None,
                        )
                        st.session_state["cover_letter"] = letter
                    except Exception as e:
                        st.error(f"Error: {e}")

        if "cover_letter" in st.session_state:
            letter_text = st.session_state["cover_letter"]
            output_placeholder.text_area("Cover Letter", letter_text, height=400)
            col_copy, col_regen = st.columns(2)
            with col_copy:
                st.download_button(
                    "Download as .txt",
                    letter_text,
                    file_name=f"cover_letter_{company.replace(' ', '_')}.txt" if company else "cover_letter.txt",
                    use_container_width=True
                )
        else:
            output_placeholder.info("Fill in the inputs and click Generate.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: APPLICATION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    tracker = st.session_state.tracker
    stats = tracker.get_stats()

    # Stats row
    metric_cols = st.columns(6)
    metric_data = [
        ("Total", stats.get("total", 0)),
        ("Applied", stats.get("applied", 0)),
        ("Interviews", stats.get("interview", 0)),
        ("Offers", stats.get("offer", 0)),
        ("Rejected", stats.get("rejected", 0)),
        ("Follow-up needed", stats.get("needs_followup", 0)),
    ]
    for col, (label, val) in zip(metric_cols, metric_data):
        with col:
            st.metric(label, val)

    st.divider()

    # Add new application
    with st.expander("➕ Add Application", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            t_company = st.text_input("Company*", key="t_company")
            t_role = st.text_input("Role", key="t_role")
        with c2:
            t_status = st.selectbox(
                "Status",
                ["applied", "screening", "interview", "offer", "rejected", "withdrawn", "no_response"],
                key="t_status"
            )
            t_contact = st.text_input("Contact name", key="t_contact")
        with c3:
            t_contact_email = st.text_input("Contact email", key="t_contact_email")
            t_salary = st.text_input("Salary range", key="t_salary")
        with c4:
            t_notes = st.text_area("Notes", height=80, key="t_notes")
            t_jd_url = st.text_input("JD URL", key="t_jd_url")

        if st.button("Add Application", type="primary"):
            if not t_company:
                st.error("Company name required.")
            else:
                tracker.add(
                    company=t_company,
                    role=t_role,
                    status=t_status,
                    contact_name=t_contact,
                    contact_email=t_contact_email,
                    notes=t_notes,
                    jd_url=t_jd_url,
                    salary_range=t_salary,
                )
                st.success(f"Added: {t_company}")
                st.rerun()

    # Applications table
    st.markdown("#### Applications")
    status_filter = st.selectbox(
        "Filter by status",
        ["All"] + ["applied", "screening", "interview", "offer", "rejected", "withdrawn", "no_response"],
        key="status_filter"
    )

    apps = tracker.get_all(
        status_filter=None if status_filter == "All" else status_filter
    )

    if not apps:
        st.info("No applications yet. Add your first one above.")
    else:
        for app in apps:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1.5, 1])
                with c1:
                    st.markdown(f"**{app['company']}**")
                    st.caption(app.get('role') or '—')
                with c2:
                    st.caption(f"Contact: {app.get('contact_name') or '—'}")
                    st.caption(f"Notes: {(app.get('notes') or '—')[:60]}")
                with c3:
                    new_status = st.selectbox(
                        "Status",
                        ["applied", "screening", "interview", "offer", "rejected", "withdrawn", "no_response"],
                        index=["applied", "screening", "interview", "offer", "rejected", "withdrawn", "no_response"].index(app["status"]),
                        key=f"status_{app['id']}",
                        label_visibility="collapsed"
                    )
                    if new_status != app["status"]:
                        tracker.update_status(app["id"], new_status)
                        st.rerun()
                with c4:
                    st.caption(f"Applied: {app.get('applied_date') or '—'}")
                    st.caption(f"Last contact: {app.get('last_contact') or '—'}")
                with c5:
                    if st.button("Delete", key=f"del_{app['id']}", type="secondary"):
                        tracker.delete(app["id"])
                        st.rerun()
                st.divider()

    # Stale applications
    stale = tracker.get_stale()
    if stale:
        st.warning(f"⚠ {len(stale)} application(s) need follow-up (no contact in 14+ days)")
        for app in stale:
            st.caption(f"  • {app['company']} — last contact: {app.get('last_contact')}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: INTERVIEW PREP
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Quick drills")
        topics = list(TOPIC_PROMPTS.keys())
        for topic in topics:
            label = topic.replace("_", " ").title()
            if st.button(label, key=f"drill_{topic}", use_container_width=True):
                if st.session_state.coach is None:
                    st.session_state.coach = InterviewCoach()
                with st.spinner(f"Starting {label} drill..."):
                    response = st.session_state.coach.start_topic(topic)
                    st.session_state.chat_history.append(
                        {"role": "coach", "content": response, "label": f"[{label}]"}
                    )

        st.divider()
        if st.button("Reset session", use_container_width=True):
            st.session_state.coach = None
            st.session_state.chat_history = []
            st.rerun()

        if st.button("Get session summary", use_container_width=True):
            if st.session_state.coach and len(st.session_state.chat_history) > 2:
                with st.spinner("Summarising..."):
                    summary = st.session_state.coach.get_summary()
                    st.session_state.chat_history.append(
                        {"role": "coach", "content": summary, "label": "[Summary]"}
                    )
            else:
                st.info("Need more conversation to summarise.")

    with col2:
        st.markdown("#### Interview Coach")

        # Chat display
        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.chat_history:
                st.info("Pick a topic from the left or type your own message below.")
            for msg in st.session_state.chat_history:
                if msg["role"] == "coach":
                    st.markdown(f"**🤖 Coach** {msg.get('label', '')}")
                    st.markdown(msg["content"])
                    st.divider()
                else:
                    st.markdown(f"**You:** {msg['content']}")
                    st.divider()

        # Input
        user_input = st.text_input(
            "Your answer or question",
            key="prep_input",
            placeholder="Type your answer here..."
        )
        if st.button("Send", type="primary", key="prep_send"):
            if user_input:
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_input}
                )
                if st.session_state.coach is None:
                    st.session_state.coach = InterviewCoach()
                with st.spinner("Coach is evaluating..."):
                    response = st.session_state.coach.chat(user_input)
                    st.session_state.chat_history.append(
                        {"role": "coach", "content": response}
                    )
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: FOLLOW-UP DRAFTER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("#### Context")
        fu_type = st.selectbox(
            "Type",
            list(FOLLOW_UP_TYPES.keys()),
            format_func=lambda x: FOLLOW_UP_TYPES[x]["description"]
        )
        fu_company = st.text_input("Company", key="fu_company")
        fu_contact = st.text_input("Contact name & title", key="fu_contact", placeholder="e.g. Himani Sharma, TA")
        fu_role = st.text_input("Role applied for", key="fu_role")
        fu_days = st.number_input("Days since last contact", min_value=0, value=7, key="fu_days")
        fu_notes = st.text_area("Notes / context", height=120, key="fu_notes",
                                 placeholder="What was discussed? Any specific points to reference?")
        fu_btn = st.button("Draft Follow-up", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### Draft")
        fu_placeholder = st.empty()

        if fu_btn:
            with st.spinner("Drafting..."):
                try:
                    drafter = FollowUpDrafter()
                    result = drafter.draft(
                        follow_up_type=fu_type,
                        company=fu_company or "the company",
                        contact=fu_contact,
                        days_since=int(fu_days),
                        role=fu_role,
                        notes=fu_notes,
                    )
                    st.session_state["followup_result"] = result
                except Exception as e:
                    st.error(f"Error: {e}")

        if "followup_result" in st.session_state:
            r = st.session_state["followup_result"]
            if r.get("subject"):
                st.markdown(f"**Subject:** `{r['subject']}`")
            st.text_area("Email body", r["body"], height=300)
            st.download_button(
                "Download as .txt",
                f"Subject: {r.get('subject', '')}\n\n{r['body']}",
                file_name="followup_email.txt",
                use_container_width=True
            )
        else:
            fu_placeholder.info("Fill in the context and click Draft.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("#### Job Search Dashboard")

    tracker = st.session_state.tracker
    stats = tracker.get_stats()
    apps = tracker.get_all()
    stale = tracker.get_stale()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Status breakdown**")
        status_counts = {}
        for app in apps:
            s = app["status"]
            status_counts[s] = status_counts.get(s, 0) + 1
        if status_counts:
            import pandas as pd
            df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
            st.bar_chart(df.set_index("Status"))
        else:
            st.info("No applications yet.")

    with col2:
        st.markdown("**Needs follow-up**")
        if stale:
            for app in stale:
                days_ago = "unknown"
                if app.get("last_contact"):
                    from datetime import date
                    try:
                        last = date.fromisoformat(app["last_contact"])
                        days_ago = (date.today() - last).days
                    except:
                        pass
                st.markdown(f"- **{app['company']}** ({app.get('role') or '—'}) — {days_ago} days ago")
        else:
            st.success("All applications up to date.")

    st.divider()
    st.markdown("**Recent applications**")
    recent = apps[:5]
    if recent:
        import pandas as pd
        df = pd.DataFrame([{
            "Company": a["company"],
            "Role": a.get("role") or "—",
            "Status": a["status"],
            "Applied": a.get("applied_date") or "—",
            "Last contact": a.get("last_contact") or "—",
        } for a in recent])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No applications yet.")
