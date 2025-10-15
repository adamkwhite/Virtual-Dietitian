# Agent Builder Examples
Few-shot prompt examples for Vertex AI Agent Builder

## How to Use These Examples

1. Go to Agent Builder UI → Your Agent → **Examples** section
2. Click **"Add Example"**
3. Copy the conversation flow (User Input → Tool Call → Agent Response)
4. Paste into the example editor
5. Repeat for each example below

---

## English Examples

### Example 1: Balanced Breakfast

**User Input:**
```
I had oatmeal with blueberries and almond butter for breakfast
```

**Tool Call:** `nutrition-analyzer`
```json
{
  "meal_description": "I had oatmeal with blueberries and almond butter for breakfast"
}
```

**Tool Response:**
```json
{
  "total_nutrition": {
    "calories": 332,
    "protein_g": 11,
    "carbs_g": 48,
    "fat_g": 11,
    "fiber_g": 9,
    "sodium_mg": 156
  },
  "macro_percentages": {
    "protein_pct": 11,
    "carbs_pct": 58,
    "fat_pct": 31
  },
  "insights": [
    {
      "type": "positive",
      "message": "Great source of Vitamin C from fruit"
    },
    {
      "type": "positive",
      "message": "Excellent fiber content from whole grains"
    },
    {
      "type": "recommendation",
      "message": "Protein is a bit low (11%). Consider adding Greek yogurt or an egg to reach 15-30%"
    }
  ],
  "follow_up": "What are you planning for lunch?"
}
```

**Agent Response:**
```
Great breakfast choice! Here's your nutritional breakdown:

📊 **Nutritional Summary:**
- Calories: 332
- Protein: 11g (11%)
- Carbs: 48g (58%)
- Fat: 11g (31%)
- Fiber: 9g
- Sodium: 156mg

✅ **Insights:**
- Great source of Vitamin C from fruit
- Excellent fiber content from whole grains
- Protein is a bit low (11%). Consider adding Greek yogurt or an egg to reach 15-30%

What are you planning for lunch?
```

---

### Example 2: Fruit Snack (Low Protein)

**User Input:**
```
I just had an apple and banana
```

**Tool Call:** `nutrition-analyzer`
```json
{
  "meal_description": "I just had an apple and banana"
}
```

**Tool Response:**
```json
{
  "total_nutrition": {
    "calories": 157,
    "protein_g": 2,
    "carbs_g": 41,
    "fat_g": 0,
    "fiber_g": 6,
    "sodium_mg": 2
  },
  "macro_percentages": {
    "protein_pct": 4,
    "carbs_pct": 94,
    "fat_pct": 2
  },
  "insights": [
    {
      "type": "positive",
      "message": "Great source of Vitamin C from fruit"
    },
    {
      "type": "recommendation",
      "message": "Very low protein (4%). Add nuts, cheese, or yogurt for better satiety"
    }
  ],
  "follow_up": "This is a light snack. Are you planning a meal soon?"
}
```

**Agent Response:**
```
Healthy snack! Here's the breakdown:

📊 **Nutritional Summary:**
- Calories: 157
- Protein: 2g (4%)
- Carbs: 41g (94%)
- Fat: 0g (2%)
- Fiber: 6g
- Sodium: 2mg

✅ **Insights:**
- Great source of Vitamin C from fruit
- Very low protein (4%). Add nuts, cheese, or yogurt for better satiety

This is a light snack. Are you planning a meal soon?
```

---

### Example 3: Protein-Rich Lunch

**User Input:**
```
I had grilled chicken, quinoa, and broccoli for lunch
```

**Tool Call:** `nutrition-analyzer`
```json
{
  "meal_description": "I had grilled chicken, quinoa, and broccoli for lunch"
}
```

**Tool Response:**
```json
{
  "total_nutrition": {
    "calories": 491,
    "protein_g": 42,
    "carbs_g": 47,
    "fat_g": 12,
    "fiber_g": 9,
    "sodium_mg": 133
  },
  "macro_percentages": {
    "protein_pct": 33,
    "carbs_pct": 37,
    "fat_pct": 30
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excellent protein content for muscle health"
    },
    {
      "type": "positive",
      "message": "Great source of Vitamin C from vegetables"
    },
    {
      "type": "positive",
      "message": "Well-balanced macros - great job!"
    }
  ],
  "follow_up": "How do you feel after this meal?"
}
```

**Agent Response:**
```
Excellent meal choice! Very well balanced. Here's your breakdown:

📊 **Nutritional Summary:**
- Calories: 491
- Protein: 42g (33%)
- Carbs: 47g (37%)
- Fat: 12g (30%)
- Fiber: 9g
- Sodium: 133mg

✅ **Insights:**
- Excellent protein content for muscle health
- Great source of Vitamin C from vegetables
- Well-balanced macros - great job!

How do you feel after this meal?
```

---

### Example 4: Unknown Food Handling

**User Input:**
```
I had dragon fruit smoothie bowl
```

**Tool Call:** `nutrition-analyzer`
```json
{
  "meal_description": "I had dragon fruit smoothie bowl"
}
```

**Tool Response:**
```json
{
  "total_nutrition": {
    "calories": 0,
    "protein_g": 0,
    "carbs_g": 0,
    "fat_g": 0,
    "fiber_g": 0,
    "sodium_mg": 0
  },
  "macro_percentages": {
    "protein_pct": 0,
    "carbs_pct": 0,
    "fat_pct": 0
  },
  "unknown_foods": ["dragon fruit smoothie bowl"],
  "insights": [],
  "follow_up": "Could you describe what ingredients were in it?"
}
```

**Agent Response:**
```
I don't have nutritional data for "dragon fruit smoothie bowl" in my database yet. Could you tell me what ingredients were in it? For example:

- What fruits were included?
- Was there yogurt or milk?
- Any toppings like granola, nuts, or seeds?

This will help me give you an accurate nutritional breakdown!
```

---

### Example 5: Quantity Specification

**User Input:**
```
I had half a banana and two eggs
```

**Tool Call:** `nutrition-analyzer`
```json
{
  "meal_description": "I had half a banana and two eggs"
}
```

**Tool Response:**
```json
{
  "total_nutrition": {
    "calories": 195,
    "protein_g": 13,
    "carbs_g": 14,
    "fat_g": 10,
    "fiber_g": 2,
    "sodium_mg": 142
  },
  "macro_percentages": {
    "protein_pct": 26,
    "carbs_pct": 28,
    "fat_pct": 46
  },
  "insights": [
    {
      "type": "positive",
      "message": "Good protein content for muscle health"
    }
  ],
  "follow_up": "Nice light breakfast! What's your plan for lunch?"
}
```

**Agent Response:**
```
Nice light breakfast! Here's your nutritional breakdown:

📊 **Nutritional Summary:**
- Calories: 195
- Protein: 13g (26%)
- Carbs: 14g (28%)
- Fat: 10g (46%)
- Fiber: 2g
- Sodium: 142mg

✅ **Insights:**
- Good protein content for muscle health

Nice light breakfast! What's your plan for lunch?
```

---

## French Examples

### Exemple 1: Petit-déjeuner équilibré

**Entrée utilisateur:**
```
J'ai mangé des flocons d'avoine avec des myrtilles et du beurre d'amande pour le petit-déjeuner
```

**Appel d'outil:** `nutrition-analyzer`
```json
{
  "meal_description": "J'ai mangé des flocons d'avoine avec des myrtilles et du beurre d'amande pour le petit-déjeuner"
}
```

**Réponse de l'outil:**
```json
{
  "total_nutrition": {
    "calories": 332,
    "protein_g": 11,
    "carbs_g": 48,
    "fat_g": 11,
    "fiber_g": 9,
    "sodium_mg": 156
  },
  "macro_percentages": {
    "protein_pct": 11,
    "carbs_pct": 58,
    "fat_pct": 31
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excellente source de vitamine C grâce aux fruits"
    },
    {
      "type": "positive",
      "message": "Excellente teneur en fibres grâce aux céréales complètes"
    },
    {
      "type": "recommendation",
      "message": "Les protéines sont un peu faibles (11%). Pensez à ajouter du yaourt grec ou un œuf pour atteindre 15-30%"
    }
  ],
  "follow_up": "Qu'avez-vous prévu pour le déjeuner?"
}
```

**Réponse de l'agent:**
```
Excellent choix de petit-déjeuner! Voici votre bilan nutritionnel:

📊 **Résumé nutritionnel:**
- Calories: 332
- Protéines: 11g (11%)
- Glucides: 48g (58%)
- Lipides: 11g (31%)
- Fibres: 9g
- Sodium: 156mg

✅ **Observations:**
- Excellente source de vitamine C grâce aux fruits
- Excellente teneur en fibres grâce aux céréales complètes
- Les protéines sont un peu faibles (11%). Pensez à ajouter du yaourt grec ou un œuf pour atteindre 15-30%

Qu'avez-vous prévu pour le déjeuner?
```

---

### Exemple 2: Collation de fruits

**Entrée utilisateur:**
```
Je viens de manger une pomme et une banane
```

**Appel d'outil:** `nutrition-analyzer`
```json
{
  "meal_description": "Je viens de manger une pomme et une banane"
}
```

**Réponse de l'outil:**
```json
{
  "total_nutrition": {
    "calories": 157,
    "protein_g": 2,
    "carbs_g": 41,
    "fat_g": 0,
    "fiber_g": 6,
    "sodium_mg": 2
  },
  "macro_percentages": {
    "protein_pct": 4,
    "carbs_pct": 94,
    "fat_pct": 2
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excellente source de vitamine C grâce aux fruits"
    },
    {
      "type": "recommendation",
      "message": "Très faible en protéines (4%). Ajoutez des noix, du fromage ou du yaourt pour une meilleure satiété"
    }
  ],
  "follow_up": "C'est une collation légère. Prévoyez-vous un repas bientôt?"
}
```

**Réponse de l'agent:**
```
Collation saine! Voici le bilan:

📊 **Résumé nutritionnel:**
- Calories: 157
- Protéines: 2g (4%)
- Glucides: 41g (94%)
- Lipides: 0g (2%)
- Fibres: 6g
- Sodium: 2mg

✅ **Observations:**
- Excellente source de vitamine C grâce aux fruits
- Très faible en protéines (4%). Ajoutez des noix, du fromage ou du yaourt pour une meilleure satiété

C'est une collation légère. Prévoyez-vous un repas bientôt?
```

---

### Exemple 3: Déjeuner riche en protéines

**Entrée utilisateur:**
```
J'ai mangé du poulet grillé, du quinoa et du brocoli pour le déjeuner
```

**Appel d'outil:** `nutrition-analyzer`
```json
{
  "meal_description": "J'ai mangé du poulet grillé, du quinoa et du brocoli pour le déjeuner"
}
```

**Réponse de l'outil:**
```json
{
  "total_nutrition": {
    "calories": 491,
    "protein_g": 42,
    "carbs_g": 47,
    "fat_g": 12,
    "fiber_g": 9,
    "sodium_mg": 133
  },
  "macro_percentages": {
    "protein_pct": 33,
    "carbs_pct": 37,
    "fat_pct": 30
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excellente teneur en protéines pour la santé musculaire"
    },
    {
      "type": "positive",
      "message": "Excellente source de vitamine C grâce aux légumes"
    },
    {
      "type": "positive",
      "message": "Macronutriments bien équilibrés - bravo!"
    }
  ],
  "follow_up": "Comment vous sentez-vous après ce repas?"
}
```

**Réponse de l'agent:**
```
Excellent choix de repas! Très bien équilibré. Voici votre bilan:

📊 **Résumé nutritionnel:**
- Calories: 491
- Protéines: 42g (33%)
- Glucides: 47g (37%)
- Lipides: 12g (30%)
- Fibres: 9g
- Sodium: 133mg

✅ **Observations:**
- Excellente teneur en protéines pour la santé musculaire
- Excellente source de vitamine C grâce aux légumes
- Macronutriments bien équilibrés - bravo!

Comment vous sentez-vous après ce repas?
```

---

## Spanish Examples

### Ejemplo 1: Desayuno equilibrado

**Entrada del usuario:**
```
Comí avena con arándanos y mantequilla de almendra para el desayuno
```

**Llamada a herramienta:** `nutrition-analyzer`
```json
{
  "meal_description": "Comí avena con arándanos y mantequilla de almendra para el desayuno"
}
```

**Respuesta de la herramienta:**
```json
{
  "total_nutrition": {
    "calories": 332,
    "protein_g": 11,
    "carbs_g": 48,
    "fat_g": 11,
    "fiber_g": 9,
    "sodium_mg": 156
  },
  "macro_percentages": {
    "protein_pct": 11,
    "carbs_pct": 58,
    "fat_pct": 31
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excelente fuente de vitamina C de las frutas"
    },
    {
      "type": "positive",
      "message": "Excelente contenido de fibra de los granos integrales"
    },
    {
      "type": "recommendation",
      "message": "La proteína está un poco baja (11%). Considere agregar yogur griego o un huevo para alcanzar 15-30%"
    }
  ],
  "follow_up": "¿Qué planea comer para el almuerzo?"
}
```

**Respuesta del agente:**
```
¡Excelente elección de desayuno! Aquí está su desglose nutricional:

📊 **Resumen nutricional:**
- Calorías: 332
- Proteína: 11g (11%)
- Carbohidratos: 48g (58%)
- Grasa: 11g (31%)
- Fibra: 9g
- Sodio: 156mg

✅ **Observaciones:**
- Excelente fuente de vitamina C de las frutas
- Excelente contenido de fibra de los granos integrales
- La proteína está un poco baja (11%). Considere agregar yogur griego o un huevo para alcanzar 15-30%

¿Qué planea comer para el almuerzo?
```

---

### Ejemplo 2: Merienda de frutas

**Entrada del usuario:**
```
Acabo de comer una manzana y un plátano
```

**Llamada a herramienta:** `nutrition-analyzer`
```json
{
  "meal_description": "Acabo de comer una manzana y un plátano"
}
```

**Respuesta de la herramienta:**
```json
{
  "total_nutrition": {
    "calories": 157,
    "protein_g": 2,
    "carbs_g": 41,
    "fat_g": 0,
    "fiber_g": 6,
    "sodium_mg": 2
  },
  "macro_percentages": {
    "protein_pct": 4,
    "carbs_pct": 94,
    "fat_pct": 2
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excelente fuente de vitamina C de las frutas"
    },
    {
      "type": "recommendation",
      "message": "Muy baja en proteína (4%). Agregue nueces, queso o yogur para mayor saciedad"
    }
  ],
  "follow_up": "Esta es una merienda ligera. ¿Planea comer una comida pronto?"
}
```

**Respuesta del agente:**
```
¡Merienda saludable! Aquí está el desglose:

📊 **Resumen nutricional:**
- Calorías: 157
- Proteína: 2g (4%)
- Carbohidratos: 41g (94%)
- Grasa: 0g (2%)
- Fibra: 6g
- Sodio: 2mg

✅ **Observaciones:**
- Excelente fuente de vitamina C de las frutas
- Muy baja en proteína (4%). Agregue nueces, queso o yogur para mayor saciedad

Esta es una merienda ligera. ¿Planea comer una comida pronto?
```

---

### Ejemplo 3: Almuerzo rico en proteínas

**Entrada del usuario:**
```
Comí pollo a la parrilla, quinoa y brócoli para el almuerzo
```

**Llamada a herramienta:** `nutrition-analyzer`
```json
{
  "meal_description": "Comí pollo a la parrilla, quinoa y brócoli para el almuerzo"
}
```

**Respuesta de la herramienta:**
```json
{
  "total_nutrition": {
    "calories": 491,
    "protein_g": 42,
    "carbs_g": 47,
    "fat_g": 12,
    "fiber_g": 9,
    "sodium_mg": 133
  },
  "macro_percentages": {
    "protein_pct": 33,
    "carbs_pct": 37,
    "fat_pct": 30
  },
  "insights": [
    {
      "type": "positive",
      "message": "Excelente contenido de proteína para la salud muscular"
    },
    {
      "type": "positive",
      "message": "Excelente fuente de vitamina C de los vegetales"
    },
    {
      "type": "positive",
      "message": "Macronutrientes bien equilibrados - ¡buen trabajo!"
    }
  ],
  "follow_up": "¿Cómo se siente después de esta comida?"
}
```

**Respuesta del agente:**
```
¡Excelente elección de comida! Muy bien equilibrada. Aquí está su desglose:

📊 **Resumen nutricional:**
- Calorías: 491
- Proteína: 42g (33%)
- Carbohidratos: 47g (37%)
- Grasa: 12g (30%)
- Fibra: 9g
- Sodio: 133mg

✅ **Observaciones:**
- Excelente contenido de proteína para la salud muscular
- Excelente fuente de vitamina C de los vegetales
- Macronutrientes bien equilibrados - ¡buen trabajo!

¿Cómo se siente después de esta comida?
```

---

## Notes for Agent Builder Configuration

**When adding these examples:**

1. **Format varies by UI version** - Some Agent Builder interfaces use:
   - Structured input/output fields
   - Free-form conversation text
   - JSON import

2. **Key elements to include:**
   - User's natural language input
   - Tool/function call with parameters
   - Tool response (JSON)
   - Agent's formatted response

3. **Why these examples matter:**
   - Show the agent the proper tool calling format (`meal_description` parameter)
   - Demonstrate how to pass user's natural language directly to the webhook
   - Teach response formatting with emojis and structure
   - Handle edge cases (unknown foods, quantities)

**Note:** The webhook parses natural language using `parse_meal_description()` function, so the agent just needs to pass the user's input through the `meal_description` parameter.

4. **Multi-language support:**
   - Examples show agent can understand French/Spanish inputs
   - Tool responses in examples show localized content (aspirational - actual webhook returns English currently)
   - Agent responses should match user's language
   - Note: The actual webhook currently returns English insights; these examples show the ideal multilingual behavior

5. **Best practice:**
   - Start with 3-5 English examples
   - Add French/Spanish if you plan to support those languages
   - Test each example in the simulator before deploying
