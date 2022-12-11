
# Neo4j-GraphDB

In this project i created graph database with neo4j platform.

The aim of this project was to build a DB graph for breast cancer patients that includes mutation genes, patients, cancer stage and characteristics of malignancy and cancer subgroups.
and to find the most similar patients with the characteristics they share and to be able to treat them with the same manner.
This division and similarity will help us move forward with personalized medicine.

# The data folder:
  * patients IDs and personal information such as patient's ID, age, gender,cancer stage.
  * 300 genes of mutation genes that is most common in breat cancer.
  * MUT_BRACA_for_300_genes includes the mutation each patients has.
  * Tnm_Subtype a file that contains the id of patients and Tnm and subtpye that match for the cancer status.

The structure of the graph:
## nodes Type:
- Person
- Gene
- Stage
- Subtype  
- Tnm
  
## Relationship Types:
Has_a - relationship that connects between Person(patient) and his Gene mutation.

Level - relationship that connects between Person and the cancer Stage.

Sub - relationship that connects between Person and the Subtype group of the cancer.

Category - relationship that connects between Person and the malignancy of cancer.

### Example image of the graph:
<p align="left">
  <img src=images_folder\graph_image.png width="350" title="hover text"  width="800" height="400"
</p>


# Queries notebook:
  A notebook with queries for understanding ,analysing and visualising the data.
  
# The app folder:
An application for user interface that allowes the user to enter a patients ID and to get the similar patients.

There are two options of similarities:

- clinic similarity which based on gene mutations.
  
- Not clinic similarity which based on sub category, stage of cancer and malignancy.

  
To calculate the similarity I used a graph science algorithm that uses Jaccard Similarity:
 
<p align="left">
  <img src=images_folder\similarity.png width="350" title="hover text"  width="1000" height="150"
</p>
 
 ### Example image of the application:
  
  <p align="left">
    <img src=images_folder\open_screen.png width="350" title="hover text"  width="1000" height="300"
  </p>
  
    
  <p align="left">
    <img src=images_folder\result.png width="350" title="hover text"  width="800" height="400"
  </p>

  
 # Docker infrastructure: 
builds a docker compose that create two containers - one is for neo4j database and the other one for the application that communicates with that database.
