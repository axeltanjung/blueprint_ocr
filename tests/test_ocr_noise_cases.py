from ocr.preprocess import OCRPreprocessor


def test_numeric_noise_and_symbols():
    raw_ocr = """
    Ø 1O mm ± O.2
    A - 12
    """

    processor = OCRPreprocessor()
    cleaned = processor.preprocess(raw_ocr)

    assert "DIAMETER 10mm +/- 0.2" in cleaned
    assert "A - 12" not in cleaned  # noise line removed
