from nlp.extractor import construir_diccionario, extraer
def test_extractor_siglas_y_alias():
    d = construir_diccionario([(1, "SQL", "PostgreSQL"), (2, "C / C++ embebido", "C++")])
    assert [h for h, _ in extraer("Manejo de postgresql y c++", d)] == [1, 2]
def test_no_confunde_subcadenas():
    d = construir_diccionario([(1, "Git", "")])
    assert extraer("digital y digitalización", d) == []
