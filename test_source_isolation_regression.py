import unittest
from backend.state import product_state
from backend.ingestion.models import SourceDocument

def create_mock_doc(source_id, source_name, source_type="pdf"):
    return SourceDocument(
        source_id=source_id,
        source_type=source_type,
        source_name=source_name,
        content=f"Content for {source_name}",
        metadata={"filename": source_name}
    )

class TestSourceIsolation(unittest.TestCase):

    def test_pdf_a_then_pdf_b_replacement(self):
        """Verify uploading PDF A, then PDF B replaces PDF A in single-source mode."""
        product_state.reset()
        doc_a = create_mock_doc("doc_a", "ProductA.pdf")
        
        # 1. Upload PDF A
        product_state.add_sources([doc_a], replace=True)
        self.assertEqual(len(product_state.get_sources()), 1)
        self.assertEqual(product_state.get_sources()[0].source_name, "ProductA.pdf")
        
        # 2. Upload PDF B
        doc_b = create_mock_doc("doc_b", "ProductB.pdf")
        product_state.add_sources([doc_b], replace=True)
        
        sources = product_state.get_sources()
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].source_name, "ProductB.pdf")
        self.assertNotIn("ProductA.pdf", [s.source_name for s in sources])

    def test_url_a_then_url_b_replacement(self):
        """Verify URL A is replaced by URL B in single-source mode."""
        product_state.reset()
        url_a = create_mock_doc("url_a", "https://example.com/productA", source_type="url")
        product_state.add_sources([url_a], replace=True)
        
        url_b = create_mock_doc("url_b", "https://example.com/productB", source_type="url")
        product_state.add_sources([url_b], replace=True)
        
        sources = product_state.get_sources()
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].source_name, "https://example.com/productB")

    def test_multi_source_combination(self):
        """Verify PDF + URL + Text combination in multi-source mode."""
        product_state.reset()
        product_state.enable_multi_source()
        
        doc_pdf = create_mock_doc("pdf_1", "Datasheet.pdf", source_type="pdf")
        doc_url = create_mock_doc("url_1", "https://example.com/spec", source_type="url")
        doc_txt = create_mock_doc("txt_1", "Pasted specs", source_type="text")
        
        product_state.add_sources([doc_pdf], replace=False)
        product_state.add_sources([doc_url], replace=False)
        product_state.add_sources([doc_txt], replace=False)
        
        sources = product_state.get_sources()
        self.assertEqual(len(sources), 3)
        types = [s.source_type for s in sources]
        self.assertTrue("pdf" in types and "url" in types and "text" in types)

    def test_sample_to_user_pdf_isolation(self):
        """Verify switching from Sample PDF to User PDF purges sample references."""
        product_state.reset()
        sample_doc = create_mock_doc("sample", "sample_pneumatic_cylinder.pdf")
        product_state.add_sources([sample_doc], replace=True)
        
        user_doc = create_mock_doc("user_pdf", "UserCustomPump.pdf")
        product_state.add_sources([user_doc], replace=True)
        
        sources = product_state.get_sources()
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].source_name, "UserCustomPump.pdf")

if __name__ == "__main__":
    unittest.main()
