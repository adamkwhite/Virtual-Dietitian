"""
Unit tests for main.py
Tests multi-language meal description parsing and translation.
"""

from main import parse_meal_description


class TestParseMealDescriptionEnglish:
    """Test English meal description parsing."""

    def test_single_food_english(self):
        """Test parsing single English food item."""
        result = parse_meal_description("I had oatmeal")
        assert len(result) == 1
        assert result[0]["name"] == "oatmeal"
        assert result[0]["quantity"] == 1.0

    def test_multiple_foods_english(self):
        """Test parsing multiple English food items."""
        result = parse_meal_description("oatmeal with blueberries and banana")
        assert len(result) == 3
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names
        assert "blueberries" in food_names
        assert "banana" in food_names

    def test_two_word_phrase_english(self):
        """Test parsing two-word food phrases."""
        result = parse_meal_description("I had almond butter")
        assert len(result) == 1
        assert result[0]["name"] == "almond butter"

    def test_mixed_single_and_two_word(self):
        """Test parsing mix of single and two-word foods."""
        result = parse_meal_description("chicken breast with rice")
        food_names = [item["name"] for item in result]
        assert "chicken breast" in food_names
        assert "rice" in food_names


class TestParseMealDescriptionFrench:
    """Test French meal description parsing with translation."""

    def test_single_food_french(self):
        """Test parsing single French food item."""
        result = parse_meal_description("avoine")
        assert len(result) == 1
        assert result[0]["name"] == "oatmeal"

    def test_multiple_foods_french(self):
        """Test parsing multiple French food items."""
        result = parse_meal_description("avoine et myrtilles")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names
        assert "blueberries" in food_names

    def test_french_with_contractions(self):
        """Test French contractions (l'avoine, d'orange)."""
        result = parse_meal_description("J'ai mangé de l'avoine")
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names

    def test_french_full_sentence(self):
        """Test full French sentence."""
        result = parse_meal_description("J'ai mangé de l'avoine et des myrtilles")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names
        assert "blueberries" in food_names

    def test_french_poulet_et_riz(self):
        """Test French: poulet et riz → chicken and rice."""
        result = parse_meal_description("poulet et riz")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "chicken" in food_names
        assert "rice" in food_names

    def test_french_with_accents(self):
        """Test French words with special characters."""
        result = parse_meal_description("œuf et pomme")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "egg" in food_names
        assert "apple" in food_names

    def test_french_accent_variations(self):
        """Test French accent variations (œuf vs oeuf)."""
        result1 = parse_meal_description("œuf")
        result2 = parse_meal_description("oeuf")
        assert result1[0]["name"] == "egg"
        assert result2[0]["name"] == "egg"


class TestParseMealDescriptionSpanish:
    """Test Spanish meal description parsing with translation."""

    def test_single_food_spanish(self):
        """Test parsing single Spanish food item."""
        result = parse_meal_description("avena")
        assert len(result) == 1
        assert result[0]["name"] == "oatmeal"

    def test_multiple_foods_spanish(self):
        """Test parsing multiple Spanish food items."""
        result = parse_meal_description("avena y arándanos")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names
        assert "blueberries" in food_names

    def test_spanish_full_sentence(self):
        """Test full Spanish sentence."""
        result = parse_meal_description("Comí avena y arándanos")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names
        assert "blueberries" in food_names

    def test_spanish_pollo_y_arroz(self):
        """Test Spanish: pollo y arroz → chicken and rice."""
        result = parse_meal_description("pollo y arroz")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "chicken" in food_names
        assert "rice" in food_names

    def test_spanish_accent_variations(self):
        """Test Spanish accent variations (arándanos vs arandanos)."""
        result1 = parse_meal_description("arándanos")
        result2 = parse_meal_description("arandanos")
        assert result1[0]["name"] == "blueberries"
        assert result2[0]["name"] == "blueberries"

    def test_spanish_with_accents(self):
        """Test Spanish words with tildes."""
        result = parse_meal_description("plátano y manzana")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "banana" in food_names
        assert "apple" in food_names

    def test_spanish_accent_variations_platano(self):
        """Test plátano vs platano both work."""
        result1 = parse_meal_description("plátano")
        result2 = parse_meal_description("platano")
        assert result1[0]["name"] == "banana"
        assert result2[0]["name"] == "banana"


class TestParseMealDescriptionEdgeCases:
    """Test edge cases and mixed scenarios."""

    def test_unknown_food_passes_through(self):
        """Test unknown foods pass through to 3-tier fallback."""
        result = parse_meal_description("pizza")
        assert len(result) == 1
        assert result[0]["name"] == "pizza"

    def test_mixed_known_unknown(self):
        """Test mix of known and unknown foods (both pass through)."""
        result = parse_meal_description("chicken and pizza")
        assert len(result) == 2
        food_names = [item["name"] for item in result]
        assert "chicken" in food_names
        assert "pizza" in food_names

    def test_empty_string(self):
        """Test empty meal description."""
        result = parse_meal_description("")
        assert len(result) == 0

    def test_punctuation_handling(self):
        """Test that commas and periods are removed."""
        result = parse_meal_description("chicken, rice, and broccoli.")
        assert len(result) == 3
        food_names = [item["name"] for item in result]
        assert "chicken" in food_names
        assert "rice" in food_names
        assert "broccoli" in food_names

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        result1 = parse_meal_description("CHICKEN")
        result2 = parse_meal_description("chicken")
        result3 = parse_meal_description("Chicken")
        assert result1[0]["name"] == result2[0]["name"] == result3[0]["name"]

    def test_all_quantities_default_to_one(self):
        """Test that all parsed foods have quantity=1.0."""
        result = parse_meal_description("chicken rice broccoli")
        for item in result:
            assert item["quantity"] == 1.0

    def test_cnf_passthrough(self):
        """Test CNF foods (not in local DB) pass through to 3-tier fallback."""
        result = parse_meal_description("I ate gouda")
        assert len(result) == 1
        assert result[0]["name"] == "gouda"

    def test_stopwords_filtered(self):
        """Test stopwords are filtered from passthrough."""
        result = parse_meal_description("I had some cheese")
        # Should find: cheese (local DB)
        # Should filter: I, had, some (all stopwords)
        assert len(result) == 1
        assert result[0]["name"] == "cheese"

    def test_short_words_filtered(self):
        """Test very short words (<3 chars) are filtered."""
        result = parse_meal_description("I ate an apple")
        # Should find: apple (local DB)
        # Should filter: I, ate, an (stopwords or too short)
        assert len(result) == 1
        assert result[0]["name"] == "apple"

    def test_mixed_local_and_cnf_foods(self):
        """Test mix of local DB and CNF foods both pass through."""
        result = parse_meal_description("oatmeal with gouda and crackers")
        # Should find: oatmeal (local DB), gouda (CNF), crackers (passthrough)
        assert len(result) >= 2
        food_names = [item["name"] for item in result]
        assert "oatmeal" in food_names
        assert "gouda" in food_names
