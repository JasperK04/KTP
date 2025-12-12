class InferenceEngine:
    """Forward-chaining inference engine for fastener selection"""
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.facts: Dict[str, Any] = {}
        self.conclusions: Dict[str, Any] = {}
    
    def add_fact(self, question_id: str, value: Any):
        """Add a fact from user answer"""
        self.facts[question_id] = value
    
    def reset(self):
        """Clear all facts and conclusions"""
        self.facts.clear()
        self.conclusions.clear()
    
    def evaluate_rule(self, rule: Rule) -> bool:
        """Check if a rule's conditions are satisfied"""
        for question_id, expected in rule.conditions.items():
            if question_id not in self.facts:
                return False
            
            actual = self.facts[question_id]
            
            # Handle list of acceptable values
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        
        return True
    
    def apply_rule(self, rule: Rule):
        """Apply a rule's conclusions"""
        for key, value in rule.conclusion.items():
            if key not in self.conclusions:
                self.conclusions[key] = []
            
            if isinstance(value, list):
                self.conclusions[key].extend(value)
            else:
                self.conclusions[key].append(value)
    
    def infer(self):
        """Run forward-chaining inference"""
        # Sort rules by priority
        sorted_rules = sorted(self.kb.rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if self.evaluate_rule(rule):
                self.apply_rule(rule)
    
    def score_fastener(self, fastener: Fastener) -> float:
        """Score a fastener based on facts and inferred conclusions"""
        score = 0.0
        max_score = 0.0
        
        # Check material compatibility
        if "q1" in self.facts:
            max_score += 10
            material = self.facts["q1"]
            if material in fastener.properties.compatible_materials or self.facts["q1"] == "multiple":
                score += 10
        
        # Check strength requirements
        if "q2" in self.facts:
            max_score += 8
            required = self.facts["q2"]
            strength_order = ["none", "very_low", "low", "moderate", "high", "very_high"]
            req_idx = strength_order.index(required)
            fastener_idx = strength_order.index(fastener.properties.tensile_strength.value)
            if fastener_idx >= req_idx:
                score += 8
        
        # Check water/weather resistance
        if "q3" in self.facts:
            max_score += 7
            exposure = self.facts["q3"]
            resistance_order = ["poor", "fair", "good", "excellent"]
            
            if exposure == "submerged":
                req_idx = 3  # excellent
            elif exposure == "outdoor":
                req_idx = 2  # good
            elif exposure == "splash":
                req_idx = 1  # fair
            else:
                req_idx = 0  # poor is acceptable
            
            water_idx = resistance_order.index(fastener.properties.water_resistance.value)
            if water_idx >= req_idx:
                score += 7
        
        # Check permanence
        if "q4" in self.facts:
            max_score += 6
            required = self.facts["q4"]
            if required == fastener.properties.permanence.value:
                score += 6
            elif required == "semi_permanent" and fastener.properties.permanence.value in ["removable", "permanent"]:
                score += 3
        
        # Check flexibility
        if "q8" in self.facts:
            max_score += 5
            needs_flexibility = self.facts["q8"]
            is_flexible = fastener.properties.rigidity in [Rigidity.FLEXIBLE, Rigidity.SEMI_FLEXIBLE]
            if needs_flexibility == is_flexible:
                score += 5
        
        # Check vibration resistance
        if "q6" in self.facts:
            max_score += 4
            load_type = self.facts["q6"]
            if load_type in ["heavy_dynamic", "vibration"]:
                resistance_order = ["poor", "fair", "good", "excellent"]
                vib_idx = resistance_order.index(fastener.properties.vibration_resistance.value)
                if vib_idx >= 2:  # good or excellent
                    score += 4
        
        # Normalize score
        return score / max_score if max_score > 0 else 0.0
    
    def recommend_fasteners(self, top_n: int = 5) -> List[tuple[Fastener, float]]:
        """Get ranked list of recommended fasteners"""
        self.infer()
        
        scored_fasteners = []
        for fastener in self.kb.fasteners:
            score = self.score_fastener(fastener)
            scored_fasteners.append((fastener, score))
        
        # Sort by score descending
        scored_fasteners.sort(key=lambda x: x[1], reverse=True)
        
        return scored_fasteners[:top_n]


# Example usage
if __name__ == "__main__":
    # Load knowledge base from JSON file
    kb = KnowledgeBase()
    kb.load_from_file("fastener_kb.json")
    
    # Create inference engine
    engine = InferenceEngine(kb)
    
    # Simulate user answers
    engine.add_fact("q1", "wood")
    engine.add_fact("q2", "moderate")
    engine.add_fact("q3", "no")
    engine.add_fact("q4", "semi_permanent")
    engine.add_fact("q8", False)
    
    # Get recommendations
    recommendations = engine.recommend_fasteners(top_n=3)
    
    print("Top 3 Recommended Fasteners:")
    print("-" * 50)
    for fastener, score in recommendations:
        print(f"\n{fastener.name} (Score: {score:.2%})")
        print(f"  Category: {fastener.category}")
        print(f"  Materials: {', '.join(fastener.properties.compatible_materials)}")
        print(f"  Strength: {fastener.properties.tensile_strength.value}")
        print(f"  Permanence: {fastener.properties.permanence.value}")