import streamlit as st
from transformers import pipeline
import pandas as pd  # Added this to fix the CSV processing error

# 1. Page Configuration
st.set_page_config(page_title="Shopify AI Review Classifier", page_icon="🛍️")
st.title("🛍️ Shopify AI Review Classifier")
st.subheader("Automated Customer Feedback Analysis System")

# 2. Load AI Model (Force CPU usage for stability)
@st.cache_resource
def load_model():
    return pipeline(
        "sentiment-analysis", 
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        device=-1
    )

classifier = load_model()

# 3. Batch Processing (CSV Upload)
st.divider()
st.subheader("📦 Batch Processing")
uploaded_file = st.file_uploader("Choose a CSV review file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if "review_text" in df.columns:
        with st.spinner("AI is analyzing your data..."):
            # lambda function to extract the label from model output
            df["AI Analysis"] = df['review_text'].apply(lambda x: classifier(x)[0]['label'])
            st.write("### Analysis Results")
            st.dataframe(df) # Display as interactive table
            
            # Export processed data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Result CSV",
                data=csv,
                file_name="ai_analysis_results.csv",
                mime="text/csv",
            )
    else:
        st.error("Error: The file must contain a column named 'review_text'")

# 4. Single Entry Analysis
st.divider()
st.subheader("🔍 Real-time Single Analysis")
input_text = st.text_area("Enter customer review here:", placeholder="Example: Great product, but slow delivery...")

if st.button("Classify Now"):
    if input_text:
        result = classifier(input_text)[0]
        label = result['label']
        score = result['score']
        
        st.write(f"**AI Confidence Score:** {score:.2f}")
        
        # Mapping labels to UI feedback
        if label in ['1 star', '2 stars']:
            st.error(f"Classification: NEGATIVE (Action Required)")
        elif label == '3 stars':
            st.warning(f"Classification: NEUTRAL")
        else:
            st.success(f"Classification: POSITIVE")
    else:
        st.info("Please enter some text to analyze.")
