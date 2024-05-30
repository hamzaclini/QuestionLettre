import streamlit as st
import pandas as pd
import datetime
import pymongo
import hmac
import time
import os

st.set_page_config(page_title="Clinicog Questionaire", page_icon="🧠")

# Function to check password
def check_password(questionnaire_passwords):
    """Returns the name of the questionnaire if the user has the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        password_correct = False  # Assume the password is incorrect initially
        for key, value in questionnaire_passwords.items():
            if hmac.compare_digest(st.session_state["password"], value):
                password_correct = True
                st.session_state["questionnaire"] = key
                break
        
        st.session_state["password_correct"] = password_correct
        st.session_state["password_attempted"] = True
        del st.session_state["password"]  # Always delete the password after checking

    # Initialize the state
    if "password" not in st.session_state:
        st.session_state["password"] = ""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = None
    if "password_attempted" not in st.session_state:
        st.session_state["password_attempted"] = False

    # Show input for password in the main page.
    if not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")

        # Check if password is incorrect
        if st.session_state["password_attempted"] and not st.session_state["password_correct"]:
            st.error("😕 Password incorrect")
        
        st.stop()
    else:
        return st.session_state.get("questionnaire", None)

# Load passwords from secrets
questionnaire_passwords = {k: v for k, v in st.secrets["passwords"].items()}

# Check password and get the corresponding questionnaire
questionnaire_name = check_password(questionnaire_passwords)
if questionnaire_name:
    pass
else:
    st.stop()  # Do not continue if the password is not correct.

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

sex_mapping = {'male': 0, 'female': 1}
answers = {}

st.markdown(
        """<style>
        div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
                }
        </style>
                """, unsafe_allow_html=True)


st.markdown(
    """
    <style>
    .centered_button {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.sidebar.header('Informations')

#slider_values = [1,2,3,4]

#slider_strings = ["Très insuffisant", "Insuffisant", "Satisfaisant", "Très satisfaisant"]


def stringify(i:int = 0) -> str:
    return slider_strings[i-1]


def write_data(new_data):
    db = client.Questions
    db.Lettres.insert_one(new_data)


def check_data(code):
    db = client.Questions
    collection = db.Lettres
    query = {"user.Code": code}
    result = collection.find_one(query)
    #print(result)
    return result
    #print(query)
    #print(result)
    #if result:
    #    collection.delete_one(query)
    #    return True
    #else:
    #    return False
    
#def read_from_file(file_path):
#    with open(file_path, "r", encoding="utf-8") as file:
#        comp_list = [line.strip() for line in file]
#    return comp_list

def read_data_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    all_lists = [item.strip() for item in file_content.split("***")]
    #print(all_lists)

    return all_lists

all_data = read_data_file(questionnaire_name + ".txt")

st.write(f"""
# {all_data[0]}
""")

all_questions = all_data[1].split("\n\n")
loop = len(all_questions)
if(loop==1):
    Comp = all_data[1].split("\n")


slider_strings = all_data[2].split("\n")
slider_values = [i for i in range(int(all_data[3]), len(slider_strings) + 1)]
slider_values_inv = [i for i in range(len(slider_strings), int(all_data[3])-1, -1)]

def user_input_features():
        #current_date = datetime.date.today()
        code = st.sidebar.text_input("Code")
        #surname = st.sidebar.text_input("Nom")
        #name = st.sidebar.text_input("Prénom")
        #date = st.sidebar.date_input("Date de naissance", datetime.date(2010, 1, 1))
        #age = current_date.year - date.year - ((current_date.month, current_date.day) < (date.month, date.day))
        #sex = st.sidebar.selectbox('Genre',('Homme','Femme'))
        #age = st.sidebar.number_input('Age:', min_value=0, max_value=120, step=1)
        #study = st.sidebar.selectbox("Niveau d'etude",('CAP/BEP','Baccalauréat professionnel','Baccalauréat général', 'Bac +2 (DUT/BTS)', 'Bac +3 (Licence)',
        #                                               'Bac +5 (Master)', 'Bac +7 (Doctorat, écoles supérieurs)'))
        #questionnaire = st.sidebar.selectbox('Questionnaire',('TRAQ','FAST','TRAQ+FAST'))
        #st.write("""## Concernant mon utilisation de la planche de transfert:""")
        if (loop == 1):
            param = Comp[0]
            Comp = Comp[1:]
            for i, question in enumerate(Comp, start=1):
                if(question[0] == "-"):
                    slider_output = st.select_slider(
                    #f":red[{question}]",
                    f"{question[1:]}",
                    options=slider_values_inv,
                    value=slider_values_inv[0],
                    format_func=stringify
                    )
                else:
                    slider_output = st.select_slider(
                    #f":red[{question}]",
                    f"{question}",
                    options=slider_values,
                    value=slider_values[0],
                    format_func=stringify
                    )
                answers[f"{param}{i}"] = slider_output
        else:
            for j in range(len(all_questions)):
                Comp = all_questions[j].split("\n")
                param = Comp[0]
                Comp = Comp[1:]
                for i, question in enumerate(Comp, start=1):
                    if(question[0] == "-"):
                        slider_output = st.select_slider(
                        f"{question[1:]}",
                        options=slider_values_inv,
                        value=slider_values_inv[0],
                        format_func=stringify
                        )
                    else:
                        slider_output = st.select_slider(
                        f"{question}",
                        options=slider_values,
                        value=1,
                        format_func=stringify
                        )
                    answers[f"{param}{i}"] = slider_output


        user_data = {'Questionnaire': all_data[0],
                     'Code': code,
                     #'Sex': sex,
                     #'Age': age,
                     'Qdate': datetime.date.today().strftime('%Y-%m-%d')}
                     #'educationalLevel': study}
        answers_data = answers

        document = {
        #"_id": ObjectId(),  # Generate a new ObjectId
        "user": user_data,
        "answers": answers_data
        #"__v": 0
        }
                
        return document, code 



document, code = user_input_features()
result = check_data(code)

if "disabled" not in st.session_state:
    st.session_state.disabled = False
     
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    button = st.button('Enregistrer', disabled=st.session_state.disabled)
    st.image("clinicogImg.png", width=200)

if button:
     if(result):
        if("Questionnaire" in result['user']):
            write_data(document)
            st.write("## Merci d'avoir participé(e) à ce questionnaire")
            #st.write("## Vous avez déjà participé à ce questionnaire!")
            st.session_state.disabled = True
            time.sleep(5)
            st.rerun()
        else:
            db = client.Questions
            collection = db.Lettres
            collection.delete_one(result)
            write_data(document)
            st.write("## Merci d'avoir participé(e) à ce questionnaire")
            st.session_state.disabled = True
            time.sleep(5)
            st.rerun()
     else:
        st.write("## Vous n'avez pas le droit de participer")
        st.session_state.disabled = True
        time.sleep(5)
        st.rerun()
    
#if button:
#     if(result):
#        if("Questionnaire" in result['user']):
#            st.write("## Vous avez déjà participé à ce questionnaire!")
#            st.session_state.disabled = True
#            time.sleep(5)
#            st.rerun()
#        else:
#            db = client.Questionnaire
#            collection = db.General
#            collection.delete_one(result)
#            write_data(document)
#            st.write("## Merci d'avoir participé(e) à ce questionnaire")
#            st.session_state.disabled = True
#            time.sleep(5)
#            st.rerun()
#     else:
#        st.write("## Vous n'avez pas le droit de participer")
#        st.session_state.disabled = True
#        time.sleep(5)
#        st.rerun()


