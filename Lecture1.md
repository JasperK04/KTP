# introduction

## problem solving model
the stages in which you solve the problem

## Domain models
the classes and objects that reason about and how they relate to eachother

## Rule models
a model that has all the rules


## example chaining:
`IF rpm >= 1000, THEN alarm = True`

`IF alarm, THEN action = "check machine"` -> user input required -> leaking

`IF alarm, leaking, THEN problem = "broken seal"`

`IF leaking, THEN recolution = "replace seal"`

can be forward chaining like the above example to find the issue
or
can be backward chaining to prove a goal you set is true

# System project
- find an expert
- build a system
- validate system with expert
- written report
- presentation


## system requirements
- declarative knowledge
- knowledge base modular
- inference
- knowledge from an expert
- specificity (one clear task)
- complexity (min 100 elements)

## technical requirements
- User interface
- git repo link
- <span>main.py</span>
- <span>readme.md</span>
- requirements.txt

## report requirements
- problem
- expert
- role of knowledge technology
- the knowledge model
- inference type used
- user interface
- walktrough
- explanation of use of generative AI
- Task division
- Reflection

## grading key
- 50% system and 50% report
- first draft pass/fail
- presentation pass/fail
- 0.5 x System grade + 0.5 x Report grade >= 5.5