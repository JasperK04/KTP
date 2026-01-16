# Knowledge Acquisition Report

## Introduction
This report describes the knowledge acquisition process carried out as part of the Knowledge Technology Practical (KTP). The aim of the project is to capture expert knowledge in the domain of fastening and bonding solutions and to formalize this knowledge in a structured form that can be used by a rule-based system. The focus of this report is strictly descriptive: it outlines what knowledge was acquired, how the acquisition was organized, and how the expert’s practical reasoning was translated into explicit knowledge structures.  

The acquisition process was divided into three expert sessions. Each session built upon the results of the previous one, moving from broad domain exploration to detailed formalization and refinement. Because detailed meeting notes are not available for all sessions, this report reconstructs a coherent and realistic account based on the produced artifacts and the context of the assignment.

## The Expert
The expert consulted for this project is Klaas Kleine, one of the two co-owners of Hubo Noordhorn, a local hardware store specializing in construction materials, tools, and installation components. He has been working at this store since 2004 and is currently 56 years old. Over the course of more than twenty years, he has developed extensive practical knowledge about fastening and bonding solutions through daily interactions with customers.  

His expertise is characterized by a strong focus on applicability and problem-solving. Rather than reasoning in abstract or theoretical terms, he evaluates situations based on material combinations, load conditions, environmental exposure, and the practical constraints of do-it-yourself and professional construction tasks. This makes his knowledge particularly suitable for knowledge-based systems.  

In this project, his role was to act as the primary source of domain knowledge. The student team translated his explanations, examples, and corrections into structured representations, while repeatedly checking whether the formalized knowledge remained faithful to his original reasoning.

## Session 1: General Knowledge and Domain Exploration
The first knowledge acquisition session focused on establishing a shared understanding of the domain. This session was conducted in a conversational, question-and-answer style. The goal was not yet to formalize knowledge, but to explore how the expert conceptually organizes fastening and bonding solutions.  

During this session, fasteners were first discussed at the level of broad categories, such as adhesives, mechanical fasteners, and thermal joining methods. For each category, the expert explained typical characteristics and limitations. Important dimensions included mechanical strength (tensile, shear, and compressive), resistance to moisture and weather, rigidity versus flexibility, permanence of the connection, and sensitivity to vibration or temperature changes.  

In parallel, a comprehensive list of approximately seventy fastening and bonding types was compiled. This list included various adhesives (e.g. wood glue, epoxies, sealants), mechanical fasteners (e.g. screws, bolts, nails, brackets), and alternative joining techniques (e.g. welding and soldering). The purpose of this list was not to be exhaustive in a technical sense, but to represent the range of solutions that customers typically encounter in a hardware store context.  

A key outcome of this session was the identification of the questions the expert implicitly asks when advising customers. These questions concerned, among others, the materials to be joined, the required mechanical strength, exposure to moisture or outdoor conditions, desired permanence, and acceptable curing time. These insights directly informed the initial design of the user-facing question set used by the system.

## Session 2: Selection and Structuring of Fasteners
The second session marked the transition from exploratory knowledge acquisition to formal knowledge structuring. This session was conducted through a combination of targeted question-and-answer interactions and interactive editing of the knowledge base.  

In this session, the broad list of fastening methods from the first meeting was reduced to a selection of 54 representative fasteners and bonding solutions. The selection was guided by relevance and frequency of use in practice. For each selected fastener, the expert helped determine which properties were essential to describe its behavior and suitability.  

These properties were then explicitly defined and filled in. They included compatible materials, different forms of mechanical strength, resistance levels (water, weather, chemical, temperature), rigidity, permanence, required tools, surface preparation, and curing time where applicable. Qualitative expert judgments were translated into standardized values, enabling consistent comparison between fasteners.  

At the same time, the initial set of questions was refined to ensure that each question corresponded to a decision factor the expert actually uses in practice. The knowledge base was actively edited during the session, allowing immediate clarification when a property definition or value did not adequately capture the expert’s intent. This interactive process helped prevent misunderstandings and ensured that the formal representation remained grounded in real-world reasoning.

## Session 3: Walkthrough and Refinement
The third session focused on validation and refinement of the existing knowledge base. This session took the form of walkthroughs of the current system behavior, followed by interactive editing.  

The expert reviewed the structured fastener descriptions and the implications of the encoded rules. Particular attention was paid to edge cases and practical nuances, such as how vibration resistance should influence recommendations or how curing time constraints affect usability in real situations. Small mistakes and inconsistencies were identified, including property values that were too strict or too lenient, and cases where the interaction between rules did not fully align with the expert’s expectations.  

Corrections were made directly to the knowledge base during the session. This iterative refinement ensured internal consistency and improved the alignment between the system’s conclusions and the expert’s intuitive judgments. While no entirely new knowledge categories were introduced, this session significantly improved the quality and reliability of the captured knowledge.

## Session 4: Expert review

#### the prosess
The last session focusses on reviewing the system from the perspective of the experts reasoning. The aim will be to assess whether the system not only produces reasonable outcomes, but does so for the same reasons as the expert.  

The session begins with the presentation of realistic use cases, similar to those encountered in a hardware store. For each case, the expert performs a walktrough of the system. Then the Expert explains if the suggestions are correct, if the asked questions ware similar to the questions he would have asked, and then finally explain why or why not the model matches his reasoning.  

Any mismatches will be discussed in detail, with attention to whether they stem from missing knowledge, incorrect rule priorities, or oversimplified property definitions. Based on these discussions, targeted refinements will be made to the knowledge base. The session will conclude with an assessment of whether the system’s reasoning process can be considered a faithful operationalization of the expert’s decision-making approach.

#### the Usecases
Scenario 1
“I want to seal a gap around a window so no air comes through.”
Answered Questions
 	Question	Your Answer
1	What is the first surface it is intended for?	Glass
2	What is the second surface it is intended for?	Wood
3	Does the connection need to be permanent or removable?	Semi permanent
4	Will the connection be exposed to weather or moisture?	Outdoor
5	What load will the connection experience?	Light dynamic
6	What type of mechanical strength is required?	Very low
7	Is flexibility required in the cured state?	False
8	What is the acceptable curing/drying time?	Days

Possible Fasteners
Silicone sealant (adhesive)
Flooring adhesive (adhesive)

Expert suggests: Silicone Sealant

Scenario 2
“I want to fix a loose wooden chair leg so it becomes stable again.”
Answered Questions
	Question	Your Answer
1	What is the first surface it is intended for?	Wood
2	What is the second surface it is intended for?	Wood
3	Does the connection need to be permanent or removable?	Semi permanent
4	Will the connection be exposed to weather or moisture?	No
5	What load will the connection experience?	Light dynamic
6	What type of mechanical strength is required?	Moderate
7	Is flexibility required in the cured state?	Skipped
8	What is the acceptable curing/drying time?	Immediate

Possible Fasteners
Hex bolt (mechanical)
Wood screw (mechanical)
Dowel pin (mechanical)
Carriage bolt (mechanical)
Lag bolt (mechanical)
Drywall screw (mechanical)
Deck screw (mechanical)
Angle bracket (mechanical)
Flat bracket (mechanical)
Corner brace (mechanical)

Expert suggests: 
Depending on the structure of the chair: 
Wood Screws, Dowel Pins with Wood glue or Nails

Scenario 3
“I have a plastic bucket i use outside that is cracked and now leaking, and I want to fix it.”
Answered Questions
	Question	Your Answer
1	What is the first surface it is intended for?	Plastic
2	What is the second surface it is intended for?	Plastic
3	Does the connection need to be permanent or removable?	Permanent
4	What load will the connection experience?	Light dynamic
5	Will the connection be exposed to weather or moisture?	Outdoor
6	What type of mechanical strength is required?	Moderate
7	Is flexibility required in the cured state?	False
8	What is the acceptable curing/drying time?	Hours

Possible Fasteners
Polyurethane glue (adhesive)
Construction adhesive (adhesive)
High-temperature adhesive (adhesive)
Rivet (mechanical)
Plastic welding (thermal)

Expert suggests: Polyurethane glue or Plastic welding if the cracks permits it

#### The expert review

In this final session, the system was evaluated by comparing its behavior to how I reason when advising customers in a hardware store. A key difference between expert reasoning and the system’s behavior is that, in practice, I rarely ask all the questions the system poses. Many properties are inferred immediately from the context of the customer’s request. The system, however, must make these assumptions explicit, which results in longer questioning and a broader solution space.

In the first scenario, sealing a gap around a window, I would immediately recommend silicone sealant without asking further questions. From experience, such a task implicitly involves outdoor exposure, minimal mechanical load, the need for flexibility, and a semi-permanent connection. The system asked additional questions about load, strength, moisture exposure, and curing time to arrive at these same conclusions. While this reconstructs my mental reasoning steps, it also led to the inclusion of flooring adhesive as a possible option. In practice, I would rule this out immediately based on contextual understanding alone. The system lacks the knowledge to exclude such alternatives early, as it does not fully capture the implicit link between “window sealing” and movement accommodation.

In the second scenario, fixing a loose wooden chair leg, I would again infer several constraints without explicitly questioning them. Indoor use and wood-to-wood contact are clear from the description, and my focus would be on reinforcing the joint mechanically. The system correctly restricted itself to mechanical fasteners, but it produced a relatively large set of options. Some of these, such as large bolts or brackets, would likely be impractical for a typical chair and would normally be dismissed immediately by an expert. Their inclusion shows that the system reasons conservatively and lacks fine-grained contextual knowledge about furniture construction.

In the third scenario, repairing a cracked plastic bucket used outdoors, the system performed more convincingly. I would quickly narrow the options to adhesives or plastic welding, depending on the crack. The system followed a similar path, but still retained options such as rivets, which I would generally avoid due to leakage risk and material deformation. This again highlights that the system does not always distinguish between technically possible and practically advisable solutions.

Overall, the system succeeds in explicitly reconstructing expert reasoning, but it does not yet replicate expert intuition. Its main limitation lies in the absence of contextual knowledge that allows experts to rule out certain solutions immediately. As a result, the system sometimes overgenerates suggestions that are technically valid but unlikely to be recommended in practice.


## Conclusion
The knowledge acquisition process described in this report followed a structured and incremental approach. Starting from broad domain exploration, the project gradually moved toward detailed formalization and validation of expert knowledge. Through conversational elicitation, interactive editing, and iterative walkthroughs, practical expertise was transformed into a structured knowledge base suitable for rule-based reasoning.  

By maintaining close alignment with the expert throughout all sessions, the project ensured that the resulting system reflects practical, experience-based reasoning rather than abstract or purely theoretical models. This forms a solid foundation for subsequent system evaluation and refinement.

## important Note:
This report was written after the first progress meeting, this means that there has passed some time between writing this report and the actual expert meetings, as a result not all details may have been remembered and added to this document