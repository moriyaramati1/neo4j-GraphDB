import os
import numpy as np
import pandas as pd


# importing the packages that will help us build the DB using py2neo. 
from py2neo import Graph
from py2neo import Node, Relationship
from py2neo.matching import *



class GraphDB:
    def __init__(self) -> None:
        self.db_host = os.environ.get('NEO4J_HOST', 'localhost')
        self.db_port = os.environ.get('NEO4J_PORT', '7687')
        
        self.graph = Graph(f'neo4j://{self.db_host}:{ self.db_port}', auth=("neo4j","1234"))
        # self.graph = Graph(f'bolt://{self.db_host}:{ self.db_port}', auth=("neo4j","1234"))

        self.nodes = NodeMatcher(self.graph)

        self.patients = pd.read_csv('data//all_patients.csv') 
        self.genes = pd.read_csv('data//genes_300.csv')
        self.mutations = pd.read_csv('data//MUT_BRACA_for_300_genes.csv')
        self.subtype = pd.read_csv('data//TNM_SUBTYPE.csv')
        

    def build_nodes(self):
    
        #build the different nodes of the DB. 
    
        # create the node Gene. 
        for _,row in self.genes.iterrows():  
            if not self.nodes.match("Gene", Name=row["Hugo_Symbol"]).first(): 
                Gene = Node("Gene", Name=row["Hugo_Symbol"])  
                self.graph.create(Gene) 
        
        # create the node stage. 
        for i in range(1,5): 
            if not self.nodes.match("Stage", Level=i).first(): 
                Stage = Node("Stage", Level=i) 
                self.graph.create(Stage) 

        # create the node Person. 
        for _, row in self.patients.iterrows(): 
            if not self.nodes.match("Person", ID=row["Patient ID"], Sex = row["Sex"],Age=row["Diagnosis Age"]).first(): 
                Person = Node("Person", ID=row["Patient ID"], Sex = row["Sex"],Age=row["Diagnosis Age"]) 
                self.graph.create(Person)  

        # create the node subtype. 
        for _, row in self.subtype.iterrows(): 
        
            if not self.nodes.match("Tnm", Name=row["stage_event_tnm_categories"]).first(): 
                Tnm = Node("Tnm", Name=row["stage_event_tnm_categories"]) 
                self.graph.create(Tnm) 
        
            if not self.nodes.match("Subtype", Name=row["subtype_BRCA_Subtype_PAM50"]).first():
                if (row["subtype_BRCA_Subtype_PAM50"]!="nan"):
                    Subtype = Node("Subtype", Name=row["subtype_BRCA_Subtype_PAM50"]) 
                    self.graph.create(Subtype)




    def bulid_relationships(self):
        # create relationship between two nodes: Person -> has a ->Gene
        for _, row in self.mutations.iterrows(): 
        
            if (self.nodes.match("Person",ID = row["patiant"]).first()) and (self.nodes.match("Gene",Name=row["Hugo_Symbol"]).first()):
                Person = self.nodes.match("Person",ID = row["patiant"]).first() 
                Gene = self.nodes.match("Gene",Name=row["Hugo_Symbol"]).first()  
                Has_a = Relationship(Person, "Has_a",Gene) 
                self.graph.create(Has_a) 

        # create relationship between two nodes: Person -> Category ->Tnm
        for _, row in self.subtype.iterrows(): 
        
            if (self.nodes.match("Person",ID = row["bcr_patient_barcode"]).first()) and (self.nodes.match("Tnm",Name=row["stage_event_tnm_categories"]).first()):
                Person = self.nodes.match("Person",ID = row["bcr_patient_barcode"]).first() 
                Tnm = self.nodes.match("Tnm",Name=row["stage_event_tnm_categories"]).first()
                Category = Relationship(Person, "Category",Tnm) 
                self.graph.create(Category) 

        # create relationship between two nodes: Person -> Sub ->Subtype
        for _, row in self.subtype.iterrows():
            if (self.nodes.match("Person",ID = row["bcr_patient_barcode"]).first()) and (self.nodes.match("Subtype", Name=row["subtype_BRCA_Subtype_PAM50"]).first()):
                Person = self.nodes.match("Person",ID = row["bcr_patient_barcode"]).first()
                Subtype = self.nodes.match("Subtype",Name=row["subtype_BRCA_Subtype_PAM50"]).first()
                Sub = Relationship(Person, "Sub",Subtype)# add the relationship bewteen them.
                self.nodes.graph.create(Sub)

        # create relationship between two nodes: Person -> level ->Stage
        for _, row in self.patients.iterrows(): 
        
            if (self.nodes.match("Person",ID = row["Patient ID"]).first()):
                Person = self.nodes.match("Person",ID = row["Patient ID"]).first()
                Stage = None
                x=row["Neoplasm Disease Stage American Joint Committee on Cancer Code"]
                if (x=="Stage IA" or x=="Stage IB" or x=="Stage I"):
                    Stage= self.nodes.match("Stage",Level=1).first()
                if (x=="Stage IIA" or x=="Stage IIB" or x=="Stage II"):
                    Stage= self.nodes.match("Stage",Level=2).first()
                if (x=="Stage IIIA" or x=="Stage IIIB" or x=="Stage IIIC"or x=="Stage III"):
                    Stage= self.nodes.match("Stage",Level=3).first()
                if (x=="Stage IV"):
                    Stage= self.nodes.match("Stage",Level=4).first()
                if Stage:
                    level = Relationship(Person, "level",Stage)# add the relationship bewteen them.
                    self.graph.create(level)


    

    def create_similarity(self):
        
        # create a sub graph called 'Similarity_Graph_Clinic' which contains Person and Gene nodes and a relationship Has_a. 
        query ="CALL gds.graph.project('Similarity_Graph_Clinic',['Person', 'Gene'],'Has_a')"
        self.graph.run(query)
        
        # we would like to add relationships on the 'Similarity_Graph_Clinic' graph, the relationship is called Clinic_Similarity and it has a 
        # property 'SIMILARITY' which will contain the level of the two nodes similarity according to the algorithm. 
        query="CALL gds.nodeSimilarity.write('Similarity_Graph_Clinic',{writeRelationshipType: 'Clinic_Similarity',writeProperty: 'SIMILARITY'})"
        self.graph.run(query)  
        
        # creating the similarity and returning every two person nodes and their value of similarity in a descinding order. 
        query="CALL gds.nodeSimilarity.stream('Similarity_Graph_Clinic')YIELD node1, node2, similarity RETURN gds.util.asNode(node1).ID AS Person1, gds.util.asNode(node2).ID AS Person2, similarity ORDER BY similarity DESCENDING, Person1, Person2"
        clinic = self.graph.run(query).to_data_frame() # create a dataframe from the query.

      

        # create a sub graph called 'Similarity_Graph_Not_Clinic' which contains Person, Stage, Subtype and Tnm nodes
        # and a relationships Sub, level and Category. 
        query = "CALL gds.graph.project('Similarity_Graph_Not_Clinic', ['Person', 'Stage', 'Subtype','Tnm'], ['Sub','level','Category'])"
        self.graph.run(query)
    
        # we would like to add relationships on the 'Similarity_Graph_Not_Clinic' graph, the relationship is called Not_Clinic_Similarity and it has a 
        # property 'SIMILARITY' which will contain the level of the two nodes similarity according to the algorithm. 
        query="CALL gds.nodeSimilarity.write('Similarity_Graph_Not_Clinic',{writeRelationshipType: 'Not_Clinic_Similarity',writeProperty: 'SIMILARITY'})"
        self.graph.run(query)  
        
        # creating the similarity and returning every two person nodes and their value of similarity in a descinding order. 
        query="CALL gds.nodeSimilarity.stream('Similarity_Graph_Not_Clinic')YIELD node1, node2, similarity RETURN gds.util.asNode(node1).ID AS Person1, gds.util.asNode(node2).ID AS Person2, similarity ORDER BY similarity DESCENDING, Person1, Person2"
        not_clinic = self.graph.run(query).to_data_frame()
        

        # find all relationships from type Clinic_Similarity and Not_Clinic_Similarity that connect any two nodes and delete the relationship. 
        query="MATCH ()-[r:Clinic_Similarity]-() DELETE r"
        self.graph.run(query) # run the query
        query="MATCH ()-[r:Not_Clinic_Similarity]-() DELETE r"
        self.graph.run(query)

        query="CALL gds.graph.drop('Similarity_Graph_Clinic', false)"
        self.graph.run(query) # run the query
        query="CALL gds.graph.drop('Similarity_Graph_Not_Clinic', false)"
        self.graph.run(query) # run the query
        
        
        return clinic,not_clinic
    
