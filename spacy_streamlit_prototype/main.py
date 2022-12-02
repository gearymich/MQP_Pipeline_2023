
import spacy
import streamlit as st
from spacy_streamlit import visualize_ner, process_text

# uploaded_file = st.file_uploader("Choose a file")
# if uploaded_file is not None:
#     # To read file as bytes:
#     bytes_data = uploaded_file.getvalue()
#     st.write(bytes_data)
#     print("here!")

spacy_model = "/Users/geary/MQP_etc/ner_model/output/model-best"

# nlp = spacy.load(spacy_model)
text = st.text_area("Text to analyze", "")
doc = process_text(spacy_model, text)
traf_labels={"traffickerBirthYear": "#7feceb", "traffickerName": "#aa9ff9", "traffickerOrigin": "#c0e1d9"}

trafficker_ner_visuals = {  "ents": list(traf_labels.keys()),
                            "colors": traf_labels}

visualize_ner(  doc, 
                labels=list(traf_labels.keys()),
                title="Wildlife MQP - Trafficker Info NER Visualization",
                show_table=True,
                displacy_options=trafficker_ner_visuals)


# sst.visualize(  models,
#                 text,
#                 visualizers=visualizers, 
#                 default_model="/Users/geary/MQP_etc/ner_model/output/model-best",
#                 show_json_doc=False,
#                 show_meta=False,
#                 show_config=False,
#                 show_logo=False)
