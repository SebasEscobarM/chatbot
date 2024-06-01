from experta import *
import os
os.environ['TQDM_DISABLE'] = '1'
import logging
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import numpy as np
import itertools

# Configurar el registro para ocultar los mensajes de progreso
logging.getLogger('pgmpy').setLevel(logging.WARNING)

printed = False

class Symptom(Fact):
    pass

class History(Fact):
    pass

class SymptomsExpert(KnowledgeEngine):

    generated_facts=[]

    def declare(self, *facts):
        for fact in facts:
            SymptomsExpert.generated_facts.append(fact)
        super().declare(*facts)

    # -------------------------------- DEPRESSION -----------------------------------
    # BAD FELLINGS
    @Rule(Symptom(positive_feeling="yes"))
    def bad_felling(self):
        self.declare(Symptom(DEP_initial_bad_felling="yes"))

    @Rule(AND(Symptom(depressed="yes"), Symptom(DEP_initial_bad_felling="yes")))
    def bad_felling2(self):
        self.declare(Symptom(DEP_bad_felling="yes"))

    # LOSS OF INTEREST
    @Rule(Symptom(initiative="yes"))
    def loss_interest1(self):
        self.declare(Symptom(DEP_initial_loss_interest="yes"))

    @Rule(AND(Symptom(illusion="yes"), Symptom(DEP_initial_loss_interest="yes")))
    def loss_interest2(self):
        self.declare(Symptom(DEP_mid_loss_interest="yes"))

    @Rule(AND(Symptom(nothing_enthusiastic="yes"), Symptom(DEP_mid_loss_interest="yes")))
    def loss_interest3(self):
        self.declare(Symptom(DEP_loss_interest="yes"))

    # SUICIDAL THOUGHTS
    @Rule(Symptom(worth_little="yes"))
    def suicidal_thoughts(self):
        self.declare(Symptom(DEP_initial_suicidal_thought="yes"))

    @Rule(AND(Symptom(no_sense="yes"), Symptom(DEP_initial_suicidal_thought="yes")))
    def suicidal_thoughts2(self):
        self.declare(Symptom(DEP_suicidal_thought="yes"))

    # --------------------------------- ANXIETY ------------------------------------
    # DECONTROL BODY
    @Rule(OR(Symptom(dry_mouth="yes")))
    def decontrol_body(self):
        self.declare(Symptom(ANX_initial_decontrol_body="yes"))

    @Rule(AND(Symptom(difficulty_breathing="yes")), Symptom(ANX_initial_decontrol_body="yes"))
    def decontrol_body2(self):
        self.declare(Symptom(ANX_mid_decontrol_body="yes"))

    @Rule(AND(Symptom(hands_trembled="yes"), Symptom(ANX_mid_decontrol_body="yes")))
    def decontrol_body3(self):
        self.declare(Symptom(ANX_decontrol_body="yes"))

    # PANIC PROBLEMS
    @Rule(OR(Symptom(panic_ridicule="yes")))
    def panic_problems(self):
        self.declare(Symptom(ANX_initial_panic_problems="yes"))

    @Rule(AND(Symptom(panic="yes")), Symptom(ANX_initial_panic_problems="yes"))
    def panic_problems(self):
        self.declare(Symptom(ANX_panic_problems="yes"))
    
    # BODY TENSION
    @Rule(OR(Symptom(heartbeat_physicalexertion="yes")))
    def body_tension(self):
        self.declare(Symptom(ANX_body_tension="yes"))

    # FEAR WITHOUT REASON
    @Rule(OR(Symptom(fear_no_reason="yes")))
    def fear_no_reason(self):
        self.declare(Symptom(ANX_fear_no_reason="yes"))

    # ISOLATION COMPLEX
    @Rule(AND(Symptom(panic_problems="yes")), Symptom(ANX_fear_no_reason="yes"))
    def isolation_complex(self):
        self.declare(Symptom(ANX_isolation_complex="yes"))

    # ------------------------------- STRESS --------------------------------
    # RELAXATION PROBLEMS
    @Rule(OR(Symptom(unloading_tension="yes")))
    def relaxation_problem(self):
        self.declare(Symptom(STRS_mid_relaxation_problems="yes"))

    @Rule(AND(Symptom(difficult_relax="yes")), Symptom(STRS_mid_relaxation_problems="yes"))
    def relaxation_problem2(self):
        self.declare(Symptom(STRS_relaxation_problems="yes"))

    # ANGER MISMANAGEMENT
    @Rule(OR(Symptom(exaggerated_reaction="yes")))
    def anger_mismanagement(self):
        self.declare(Symptom(STRS_initial_anger_mismanagement="yes"))

    @Rule(AND(Symptom(no_tolerate_continue="yes")), Symptom(STRS_initial_anger_mismanagement="yes"))
    def anger_mismanagement2(self):
        self.declare(Symptom(STRS_mid_anger_mismanagement="yes"))

    @Rule(AND(Symptom(easily_angered="yes")), Symptom(STRS_mid_anger_mismanagement="yes"))
    def anger_mismanagement3(self):
        self.declare(Symptom(STRS_anger_mismanagement="yes"))

    # ENERGY DECONTROL
    @Rule(OR(Symptom(expending_great_energy="yes")))
    def decontrol_energy(self):
        self.declare(Symptom(STRS_decontrol_energy="yes"))

    # IMPERACTIVITY
    @Rule(AND(Symptom(restlessness="yes")), Symptom(STRS_decontrol_energy="yes"))
    def imperactivity(self):
        self.declare(Symptom(STRS_imperactivity="yes"))
        
class MentalHealthNetwork:
    def __init__(self, condition_name, thresholds):
        self.condition_name = condition_name
        self.thresholds = thresholds
        self.questions = [f'Q{i}' for i in range(1, 8)]
        self.model = self._create_network()
    
    def _create_network(self):
        model = BayesianNetwork()
        model.add_nodes_from(self.questions + [self.condition_name])
        for question in self.questions:
            model.add_edge(question, self.condition_name)
        
        for question in self.questions:
            cpd_question = TabularCPD(variable=question, variable_card=2, values=[[0.5], [0.5]])
            model.add_cpds(cpd_question)
        
        num_combinations = 2 ** len(self.questions)
        values = np.zeros((4, num_combinations))

        for i, combination in enumerate(itertools.product([0, 1], repeat=len(self.questions))):
            num_yes = sum(combination)
            yes_ratio = num_yes / len(self.questions)
            if yes_ratio < self.thresholds[0]:
                values[0][i] = 1  # leve
            elif yes_ratio < self.thresholds[1]:
                values[1][i] = 1  # moderada
            elif yes_ratio < self.thresholds[2]:
                values[2][i] = 1  # severa
            else:
                values[3][i] = 1  # muy severa
        
        cpd_condition = TabularCPD(variable=self.condition_name, variable_card=4, values=values, evidence=self.questions, evidence_card=[2]*7)
        model.add_cpds(cpd_condition)
        assert model.check_model()
        return model

    def infer_condition_level(self, facts):
        inference = VariableElimination(self.model)
        evidence = {f'Q{i+1}': facts[i] for i in range(7)}
        result = inference.map_query([self.condition_name], evidence=evidence)
        return result[self.condition_name]

class DepressionNetwork(MentalHealthNetwork):
    def __init__(self):
        thresholds = [0.428, 0.71, 0.85, 1]
        super().__init__('Depression', thresholds)

class AnxietyNetwork(MentalHealthNetwork):
    def __init__(self):
        thresholds = [0.285, 0.428, 0.57, 1]
        super().__init__('Anxiety', thresholds)

class StressNetwork(MentalHealthNetwork):
    def __init__(self):
        thresholds = [0.428, 0.57, 0.71, 1]
        super().__init__('Stress', thresholds)
        
def toNumber(number):
    if number == 0:
        return "Leve"
    elif number == 1:
        return "Moderada"
    elif number == 2:
        return "Severa"
    elif number == 3:
        return "Muy severa"

def convert_responses_to_binary(responses):
    return [1 if response.lower() == "yes" else 0 for response in responses]


def bn(expert_system):

    depression_network = DepressionNetwork()
    anxiety_network = AnxietyNetwork()
    stress_network = StressNetwork()

    generated_facts = expert_system.facts

    de=[]
    an=[]
    st=[]

    for _ in range(len(generated_facts)):
        s = generated_facts.popitem()
        a = list(s[1].keys())
        if "STRS" in  a[0]:
            st.append(a[0])
        elif "DEP" in  a[0]:
            de.append(a[0])
        elif "ANX" in  a[0]:
            an.append(a[0])

    estres = [
        "STRS_mid_relaxation_problems",
        "STRS_relaxation_problems",
        "STRS_initial_anger_mismanagement",
        "STRS_mid_anger_mismanagement",
        "STRS_anger_mismanagement",
        "STRS_decontrol_energy",
        "STRS_imperactivity"
    ]

    depresion = [
        "DEP_initial_bad_felling",
        "DEP_bad_felling",
        "DEP_initial_loss_interest",
        "DEP_mid_loss_interest",
        "DEP_loss_interest",
        "DEP_initial_suicidal_thought",
        "DEP_suicidal_thought"
    ]

    ansiedad = [
        "ANX_initial_decontrol_body",
        "ANX_mid_decontrol_body",
        "ANX_decontrol_body",
        "ANX_initial_panic_problems",
        "ANX_panic_problems",
        "ANX_body_tension",
        "ANX_fear_no_reason",
        "ANX_isolation_complex"
    ]
    
    depression_facts = []

    for f in depresion:
        if f in de:
            depression_facts.append(1)
        else:
            depression_facts.append(0)
    
    anxiety_facts = []
    
    for f in ansiedad:
        if f in an:
            anxiety_facts.append(1)
        else:
            anxiety_facts.append(0)

    stress_facts = []

    for f in estres:
        if f in st:
            stress_facts.append(1)
        else:
            stress_facts.append(0)
    ans=[]
    ans.append(toNumber(depression_network.infer_condition_level(depression_facts)))
    ans.append(toNumber(anxiety_network.infer_condition_level(anxiety_facts)))
    ans.append(toNumber(stress_network.infer_condition_level(stress_facts)))

    return ans

# MAIN
def main():
    expert_system = SymptomsExpert()
    depression_network = DepressionNetwork()
    anxiety_network = AnxietyNetwork()
    stress_network = StressNetwork()

    print("Welcome to the Diagnostic Expert System!")
    while True:
        id = input("Id of the patient: ").lower()

        # ---------------------------- DEPRESSION -------------------------------
        """positive_feeling = input("¿No podía sentir ningún sentimiento positivo?\n").lower()   #1
        initiative = input("¿Se me hizo difícil tomar la iniciativa para hacer cosas?\n").lower()    #2
        illusion = input("¿He sentido que no había nada que me ilusionara?\n").lower()    #2
        depressed = input("¿Me sentí triste y deprimido'\n").lower()   #1
        nothing_enthusiastic = input("¿No me pude entusiasmar por nada?\n").lower()     #2
        worth_little = input("¿Sentí que valía muy poco como persona?\n").lower()    #3
        no_sense = input("¿Sentí que la vida no tenía ningún sentido?\n").lower()   #3

        # -------------------------------- ANXIETY -------------------------------------
        dry_mouth = input("¿Me di cuenta que tenía la boca seca?\n").lower()    #1
        difficulty_breathing = input("¿Se me hizo difícil respirar?\n").lower()    #1
        hands_trembled = input("¿Sentí que mis manos temblaban?\n").lower()    #1
        panic_ridicule = input("¿Estaba preocupado por situaciones en las cuales podía tener pánico o en las que podría hacer el ridículo?\n").lower()  #2
        panic = input("¿Sentí que estaba a punto del pánico?\n").lower()    #2
        heartbeat_physicalexertion = input("¿Sentí los latidos de mi corazón a pesar de no haber hecho ningún esfuerzo físico?\n").lower()  #3
        fear_no_reason = input("¿Tuve miedo sin razón?\n").lower()  #4

        # ----------------------------------- STRESS ---------------------------------
        unloading_tension = input("¿Me ha costado mucho descargar la tensión?\n").lower()   #1
        exaggerated_reaction = input("¿Reaccioné exageradamente en ciertas situaciones?\n").lower()     #2
        expending_great_energy = input("¿He sentido que estaba gastando una gran cantidad de energía?\n").lower()   #3
        restlessness = input("¿Me he sentido inquieto?\n").lower()  #3
        difficult_relax = input("¿Se me hizo difícil relajarme?\n").lower()     #1
        no_tolerate_continue = input("¿No toleré nada que no me permitiera continuar con lo que estaba haciendo?\n").lower()    #2
        easily_angered = input("¿He tendido a sentirme enfadado con facilidad?\n").lower()  #2
        """


        positive_feeling = "yes"   #1
        initiative = "no"     #2
        illusion = "yes"    #2
        depressed = "no"   #1
        nothing_enthusiastic = "yes"     #2
        worth_little = "yes"    #3
        no_sense = "no"    #3

        # -------------------------------- ANXIETY -------------------------------------
        dry_mouth = "yes"    #1
        difficulty_breathing = "no"    #1
        hands_trembled = "no"     #1
        panic_ridicule = "yes"  #2
        panic = "yes"    #2
        heartbeat_physicalexertion = "no"   #3
        fear_no_reason = "yes"  #4

        # ----------------------------------- STRESS ---------------------------------
        unloading_tension = "yes"#1
        exaggerated_reaction = "yes"     #2
        expending_great_energy = "yes"   #3
        restlessness = "no"   #3
        difficult_relax = "no"      #1
        no_tolerate_continue = "no"    #2
        easily_angered = "yes"  #2


        expert_system.reset()
        expert_system.declare(Symptom(positive_feeling=positive_feeling, initiative=initiative, depressed=depressed, illusion=illusion,
                        nothing_enthusiastic=nothing_enthusiastic, worth_little=worth_little, no_sense=no_sense, dry_mouth=dry_mouth, difficulty_breathing=difficulty_breathing,
                        hands_trembled=hands_trembled, panic_ridicule=panic_ridicule, panic=panic, heartbeat_physicalexertion=heartbeat_physicalexertion, fear_no_reason=fear_no_reason,
                        unloading_tension=unloading_tension, exaggerated_reaction=exaggerated_reaction, expending_great_energy=expending_great_energy, restlessness=restlessness,
                        difficult_relax=difficult_relax, no_tolerate_continue=no_tolerate_continue, easily_angered=easily_angered))
        
        expert_system.run()

        a = bn(expert_system)
        for i in a:
            print(i)
        """""
        generated_facts = expert_system.facts

        de=[]
        an=[]
        st=[]

        for _ in range(len(generated_facts)):
            s = generated_facts.popitem()
            a = list(s[1].keys())
            if "STRS" in  a[0]:
                st.append(a[0])
            elif "DEP" in  a[0]:
                de.append(a[0])
            elif "ANX" in  a[0]:
                an.append(a[0])

        estres = [
            "STRS_mid_relaxation_problems",
            "STRS_relaxation_problems",
            "STRS_initial_anger_mismanagement",
            "STRS_mid_anger_mismanagement",
            "STRS_anger_mismanagement",
            "STRS_decontrol_energy",
            "STRS_imperactivity"
        ]

        depresion = [
            "DEP_initial_bad_felling",
            "DEP_bad_felling",
            "DEP_initial_loss_interest",
            "DEP_mid_loss_interest",
            "DEP_loss_interest",
            "DEP_initial_suicidal_thought",
            "DEP_suicidal_thought"
        ]

        ansiedad = [
            "ANX_initial_decontrol_body",
            "ANX_mid_decontrol_body",
            "ANX_decontrol_body",
            "ANX_initial_panic_problems",
            "ANX_panic_problems",
            "ANX_body_tension",
            "ANX_fear_no_reason",
            "ANX_isolation_complex"
        ]
        
        depression_facts = []

        for f in depresion:
            if f in de:
                depression_facts.append(1)
            else:
                depression_facts.append(0)
        
        anxiety_facts = []
        
        for f in ansiedad:
            if f in an:
                anxiety_facts.append(1)
            else:
                anxiety_facts.append(0)

        stress_facts = []

        for f in estres:
            if f in st:
                stress_facts.append(1)
            else:
                stress_facts.append(0)

        depression_level = depression_network.infer_condition_level(depression_facts)
        anxiety_level = anxiety_network.infer_condition_level(anxiety_facts)
        stress_level = stress_network.infer_condition_level(stress_facts)

        print(f"Depression Level: {toNumber(depression_level)}")
        print(f"Anxiety Level: {toNumber(anxiety_level)}")
        print(f"Stress Level: {toNumber(stress_level)}")
        """
        cont = input("Continue? (yes or no): ").lower()
        if cont == "no":
            break

if __name__ == "__main__":
    main()