
#good examples with a lot information
#TCGA-E2-A158
#TCGA-A2-A04Y

# import libraries:

import pandas as pd
import streamlit as st
import altair as alt
from PIL import Image
import sys
import os
sys.path.insert(1,os.getcwd())
from DB_Load import GraphDB


# my_graph  = GraphDB()
# my_graph.build_nodes()
# my_graph.bulid_relationships()
# clinic,not_clinic = my_graph.create_similarity()




# web site start app\logoneo.png
image = Image.open('./app/open_screen.png')
st.image(image,use_column_width=True)


#that will explain the discription lines of the weeb program.
st.title("""
Find The most similar patients
**This app return the similar patients for the patient you ask, depends on clinic or not clinic properties.**

*** 
""")

name = st.text_input("Enter Your Patients ID", "Type Here ...")
if (st.button('Submit')):
    result = name.title()
    st.success(result)


st.write(""" Which type of similarity do you want: """)

# Create a simple button
if(st.button("Clinic")):

    # if (not my_graph.nodes.match("Person", ID=name).first()):
    #     st.text("No such patient exists, please try again")
    if clinic["Person1"].str.contains(name).any() == False:
        st.text("No such patient exists, please try again")
    else:
        st.header('INPUT(Patient Identifier)')
        # print the procecced dna
        name

        st.header('OUTPUT(Similar Patients)')
        x = clinic[clinic["Person1"] == name]
        row_1 = x.iloc[0]
        sim = row_1['similarity']
        y = x[x['similarity'] == sim]
        st.write("The similarity is:", sim, "\n")
        similar = pd.DataFrame(columns=["Patient", "Gene"], index=list(range(0, len(y))))
        for i in range(0, len(y)):
            person = y['Person2'].iloc[i]
            similar.iloc[i]["Patient"] = person
            query = "match(p1:Person{ID:'" + person + "'})-->(gene:Gene)<--(p2:Person{ID:'" + name + "'}) return gene"
            data = my_graph.graph.run(query).to_data_frame()

            st.write("""***""")
            st.write(" The Similar patient:   ", person)

            res = []
            for j in data["gene"].index:
                for key in data["gene"].tolist()[j].keys():
                    res.append(data["gene"].tolist()[j][key])
                    st.write(""" The Similar Property Is The Gene  """, data["gene"].tolist()[j][key], """ Node """)

            similar.iloc[i]["Gene"] = res
        st.header('Summarize table')
        st.write(similar)


elif(st.button("Not Clinic")):

    if not_clinic["Person1"].str.contains(name).any() == False:
        st.text("No such patient exists, please try again")
    else:
        st.header('''INPUT: Patient Identifier ''')
        # print the procecced dna
        name
        st.header('OUTPUT:Similar Patients')
        x = not_clinic[not_clinic["Person1"] == name]
        row_1 = x.iloc[0]
        sim = row_1['similarity']
        y = x[x['similarity'] == sim]
        st.write("The similarity is: ", sim, "\n")

        similar = pd.DataFrame(columns=["Patient","Stage,Subtype,Tnm"], index=list(range(0, len(y))))
        for i in range(0, len(y)):
            person = y['Person2'].iloc[i]
            similar.iloc[i]["Patient"] = person
            query="match(p1:Person{ID:'"+person+"'})-->(n)<--(p2:Person{ID:'"+name+"'}) where not(n:Person) and not(n:Gene) return n"
            data = my_graph.graph.run(query).to_data_frame()
            # st.write(d["g"])

            st.write("""***""")
            st.write("**The Similar patient:**  ", person)
            res = []
            for j in data["n"].index:
                for key in data["n"].tolist()[j].keys():
                    res.append(str(data["n"].tolist()[j][key]))
                    if(type(data["n"].tolist()[j][key])==str):
                       st.write("The Similar Property Is Subtype or Category of   ", data["n"].tolist()[j][key],"  Node  ")
                    else:
                        st.write("  The Similar Property Is Stage   ", data["n"].tolist()[j][key], " Node ")
            similar.iloc[i]["Stage,Subtype,Tnm"] = res
        st.header('Summarize table')
        st.write(similar)



