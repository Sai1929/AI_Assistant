"""Streamlit 3-tab UI — Phase 8."""
import base64
import json
import os
import uuid

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="Christianity AI Assistant",
    layout="wide",
    page_icon="✝",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    # list of {"role": "user"|"assistant", "content": str, "image_b64": str|None}
    st.session_state.messages = []


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Christianity AI Assistant")
    st.caption("Scripture-grounded theological guide")
    st.divider()

    st.selectbox(
        "Denomination",
        ["(auto-detect)", "Catholic", "Protestant", "Orthodox"],
        key="denomination",
    )

    st.divider()
    st.write(f"**Session:** `{st.session_state.session_id[:8]}…`")

    if st.button("Clear Session", use_container_width=True):
        try:
            requests.delete(f"{API_BASE}/session/{st.session_state.session_id}", timeout=10)
        except Exception:
            pass  # backend may not be running — still reset local state
        st.session_state.messages = []
        st.success("Session cleared.")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_chat, tab_image, tab_eval = st.tabs(["💬 Chat", "🖼️ Image Generation", "📊 Eval Results"])


# ── Tab 1: Chat ──────────────────────────────────────────────────────────────

with tab_chat:
    # Display existing conversation
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        image_b64 = msg.get("image_b64")

        if role == "user":
            st.chat_message("user").write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)
                if image_b64:
                    st.image(base64.b64decode(image_b64))

    # Input
    user_input = st.chat_input("Ask about scripture, theology, or Christian history...")
    if user_input:
        # Append user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input, "image_b64": None})
        st.chat_message("user").write(user_input)

        try:
            with st.spinner("Thinking…"):
                resp = requests.post(
                    f"{API_BASE}/chat",
                    json={"session_id": st.session_state.session_id, "message": user_input},
                    timeout=60,
                )
            resp.raise_for_status()
            data = resp.json()

            assistant_content = data.get("response") or ""
            image_b64 = data.get("image_b64")

            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_content, "image_b64": image_b64}
            )
            with st.chat_message("assistant"):
                st.write(assistant_content)
                if image_b64:
                    st.image(base64.b64decode(image_b64))

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Make sure `uvicorn app.main:app` is running.")
        except Exception as e:
            st.error(f"Error: {e}")


# ── Tab 2: Image Generation ───────────────────────────────────────────────────

with tab_image:
    st.header("Generate Christian Art")

    image_prompt = st.text_area(
        "Describe the image you'd like…",
        placeholder="A peaceful nativity scene with warm candlelight…",
        height=120,
    )

    if st.button("Generate Image", use_container_width=True):
        if not image_prompt.strip():
            st.warning("Please enter an image description first.")
        else:
            try:
                with st.spinner("Generating image… this may take a moment."):
                    resp = requests.post(
                        f"{API_BASE}/chat",
                        json={
                            "session_id": st.session_state.session_id,
                            "message": image_prompt,
                        },
                        timeout=120,
                    )
                resp.raise_for_status()
                data = resp.json()

                image_b64 = data.get("image_b64")
                response_text = data.get("response") or ""

                if image_b64:
                    st.image(base64.b64decode(image_b64), caption="Generated Christian Art")
                else:
                    st.warning(response_text or "No image was generated.")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API. Make sure `uvicorn app.main:app` is running.")
            except Exception as e:
                st.error(f"Error: {e}")


# ── Tab 3: Eval Results ───────────────────────────────────────────────────────

with tab_eval:
    st.header("Evaluation Results")

    EVAL_RESULTS_PATH = os.path.join(
        os.path.dirname(__file__), "..", "evaluation", "results.json"
    )

    def load_eval_results():
        if os.path.exists(EVAL_RESULTS_PATH):
            with open(EVAL_RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    results = load_eval_results()

    if results is None:
        st.info("Run `python scripts/run_eval.py` to generate evaluation results.")
    else:
        import pandas as pd  # lazy import — only needed in this tab

        # Summary metrics
        if isinstance(results, list) and results:
            df = pd.DataFrame(results)
            st.subheader("Summary Metrics")
            col1, col2, col3 = st.columns(3)

            if "passed" in df.columns:
                pass_rate = df["passed"].mean() * 100
                col1.metric("Pass Rate", f"{pass_rate:.1f}%")
            if "confidence" in df.columns:
                avg_conf = df["confidence"].mean()
                col2.metric("Avg Confidence", f"{avg_conf:.2f}")
            if "intent" in df.columns:
                col3.metric("Test Cases", len(df))

            st.subheader("Detailed Results")
            st.dataframe(df, use_container_width=True)

        elif isinstance(results, dict):
            # Results stored as a dict with summary + cases
            summary = results.get("summary", {})
            if summary:
                st.subheader("Summary Metrics")
                col1, col2 = st.columns(2)
                if "pass_rate" in summary:
                    col1.metric("Pass Rate", f"{summary['pass_rate'] * 100:.1f}%")
                if "avg_confidence" in summary:
                    col2.metric("Avg Confidence", f"{summary['avg_confidence']:.2f}")

            cases = results.get("cases", results)
            if isinstance(cases, list):
                df = pd.DataFrame(cases)
                st.subheader("Detailed Results")
                st.dataframe(df, use_container_width=True)
            else:
                st.json(results)
        else:
            st.json(results)

    if st.button("Refresh Results", use_container_width=True):
        results = load_eval_results()
        if results is None:
            st.info("No results file found yet. Run `python scripts/run_eval.py`.")
        else:
            st.success("Results refreshed.")
            st.rerun()
