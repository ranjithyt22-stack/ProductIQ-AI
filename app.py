import gradio as gr
import fitz


def extract_pdf_text(pdf_file):
    if pdf_file is None:
        return "Please upload a PDF."

    try:
        document = fitz.open(pdf_file.name)

        pages = []

        for page_number, page in enumerate(document, start=1):
            text = page.get_text()

            if text.strip():
                pages.append(
                    f"\n========== PAGE {page_number} ==========\n{text}"
                )

        document.close()

        if not pages:
            return "No readable text found in this PDF."

        return "\n".join(pages)

    except Exception as e:
        return f"Error processing PDF: {str(e)}"


with gr.Blocks(title="ProductIQ AI") as demo:

    gr.Markdown(
        """
        # ProductIQ AI

        ### AI-Powered Product Intelligence for Industrial Commerce

        Upload an industrial product datasheet to extract its contents.
        """
    )

    pdf_input = gr.File(
        label="Upload Product Datasheet",
        file_types=[".pdf"],
        type="filepath"
    )

    analyze_button = gr.Button(
        "Extract Product Data",
        variant="primary"
    )

    output = gr.Textbox(
        label="Extracted Product Information",
        lines=25
    )

    analyze_button.click(
        fn=extract_pdf_text,
        inputs=pdf_input,
        outputs=output
    )


if __name__ == "__main__":
    demo.launch()