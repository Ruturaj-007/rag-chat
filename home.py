import streamlit as st
import backend as rag

st.title("Recommendation System with RAG Pipeline")
st.subheader("Add a subheader with more explanation if you want")
st.divider()

# * SIDEBAR
# Upload in here the context that goes into MongoDB (knowledge base)
with st.sidebar:
    st.header("Upload context")
    user_text = st.text_area("Enter knowledge here", height=150)
    if st.button("Upload to MongoDB"):
        if user_text:
            with st.spinner("Processing.."):
                rag.ingest_text(user_text)
                st.success("Uploaded!")
        else:
            st.warning("Please enter text")

st.header("Ask anything to the chat from our Knowledge Base")

# * CHAT MESSAGE
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# * HANDLES USER INPUT 
prompt = st.chat_input("Ask a question...")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt
    })

# Generate RAG response in here
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data = rag.get_rag_response(prompt)  # Brick 3!
            answer = response_data["answer"]
            sources = response_data["sources"]
            st.markdown(answer)
            with st.expander("Sources"):
                for i, source in enumerate(sources):
                    st.markdown(f"**Source {i+1}:** {source.page_content}")
    
    st.session_state.messages.append({"role": "assistant", "content": answer})



