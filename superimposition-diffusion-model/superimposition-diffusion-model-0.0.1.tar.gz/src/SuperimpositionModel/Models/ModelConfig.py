
class ModelConfig:
    def __init__(self) -> None:
        self.config = {
            "beta1" : 0,
            "beta2" : 0,
            "initial_infected": 0,
            "recovery_prob": 0,
            "Threshold" : 0,
            "number_of_groups" : 0,
            "intersection_probability": 0,
            "intersection_size": 0,
            "HO_prapagation_mechanism" : None,
            "HO_node_lists" : None,
            "HO_probability": None,
            "HO_condition" : None
        }
    
    def add_model_parameter(self , param , value):
        if param not in ["beta1" , "beta2" ,"initial_infected" ,"recovery_prob","number_of_groups" ,"Threshold" ,"diffusion_model" , "intersection_size" ,  "intersection_probability" , "HO_prapagation_mechanism" , "HO_probability" , "HO_condition" , "HO_node_lists"]:
            raise ValueError("Parameter name not correct.")
        
        if param in ["beta1" , "beta2" ,"initial_infected" ,"recovery_prob" ,"Threshold"] and (value <0 or value>1):
            raise ValueError("value should be in range of 0 to 1.")

        if param == "diffusion_model" and value not in ["SIS" , "SIRS" , "SIR"]:
            raise ValueError("Value should be in [\"SIS\" , \"SIRS\" , \"SIR\"]")

        if param in ["number_of_groups" , "intersection_size"] and value < 0 :
            raise ValueError("Value should be > 0")  

        if param == "HO_prapagation_mechanism"  and value not in ["ThresholdClique" , "Clique" , "Triangle" , "Customized"]:
            raise ValueError("value should be in [\"ThresholdClique\" , \"Clique\" , \"Triangle\" , \"Customized\"]")
        
        if param in ["HO_probability" , "HO_condition"] and not callable(value) and value.__code__.co_argcount == 3:
            raise ValueError("value should be a callable function with 3 inputs: func(num_nodes , num_infected , threshold)")

        self.config[param] = value
